import React, { useEffect, useState } from 'react';
import './AIDecision.css';
import * as echarts from 'echarts';

import { getAIDecisionGraph } from '../../services/aiService';

const AIDecision: React.FC = () => {
  const [data, setData] = useState<any>({});
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const fetchGraph = async () => {
      try {
        const result = await getAIDecisionGraph(1); // 假设角色ID为1
        setData(result);
      } catch (err: any) {
        setError(err.message);
      }
    };
    fetchGraph();
  }, []);

  useEffect(() => {
    if (!data.nodes || !data.links) return;
    const chart = echarts.init(document.getElementById('ai-graph')!, 'dark');
    const option = {
      title: { text: 'AI 决策路径图', left: 'center', textStyle: { color: '#fff' } },
      tooltip: {},
      series: [{
        type: 'graph',
        layout: 'force',
        roam: true,
        force: {
          repulsion: 150,
          edgeLength: 100
        },
        data: data.nodes,
        links: data.links,
        label: {
          show: true,
          formatter: '{b}'
        },
        lineStyle: {
          color: 'source',
          curveness: 0.3
        }
      }]
    };
    chart.setOption(option);
    const resize = () => chart.resize();
    window.addEventListener('resize', resize);
    return () => {
      chart.dispose();
      window.removeEventListener('resize', resize);
    };
  }, [data]);

  return (
    <div className="ai-decision-container">
      <h1>AI 决策可视化</h1>
      {error && <p className="error">{error}</p>}
      <div id="ai-graph" className="graph-area">加载中...</div>
    </div>
  );
};

export default AIDecision;
