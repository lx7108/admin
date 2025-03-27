class DuelLogger:
    def __init__(self, id1, id2):
        self.log = []
        self.parties = [id1, id2]

    def log(self, turn, action, reward, actor_name=None):
        self.log.append({
            "actor": f"角色#{self.parties[turn]}",
            "actor_name": actor_name or f"角色#{self.parties[turn]}",
            "action": action,
            "reward": reward
        })

    def export(self):
        # 动作名称对应表
        action_names = {
            0: "妥协",
            1: "冲突",
            2: "冷处理",
            3: "威胁",
            4: "哭诉"
        }
        
        # 处理记录，将数字动作转为文本
        processed_logs = []
        for entry in self.log:
            processed_entry = entry.copy()
            action_num = entry["action"]
            processed_entry["action_name"] = action_names.get(action_num, "未知行为")
            processed_logs.append(processed_entry)
            
        dialogue = self._generate_dialogue(processed_logs)
            
        return {
            "title": f"命运对抗剧场#{self.parties[0]}vs{self.parties[1]}",
            "duel_flow": processed_logs,
            "dialogue": dialogue
        }
        
    def _generate_dialogue(self, logs):
        """生成对白"""
        dialogues = []
        
        for entry in logs:
            action_name = entry["action_name"]
            actor = entry["actor_name"]
            
            # 根据动作生成对白
            if action_name == "妥协":
                line = "也许我们还可以谈谈。"
            elif action_name == "冲突":
                line = "你根本不配站在这里！"
            elif action_name == "冷处理":
                line = "我暂时不会回应，但别以为我退让。"
            elif action_name == "威胁":
                line = "再有下次，我不会手软。"
            elif action_name == "哭诉":
                line = "你知道我也有我的苦衷…"
            else:
                line = "……"
                
            dialogues.append({
                "actor": actor,
                "line": line
            })
            
        return dialogues 