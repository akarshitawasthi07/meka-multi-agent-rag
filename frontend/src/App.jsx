import { useState, useEffect } from 'react'
import './index.css'

function App() {
  const [query, setQuery] = useState('')
  const [useWeb, setUseWeb] = useState(false)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [history, setHistory] = useState([])
  const [showHistory, setShowHistory] = useState(false)
  const [threadId, setThreadId] = useState(localStorage.getItem('meka_thread_id') || Math.random().toString(36).substring(7))

  useEffect(() => {
    localStorage.setItem('meka_thread_id', threadId)
    fetchHistory()
  }, [threadId])

  const fetchHistory = async () => {
    try {
      const response = await fetch('http://localhost:8000/history')
      if (response.ok) {
        const data = await response.json()
        setHistory(data)
      }
    } catch (err) {
      console.error('Failed to fetch history:', err)
    }
  }

  const handleSearch = async () => {
    if (!query.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: query,
          web_search: useWeb,
          thread_id: threadId
        }),
      })

      if (!response.ok) {
        const errData = await response.json()
        throw new Error(errData.error || 'Failed to fetch response from agent')
      }

      const data = await response.json()
      setResult(data.answer)
      fetchHistory()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const loadFromHistory = (item) => {
    setResult(item.result)
    setQuery(item.question)
    setShowHistory(false)
  }

  const handleDeleteHistory = async (e, queryId) => {
    e.stopPropagation() // Prevent loading the history item
    if (!window.confirm('Are you sure you want to delete this query?')) return

    try {
      const response = await fetch(`http://localhost:8000/history/${queryId}`, {
        method: 'DELETE',
      })
      if (response.ok) {
        setHistory(history.filter((item) => item.query_id !== queryId))
      }
    } catch (err) {
      console.error('Failed to delete history:', err)
    }
  }

  const resetSession = () => {
    const newId = Math.random().toString(36).substring(7)
    setThreadId(newId)
    setResult(null)
    setQuery('')
  }

  return (
    <div className="app-container">
      <header>
        <div className="header-content">
          <div>
            <h1>MEKA</h1>
            <p className="subtitle">Multi-Agent Expert Knowledge Assistant</p>
          </div>
          <div className="header-actions">
            <button className="reset-btn" onClick={resetSession}>New Session</button>
            <button className="history-toggle" onClick={() => setShowHistory(!showHistory)}>
              {showHistory ? 'Close History' : 'View History'}
            </button>
          </div>
        </div>
      </header>

      {showHistory && (
        <div className="history-panel card">
          <h3>Recent Queries</h3>
          <div className="history-list">
            {history.length === 0 ? <p>No history found</p> : history.map((item, idx) => (
              <div key={idx} className="history-item" onClick={() => loadFromHistory(item)}>
                <div className="history-info">
                  <p className="history-q">{item.question}</p>
                  <span className="history-t">{new Date(item.timestamp).toLocaleString()}</span>
                </div>
                <button
                  className="delete-item-btn"
                  onClick={(e) => handleDeleteHistory(e, item.query_id)}
                  title="Delete this query"
                >
                  🗑️
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="search-section">
        <div className="input-group">
          <input
            type="text"
            placeholder="Ask a question or a follow-up..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button onClick={handleSearch} disabled={loading}>
            {loading ? 'Thinking...' : 'Analyze'}
          </button>
        </div>
        <div className="search-meta">
          <div className="toggle-group">
            <label className="switch">
              <input
                type="checkbox"
                checked={useWeb}
                onChange={() => setUseWeb(!useWeb)}
              />
              <span className="slider round"></span>
            </label>
            <span className="toggle-label">Include Web Supplemental Search</span>
          </div>
          <span className="session-id">Session: {threadId}</span>
        </div>
      </div>

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Orchestrating agents and retrieving knowledge...</p>
        </div>
      )}

      {error && <div className="card error-card">Error: {error}</div>}

      {result && (
        <div className="results-container">
          <div className="reasoning-trace card">
            <div className="card-title"><span>⛓️</span> Agent Reasoning Chain</div>
            <div className="trace-list">
              {result.reasoning_trace?.map((line, idx) => (
                <div key={idx} className="trace-item">{line}</div>
              ))}
            </div>
          </div>

          <div className="results-grid">
            <div className="card">
              <div className="card-title">
                <span>📋</span> Planner Output
              </div>
              <p className="planner-content">{result.planner_output}</p>
            </div>

            <div className="card">
              <div className="card-title">
                <span>🔍</span> Reranked Context
              </div>
              <div className="context-list">
                {result.reranked_docs?.map((doc, idx) => (
                  <div key={idx} className="context-item">
                    <p>{doc.page_content}</p>
                    <div className="context-meta">
                      <span className="score">Score: {doc.metadata?.rerank_score?.toFixed(4)}</span>
                      {doc.metadata?.source && <span className="source">Source: {doc.metadata.source}</span>}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="card final-answer-card">
              <div className="card-title">
                <span>💡</span> Final Answer
              </div>
              <div className="answer">{result.final_answer}</div>

              <div className={`validation ${result.validation?.toLowerCase()}`}>
                {result.validation === 'GROUNDED' ? '✅' : '⚠️'} Grounding: {result.validation}
              </div>
              <p className="reason-text">
                <strong>Reasoning:</strong> {result.reason}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
