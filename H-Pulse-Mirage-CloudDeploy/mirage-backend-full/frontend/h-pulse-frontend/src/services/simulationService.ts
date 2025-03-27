import axios from 'axios';

const API_URL = 'http://localhost:8000'; // 替换为你的后端地址

export const startSimulation = async () => {
  try {
    const res = await axios.post(`${API_URL}/api/simulation/start`, {}, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    });
    return res.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.message || '启动仿真失败');
  }
};

export const stopSimulation = async () => {
  try {
    const res = await axios.post(`${API_URL}/api/simulation/stop`, {}, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    });
    return res.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.message || '停止仿真失败');
  }
};

export const getSimulationStatus = async () => {
  try {
    const res = await axios.get(`${API_URL}/api/simulation/status`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    });
    return res.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.message || '获取仿真状态失败');
  }
};
