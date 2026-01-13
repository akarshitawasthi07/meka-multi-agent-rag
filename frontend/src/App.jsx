import { useState } from 'react'
import './index.css'

function App() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

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
        body: JSON.stringify({ question: query }),
      })

      if (!response.ok) {
        throw new Error('Failed to fetch response from agent')
      }

      const data = await response.json()
      setResult(data.answer)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <header>
        <h1>MEKA</h1>
        <p className="subtitle">Multi-Agent Expert Knowledge Assistant</p>
      </header>

      <div className="search-section">
        <input
          type="text"
          placeholder="Ask a complex question..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <button onClick={handleSearch} disabled={loading}>
          {loading ? 'Thinking...' : 'Analyze'}
        </button>
      </div>

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Orchestrating agents and retrieving knowledge...</p>
        </div>
      )}

      {error && <div className="card" style={{ color: 'var(--error)' }}>Error: {error}</div>}

      {result && (
        <div className="results-grid">
          <div className="card">
            <div className="card-title">
              <span>📋</span> Planner Agent
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
                  <div className="score">
                    Relevance Score: {doc.metadata?.rerank_score?.toFixed(4)}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="card">
            <div className="card-title">
              <span>💡</span> Final Answer
            </div>
            <div className="answer">{result.final_answer}</div>

            <div className={`validation ${result.validation?.toLowerCase()}`}>
              {result.validation === 'GROUNDED' ? '✅' : '⚠️'} Grounding: {result.validation}
            </div>
            <p style={{ marginTop: '12px', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
              <strong>Reasoning:</strong> {result.reason}
            </p>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
