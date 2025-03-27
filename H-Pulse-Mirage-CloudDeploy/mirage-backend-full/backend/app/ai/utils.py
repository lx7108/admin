import numpy as np

def build_state(profile: dict) -> np.ndarray:
    """
    构建状态向量：人格（5）+ 命理五行（5）+ 情绪（4）+ 社会变量（4）
    """
    state = []

    # 大五人格
    for trait in ["O", "C", "E", "A", "N"]:
        state.append(profile.get(trait, 0.5))

    # 命理五行偏向
    for element in ["金", "木", "水", "火", "土"]:
        state.append(profile.get("wuxing", {}).get(element, 0.2))

    # 情绪状态
    for e in ["joy", "anger", "sadness", "fear"]:
        state.append(profile.get("emotion_state", {}).get(e, 0.25))

    # 社会标签
    state.append(profile.get("reputation", 0.5))
    state.append(profile.get("trust", 0.5))
    state.append(profile.get("wealth", 0.5))
    state.append(profile.get("status", 0.5))

    return np.array(state, dtype=np.float32)

def compute_reward(profile, state, action):
    reward = 0.0
    if action == 0:  # 合作
        reward += state[10] * 2 + state[11]
    elif action == 1:  # 欺骗
        reward += 0.5 - state[11]
    elif action == 2:  # 索取
        reward += state[12] - 0.1
    elif action == 3:  # 退出
        reward -= 0.2
    elif action == 4:  # 反抗
        reward += state[13] - 0.3
    elif action == 5:  # 牺牲
        reward += (state[10] + state[11]) * 0.5 - 0.2
    return reward 