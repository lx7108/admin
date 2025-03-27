import axios from 'axios';

const API_URL = 'http://localhost:8000'; // 替换为后端实际地址和端口

export const login = async (username: string, password: string) => {
  try {
    const response = await axios.post(`${API_URL}/api/login`, {
      username,
      password
    });
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.message || '登录失败');
  }
};

export const register = async (username: string, password: string) => {
  try {
    const response = await axios.post(`${API_URL}/api/register`, {
      username,
      password
    });
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.message || '注册失败');
  }
};
