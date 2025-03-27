import React, { useEffect, useRef, useState } from 'react';
import './WebSocketConsole.css';

const WebSocketConsole: React.FC = () => {
  const [messages, setMessages] = useState<string[]>([]);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    ws.current = new WebSocket('ws://localhost:8000/ws/simulation');

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      const formatted = `[${data.timestamp}] ${data.status} - ${data.event}`;
      setMessages((prev) => [formatted, ...prev.slice(0, 49)]);
    };

    ws.current.onerror = () => {
      setMessages((prev) => ["[错误] WebSocket 连接失败", ...prev]);
    };

    ws.current.onclose = () => {
      setMessages((prev) => ["[关闭] WebSocket 连接已断开", ...prev]);
    };

    return () => {
      ws.current?.close();
    };
  }, []);

  return (
    <div className="ws-console">
      <h2>仿真事件控制台</h2>
      <div className="ws-log">
        {messages.map((msg, index) => (
          <div key={index} className="log-line">{msg}</div>
        ))}
      </div>
    </div>
  );
};

export default WebSocketConsole;
