import { useState, useRef, useEffect } from 'react'

type LogEntry = {
  id: string;
  type: 'info' | 'tool_call' | 'tool_result' | 'final_plan' | 'error' | 'done';
  model: string;
  content?: string;
  tool?: string;
  args?: any;
  result?: string;
}

function App() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [activeAgent, setActiveAgent] = useState<'system' | 'magistral' | 'devstral' | 'voxtral'>('system');
  const terminalEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    terminalEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [logs]);

  useEffect(() => {
    const eventSource = new EventSource('http://localhost:8001/api/stream');

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      const newLog: LogEntry = {
        id: Math.random().toString(36).substr(2, 9),
        ...data
      };

      setLogs((prev) => {
        // If we get the "No active incident" message, we can clear previous logs 
        // to reset the dashboard for a new session.
        if (data.type === 'info' && data.content === "No active incident. Awaiting trigger...") {
          return [newLog];
        }
        return [...prev, newLog];
      });

      if (data.model === 'Magistral (Brain)') setActiveAgent('magistral');
      else if (data.model === 'Devstral 2 (Coder)') setActiveAgent('devstral');
      else if (data.model.includes('Voxtral')) setActiveAgent('voxtral');
      else setActiveAgent('system');

      if (data.type === 'done' || data.type === 'error') {
        setIsRunning(false);
        // We don't close the eventSource here so it can listen for the next incident!
      } else if (data.type !== 'info' || data.content !== "No active incident. Awaiting trigger...") {
        setIsRunning(true);
      }
    };

    eventSource.onerror = (e) => {
      console.error("SSE Error:", e);
      setIsRunning(false);
    };

    return () => {
      eventSource.close();
    };
  }, []);

  const triggerIncident = async () => {
    setIsRunning(true);
    setLogs([]);
    setActiveAgent('system');

    try {
      await fetch('http://localhost:8001/api/trigger', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      });
    } catch (e) {
      console.error(e);
      setIsRunning(false);
    }
  };

  return (
    <>
      <header className="dashboard-header">
        <div className="logo">
          <span className="logo-icon">▲</span> Mistral OpsCommander
        </div>
        <button
          className="trigger-btn"
          onClick={triggerIncident}
          disabled={isRunning}
        >
          {isRunning ? "Incident in Progress..." : "Trigger Critical Incident"}
        </button>
      </header>

      <main className="dashboard-content">
        <aside className="node-graph">
          <div className={`agent-node ${activeAgent === 'system' ? 'active' : ''}`}>
            <h3>System Monitor</h3>
            <p>Observability & Alerting Hook</p>
          </div>
          <div className={`agent-node ${activeAgent === 'magistral' ? 'active' : ''}`}>
            <h3>Magistral Brain</h3>
            <p>Reasoning & Tool Orchestration</p>
          </div>
          <div className={`agent-node ${activeAgent === 'devstral' ? 'active' : ''}`}>
            <h3>Devstral Coder</h3>
            <p>256k Context Patch Generation</p>
          </div>
          <div className={`agent-node ${activeAgent === 'voxtral' ? 'active' : ''}`}>
            <h3>Voxtral Voice</h3>
            <p>Realtime Huddle Briefing</p>
          </div>
        </aside>

        <section className="terminal-container">
          {logs.length === 0 && (
            <div className="log-entry" style={{ color: "var(--text-muted)" }}>
              Waiting for incoming critical alerts...
            </div>
          )}
          {logs.map((log) => (
            <div key={log.id} className="log-entry">
              <div className="log-meta">
                <span className="log-model">{log.model}</span>
                <span>[{new Date().toLocaleTimeString()}]</span>
              </div>

              {log.type === 'info' && (
                <div className="log-content">{log.content}</div>
              )}

              {log.type === 'tool_call' && (
                <div className="log-content tool-call">
                  Executing tool: {log.tool}({JSON.stringify(log.args)})
                </div>
              )}

              {log.type === 'tool_result' && (
                <div className="log-content tool-result">
                  {log.result}
                </div>
              )}

              {log.type === 'final_plan' && (
                <div className="log-content" style={{ color: 'var(--success)' }}>
                  {log.content}
                </div>
              )}

              {log.type === 'error' && (
                <div className="log-content" style={{ color: '#ef4444' }}>
                  {log.content}
                </div>
              )}
            </div>
          ))}
          <div ref={terminalEndRef} />
        </section>
      </main>
    </>
  )
}

export default App
