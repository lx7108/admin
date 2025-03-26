from app.pvp_arena.pvp_env import PvPArenaEnv
from app.ai.ppo_trainer import PPOTrainer
from app.pvp_arena.duel_logger import DuelLogger

def simulate_duel(profile1, profile2, rounds=10):
    """
    模拟两个角色的对抗互动
    
    Args:
        profile1, profile2: 角色配置文件
        rounds: 对抗回合数
        
    Returns:
        对抗记录对象，包含对抗流程和对白
    """
    env = PvPArenaEnv(profile1, profile2)
    trainer1 = PPOTrainer(env)
    trainer2 = PPOTrainer(env)

    # 初始训练
    trainer1.train(episodes=10)
    trainer2.train(episodes=10)

    logger = DuelLogger(profile1["id"], profile2["id"])

    # 交替行动
    for round_num in range(rounds):
        # 确定当前行动的训练器
        active_trainer = trainer1 if env.turn == 0 else trainer2
        action, reward = active_trainer.run_step()
        
        # 记录行动和结果
        logger.log(
            turn=env.turn, 
            action=action, 
            reward=reward,
            actor_name=profile1["name"] if env.turn == 0 else profile2["name"]
        )

    return logger.export() 