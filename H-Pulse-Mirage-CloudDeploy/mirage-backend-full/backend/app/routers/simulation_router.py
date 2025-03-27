from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import os
import json
import random
from datetime import datetime

from app.database import get_db
from app.models.character import Character
from app.core.ppo_agent import PPOAgent, CharacterEnvironment
from app.core.security import get_current_user
from app.models.user import User
from app.core.fate_engine import update_fate_score
from app.schemas.character_schema import CharacterSimulation
from app.config import settings

router = APIRouter()

# 共享智能体字典，用于避免重复加载模型
AGENT_CACHE = {}

@router.post("/character/{character_id}/simulate", response_model=CharacterSimulation)
def simulate_character_behavior(
    character_id: int = Path(..., gt=0),
    steps: int = Query(10, ge=1, le=100),
    deterministic: bool = Query(False),
    scenario: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    模拟角色行为决策
    
    基于角色特性和环境，模拟角色的行为决策序列
    
    Args:
        character_id: 角色ID
        steps: 模拟步数
        deterministic: 是否使用确定性策略（否则使用随机采样）
        scenario: 特定场景描述（可选）
        current_user: 当前已认证的用户
        db: 数据库会话
        
    Returns:
        角色行为模拟结果，包含行为序列和结果
        
    Raises:
        HTTPException: 如果角色不存在或无权访问
    """
    # 验证角色存在且归当前用户所有
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    if character.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权模拟此角色")
    
    # 获取角色配置
    profile = character.to_profile()
    
    # 初始化环境
    env = CharacterEnvironment(profile, max_steps=steps)
    
    # 根据场景调整环境
    if scenario:
        env = configure_scenario(env, scenario)
    
    # 获取或创建智能体
    agent = get_agent_for_character(character_id, env)
    
    # 执行模拟
    sim_results = run_simulation(agent, env, steps, deterministic)
    
    # 更新角色属性（可选，根据模拟结果更新角色状态）
    update_character_based_on_simulation(character, sim_results, db)
    
    return {
        "character_id": character_id,
        "name": character.name,
        "actions": sim_results["history"],
        "fate_delta": sim_results["fate_delta"]
    }

@router.post("/character/{character_id}/train", status_code=status.HTTP_200_OK)
def train_character_agent(
    character_id: int,
    episodes: int = Query(5, ge=1, le=50),
    steps_per_episode: int = Query(100, ge=10, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    训练角色行为模型
    
    针对特定角色，训练其行为决策模型
    
    Args:
        character_id: 角色ID
        episodes: 训练轮次
        steps_per_episode: 每轮步数
        current_user: 当前已认证的用户
        db: 数据库会话
        
    Returns:
        训练结果统计
        
    Raises:
        HTTPException: 如果角色不存在或无权访问
    """
    # 验证角色存在且归当前用户所有
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    if character.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权训练此角色模型")
    
    # 获取角色配置
    profile = character.to_profile()
    
    # 初始化环境
    env = CharacterEnvironment(profile, max_steps=steps_per_episode)
    
    # 训练智能体
    training_stats = train_agent(character_id, env, episodes=episodes, steps_per_episode=steps_per_episode)
    
    return {
        "character_id": character_id,
        "episodes_completed": episodes,
        "steps_per_episode": steps_per_episode,
        "final_episode_reward": training_stats["final_reward"],
        "avg_episode_length": training_stats["avg_length"],
        "reward_history": training_stats["reward_history"][-5:],  # 只返回最后5轮的奖励
        "message": "角色行为模型训练完成"
    }

@router.post("/characters/{character_id_1}/interact/{character_id_2}", response_model=Dict[str, Any])
def simulate_character_interaction(
    character_id_1: int,
    character_id_2: int,
    scenario: Optional[str] = None,
    interaction_rounds: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    模拟两个角色之间的互动
    
    基于两个角色的特性和行为模型，模拟它们之间的互动
    
    Args:
        character_id_1: 第一个角色ID
        character_id_2: 第二个角色ID
        scenario: 互动场景描述
        interaction_rounds: 互动轮次
        current_user: 当前已认证的用户
        db: 数据库会话
        
    Returns:
        角色互动记录，包含互动过程和结果
        
    Raises:
        HTTPException: 如果角色不存在或无权访问
    """
    # 验证角色存在且归当前用户所有
    char1 = db.query(Character).filter(Character.id == character_id_1).first()
    char2 = db.query(Character).filter(Character.id == character_id_2).first()
    
    if not char1 or not char2:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    if char1.user_id != current_user.id or char2.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问其中一个或两个角色")
    
    # 获取角色配置
    profile1 = char1.to_profile()
    profile2 = char2.to_profile()
    
    # 创建互动环境
    interaction_env = create_interaction_environment(profile1, profile2, scenario)
    
    # 获取智能体
    agent1 = get_agent_for_character(character_id_1, interaction_env)
    agent2 = get_agent_for_character(character_id_2, interaction_env)
    
    # 执行互动模拟
    interaction_results = simulate_agents_interaction(
        agent1, agent2, interaction_env, interaction_rounds
    )
    
    # 返回互动结果
    return {
        "character1": {
            "id": character_id_1,
            "name": char1.name,
            "actions": interaction_results["char1_actions"]
        },
        "character2": {
            "id": character_id_2,
            "name": char2.name,
            "actions": interaction_results["char2_actions"]
        },
        "outcome": interaction_results["outcome"],
        "relationship_change": interaction_results["relationship_change"]
    }

# 辅助函数
def get_agent_for_character(character_id: int, env) -> PPOAgent:
    """
    获取或创建角色的智能体
    
    Args:
        character_id: 角色ID
        env: 环境对象
        
    Returns:
        PPOAgent 智能体
    """
    global AGENT_CACHE
    
    # 检查缓存中是否已存在
    if character_id in AGENT_CACHE:
        return AGENT_CACHE[character_id]
    
    # 检查是否有保存的模型
    model_path = os.path.join(settings.STORAGE_PATH, f"agent_{character_id}.pt")
    if os.path.exists(model_path):
        # 加载现有模型
        agent = PPOAgent.load_model(model_path)
    else:
        # 创建新智能体
        state_dim = env.get_state_dim()
        action_dim = env.action_dim
        agent = PPOAgent(state_dim=state_dim, action_dim=action_dim)
    
    # 添加到缓存
    AGENT_CACHE[character_id] = agent
    return agent

def run_simulation(agent: PPOAgent, env, steps: int, deterministic: bool) -> Dict[str, Any]:
    """
    运行模拟
    
    Args:
        agent: 智能体
        env: 环境
        steps: 步数
        deterministic: 是否确定性
        
    Returns:
        模拟结果
    """
    # 重置环境
    state = env.reset()
    
    done = False
    rewards = []
    history = []
    
    for i in range(steps):
        if done:
            break
        
        # 选择动作
        action, log_prob, _ = agent.select_action(state, deterministic)
        
        # 执行动作
        next_state, reward, done, info = env.step(action)
        
        # 记录
        rewards.append(reward)
        history.append({
            "step": i,
            "action": env.action_space[action],
            "outcome": info["outcome"],
            "reward": reward
        })
        
        # 更新状态
        state = next_state
    
    # 计算命运影响
    total_reward = sum(rewards)
    fate_delta = total_reward / 10.0  # 缩放到合理范围
    
    return {
        "history": history,
        "total_reward": total_reward,
        "fate_delta": fate_delta,
        "final_state": env.state
    }

def train_agent(character_id: int, env, episodes: int, steps_per_episode: int) -> Dict[str, Any]:
    """
    训练智能体
    
    Args:
        character_id: 角色ID
        env: 环境
        episodes: 训练轮次
        steps_per_episode: 每轮步数
        
    Returns:
        训练统计信息
    """
    # 获取或创建智能体
    agent = get_agent_for_character(character_id, env)
    
    # 训练参数
    gamma = 0.99
    gae_lambda = 0.95
    update_epochs = 10
    
    # 训练统计
    reward_history = []
    episode_length_history = []
    
    for episode in range(episodes):
        # 收集轨迹
        states = []
        actions = []
        log_probs = []
        rewards = []
        dones = []
        values = []
        
        state = env.reset()
        episode_reward = 0
        episode_length = 0
        
        for _ in range(steps_per_episode):
            # 选择动作
            action, log_prob, action_probs = agent.select_action(state)
            
            # 获取状态价值估计
            with torch.no_grad():
                state_tensor = torch.FloatTensor(state).unsqueeze(0)
                _, value = agent.policy(state_tensor)
                value = value.item()
            
            # 执行动作
            next_state, reward, done, _ = env.step(action)
            
            # 存储轨迹
            states.append(state)
            actions.append(action)
            log_probs.append(log_prob)
            rewards.append(reward)
            dones.append(done)
            values.append(value)
            
            # 更新状态和统计
            state = next_state
            episode_reward += reward
            episode_length += 1
            
            if done:
                break
        
        # 计算最终状态的价值
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            _, last_value = agent.policy(state_tensor)
            last_value = last_value.item()
        
        # 计算回报和优势
        returns, advantages = agent.compute_returns_and_advantages(
            rewards, values, last_value, dones, gamma, gae_lambda
        )
        
        # 更新策略
        update_stats = agent.update_policy(
            states, actions, log_probs, returns, advantages, update_epochs
        )
        
        # 记录统计
        reward_history.append(episode_reward)
        episode_length_history.append(episode_length)
    
    # 保存模型
    os.makedirs(settings.STORAGE_PATH, exist_ok=True)
    model_path = os.path.join(settings.STORAGE_PATH, f"agent_{character_id}.pt")
    agent.save_model(model_path)
    
    # 更新缓存
    global AGENT_CACHE
    AGENT_CACHE[character_id] = agent
    
    return {
        "reward_history": reward_history,
        "final_reward": reward_history[-1] if reward_history else 0,
        "avg_length": sum(episode_length_history) / len(episode_length_history) if episode_length_history else 0,
        "policy_loss": update_stats["policy_loss"],
        "value_loss": update_stats["value_loss"],
        "entropy": update_stats["entropy"]
    }

def configure_scenario(env, scenario: str):
    """
    根据场景描述配置环境
    
    Args:
        env: 环境对象
        scenario: 场景描述
        
    Returns:
        配置后的环境
    """
    # 关键词分析和场景设置
    if "危险" in scenario or "威胁" in scenario or "战斗" in scenario:
        env.state["environment"]["threat_level"] = 0.8
        env.state["emotions"]["fear"] = 0.6
    
    if "机会" in scenario or "幸运" in scenario or "发现" in scenario:
        env.state["environment"]["opportunity"] = 0.8
        env.state["emotions"]["joy"] = 0.6
    
    if "紧急" in scenario or "限时" in scenario:
        env.state["environment"]["time_pressure"] = 0.8
    
    if "社交" in scenario or "人群" in scenario or "公众" in scenario:
        env.state["environment"]["social_pressure"] = 0.7
    
    if "愤怒" in scenario or "背叛" in scenario:
        env.state["emotions"]["anger"] = 0.7
    
    if "悲伤" in scenario or "损失" in scenario:
        env.state["emotions"]["sadness"] = 0.7
    
    return env

def update_character_based_on_simulation(character, sim_results, db):
    """
    根据模拟结果更新角色
    
    Args:
        character: 角色对象
        sim_results: 模拟结果
        db: 数据库会话
    """
    # 记录模拟时间
    character.last_simulation_date = datetime.utcnow()
    
    # 更新命运评分
    fate_delta = sim_results["fate_delta"]
    character.fate_score = max(0, min(100, character.fate_score + fate_delta))
    
    # 记录模拟事件（可选）
    if abs(fate_delta) > 1.0:
        from app.models.destiny import DestinyNode
        
        # 创建命运节点
        event_name = "行为模拟"
        if fate_delta > 0:
            event_name = "积极" + event_name
        else:
            event_name = "消极" + event_name
        
        event_type = "决策"
        
        # 提取最后一个有意义的行动
        last_action = next((act for act in reversed(sim_results["history"]) if act["reward"] != 0), None)
        decision = last_action["action"] if last_action else sim_results["history"][-1]["action"]
        result = last_action["outcome"] if last_action else sim_results["history"][-1]["outcome"]
        
        node = DestinyNode(
            character_id=character.id,
            event_name=event_name,
            event_type=event_type,
            decision=decision,
            result=result,
            consequence={"fate_score": fate_delta},
            description=f"角色行为模拟结果: {sim_results['total_reward']:.2f}",
            impact_level=abs(fate_delta)
        )
        
        db.add(node)
    
    db.commit()

def create_interaction_environment(profile1, profile2, scenario=None):
    """
    创建双角色互动环境
    
    Args:
        profile1: 第一个角色配置
        profile2: 第二个角色配置
        scenario: 互动场景
        
    Returns:
        互动环境
    """
    # 创建互动专用的环境
    interaction_actions = [
        "合作", "竞争", "妥协", "避让", 
        "分享", "保留", "攻击", "防御",
        "说服", "拒绝", "帮助", "忽视"
    ]
    
    # 使用第一个角色初始化环境
    env = CharacterEnvironment(profile1, action_space=interaction_actions)
    
    # 在环境中添加第二个角色信息
    env.other_character = profile2
    
    # 配置特定场景
    if scenario:
        env = configure_scenario(env, scenario)
    
    # 自定义步进函数处理角色互动
    original_step = env.step
    
    def interaction_step(action_idx):
        """重载步进函数处理角色互动"""
        action = env.action_space[action_idx]
        
        # 原始动作处理
        next_state, reward, done, info = original_step(action_idx)
        
        # 基于第二个角色特性调整结果
        # 例如：合作性角色对合作行为回应更积极
        if action in ["合作", "分享", "帮助"]:
            if env.other_character.get("A", 0.5) > 0.6:  # 宜人性高
                reward *= 1.2
                info["outcome"] += "，对方积极回应"
            elif env.other_character.get("A", 0.5) < 0.3:  # 宜人性低
                reward *= 0.8
                info["outcome"] += "，对方反应冷淡"
        
        # 修改环境状态反映互动
        env.state["other_response"] = action
        
        return next_state, reward, done, info
    
    # 替换步进函数
    env.step = interaction_step
    
    return env

def simulate_agents_interaction(agent1, agent2, env, rounds):
    """
    模拟两个智能体的互动
    
    Args:
        agent1: 第一个智能体
        agent2: 第二个智能体
        env: 互动环境
        rounds: 互动轮次
        
    Returns:
        互动结果
    """
    # 重置环境
    state = env.reset()
    
    char1_actions = []
    char2_actions = []
    char1_rewards = []
    char2_rewards = []
    
    for r in range(rounds):
        # 角色1行动
        action1, _, _ = agent1.select_action(state)
        next_state, reward1, done, info1 = env.step(action1)
        
        char1_actions.append({
            "round": r+1,
            "action": env.action_space[action1],
            "outcome": info1["outcome"],
            "reward": reward1
        })
        char1_rewards.append(reward1)
        
        if done:
            break
        
        # 保存状态用于角色2
        state_for_char2 = next_state.copy()
        
        # 角色2行动
        action2, _, _ = agent2.select_action(state_for_char2)
        next_state, reward2, done, info2 = env.step(action2)
        
        char2_actions.append({
            "round": r+1,
            "action": env.action_space[action2],
            "outcome": info2["outcome"],
            "reward": reward2
        })
        char2_rewards.append(reward2)
        
        # 更新状态
        state = next_state
        
        if done:
            break
    
    # 计算互动结果
    total_reward1 = sum(char1_rewards)
    total_reward2 = sum(char2_rewards)
    
    # 确定总体结果
    if total_reward1 > total_reward2 * 1.5:
        outcome = "角色1占据主导"
    elif total_reward2 > total_reward1 * 1.5:
        outcome = "角色2占据主导"
    elif total_reward1 > 0 and total_reward2 > 0:
        outcome = "双方互利共赢"
    elif total_reward1 < 0 and total_reward2 < 0:
        outcome = "双方均受损失"
    else:
        outcome = "互动结果不确定"
    
    # 计算关系变化
    relationship_score = (total_reward1 + total_reward2) / 2
    if relationship_score > 5:
        relationship_change = "关系显著改善"
    elif relationship_score > 2:
        relationship_change = "关系略有改善"
    elif relationship_score < -5:
        relationship_change = "关系显著恶化"
    elif relationship_score < -2:
        relationship_change = "关系略有恶化"
    else:
        relationship_change = "关系基本不变"
    
    return {
        "char1_actions": char1_actions,
        "char2_actions": char2_actions,
        "char1_total_reward": total_reward1,
        "char2_total_reward": total_reward2,
        "outcome": outcome,
        "relationship_change": relationship_change
    } 