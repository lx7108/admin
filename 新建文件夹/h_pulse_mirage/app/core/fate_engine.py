from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import math
import random
from app.schemas.destiny_schema import DestinyInput

def update_fate_score(character, destiny_data):
    """
    更新角色命运评分
    
    基于角色特性和事件性质，计算命运评分变动。影响因素包括：
    1. 事件类型和结果
    2. 角色人格特质
    3. 八字命理因素
    4. 历史行为积累
    
    Args:
        character: 角色对象
        destiny_data: 命运事件数据
        
    Returns:
        更新后的命运评分
    """
    # 当前评分（默认为0）
    current_score = character.fate_score or 0.0
    
    # 基础影响分数
    base_impact = 0.0
    
    # ===== 1. 事件类型影响 =====
    event_type_impacts = {
        "情感": 1.5,      # 情感事件影响较大
        "社会": 2.0,      # 社会事件影响最大
        "决策": 1.2,      # 决策影响中等
        "健康": 1.0,      # 健康影响标准
        "命理": 2.5       # 命理影响极大
    }
    
    # 获取事件类型影响系数
    event_multiplier = event_type_impacts.get(destiny_data.event_type, 1.0)
    
    # ===== 2. 事件结果分析 =====
    # 关键词分析以确定结果性质
    positive_keywords = ["成功", "获得", "解决", "拯救", "帮助", "收获", "提升", "胜利"]
    negative_keywords = ["失败", "损失", "背叛", "伤害", "错过", "降低", "失去", "危机"]
    
    result_score = 0.0
    
    # 统计正面/负面关键词
    positive_count = sum(1 for keyword in positive_keywords if keyword in destiny_data.result)
    negative_count = sum(1 for keyword in negative_keywords if keyword in destiny_data.result)
    
    # 基于关键词计算结果分数
    if positive_count > negative_count:
        result_score = 1.0 * (positive_count - negative_count * 0.5)
    else:
        result_score = -1.0 * (negative_count - positive_count * 0.5)
    
    # ===== 3. 人格特质影响 =====
    personality = character.personality
    
    # 事件与人格适配度分析
    personality_bonus = 0.0
    
    # 例如：高开放性和创新相关事件的匹配
    if "创新" in destiny_data.result or "探索" in destiny_data.result:
        personality_bonus += (personality.get("O", 0.5) - 0.5) * 2
    
    # 高尽责性和可靠/坚持相关事件的匹配
    if "坚持" in destiny_data.decision or "责任" in destiny_data.decision:
        personality_bonus += (personality.get("C", 0.5) - 0.5) * 2
    
    # 高外向性和社交/领导相关事件的匹配
    if "社交" in destiny_data.event_name or "领导" in destiny_data.event_name:
        personality_bonus += (personality.get("E", 0.5) - 0.5) * 2
    
    # ===== 4. 命理因素影响 =====
    # 根据出生时间判断当前时间是否处于有利五行
    birth_time = character.birth_time
    current_month = datetime.now().month
    
    # 简化版五行月份对应（实际应详细考虑命理学）
    month_wuxing = {
        # 春季-木
        3: "木", 4: "木", 
        # 夏季-火
        5: "火", 6: "火", 7: "火", 
        # 秋季-金
        8: "金", 9: "金", 10: "金",
        # 冬季-水
        11: "水", 12: "水", 1: "水", 2: "水"
    }
    
    current_wuxing = month_wuxing.get(current_month, "土")
    
    # 如果角色八字摘要中包含五行信息，则使用提取的数据
    fate_multiplier = 1.0
    if hasattr(character, 'bazi_summary') and character.bazi_summary:
        try:
            dominant_wuxing = character.bazi_summary.get("五行", {}).get("主导五行")
            
            # 判断当前季节五行是否与角色主导五行相生，相克或相同
            if dominant_wuxing:
                # 相同五行，增强效果
                if dominant_wuxing == current_wuxing:
                    fate_multiplier = 1.2
                # 相生关系，例如水生木、木生火等
                elif (dominant_wuxing == "水" and current_wuxing == "木") or \
                     (dominant_wuxing == "木" and current_wuxing == "火") or \
                     (dominant_wuxing == "火" and current_wuxing == "土") or \
                     (dominant_wuxing == "土" and current_wuxing == "金") or \
                     (dominant_wuxing == "金" and current_wuxing == "水"):
                    fate_multiplier = 1.1
                # 相克关系，例如水克火、火克金等
                elif (dominant_wuxing == "水" and current_wuxing == "火") or \
                     (dominant_wuxing == "火" and current_wuxing == "金") or \
                     (dominant_wuxing == "金" and current_wuxing == "木") or \
                     (dominant_wuxing == "木" and current_wuxing == "土") or \
                     (dominant_wuxing == "土" and current_wuxing == "水"):
                    fate_multiplier = 0.9
        except:
            # 如果提取失败，使用默认值
            fate_multiplier = 1.0
    
    # ===== 5. 综合计算 =====
    # 基础影响 = 结果评分 * 事件类型系数
    base_impact = result_score * event_multiplier
    
    # 添加人格特质影响
    base_impact += personality_bonus
    
    # 应用命理因素调整
    final_impact = base_impact * fate_multiplier
    
    # 增加一些随机波动（命运的不确定性）
    random_factor = random.uniform(0.9, 1.1)
    final_impact *= random_factor
    
    # 更新最终评分
    updated_score = current_score + final_impact
    
    # 确保分数在合理范围内 (0-100)
    updated_score = max(0, min(100, updated_score))
    
    return round(updated_score, 2)

def calculate_importance_score(destiny_node) -> float:
    """
    计算事件的重要性评分
    
    Args:
        destiny_node: 命运节点对象
        
    Returns:
        重要性评分 (0-10)
    """
    # 基础分
    base_score = destiny_node.impact_level if hasattr(destiny_node, 'impact_level') and destiny_node.impact_level else 5.0
    
    # 如果是关键事件，提高分数
    if hasattr(destiny_node, 'is_critical') and destiny_node.is_critical:
        base_score += 2.0
    
    # 分析事件描述和结果的重要性
    event_text = " ".join([
        destiny_node.event_name,
        destiny_node.decision if hasattr(destiny_node, 'decision') else "",
        destiny_node.result if hasattr(destiny_node, 'result') else ""
    ])
    
    # 重要性关键词列表
    critical_keywords = ["命运", "转折", "决定性", "生死", "重大", "关键", "永远", "灾难", "革命", "根本"]
    
    # 统计重要性关键词出现次数
    keyword_count = sum(1 for keyword in critical_keywords if keyword in event_text)
    keyword_bonus = min(2.0, keyword_count * 0.5)  # 最高加2分
    
    # 添加关键词奖励
    importance_score = base_score + keyword_bonus
    
    # 确保分数在0-10范围内
    return max(0, min(10, importance_score))

def predict_character_trend(character_id, db) -> Dict[str, Any]:
    """
    预测角色命运趋势
    
    Args:
        character_id: 角色ID
        db: 数据库会话
        
    Returns:
        命运趋势预测结果
    """
    # 获取角色最近的命运事件
    from app.models.destiny import DestinyNode
    
    recent_events = db.query(DestinyNode).filter(
        DestinyNode.character_id == character_id
    ).order_by(DestinyNode.timestamp.desc()).limit(5).all()
    
    if not recent_events:
        return {
            "trend": "平稳",
            "prediction": "缺乏足够数据进行预测",
            "confidence": 0.3
        }
    
    # 分析最近事件的得分变化趋势
    fate_changes = []
    for event in recent_events:
        # 计算该事件导致的命运分数变化
        if event.consequence and isinstance(event.consequence, dict):
            # 可以从事件后果中提取评分变化
            fate_delta = event.consequence.get("fate_score", 0)
            fate_changes.append(fate_delta)
    
    # 如果没有足够的命运变化数据，使用最近事件的结果性质
    if not fate_changes:
        positive_keywords = ["成功", "获得", "解决", "拯救", "帮助", "收获", "提升", "胜利"]
        negative_keywords = ["失败", "损失", "背叛", "伤害", "错过", "降低", "失去", "危机"]
        
        # 分析最近事件的结果
        positive_count = 0
        negative_count = 0
        
        for event in recent_events:
            result = event.result if hasattr(event, 'result') else ""
            positive_count += sum(1 for keyword in positive_keywords if keyword in result)
            negative_count += sum(1 for keyword in negative_keywords if keyword in result)
        
        # 根据正负面事件比例确定趋势
        if positive_count > negative_count * 1.5:
            trend = "上升"
            prediction = "基于最近的积极事件，命运可能呈现上升趋势"
            confidence = 0.7
        elif negative_count > positive_count * 1.5:
            trend = "下降"
            prediction = "基于最近的负面事件，命运可能呈现下降趋势"
            confidence = 0.7
        else:
            trend = "波动"
            prediction = "基于最近的混合事件，命运可能呈现波动状态"
            confidence = 0.5
    else:
        # 基于评分变化计算趋势
        avg_change = sum(fate_changes) / len(fate_changes)
        
        if avg_change > 1.0:
            trend = "明显上升"
            prediction = "命运呈现明显上升趋势，积极事件增多"
            confidence = 0.8
        elif avg_change > 0.2:
            trend = "小幅上升"
            prediction = "命运呈现小幅上升趋势，有利发展"
            confidence = 0.7
        elif avg_change < -1.0:
            trend = "明显下降"
            prediction = "命运呈现明显下降趋势，需谨慎应对"
            confidence = 0.8
        elif avg_change < -0.2:
            trend = "小幅下降"
            prediction = "命运呈现小幅下降趋势，需调整策略"
            confidence = 0.7
        else:
            trend = "基本平稳"
            prediction = "命运趋势基本平稳，维持现状"
            confidence = 0.6
    
    return {
        "trend": trend,
        "prediction": prediction,
        "confidence": confidence
    } 