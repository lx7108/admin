from datetime import datetime, timedelta
import math
from typing import Dict, List, Tuple, Optional, Any

# 基础数据表
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 天干五行
TIANGAN_WUXING = {
    "甲": "木", "乙": "木",
    "丙": "火", "丁": "火",
    "戊": "土", "己": "土",
    "庚": "金", "辛": "金",
    "壬": "水", "癸": "水"
}

# 地支五行（主气为主）
DIZHI_WUXING = {
    "子": "水", "丑": "土",
    "寅": "木", "卯": "木",
    "辰": "土", "巳": "火",
    "午": "火", "未": "土",
    "申": "金", "酉": "金",
    "戌": "土", "亥": "水"
}

# 地支藏干（每个地支中还藏有天干）
DIZHI_CANGGAN = {
    "子": ["癸"],
    "丑": ["己", "癸", "辛"],
    "寅": ["甲", "丙", "戊"],
    "卯": ["乙"],
    "辰": ["戊", "乙", "癸"],
    "巳": ["丙", "庚", "戊"],
    "午": ["丁", "己"],
    "未": ["己", "丁", "乙"],
    "申": ["庚", "壬", "戊"],
    "酉": ["辛"],
    "戌": ["戊", "辛", "丁"],
    "亥": ["壬", "甲"]
}

# 干支阴阳（阳 True，阴 False）
GAN_YANG = {"甲": True, "乙": False, "丙": True, "丁": False, "戊": True, 
           "己": False, "庚": True, "辛": False, "壬": True, "癸": False}
ZHI_YANG = {"子": False, "丑": True, "寅": False, "卯": True, "辰": False, 
           "巳": True, "午": False, "未": True, "申": False, "酉": True, 
           "戌": False, "亥": True}

# 五行相生相克
WUXING_SHENG = {
    "木": "火",
    "火": "土",
    "土": "金",
    "金": "水",
    "水": "木"
}

WUXING_KE = {
    "木": "土",
    "土": "水",
    "水": "火",
    "火": "金",
    "金": "木"
}

# 天干地支相合
TIANGAN_HE = {
    ("甲", "己"): "土",
    ("乙", "庚"): "金",
    ("丙", "辛"): "水",
    ("丁", "壬"): "木",
    ("戊", "癸"): "火"
}

DIZHI_LIUHE = {
    ("子", "丑"): "土",
    ("寅", "亥"): "木",
    ("卯", "戌"): "火",
    ("辰", "酉"): "金",
    ("巳", "申"): "水",
    ("午", "未"): "土"
}

# 地支三合（生成十二长生）
SANHE = {
    "寅巳申": "火",
    "亥卯未": "木",
    "子辰申": "金",
    "丑戌辰": "土"
}

# 节气表（简化版）
JIEQI = {
    (1, 6): "小寒", (1, 20): "大寒",
    (2, 4): "立春", (2, 19): "雨水",
    (3, 6): "惊蛰", (3, 21): "春分",
    (4, 5): "清明", (4, 20): "谷雨",
    (5, 6): "立夏", (5, 21): "小满",
    (6, 6): "芒种", (6, 21): "夏至",
    (7, 7): "小暑", (7, 23): "大暑",
    (8, 8): "立秋", (8, 23): "处暑",
    (9, 8): "白露", (9, 23): "秋分",
    (10, 8): "寒露", (10, 23): "霜降",
    (11, 7): "立冬", (11, 22): "小雪",
    (12, 7): "大雪", (12, 22): "冬至"
}

def get_ganzhi_index(year):
    """
    计算干支索引
    
    Args:
        year: 年份
        
    Returns:
        (天干索引, 地支索引) 元组
    """
    # 天干地支组合：60年轮回
    offset = (year - 1984) % 60
    tiangan_index = offset % 10
    dizhi_index = offset % 12
    return tiangan_index, dizhi_index

def get_month_ganzhi(year_gz, month):
    """
    计算月干支
    
    Args:
        year_gz: 年干支
        month: 月份
        
    Returns:
        月干支
    """
    # 从节气看是否需要调整月份
    # 简化版本，实际应考虑节气
    
    # 年干决定月干
    year_gan = year_gz[0]
    gan_idx = TIANGAN.index(year_gan)
    
    # 月干公式：（年干索引 * 2 + 月数）% 10
    month_gan_idx = (gan_idx * 2 + month) % 10
    
    # 月支固定对应
    month_zhi_idx = (month + 2) % 12
    
    return TIANGAN[month_gan_idx] + DIZHI[month_zhi_idx]

def find_jieqi_in_year(year):
    """
    计算指定年份的节气表
    （注：实际应使用天文算法，此处简化）
    
    Args:
        year: 年份
        
    Returns:
        节气字典，键为(月,日)，值为节气名
    """
    # 简化版本，固定节气日期（实际上每年会有1-2天误差）
    jieqi_dict = {key: value for key, value in JIEQI.items()}
    return jieqi_dict

def generate_bazi(birth_time: str) -> dict:
    """
    生成八字
    
    Args:
        birth_time: 出生时间，格式：'1997-07-16 11:50'
        
    Returns:
        八字字典，包含年柱、月柱、日柱、时柱
    """
    dt = datetime.strptime(birth_time, "%Y-%m-%d %H:%M")

    # 年柱
    tg_y, dz_y = get_ganzhi_index(dt.year)
    year_pillar = TIANGAN[tg_y] + DIZHI[dz_y]

    # 月柱（简化逻辑，实际应考虑节气）
    month_pillar = get_month_ganzhi(year_pillar, dt.month)

    # 日柱采用通用干支对照（简化）
    base_date = datetime(1900, 1, 31)
    delta_days = (dt - base_date).days
    tg_d = delta_days % 10
    dz_d = delta_days % 12
    day_pillar = TIANGAN[tg_d] + DIZHI[dz_d]

    # 时柱以日干 + 时辰计算（简化）
    hour = dt.hour
    dizhi_hour_index = hour // 2 % 12
    dz_h = DIZHI[dizhi_hour_index]
    tg_d_index = TIANGAN.index(day_pillar[0])
    tg_h_index = (tg_d_index * 2 + dizhi_hour_index) % 10
    hour_pillar = TIANGAN[tg_h_index] + dz_h

    return {
        "年柱": year_pillar,
        "月柱": month_pillar,
        "日柱": day_pillar,
        "时柱": hour_pillar
    }

def analyze_wuxing_distribution(bazi_dict):
    """
    分析八字中的五行分布
    
    Args:
        bazi_dict: 八字字典
        
    Returns:
        五行分布统计
    """
    counts = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
    
    # 天干五行分析
    for pillar in bazi_dict.values():
        tg = pillar[0]
        dz = pillar[1]
        
        # 天干主气五行
        tg_wx = TIANGAN_WUXING[tg]
        counts[tg_wx] += 1
        
        # 地支主气五行
        dz_wx = DIZHI_WUXING[dz]
        counts[dz_wx] += 1
        
        # 地支藏干五行（权重较低，此为简化版）
        for cang_gan in DIZHI_CANGGAN.get(dz, []):
            cang_wx = TIANGAN_WUXING[cang_gan]
            counts[cang_wx] += 0.5
    
    # 四柱相互作用
    # 天干相合
    for i, pillar1 in enumerate(bazi_dict.values()):
        for j, pillar2 in enumerate(bazi_dict.values()):
            if i < j:  # 避免重复计算
                tg1, tg2 = pillar1[0], pillar2[0]
                if (tg1, tg2) in TIANGAN_HE or (tg2, tg1) in TIANGAN_HE:
                    he_wx = TIANGAN_HE.get((tg1, tg2)) or TIANGAN_HE.get((tg2, tg1))
                    counts[he_wx] += 0.5
    
    # 地支六合
    for i, pillar1 in enumerate(bazi_dict.values()):
        for j, pillar2 in enumerate(bazi_dict.values()):
            if i < j:  # 避免重复计算
                zhi1, zhi2 = pillar1[1], pillar2[1]
                if (zhi1, zhi2) in DIZHI_LIUHE or (zhi2, zhi1) in DIZHI_LIUHE:
                    he_wx = DIZHI_LIUHE.get((zhi1, zhi2)) or DIZHI_LIUHE.get((zhi2, zhi1))
                    counts[he_wx] += 0.5
    
    # 将结果转为整数，提高可读性
    return {k: round(v, 1) for k, v in counts.items()}

def get_wuxing_bias(counts):
    """
    获取五行偏向
    
    Args:
        counts: 五行分布统计
        
    Returns:
        五行分析结果
    """
    dominant = max(counts, key=counts.get)
    weakest = min(counts, key=counts.get)
    
    # 计算五行平衡度（值越小越平衡）
    balance = max(counts.values()) - min(counts.values())
    
    # 分析相生相克关系
    sheng_relation = f"{dominant}生{WUXING_SHENG[dominant]}"
    ke_relation = f"{dominant}克{WUXING_KE[dominant]}"
    
    # 根据五行特点进行性格分析
    personality_traits = {
        "木": "创新、仁爱、决断、善变",
        "火": "热情、奔放、直率、冲动",
        "土": "稳重、保守、诚实、固执",
        "金": "坚毅、公正、理性、刚硬",
        "水": "智慧、灵活、随和、善变"
    }
    
    dominant_traits = personality_traits[dominant]
    
    # 返回分析结果
    return {
        "主导五行": dominant,
        "短缺五行": weakest,
        "分布": counts,
        "平衡度": balance,
        "相生关系": sheng_relation,
        "相克关系": ke_relation,
        "性格特点": dominant_traits
    }

def fate_score_from_wuxing(wuxing_analysis):
    """
    根据五行分析计算命运基本评分
    
    Args:
        wuxing_analysis: 五行分析结果
        
    Returns:
        命运基础评分
    """
    counts = wuxing_analysis["分布"]
    dominant = wuxing_analysis["主导五行"]
    weakest = wuxing_analysis["短缺五行"]
    balance = wuxing_analysis["平衡度"]
    
    # 基础分
    score = 60
    
    # 五行平衡度评分
    if balance >= 4:
        score -= 10  # 五行极偏，不稳定
    elif balance <= 1:
        score += 10  # 五行均衡，命局稳定
    
    # 主导五行评分
    if dominant == "木":
        score += 5  # 木主生长，有利于发展
    elif dominant == "火":
        score += 3  # 火主热情，利于社交
    elif dominant == "土":
        score += 0  # 土主稳定，平衡发展
    elif dominant == "金":
        score += 2  # 金主理性，利于事业
    elif dominant == "水":
        score += 4  # 水主智慧，利于智力发展
    
    # 短缺五行评分
    if weakest in ["土", "金"]:
        score -= 5  # 社会稳定性弱，事业基础不牢
    elif weakest == "水":
        score -= 3  # 智慧不足，应变能力弱
    elif weakest == "火":
        score -= 2  # 激情不足，社交能力弱
    elif weakest == "木":
        score -= 4  # 创新能力弱，成长性不足
    
    # 确保分数在合理范围内
    return max(0, min(100, round(score, 2)))

def analyze_character_fate(birth_str: str):
    """
    分析角色命运
    
    Args:
        birth_str: 出生时间字符串，格式：YYYY-MM-DD HH:MM
        
    Returns:
        完整的命运分析结果
    """
    # 生成八字
    bazi = generate_bazi(birth_str)
    
    # 分析五行分布
    wuxing_counts = analyze_wuxing_distribution(bazi)
    
    # 获取五行偏向
    wuxing = get_wuxing_bias(wuxing_counts)
    
    # 计算命运评分
    score = fate_score_from_wuxing(wuxing)
    
    # 提取出生年份用于进一步分析
    year = int(birth_str.split('-')[0])
    
    # 命运分析文本生成
    birth_year_gz = bazi["年柱"]
    birth_time_desc = f"出生于{year}年（{birth_year_gz}年）"
    
    # 命格特点总结
    characteristics = []
    if wuxing["平衡度"] <= 1:
        characteristics.append("五行均衡，命局稳定")
    elif wuxing["平衡度"] >= 4:
        characteristics.append(f"五行偏颇，{wuxing['主导五行']}旺而{wuxing['短缺五行']}弱")
    else:
        characteristics.append(f"{wuxing['主导五行']}较强，带来{wuxing['性格特点']}")
    
    # 组合返回结果
    return {
        "八字排盘": bazi,
        "五行分析": wuxing,
        "命运评分": score,
        "出生信息": birth_time_desc,
        "命格特点": "，".join(characteristics)
    } 