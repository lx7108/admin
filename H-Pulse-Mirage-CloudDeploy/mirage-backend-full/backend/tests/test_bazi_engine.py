import pytest
from app.core.bazi_engine import (
    generate_bazi, analyze_wuxing_distribution, 
    get_wuxing_bias, fate_score_from_wuxing, 
    analyze_character_fate
)

def test_generate_bazi():
    """测试八字生成功能"""
    birth_time = "1997-07-16 11:50"
    bazi = generate_bazi(birth_time)
    
    # 确保生成了四柱
    assert "年柱" in bazi
    assert "月柱" in bazi
    assert "日柱" in bazi
    assert "时柱" in bazi
    
    # 确保每柱长度为2个字符（天干+地支）
    assert len(bazi["年柱"]) == 2
    assert len(bazi["月柱"]) == 2
    assert len(bazi["日柱"]) == 2
    assert len(bazi["时柱"]) == 2

def test_analyze_wuxing_distribution():
    """测试五行分布分析功能"""
    # 创建测试八字
    test_bazi = {
        "年柱": "丁丑",
        "月柱": "丁未",
        "日柱": "己未",
        "时柱": "庚午"
    }
    
    distribution = analyze_wuxing_distribution(test_bazi)
    
    # 确保五行类型都存在
    assert "金" in distribution
    assert "木" in distribution
    assert "水" in distribution
    assert "火" in distribution
    assert "土" in distribution
    
    # 测试是否八字中每个具体天干地支都正确影响了分布
    # 例如丁为火，在年月柱中出现了2次
    assert distribution["火"] >= 2

def test_get_wuxing_bias():
    """测试五行偏向分析功能"""
    test_distribution = {
        "金": 1.0,
        "木": 2.0,
        "水": 1.5,
        "火": 3.0,
        "土": 2.5
    }
    
    bias = get_wuxing_bias(test_distribution)
    
    # 确保返回了主导和短缺五行
    assert bias["主导五行"] == "火"
    assert bias["短缺五行"] == "金"
    
    # 确保返回了平衡度
    assert "平衡度" in bias
    assert bias["平衡度"] == 2.0  # 最大值(3.0) - 最小值(1.0)
    
    # 确保返回了相生相克关系
    assert "相生关系" in bias
    assert "相克关系" in bias

def test_fate_score_from_wuxing():
    """测试基于五行的命运评分功能"""
    test_analysis = {
        "主导五行": "木",
        "短缺五行": "金",
        "分布": {
            "金": 1.0,
            "木": 4.0,
            "水": 2.0,
            "火": 1.5,
            "土": 1.5
        },
        "平衡度": 3.0
    }
    
    score = fate_score_from_wuxing(test_analysis)
    
    # 确保分数在合理范围内
    assert 0 <= score <= 100
    
    # 测试木为主导时的特征
    assert score > 60  # 木主性格应该提高分数

def test_analyze_character_fate():
    """测试角色命运分析功能"""
    birth_str = "1997-07-16 11:50"
    analysis = analyze_character_fate(birth_str)
    
    # 验证分析结果包含预期的字段
    assert "八字排盘" in analysis
    assert "五行分析" in analysis
    assert "命运评分" in analysis
    assert "出生信息" in analysis
    assert "命格特点" in analysis
    
    # 验证命运评分在合理范围内
    assert 0 <= analysis["命运评分"] <= 100 