import React, { useState } from 'react'
import { createRoot } from 'react-dom/client'
import Editor from '@monaco-editor/react'
import './styles.css'

const starter = `def is_even(number: int) -> bool:
    return number % 2 == 0

print(is_even(7))`

const languageMap = { Python: 'python', JavaScript: 'javascript', TypeScript: 'typescript', Java: 'java', 'C++': 'cpp', Go: 'go' }

function Card({ icon, title, children, className = '' }) {
  return <section className={`card ${className}`}><h2><span>{icon}</span>{title}</h2>{children}</section>
}

function App() {
  const [language, setLanguage] = useState('Python')
  const [code, setCode] = useState(starter)
  const [review, setReview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function submit() {
    if (!code.trim()) return setError('Paste or write some code first.')
    setLoading(true); setError('')
    try {
      const response = await fetch('http://localhost:8000/api/review', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ language, code }) })
      const body = await response.json()
      if (!response.ok) throw new Error(body.detail || 'Review failed.')
      setReview(body)
    } catch (e) { setError(e.message || 'Could not connect to the backend. Is it running?') }
    finally { setLoading(false) }
  }

  return <main>
    <header><div className="brand"><i>⌘</i><span>CodeMentor <b>AI</b></span></div><div className="tag">Your thoughtful code companion</div></header>
    <div className="hero"><p className="eyebrow">AI-POWERED CODE REVIEW</p><h1>Ship clearer, more confident code.</h1><p>Paste a snippet for a kind, practical review with explanations, fixes, and test ideas.</p></div>
    <div className="workspace">
      <section className="editor-card"><div className="editor-bar"><div><label htmlFor="language">Language</label><select id="language" value={language} onChange={e => setLanguage(e.target.value)}>{Object.keys(languageMap).map(x => <option key={x}>{x}</option>)}</select></div><span className="status-dot">Ready to review</span></div>
        <Editor height="430px" theme="vs-dark" language={languageMap[language]} value={code} onChange={value => setCode(value ?? '')} options={{ minimap: { enabled: false }, fontSize: 14, fontFamily: 'JetBrains Mono, Consolas, monospace', padding: { top: 18 }, scrollBeyondLastLine: false, automaticLayout: true }} />
        <div className="editor-footer"><span>Tip: focused snippets get the most actionable review.</span><button onClick={submit} disabled={loading}>{loading ? 'Reviewing…' : '✦ Review my code'}</button></div>
      </section>
      {error && <div className="error">{error}</div>}
      {!review && !loading && <div className="empty"><div>✦</div><h2>Your review will appear here</h2><p>We’ll explain the code, spot risks, and propose a cleaner next version.</p></div>}
      {review && <section className="results">
        <div className="results-head"><div><p className="eyebrow">CODE REVIEW</p><h2>Here’s your mentor’s take</h2>{review.source === 'demo' && <small>Demo feedback — add an API key for a code-specific AI review.</small>}</div><div className="score"><strong>{review.score}</strong><span>/ 100</span><small>Quality score</small></div></div>
        <div className="grid"><Card icon="◎" title="What this code does"><p>{review.explanation}</p></Card><Card icon="⚠" title="Potential bugs"><ul>{review.bugs.map((x, i) => <li key={i}>{x}</li>)}</ul></Card><Card icon="↗" title="Ways to improve"><ul>{review.improvements.map((x, i) => <li key={i}>{x}</li>)}</ul></Card><Card icon="✓" title="Suggested tests" className="code-card"><pre>{review.unit_tests}</pre></Card></div>
        <Card icon="✦" title="Improved version" className="code-card"><pre>{review.improved_code}</pre></Card>
      </section>}
    </div>
    <footer>CodeMentor AI gives suggestions, not guarantees. Always run and test important changes.</footer>
  </main>
}
createRoot(document.getElementById('root')).render(<App />)
