import torch
import torch.optim as optim
from app.ai.policy_model import PolicyNetwork
from torch.distributions import Categorical

class PPOTrainer:
    def __init__(self, env, gamma=0.99, lr=2.5e-4, clip=0.2):
        self.env = env
        self.gamma = gamma
        self.clip = clip
        self.policy = PolicyNetwork()
        self.optimizer = optim.Adam(self.policy.parameters(), lr=lr)

    def train(self, episodes=2000):
        for ep in range(episodes):
            states, actions, rewards, dones, log_probs = [], [], [], [], []
            state = self.env.reset()

            for _ in range(100):
                state_tensor = torch.FloatTensor(state)
                logits, value = self.policy(state_tensor)
                dist = Categorical(logits=logits)
                action = dist.sample()
                log_prob = dist.log_prob(action)

                next_state, reward, done, _ = self.env.step(action.item())

                states.append(state_tensor)
                actions.append(action)
                rewards.append(reward)
                log_probs.append(log_prob)
                dones.append(done)

                state = next_state
                if done:
                    break

            self.update(states, actions, rewards, log_probs)
            
    def run_step(self):
        """执行单步行为并返回动作和奖励"""
        state = self.env.state
        state_tensor = torch.FloatTensor(state)
        
        with torch.no_grad():
            logits, _ = self.policy(state_tensor)
            dist = Categorical(logits=logits)
            action = dist.sample().item()
            
        next_state, reward, done, _ = self.env.step(action)
        return action, reward

    def update(self, states, actions, rewards, log_probs):
        returns = []
        G = 0
        for r in reversed(rewards):
            G = r + self.gamma * G
            returns.insert(0, G)
        returns = torch.tensor(returns)

        for i in range(len(states)):
            logits, value = self.policy(states[i])
            dist = Categorical(logits=logits)
            entropy = dist.entropy().mean()
            new_log_prob = dist.log_prob(actions[i])

            ratio = (new_log_prob - log_probs[i]).exp()
            advantage = returns[i] - value

            surr1 = ratio * advantage
            surr2 = torch.clamp(ratio, 1 - self.clip, 1 + self.clip) * advantage

            loss = -torch.min(surr1, surr2) + 0.5 * advantage.pow(2) - 0.01 * entropy
            self.optimizer.zero_grad()
            loss.mean().backward()
            self.optimizer.step() 