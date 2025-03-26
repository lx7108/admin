from collections import defaultdict
from app.models.causal_node import CausalEvent
from sqlalchemy.orm import Session

class CausalGraph:
    def __init__(self, db: Session):
        self.db = db
        self.graph = defaultdict(list)  # key: node_id, value: [children]
        self.events = {}

    def build(self):
        """构建因果图"""
        all_events = self.db.query(CausalEvent).all()
        for event in all_events:
            self.events[event.id] = event
            if event.origin_event:
                self.graph[event.origin_event].append(event.id)

    def trace_path_to_root(self, event_id):
        """向上溯源路径"""
        path = []
        current = self.events.get(event_id)
        while current and current.origin_event:
            path.append(current)
            current = self.events.get(current.origin_event)
        if current:
            path.append(current)
        return list(reversed(path))
    
    def get_children(self, event_id):
        """获取所有子事件"""
        return self.graph.get(event_id, [])

    def predict_next_possible_events(self, event_id, depth=3):
        """基于事件类型和人物性格模拟可能未来分支"""
        base_event = self.events.get(event_id)
        if not base_event:
            return []
            
        # 伪模拟，后续可接入 GPT 分支生成器
        predictions = []
        for i in range(depth):
            predictions.append({
                "based_on": base_event.id,
                "future_event": f"预测事件#{event_id + i + 1}：某角色将因{base_event.action}爆发冲突",
                "probability": 0.8 - i * 0.2  # 概率随时间递减
            })
        return predictions
    
    def to_visual_format(self):
        """转换为可视化格式（适用于D3.js）"""
        nodes = []
        links = []
        
        # 添加节点
        for event_id, event in self.events.items():
            nodes.append({
                "id": event_id,
                "label": f"事件#{event_id}: {event.action}",
                "type": "event"
            })
        
        # 添加连接
        for event_id, event in self.events.items():
            if event.origin_event:
                links.append({
                    "source": event.origin_event,
                    "target": event_id,
                    "value": 1
                })
                
        return {
            "nodes": nodes,
            "links": links
        } 