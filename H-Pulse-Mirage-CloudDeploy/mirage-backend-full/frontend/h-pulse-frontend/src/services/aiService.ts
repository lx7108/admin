import axios from 'axios';

const API_URL = 'http://localhost:8000'; // 替换为后端服务地址

export const getAIDecisionGraph = async (characterId: number) => {
  try {
    const response = await axios.get(`${API_URL}/api/character/${characterId}/ai-log`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    });
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.message || '获取 AI 决策数据失败');
  }
};
