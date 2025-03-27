import React, { useEffect, useState } from 'react';
import './Character.css';
import RadarChart from '../../components/RadarChart';
import FateTrendChart from '../../components/FateTrendChart';
import { getCharacterById } from '../../services/characterService';

const Character: React.FC = () => {
  const [character, setCharacter] = useState<any>(null);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const fetchCharacter = async () => {
      try {
        const data = await getCharacterById(1); // 假设ID为1
        setCharacter(data);
      } catch (err: any) {
        setError(err.message || '加载失败');
      }
    };
    fetchCharacter();
  }, []);

  if (error) return <div className="character-container"><p className="error">{error}</p></div>;
  if (!character) return <div className="character-container"><p>加载中...</p></div>;

  return (
    <div className="character-container">
      <h1>人物详情</h1>

      <div className="section card">
        <h2>基础信息</h2>
        <p><strong>姓名：</strong>{character.name}</p>
        <p><strong>性别：</strong>{character.gender}</p>
        <p><strong>年龄：</strong>{character.age}</p>
        <p><strong>职业：</strong>{character.occupation}</p>
        <p><strong>命运状态：</strong>{character.destiny}</p>
      </div>

      <div className="section card">
        <h2>八字排盘</h2>
        <div className="bazi-grid">
          {character.bazi.map((item: string, idx: number) => (
            <div key={idx} className="bazi-item">{item}</div>
          ))}
        </div>
      </div>

      <div className="section card">
        <h2>属性雷达图</h2>
        <RadarChart data={character.attributes} />
      </div>

      <div className="section card">
        <h2>命运趋势图</h2>
        <FateTrendChart data={character.fateTrend} />
      </div>

      <div className="section card">
        <h2>行为记录</h2>
        <ul className="log-list">
          {character.logs.map((log: string, idx: number) => (
            <li key={idx}>{log}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default Character;
