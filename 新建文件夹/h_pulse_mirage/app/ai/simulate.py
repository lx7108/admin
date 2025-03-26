from app.ai.environment import MirageEnv
from app.ai.ppo_trainer import PPOTrainer

def run_simulation(character_profile, steps=10):
    """
    使用角色配置文件运行行为模拟，返回行为序列和奖励
    """
    env = MirageEnv(character_profile)
    trainer = PPOTrainer(env)
    
    # 初步训练策略网络
    trainer.train(episodes=20)
    
    # 记录行为和奖励
    actions = []
    rewards = []
    
    # 执行模拟步骤
    for _ in range(steps):
        action, reward = trainer.run_step()
        actions.append(action)
        rewards.append(reward)
    
    action_names = {
        0: "合作",
        1: "欺骗",
        2: "索取",
        3: "退出",
        4: "反抗", 
        5: "牺牲"
    }
    
    results = [
        {"action": action_names.get(a, "未知"),
         "reward": r,
         "step": i} 
        for i, (a, r) in enumerate(zip(actions, rewards))
    ]
    
    return {
        "character_name": character_profile.get("name", "未命名角色"),
        "simulation_results": results,
        "final_score": sum(rewards)
    }

# 测试样例
sample_profile = {
    "name": "测试角色",
    "O": 0.7, "C": 0.6, "E": 0.4, "A": 0.5, "N": 0.3,
    "wuxing": {"金": 1, "木": 2, "水": 2, "火": 3, "土": 2},
    "emotion_state": {"joy": 0.5, "anger": 0.2, "sadness": 0.1, "fear": 0.2},
    "reputation": 0.4, "trust": 0.6, "wealth": 0.5, "status": 0.5
}

if __name__ == "__main__":
    result = run_simulation(sample_profile)
    print(result) 