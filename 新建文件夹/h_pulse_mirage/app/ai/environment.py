import gym
from gym import spaces
import numpy as np
from app.ai.utils import build_state, compute_reward

class MirageEnv(gym.Env):
    def __init__(self, character_profile):
        super(MirageEnv, self).__init__()
        self.profile = character_profile
        self.max_steps = 100
        self.current_step = 0

        self.observation_space = spaces.Box(low=0, high=1, shape=(18,), dtype=np.float32)
        self.action_space = spaces.Discrete(6)  # 合作、欺骗、索取、退出、反抗、牺牲

        self.state = build_state(self.profile)
        self.done = False

    def step(self, action):
        self.current_step += 1
        reward = compute_reward(self.profile, self.state, action)
        self._update_profile(action)
        self.state = build_state(self.profile)

        if self.current_step >= self.max_steps:
            self.done = True

        return self.state, reward, self.done, {}

    def reset(self):
        self.current_step = 0
        self.done = False
        self.state = build_state(self.profile)
        return self.state

    def _update_profile(self, action):
        # 修改性格倾向、社会标签、情绪状态等
        if action == 1:  # 欺骗
            self.profile["trust"] -= 0.1
            self.profile["emotion_state"]["anger"] += 0.05
        elif action == 0:  # 合作
            self.profile["trust"] += 0.05
            self.profile["reputation"] += 0.05
        # 其他行为更新逻辑可扩展 