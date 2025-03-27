import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts';

type FateTrendChartProps = {
  data: { date: string, score: number }[];
};

const FateTrendChart: React.FC<FateTrendChartProps> = ({ data }) => {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const chart = echarts.init(chartRef.current!, 'dark');

    const option = {
      title: {
        text: '命运评分趋势',
        left: 'center',
        textStyle: { color: '#fff' }
      },
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: data.map(item => item.date),
        boundaryGap: false
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 100
      },
      series: [
        {
          name: '命运评分',
          type: 'line',
          smooth: true,
          data: data.map(item => item.score),
          areaStyle: { opacity: 0.2 }
        }
      ]
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

export default FateTrendChart;
