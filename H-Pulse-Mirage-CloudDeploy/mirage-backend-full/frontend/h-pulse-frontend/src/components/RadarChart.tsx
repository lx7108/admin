import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts';

type RadarChartProps = {
  data: Record<string, number>;
};

const RadarChart: React.FC<RadarChartProps> = ({ data }) => {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const chart = echarts.init(chartRef.current!, 'dark');

    const indicators = Object.keys(data).map(key => ({
      name: key,
      max: 100
    }));

    const option = {
      tooltip: {},
      radar: {
        indicator: indicators,
        radius: 90
      },
      series: [{
        name: '人物属性',
        type: 'radar',
        data: [
          {
            value: Object.values(data),
            name: '属性分布',
            areaStyle: { opacity: 0.3 }
          }
        ]
      }]
    };

    chart.setOption(option);

    const handleResize = () => chart.resize();
    window.addEventListener('resize', handleResize);

    return () => {
      chart.dispose();
      window.removeEventListener('resize', handleResize);
    };
  }, [data]);

  return <div ref={chartRef} style={{ width: '100%', height: '320px' }} />;
};

export default RadarChart;
