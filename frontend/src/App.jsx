import React, { useState, useEffect, useRef } from 'react';
import './App.css';

// --- Icons (Standard SVG paths) ---
const SVGIcon = ({ name, size = 18 }) => {
  const icons = {
    search: <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />,
    delete: <path strokeLinecap="round" strokeLinejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />,
    check: <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />,
    web: <path strokeLinecap="round" strokeLinejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 013 12c0-1.605.42-3.113 1.157-4.418" />,
    node: <path strokeLinecap="round" strokeLinejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />,
  };
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      {icons[name]}
    </svg>
  );
};

// --- Sub-Components ---

const Sidebar = ({ history, onSelect, onDelete, onNew, onToggle }) => (
  <aside className="sidebar">
    <div className="sidebar-header">
      <div className="logo-container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div className="logo-icon">M</div>
          <span style={{ fontWeight: 800, fontSize: '18px', letterSpacing: '0.02em' }}>MEKA</span>
        </div>
        <button onClick={onToggle} className="icon-btn-subtle" title="Collapse Sidebar">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M11 17l-5-5 5-5M18 17l-5-5 5-5" />
          </svg>
        </button>
      </div>
      <button className="new-btn" onClick={onNew}>+ New Session</button>
    </div>
    <div className="history-list">
      <div style={{ fontSize: '11px', fontWeight: 800, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '16px' }}>Past Queries</div>
      {history.map(item => (
        <div key={item.query_id} className="history-item" onClick={() => onSelect(item)}>
          <div className="history-info">
            <div className="history-title">{item.query || item.question}</div>
            <div className="history-date">{item.timestamp ? new Date(item.timestamp).toLocaleDateString() : 'Recent'}</div>
          </div>
          <button className="history-item-del" onClick={(e) => onDelete(e, item.query_id)} title="Delete history">
            <SVGIcon name="delete" size={14} />
          </button>
        </div>
      ))}
    </div>
  </aside>
);

const PipelineStep = ({ title, text, icon, isLast, isLoading }) => {
  const [isOpen, setIsOpen] = useState(true);

  if (!text && !isLoading) return null;

  return (
    <div className={`pipeline-step ${isOpen ? 'is-open' : 'is-collapsed'}`}>
      {!isLast && <div className="step-line" />}
      <div className="step-dot">
        {isLoading ? (
          <div className="spinner" style={{ width: '14px', height: '14px', border: '2px solid var(--brand-primary)', borderTopColor: 'transparent', borderRadius: '50%' }} />
        ) : (
          <SVGIcon name={icon} size={16} />
        )}
      </div>
      <div className="step-content">
        <div className="step-header" onClick={() => setIsOpen(!isOpen)} style={{ cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div className="step-title">{title}</div>
          <div className={`step-chevron ${isOpen ? 'expanded' : ''}`}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
              <path d="M6 9l6 6 6-6" />
            </svg>
          </div>
        </div>
        {isOpen && <div className="step-text">{text || "Processing node output..."}</div>}
      </div>
    </div>
  );
};

const EvidenceCard = ({ doc }) => (
  <div className="source-card">
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <span className="source-tag">{doc.metadata?.type || 'Extracted'}</span>
      {doc.metadata?.score && <span style={{ fontSize: '10px', color: 'var(--brand-primary)', fontWeight: 700 }}>Rank: {doc.metadata.score.toFixed(3)}</span>}
    </div>
    <div className="source-snippet">{doc.page_content}</div>
    {doc.metadata?.source && (
      <a href={doc.metadata.source} target="_blank" rel="noreferrer" style={{ fontSize: '11px', color: 'var(--text-muted)', textDecoration: 'none' }}>
        {doc.metadata.source}
      </a>
    )}
  </div>
);

// --- Main App Component ---

const Modal = ({ isOpen, title, message, onConfirm, onCancel, confirmText = "Confirm", cancelText = "Cancel" }) => {
  if (!isOpen) return null;
  return (
    <div className="modal-overlay">
      <div className="modal-content animate-in zoom-in duration-300">
        <h3 className="modal-title">{title}</h3>
        <p className="modal-message">{message}</p>
        <div className="modal-actions">
          <button className="btn-neutral" onClick={onCancel}>{cancelText}</button>
          <button className="btn-danger" onClick={onConfirm}>{confirmText}</button>
        </div>
      </div>
    </div>
  );
};

// ... (PipelineStep and EvidenceCard code remains same) ...

function App() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [response, setResponse] = useState("");
  const [reasoningTrace, setReasoningTrace] = useState([]);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [useWeb, setUseWeb] = useState(false);
  const [showEvidence, setShowEvidence] = useState(true);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [activeQuery, setActiveQuery] = useState("");
  const [threadId, setThreadId] = useState(Math.random().toString(36).substring(7));

  // Custom Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [pendingDeleteId, setPendingDeleteId] = useState(null);

  const scrollRef = useRef(null);

  useEffect(() => { fetchHistory(); }, []);
  useEffect(() => { scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' }); }, [reasoningTrace, response]);

  const fetchHistory = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/history");
      const data = await res.json();
      setHistory(data);
    } catch (err) { console.error(err); }
  };

  const handleNewSession = () => {
    setQuery(""); setActiveQuery(""); setLoading(false); setError(null); setResult(null); setResponse(""); setReasoningTrace([]);
    setThreadId(Math.random().toString(36).substring(7));
  };

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    setLoading(true); setError(null); setResult(null); setResponse(""); setReasoningTrace([]);

    // Clear input immediately for a better UX but preserve for header
    setActiveQuery(query);
    const currentQuery = query;
    setQuery("");

    const socketUrl = `ws://127.0.0.1:8000/ws/ask/${threadId}`;
    let ws;

    try {
      ws = new WebSocket(socketUrl);
      ws.onopen = () => ws.send(JSON.stringify({ query: currentQuery, web_search: useWeb }));
      ws.onmessage = (ev) => {
        try {
          const data = JSON.parse(ev.data);
          if (data.event === "trace") setReasoningTrace(p => [...p, data.trace]);
          else if (data.event === "answer") setResponse(data.answer);
          else if (data.event === "done") {
            if (data.full_result) setResult(data.full_result);
            setLoading(false); fetchHistory(); ws.close();
          } else if (data.event === "error") { setError(data.error); setLoading(false); ws.close(); }
        } catch (err) { console.error(err); }
      };
      ws.onerror = () => { setError("Connection failed."); setLoading(false); };
      ws.onclose = () => setLoading(false);
    } catch (err) { setError("Socket Error."); setLoading(false); }
  };

  const loadFromHistory = (item) => {
    setResult(item.result);
    const q = item.query || item.question || "";
    setQuery("");
    setActiveQuery(q);
    if (item.result) {
      setResponse(item.result.final_answer || (typeof item.result === 'string' ? item.result : ''));
      setReasoningTrace(item.reasoning_trace || item.result.reasoning_trace || []);
    }
  };

  const triggerDelete = (e, id) => {
    e.stopPropagation();
    setPendingDeleteId(id);
    setIsModalOpen(true);
  };

  const confirmDelete = async () => {
    if (!pendingDeleteId) return;
    try {
      const res = await fetch(`http://127.0.0.1:8000/history/${pendingDeleteId}`, { method: 'DELETE' });
      if (res.ok) fetchHistory();
    } catch (err) { console.error(err); }
    setIsModalOpen(false);
    setPendingDeleteId(null);
  };

  const cancelDelete = () => {
    setIsModalOpen(false);
    setPendingDeleteId(null);
  };

  // Agent State Mapping
  const getTraceFor = (agent) => reasoningTrace.find(t => t.toLowerCase().includes(`${agent.toLowerCase()}:`));

  return (
    <div className="app-container">
      <div className={`sidebar-wrap ${isSidebarCollapsed ? 'collapsed' : ''}`}>
        <Sidebar
          history={history}
          onSelect={loadFromHistory}
          onDelete={triggerDelete}
          onNew={handleNewSession}
          onToggle={() => setIsSidebarCollapsed(true)}
        />
      </div>

      <Modal
        isOpen={isModalOpen}
        title="Delete History"
        message="Are you sure you want to delete this entry? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />

      <main className="main-content">
        <header className="header" style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          {isSidebarCollapsed && (
            <button className="icon-btn-primary" onClick={() => setIsSidebarCollapsed(false)} title="Show Sidebar">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="3" y1="12" x2="21" y2="12"></line>
                <line x1="3" y1="6" x2="21" y2="6"></line>
                <line x1="3" y1="18" x2="21" y2="18"></line>
              </svg>
            </button>
          )}
          <div className="header-title">Multi-Agent Expert Knowledge Assistant</div>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>SESSION_ID: <strong>{threadId}</strong></div>
        </header>

        <div className="scroll-area" ref={scrollRef}>
          <div className="content-container">
            {activeQuery && (response || reasoningTrace.length > 0) && (
              <div style={{ marginBottom: '40px' }}>
                <h2 style={{ fontSize: '28px', fontWeight: 800, margin: '0 0 12px 0' }}>{activeQuery}</h2>
                <div style={{ width: '40px', height: '4px', background: 'var(--brand-primary)', borderRadius: '2px' }} />
              </div>
            )}

            {error && <div style={{ background: '#421', border: '1px solid #844', color: '#c88', padding: '16px', borderRadius: '12px', fontSize: '14px', marginBottom: '24px' }}><strong>System Alert:</strong> {error}</div>}

            {(loading || reasoningTrace.length > 0) && (
              <div className="pipeline-section">
                <span className="section-label">Reasoning Chain for: "{activeQuery}"</span>
                <PipelineStep title="Planning" icon="search" text={getTraceFor('planner')} isLoading={loading && !getTraceFor('planner')} />
                <PipelineStep title="Retrieval" icon="web" text={getTraceFor('retriever')} isLoading={loading && getTraceFor('planner') && !getTraceFor('retriever')} />
                <PipelineStep title="Reranker" icon="node" text={getTraceFor('reranker')} isLoading={loading && getTraceFor('retriever') && !getTraceFor('reranker')} />
                <PipelineStep title="Summarizer" icon="check" text={getTraceFor('summarizer')} isLoading={loading && getTraceFor('reranker') && !getTraceFor('summarizer')} />
                <PipelineStep title="Verification" icon="check" text={getTraceFor('validator')} isLast isLoading={loading && getTraceFor('summarizer') && !getTraceFor('validator')} />
              </div>
            )}
            {/* Sources Display */}
            {result?.reranked_docs && (
              <section className="pipeline-section animate-in fade-in duration-1000">
                <div
                  className="section-header-collapsible"
                  onClick={() => setShowEvidence(!showEvidence)}
                  style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer', marginBottom: '16px' }}
                >
                  <h2 className="text-xl font-bold text-slate-200 flex items-center gap-3" style={{ margin: 0 }}>
                    <div className="p-1 px-2 border border-slate-600 rounded bg-slate-800/10 text-[10px] text-slate-400">EVIDENCE</div>
                    Grounded Knowledge Base
                  </h2>
                  <div className={`step-chevron ${showEvidence ? 'expanded' : ''}`}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M6 9l6 6 6-6" />
                    </svg>
                  </div>
                </div>

                {showEvidence && (
                  <div className="evidence-grid">
                    {result.reranked_docs.map((doc, idx) => (
                      <EvidenceCard key={idx} doc={doc} />
                    ))}
                  </div>
                )}
              </section>
            )}
            {response && (
              <div className="result-card">
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                  <div style={{ background: 'var(--brand-glow)', color: 'var(--brand-primary)', width: '36px', height: '36px', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '8px' }}>
                    <SVGIcon name="check" size={20} />
                  </div>
                  <div style={{ fontWeight: 800, fontSize: '18px' }}>Final Response</div>
                </div>
                <div className="result-answer">{response}</div>
                <div className="grounding-badge">
                  <div style={{ width: '6px', height: '6px', background: 'var(--success)', borderRadius: '50%' }} />
                  {getTraceFor('validator') || 'Status: Verified'}
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="search-container">
          <div className="search-box">
            <input
              className="search-input"
              placeholder="Query the Multi-Agent System..."
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSubmit()}
            />
            <button className={`pro-search-btn ${useWeb ? 'active' : ''}`} onClick={() => setUseWeb(!useWeb)}>
              <SVGIcon name="web" size={14} /> <span>Web Supplemental</span>
            </button>
            <button className="analyze-btn" onClick={handleSubmit} disabled={loading || !query.trim()}>
              {loading ? "..." : "Analyze"}
            </button>
          </div>
        </div>
      </main>

      <style dangerouslySetInnerHTML={{
        __html: `
        .history-item-del {
          opacity: 0;
          background: transparent;
          border: none;
          color: var(--text-muted);
          cursor: pointer;
          transition: var(--transition);
        }
        .history-item:hover .history-item-del {
          opacity: 1;
        }
        .history-item-del:hover {
          color: var(--warning);
        }
      `}} />
    </div>
  );
}

export default App;
