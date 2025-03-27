import axios from 'axios';

const API_URL = 'http://localhost:8000'; // 替换为你的后端地址

export const getCharacterById = async (id: number) => {
  try {
    const response = await axios.get(`${API_URL}/api/character/${id}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    });
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.message || '获取人物详情失败');
  }
};

export const getAllCharacters = async () => {
  try {
    const response = await axios.get(`${API_URL}/api/characters`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    });
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.message || '获取角色列表失败');
  }
};
