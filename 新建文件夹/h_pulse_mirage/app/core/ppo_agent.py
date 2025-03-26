import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
from typing import List, Dict, Tuple, Any, Optional
import random

# 定义PPO策略网络
class PPOPolicy(nn.Module):
    """
    PPO策略网络，包含两个输出头：动作概率（策略）和状态价值（价值）
    """
    def __init__(
        self, 
        state_dim: int, 
        action_dim: int, 
        hidden_dim: int = 64
    ):
        """
        初始化策略网络
        
        Args:
            state_dim: 状态维度
            action_dim: 动作维度
            hidden_dim: 隐藏层维度
        """
        super(PPOPolicy, self).__init__()
        
        # 共享特征提取器
        self.shared_layers = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh()
        )
        
        # 动作概率输出头
        self.actor_head = nn.Sequential(
            nn.Linear(hidden_dim, action_dim),
            nn.Softmax(dim=-1)
        )
        
        # 状态价值输出头
        self.critic_head = nn.Sequential(
            nn.Linear(hidden_dim, 1)
        )
    
    def forward(self, state: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        前向传播
        
        Args:
            state: 状态张量
            
        Returns:
            (动作概率分布, 状态价值) 元组
        """
        features = self.shared_layers(state)
        action_probs = self.actor_head(features)
        state_value = self.critic_head(features)
        
        return action_probs, state_value
    
    def get_action(self, state: np.ndarray, deterministic: bool = False) -> Tuple[int, float, np.ndarray]:
        """
        根据状态选择动作
        
        Args:
            state: 状态数组
            deterministic: 是否确定性选择（贪婪策略）
            
        Returns:
            (选择的动作, 动作的对数概率, 动作概率分布) 元组
        """
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        with torch.no_grad():
            action_probs, _ = self.forward(state_tensor)
            action_probs = action_probs.squeeze(0).numpy()
        
        if deterministic:
            # 贪婪策略，选择概率最高的动作
            action = np.argmax(action_probs)
        else:
            # 随机采样，探索环境
            action = np.random.choice(len(action_probs), p=action_probs)
        
        # 计算对数概率
        log_prob = np.log(action_probs[action] + 1e-10)
        
        return action, log_prob, action_probs

# 定义PPO智能体
class PPOAgent:
    """PPO强化学习智能体"""
    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        hidden_dim: int = 64,
        lr: float = 3e-4,
        gamma: float = 0.99,
        clip_ratio: float = 0.2,
        max_grad_norm: float = 0.5,
        value_coef: float = 0.5,
        entropy_coef: float = 0.01
    ):
        """
        初始化PPO智能体
        
        Args:
            state_dim: 状态维度
            action_dim: 动作维度
            hidden_dim: 隐藏层维度
            lr: 学习率
            gamma: 折扣因子
            clip_ratio: PPO裁剪比例
            max_grad_norm: 梯度裁剪最大范数
            value_coef: 价值损失系数
            entropy_coef: 熵正则化系数
        """
        self.policy = PPOPolicy(state_dim, action_dim, hidden_dim)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=lr)
        
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.clip_ratio = clip_ratio
        self.max_grad_norm = max_grad_norm
        self.value_coef = value_coef
        self.entropy_coef = entropy_coef
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.policy.to(self.device)
    
    def select_action(self, state: np.ndarray, deterministic: bool = False) -> Tuple[int, float, np.ndarray]:
        """
        根据状态选择动作
        
        Args:
            state: 状态数组
            deterministic: 是否确定性选择
            
        Returns:
            (选择的动作, 动作的对数概率, 动作概率分布) 元组
        """
        return self.policy.get_action(state, deterministic)
    
    def update_policy(
        self, 
        states: List[np.ndarray], 
        actions: List[int], 
        old_log_probs: List[float], 
        returns: List[float], 
        advantages: List[float], 
        epochs: int = 10
    ) -> Dict[str, float]:
        """
        使用PPO算法更新策略
        
        Args:
            states: 状态列表
            actions: 动作列表
            old_log_probs: 旧策略下的动作对数概率
            returns: 折扣累积回报
            advantages: 优势估计
            epochs: 训练轮次
            
        Returns:
            训练统计信息
        """
        # 转换为张量
        states_tensor = torch.FloatTensor(np.array(states)).to(self.device)
        actions_tensor = torch.LongTensor(actions).to(self.device)
        old_log_probs_tensor = torch.FloatTensor(old_log_probs).to(self.device)
        returns_tensor = torch.FloatTensor(returns).to(self.device)
        advantages_tensor = torch.FloatTensor(advantages).to(self.device)
        
        # 训练统计
        stats = {
            "policy_loss": 0.0,
            "value_loss": 0.0,
            "entropy": 0.0,
            "total_loss": 0.0,
            "clip_fraction": 0.0
        }
        
        # 多轮训练，提高样本利用率
        for _ in range(epochs):
            # 获取当前策略的动作概率和状态价值
            action_probs, state_values = self.policy(states_tensor)
            state_values = state_values.squeeze(-1)
            
            # 计算新策略下的动作概率
            dist = torch.distributions.Categorical(action_probs)
            new_log_probs = dist.log_prob(actions_tensor)
            entropy = dist.entropy().mean()
            
            # 计算策略比率
            ratios = torch.exp(new_log_probs - old_log_probs_tensor)
            
            # PPO-Clip 目标
            surr1 = ratios * advantages_tensor
            surr2 = torch.clamp(ratios, 1.0 - self.clip_ratio, 1.0 + self.clip_ratio) * advantages_tensor
            policy_loss = -torch.min(surr1, surr2).mean()
            
            # 价值损失
            value_loss = F.mse_loss(state_values, returns_tensor)
            
            # 总损失
            loss = policy_loss + self.value_coef * value_loss - self.entropy_coef * entropy
            
            # 优化一步
            self.optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(self.policy.parameters(), self.max_grad_norm)
            self.optimizer.step()
            
            # 统计剪裁比例
            clip_fraction = ((ratios < 1.0 - self.clip_ratio) | (ratios > 1.0 + self.clip_ratio)).float().mean().item()
            
            # 更新统计信息
            stats["policy_loss"] += policy_loss.item() / epochs
            stats["value_loss"] += value_loss.item() / epochs
            stats["entropy"] += entropy.item() / epochs
            stats["total_loss"] += loss.item() / epochs
            stats["clip_fraction"] += clip_fraction / epochs
        
        return stats
    
    def compute_returns_and_advantages(
        self, 
        rewards: List[float], 
        values: List[float], 
        next_value: float, 
        dones: List[bool],
        gamma: Optional[float] = None,
        gae_lambda: float = 0.95
    ) -> Tuple[List[float], List[float]]:
        """
        计算折扣累积回报和广义优势估计(GAE)
        
        Args:
            rewards: 奖励列表
            values: 价值估计列表
            next_value: 下一状态的价值估计
            dones: 终止状态标志列表
            gamma: 折扣因子，如果为None则使用智能体默认值
            gae_lambda: GAE平滑参数
            
        Returns:
            (returns, advantages) 元组
        """
        gamma = gamma or self.gamma
        returns = []
        advantages = []
        gae = 0
        
        # 从后向前计算
        for t in reversed(range(len(rewards))):
            if t == len(rewards) - 1:
                next_non_terminal = 1.0 - dones[-1]
                next_return = next_value
            else:
                next_non_terminal = 1.0 - dones[t+1]
                next_return = returns[0]
            
            # 计算TD目标
            delta = rewards[t] + gamma * next_value * next_non_terminal - values[t]
            
            # 计算GAE
            gae = delta + gamma * gae_lambda * next_non_terminal * gae
            
            # 插入到列表开头
            returns.insert(0, gae + values[t])
            advantages.insert(0, gae)
        
        return returns, advantages
    
    def save_model(self, path: str):
        """
        保存模型到文件
        
        Args:
            path: 保存路径
        """
        torch.save({
            "policy_state_dict": self.policy.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "state_dim": self.state_dim,
            "action_dim": self.action_dim
        }, path)
        
    @classmethod
    def load_model(cls, path: str, device: str = None):
        """
        从文件加载模型
        
        Args:
            path: 模型文件路径
            device: 设备（"cpu"或"cuda"）
            
        Returns:
            加载的PPOAgent实例
        """
        checkpoint = torch.load(path, map_location=device)
        agent = cls(
            state_dim=checkpoint["state_dim"],
            action_dim=checkpoint["action_dim"]
        )
        agent.policy.load_state_dict(checkpoint["policy_state_dict"])
        agent.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        return agent


class CharacterEnvironment:
    """
    角色行为环境，提供PPO智能体交互的接口
    
    环境包括:
    - 状态: 角色属性、情绪状态、社会状态等
    - 动作: 角色可执行的行为选择
    - 奖励: 根据行为产生的后果给予奖励或惩罚
    """
    def __init__(
        self, 
        character_profile: Dict[str, Any],
        action_space: List[str] = None,
        max_steps: int = 100
    ):
        """
        初始化角色环境
        
        Args:
            character_profile: 角色属性配置
            action_space: 可选行为空间
            max_steps: 最大步数限制
        """
        self.character = character_profile
        
        # 默认行为空间
        self.action_space = action_space or [
            "合作", "竞争", "冒险", "保守", 
            "说服", "威胁", "逃避", "对抗",
            "礼让", "强硬"
        ]
        
        self.action_dim = len(self.action_space)
        self.max_steps = max_steps
        self.current_step = 0
        
        # 初始化状态
        self.reset()
    
    def get_state_dim(self) -> int:
        """
        获取状态向量维度
        
        Returns:
            状态向量维度
        """
        return len(self.get_state_vector())
    
    def get_state_vector(self) -> np.ndarray:
        """
        将当前状态转换为向量表示
        
        Returns:
            状态向量
        """
        # 基本属性
        attrs = [
            self.state.get("health", 0.5),
            self.state.get("energy", 0.5),
            self.state.get("wealth", 0.5),
            self.state.get("reputation", 0.5),
            self.state.get("happiness", 0.5),
            self.state.get("stress", 0.5),
            self.state.get("trust", 0.5)
        ]
        
        # 性格特质 (大五人格)
        personality = [
            self.character.get("O", 0.5),  # 开放性
            self.character.get("C", 0.5),  # 尽责性
            self.character.get("E", 0.5),  # 外向性
            self.character.get("A", 0.5),  # 宜人性
            self.character.get("N", 0.5)   # 神经质
        ]
        
        # 情绪状态
        emotions = [
            self.state["emotions"].get("joy", 0.25),
            self.state["emotions"].get("anger", 0.25),
            self.state["emotions"].get("sadness", 0.25),
            self.state["emotions"].get("fear", 0.25)
        ]
        
        # 当前环境压力
        env_state = [
            self.state["environment"].get("threat_level", 0.0),
            self.state["environment"].get("opportunity", 0.0),
            self.state["environment"].get("social_pressure", 0.0),
            self.state["environment"].get("time_pressure", 0.0)
        ]
        
        # 归一化步数
        step_progress = [self.current_step / self.max_steps]
        
        # 合并所有特征
        return np.array(attrs + personality + emotions + env_state + step_progress, dtype=np.float32)
    
    def reset(self) -> np.ndarray:
        """
        重置环境到初始状态
        
        Returns:
            初始状态向量
        """
        # 重置步数
        self.current_step = 0
        
        # 初始化状态
        self.state = {
            # 基本属性
            "health": 1.0,
            "energy": 1.0,
            "wealth": self.character.get("wealth", 0.5),
            "reputation": self.character.get("reputation", 0.5),
            "happiness": 0.5,
            "stress": 0.1,
            "trust": self.character.get("trust", 0.5),
            
            # 情绪状态
            "emotions": {
                "joy": self.character.get("emotion_state", {}).get("joy", 0.25),
                "anger": self.character.get("emotion_state", {}).get("anger", 0.25),
                "sadness": self.character.get("emotion_state", {}).get("sadness", 0.25),
                "fear": self.character.get("emotion_state", {}).get("fear", 0.25)
            },
            
            # 环境状态
            "environment": {
                "threat_level": 0.1,
                "opportunity": 0.3,
                "social_pressure": 0.2,
                "time_pressure": 0.1
            },
            
            # 历史记录
            "history": []
        }
        
        # 返回初始状态向量
        return self.get_state_vector()
    
    def step(self, action_idx: int) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """
        执行动作并更新环境
        
        Args:
            action_idx: 动作索引
            
        Returns:
            (下一状态, 奖励, 是否终止, 信息字典) 元组
        """
        action = self.action_space[action_idx]
        self.current_step += 1
        
        # 根据角色性格和动作计算结果
        outcome, reward = self._calculate_outcome(action)
        
        # 更新状态
        self._update_state(action, outcome)
        
        # 记录历史
        self.state["history"].append({
            "step": self.current_step,
            "action": action,
            "outcome": outcome,
            "reward": reward
        })
        
        # 检查是否终止
        done = self.current_step >= self.max_steps or self.state["health"] <= 0
        
        return self.get_state_vector(), reward, done, {"outcome": outcome, "action": action}
    
    def _calculate_outcome(self, action: str) -> Tuple[str, float]:
        """
        根据动作和角色特性计算结果和奖励
        
        Args:
            action: 动作名称
            
        Returns:
            (结果描述, 奖励值) 元组
        """
        # 获取角色特质和当前状态
        o = self.character.get("O", 0.5)  # 开放性
        c = self.character.get("C", 0.5)  # 尽责性
        e = self.character.get("E", 0.5)  # 外向性
        a = self.character.get("A", 0.5)  # 宜人性
        n = self.character.get("N", 0.5)  # 神经质
        
        threat = self.state["environment"]["threat_level"]
        opportunity = self.state["environment"]["opportunity"]
        
        # 基础结果概率
        success_prob = 0.5
        
        # 根据动作和性格特质调整成功概率
        if action == "合作":
            success_prob += 0.2 * a - 0.1 * n  # 宜人性增加成功率，神经质降低
            success_prob += 0.1 if opportunity > 0.5 else -0.1  # 机会多时更容易成功
        elif action == "竞争":
            success_prob += 0.2 * c - 0.1 * a  # 尽责性增加成功率，过于宜人降低
            success_prob -= 0.1 if threat > 0.5 else 0  # 威胁高时风险更大
        elif action == "冒险":
            success_prob += 0.3 * o - 0.2 * c  # 开放性增加成功率，过于谨慎降低
            success_prob += 0.2 if opportunity > 0.7 else -0.1  # 高机会时更有价值
        elif action == "保守":
            success_prob += 0.2 * c - 0.1 * o  # 尽责性增加成功率，过于开放降低
            success_prob += 0.1 if threat > 0.5 else -0.1  # 高威胁时更有价值
        elif action == "说服":
            success_prob += 0.3 * e + 0.1 * a  # 外向性和宜人性增加说服力
        elif action == "威胁":
            success_prob += 0.2 * (1-a) - 0.1 * e  # 低宜人性增加威胁效果
        elif action == "逃避":
            success_prob += 0.3 * n - 0.1 * c  # 神经质增加逃避成功率
            success_prob += 0.2 if threat > 0.7 else 0  # 高威胁时逃避更合理
        elif action == "对抗":
            success_prob += 0.2 * (1-a) + 0.1 * c  # 低宜人性和高尽责增加对抗效果
        elif action == "礼让":
            success_prob += 0.3 * a  # 宜人性增加礼让效果
        elif action == "强硬":
            success_prob += 0.2 * (1-a) + 0.1 * n  # 低宜人性增加强硬效果
        
        # 确保概率在[0.1, 0.9]范围内
        success_prob = max(0.1, min(0.9, success_prob))
        
        # 随机决定是否成功
        success = random.random() < success_prob
        
        # 根据动作和结果确定奖励
        reward = 0.0
        
        # 为每种动作定义成功和失败的结果与奖励
        if action == "合作":
            if success:
                outcome = "成功建立了合作关系"
                reward = 1.5
            else:
                outcome = "合作尝试被拒绝"
                reward = -0.5
        elif action == "竞争":
            if success:
                outcome = "在竞争中获胜"
                reward = 2.0
            else:
                outcome = "竞争失败"
                reward = -1.0
        elif action == "冒险":
            if success:
                outcome = "冒险带来丰厚回报"
                reward = 2.5
            else:
                outcome = "冒险失败，损失惨重"
                reward = -2.0
        elif action == "保守":
            if success:
                outcome = "谨慎行事，避免风险"
                reward = 0.5
            else:
                outcome = "过于保守，错失机会"
                reward = -0.5
        elif action == "说服":
            if success:
                outcome = "成功说服对方"
                reward = 1.0
            else:
                outcome = "说服失败"
                reward = -0.5
        elif action == "威胁":
            if success:
                outcome = "威胁奏效，对方屈服"
                reward = 1.0
            else:
                outcome = "威胁失败，关系恶化"
                reward = -1.5
        elif action == "逃避":
            if success:
                outcome = "成功避开危险"
                reward = 0.5
            else:
                outcome = "无法逃避，必须面对"
                reward = -1.0
        elif action == "对抗":
            if success:
                outcome = "成功击败对手"
                reward = 1.5
            else:
                outcome = "对抗失败，遭受反击"
                reward = -1.5
        elif action == "礼让":
            if success:
                outcome = "礼让赢得尊重"
                reward = 0.5
            else:
                outcome = "礼让被视为软弱"
                reward = -0.5
        elif action == "强硬":
            if success:
                outcome = "强硬态度达成目标"
                reward = 1.0
            else:
                outcome = "强硬引发冲突"
                reward = -1.0
        
        # 根据角色特质调整奖励
        # 例如：开放性高的角色更喜欢冒险，宜人性高的角色更喜欢合作
        if action == "冒险":
            reward += (o - 0.5) * 0.5
        elif action == "合作" or action == "礼让":
            reward += (a - 0.5) * 0.5
        elif action == "竞争" or action == "强硬":
            reward += ((1-a) - 0.5) * 0.5
        
        return outcome, reward
    
    def _update_state(self, action: str, outcome: str):
        """
        根据动作和结果更新状态
        
        Args:
            action: 执行的动作
            outcome: 结果描述
        """
        # 更新基本属性
        # 失败结果会降低状态值
        if "失败" in outcome or "错失" in outcome or "损失" in outcome:
            self.state["energy"] = max(0.1, self.state["energy"] - 0.1)
            self.state["happiness"] = max(0.1, self.state["happiness"] - 0.1)
            self.state["stress"] = min(1.0, self.state["stress"] + 0.1)
        
        # 成功结果会提高状态值
        if "成功" in outcome or "获胜" in outcome or "回报" in outcome:
            self.state["happiness"] = min(1.0, self.state["happiness"] + 0.1)
            self.state["reputation"] = min(1.0, self.state["reputation"] + 0.05)
            self.state["stress"] = max(0.0, self.state["stress"] - 0.05)
        
        # 特定动作的特殊效果
        if action == "合作" and "成功" in outcome:
            self.state["trust"] = min(1.0, self.state["trust"] + 0.1)
            self.state["reputation"] = min(1.0, self.state["reputation"] + 0.1)
        
        if action == "冒险" and "回报" in outcome:
            self.state["wealth"] = min(1.0, self.state["wealth"] + 0.2)
        elif action == "冒险" and "损失" in outcome:
            self.state["wealth"] = max(0.0, self.state["wealth"] - 0.15)
        
        if "反击" in outcome or "冲突" in outcome:
            self.state["health"] = max(0.1, self.state["health"] - 0.1)
        
        # 更新情绪状态
        if "成功" in outcome or "获胜" in outcome or "回报" in outcome:
            self.state["emotions"]["joy"] = min(1.0, self.state["emotions"]["joy"] + 0.1)
            self.state["emotions"]["fear"] = max(0.0, self.state["emotions"]["fear"] - 0.05)
        
        if "失败" in outcome or "拒绝" in outcome:
            self.state["emotions"]["sadness"] = min(1.0, self.state["emotions"]["sadness"] + 0.1)
            self.state["emotions"]["joy"] = max(0.0, self.state["emotions"]["joy"] - 0.05)
        
        if "冲突" in outcome or "反击" in outcome:
            self.state["emotions"]["anger"] = min(1.0, self.state["emotions"]["anger"] + 0.15)
        
        if "危险" in outcome:
            self.state["emotions"]["fear"] = min(1.0, self.state["emotions"]["fear"] + 0.15)
        
        # 随机更新环境状态，模拟环境变化
        self.state["environment"]["threat_level"] = max(0.0, min(1.0, 
            self.state["environment"]["threat_level"] + random.uniform(-0.1, 0.1)))
        self.state["environment"]["opportunity"] = max(0.0, min(1.0, 
            self.state["environment"]["opportunity"] + random.uniform(-0.1, 0.1)))
        self.state["environment"]["social_pressure"] = max(0.0, min(1.0, 
            self.state["environment"]["social_pressure"] + random.uniform(-0.1, 0.1)))
        self.state["environment"]["time_pressure"] = min(1.0, 
            self.state["environment"]["time_pressure"] + 0.05)  # 时间压力随步数增加 