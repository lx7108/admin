import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';
import { login } from '../../services/authService';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await login(username, password);
      localStorage.setItem('token', res.token);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || '登录失败，请稍后再试');
    }
  };

  return (
    <div className="login-container">
      <h2>登录 H-Pulse 系统</h2>
      <form onSubmit={handleLogin}>
        <label>
          用户名：
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </label>
        <label>
          密码：
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit">登录</button>
        <p>
          还没有账户？ <a href="/register">去注册</a>
        </p>
      </form>
    </div>
  );
};

export default Login;
