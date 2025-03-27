import React, { useEffect, useState } from 'react';
import './CharacterList.css';
import { useNavigate } from 'react-router-dom';
import { getAllCharacters } from '../../services/characterService';

const CharacterList: React.FC = () => {
  const [characters, setCharacters] = useState<any[]>([]);
  const [error, setError] = useState<string>('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchList = async () => {
      try {
        const res = await getAllCharacters();
        setCharacters(res);
      } catch (err: any) {
        setError(err.message || '加载失败');
      }
    };
    fetchList();
  }, []);

  if (error) return <div className="character-list-container"><p className="error">{error}</p></div>;

  return (
    <div className="character-list-container">
      <h1>角色列表</h1>
      <div className="character-grid">
        {characters.map((char) => (
          <div className="char-card" key={char.id} onClick={() => navigate(`/character/${char.id}`)}>
            <div className="char-avatar">{char.name.slice(0, 1)}</div>
            <div className="char-info">
              <h3>{char.name}</h3>
              <p>命运：{char.destiny}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CharacterList;
