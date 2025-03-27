import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Register.css';
import { register } from '../../services/authService';

const Register: React.FC = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError('两次输入的密码不一致');
      return;
    }

    try {
      await register(username, password);
      navigate('/login');
    } catch (err: any) {
      setError(err.message || '注册失败，请稍后再试');
    }
  };

  return (
    <div className="register-container">
      <h2>注册 H-Pulse 账号</h2>
      <form onSubmit={handleRegister}>
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
        <label>
          确认密码：
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit">注册</button>
        <p>
          已有账号？ <a href="/login">去登录</a>
        </p>
      </form>
    </div>
  );
};

export default Register;
