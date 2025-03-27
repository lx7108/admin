from gym import Env
from gym.spaces import Discrete, Box
import numpy as np
from app.ai.utils import build_state, compute_reward

class PvPArenaEnv(Env):
    def __init__(self, profile_1, profile_2):
        super().__init__()
        self.profiles = [profile_1, profile_2]
        self.turn = 0  # 轮流行动
        self.action_space = Discrete(5)  # 妥协 / 冲突 / 冷处理 / 威胁 / 哭诉
        self.observation_space = Box(low=0, high=1, shape=(18,), dtype=np.float32)
        self.states = [build_state(profile_1), build_state(profile_2)]

    def step(self, action):
        actor_id = self.turn
        profile = self.profiles[actor_id]
        state = self.states[actor_id]

        reward = compute_reward(profile, state, action)
        
        # 更新角色状态
        if action == 1:  # 冲突
            profile["emotion_state"]["anger"] += 0.1
            self.profiles[1-actor_id]["emotion_state"]["anger"] += 0.05
        elif action == 0:  # 妥协
            profile["emotion_state"]["joy"] += 0.05
            self.profiles[1-actor_id]["trust"] += 0.03
        
        # 更新状态向量
        self.states[actor_id] = build_state(profile)
        self.states[1-actor_id] = build_state(self.profiles[1-actor_id])
        
        # 交替行动
        self.turn = 1 - self.turn
        
        return self.states[actor_id], reward, False, {}

    def reset(self):
        self.turn = 0
        self.states = [build_state(self.profiles[0]), build_state(self.profiles[1])]
        return self.states[self.turn] 