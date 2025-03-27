import React, { useEffect, useState } from 'react';
import './Simulation.css';
import {
  startSimulation,
  stopSimulation,
  getSimulationStatus
} from '../../services/simulationService';

const Simulation: React.FC = () => {
  const [status, setStatus] = useState<string>('未知');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const fetchStatus = async () => {
    try {
      const res = await getSimulationStatus();
      setStatus(res.status || '未知');
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleStart = async () => {
    setLoading(true);
    try {
      await startSimulation();
      await fetchStatus();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStop = async () => {
    setLoading(true);
    try {
      await stopSimulation();
      await fetchStatus();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  return (
    <div className="simulation-container">
      <h1>仿真控制台</h1>
      <p><strong>当前状态：</strong>{status}</p>
      {error && <p className="error">{error}</p>}

      <div className="btn-group">
        <button onClick={handleStart} disabled={loading}>启动仿真</button>
        <button onClick={handleStop} disabled={loading}>暂停仿真</button>
      </div>
    </div>
  );
};

export default Simulation;
