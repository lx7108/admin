from app.engine.causal_graph import CausalGraph
from app.models.character import Character
from sqlalchemy.orm import Session

def generate_fate_theater(event_id, db: Session):
    """
    生成命运剧场脚本
    
    Args:
        event_id: 事件ID（作为溯源起点）
        db: 数据库会话
        
    Returns:
        命运剧场脚本对象
    """
    # 构建因果图并溯源
    graph = CausalGraph(db)
    graph.build()
    path = graph.trace_path_to_root(event_id)
    
    if not path:
        return {"error": "找不到事件或无法构建路径"}

    # 构建脚本
    script = []
    for e in path:
        # 获取角色信息
        actor_char = db.query(Character).filter(Character.id == e.actor_id).first()
        actor_name = actor_char.name if actor_char else f"角色#{e.actor_id}"
        
        target_name = ""
        if e.target_id:
            target_char = db.query(Character).filter(Character.id == e.target_id).first()
            target_name = target_char.name if target_char else f"角色#{e.target_id}"
            target_string = f"对 {target_name}"
        else:
            target_string = ""
            
        # 构建场景描述
        result_str = str(e.result) if isinstance(e.result, str) else str(e.result.get("outcome", "未知结果"))
        scene = {
            "id": e.id,
            "actor": actor_name,
            "action": e.action,
            "target": target_string,
            "result": result_str,
            "timestamp": e.timestamp.strftime("%Y-%m-%d %H:%M"),
            "dialogue": _generate_dialogue(e, actor_name)
        }
        script.append(scene)

    # 预测未来可能性
    future_events = graph.predict_next_possible_events(event_id)
    
    return {
        "title": f"命运剧场：事件#{event_id}回溯",
        "scenes": script,
        "predictions": future_events,
        "visual": graph.to_visual_format()
    }

def _generate_dialogue(event, actor_name):
    """生成角色台词和内心独白"""
    # 根据事件类型和结果生成不同的台词
    action = event.action.lower() if event.action else ""
    
    if "背叛" in action:
        dialogue = "我别无选择，这是必须的牺牲。"
        inner_voice = "心中仍有愧疚，但命运已无回头路。"
    elif "合作" in action:
        dialogue = "我们一起面对，会找到解决的方法。"
        inner_voice = "希望这次合作能打破命运的枷锁。"
    elif "反抗" in action:
        dialogue = "我不会再屈服于这样的命运！"
        inner_voice = "内心充满恐惧，但不会再退缩。"
    else:
        dialogue = "这就是我的选择。"
        inner_voice = "不知道这是对是错，但我会承担后果。"
        
    return {
        "line": dialogue,
        "inner_voice": inner_voice,
        "actor": actor_name
    } 