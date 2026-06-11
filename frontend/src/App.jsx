import { useState, useRef, useEffect, useCallback } from 'react'
import './index.css'

/* ============================================================
   SVG ICON COMPONENTS
   ============================================================ */
const IconSettings = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="3" />
    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
  </svg>
)

const IconSparkle = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 3l1.5 5.5L19 10l-5.5 1.5L12 17l-1.5-5.5L5 10l5.5-1.5L12 3z" />
    <path d="M18 14l.7 2.3L21 17l-2.3.7L18 20l-.7-2.3L15 17l2.3-.7L18 14z" />
  </svg>
)

const IconBulb = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 18h6" />
    <path d="M10 22h4" />
    <path d="M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z" />
  </svg>
)

const IconClock = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <polyline points="12 6 12 12 16 14" />
  </svg>
)

const IconChat = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    <line x1="8" y1="9" x2="16" y2="9" />
    <line x1="8" y1="13" x2="12" y2="13" />
  </svg>
)

/* ============================================================
   STATE LABELS
   ============================================================ */
const STATE_LABELS = {
  idle: 'BEREIT',
  listening: 'ZUHÖREN',
  processing: 'VERARBEITEN',
  speaking: 'SPRECHEN',
  error: 'FEHLER',
}

const CONTEXT_LABELS = {
  idle: 'SYSTEM BEREIT',
  listening: 'AUDIO-AUFNAHME',
  processing: 'KONTEXT-IMPULS',
  speaking: 'SPRACHAUSGABE',
  error: 'VERBINDUNGSFEHLER',
}

const decodeBase64Utf8 = (value) => {
  const bytes = Uint8Array.from(atob(value), char => char.charCodeAt(0))
  return new TextDecoder().decode(bytes)
}

/* ============================================================
   MAIN APP COMPONENT
   ============================================================ */
function App() {
  // --- Core State ---
  const [orbState, setOrbState] = useState('idle') // idle | listening | processing | speaking | error
  const [isConnected, setIsConnected] = useState(false)
  const [latency, setLatency] = useState(null)
  const [showSettings, setShowSettings] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const [backendUrl, setBackendUrl] = useState('http://localhost:8000')

  // --- Conversation ---
  const [conversation, setConversation] = useState([])
  const [currentReply, setCurrentReply] = useState('')
  const [currentTranscript, setCurrentTranscript] = useState('')

  // --- Refs ---
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const audioPlayerRef = useRef(null)
  const audioUrlRef = useRef(null)

  /* ============================================================
     BACKEND HEALTH CHECK
     ============================================================ */
  const checkBackendHealth = useCallback(async () => {
    try {
      const res = await fetch(`${backendUrl}/api/health`, { signal: AbortSignal.timeout(3000) })
      if (res.ok) {
        setIsConnected(true)
      } else {
        setIsConnected(false)
      }
    } catch {
      setIsConnected(false)
    }
  }, [backendUrl])

  /* ============================================================
     BACKEND COMMUNICATION
     ============================================================ */
  const sendAudioToBackend = useCallback(async (blob) => {
    const startTime = performance.now()
    const formData = new FormData()
    formData.append('audio', blob, 'user_audio.webm')

    try {
      const response = await fetch(`${backendUrl}/api/voice`, {
        method: 'POST',
        body: formData,
      })

      const endTime = performance.now()
      setLatency(Math.round(endTime - startTime))

      if (response.ok) {
        // Read text reply from header
        const encodedReply = response.headers.get('X-Nero-Text-B64')
        let decodedReply = ''
        if (encodedReply) {
          try {
            decodedReply = decodeBase64Utf8(encodedReply)
          } catch {
            decodedReply = ''
          }
          setCurrentReply(decodedReply)
        }

        // Add to conversation history
        setConversation(prev => {
          const newConv = [...prev]
          if (decodedReply) {
            newConv.push({ role: 'nero', text: decodedReply, time: new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' }) })
          }
          // Keep last 10 entries
          return newConv.slice(-10)
        })

        // Play audio response
        if (audioUrlRef.current) URL.revokeObjectURL(audioUrlRef.current)
        const audioBlob = await response.blob()
        audioUrlRef.current = URL.createObjectURL(audioBlob)
        audioPlayerRef.current.src = audioUrlRef.current
        audioPlayerRef.current.play()
      } else {
        setOrbState('error')
        setCurrentReply('Fehler bei der Server-Antwort.')
        setTimeout(() => setOrbState('idle'), 3000)
      }
    } catch (err) {
      console.error('Backend error:', err)
      setOrbState('error')
      setCurrentReply('Server nicht erreichbar. Läuft das Backend?')
      setIsConnected(false)
      setTimeout(() => setOrbState('idle'), 3000)
    }
  }, [backendUrl])

  /* ============================================================
     AUDIO RECORDING
     ============================================================ */
  const startRecording = useCallback(async () => {
    if (orbState === 'listening' || orbState === 'processing' || orbState === 'speaking') return

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorderRef.current = new MediaRecorder(stream)

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
        }
      }

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        audioChunksRef.current = []
        await sendAudioToBackend(audioBlob)
      }

      mediaRecorderRef.current.start()
      setOrbState('listening')
      setCurrentTranscript('')
      setCurrentReply('')
    } catch (err) {
      console.error('Microphone access denied:', err)
      setOrbState('error')
      setCurrentReply('Mikrofon-Zugriff verweigert.')
      setTimeout(() => setOrbState('idle'), 3000)
    }
  }, [orbState, sendAudioToBackend])

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && orbState === 'listening') {
      mediaRecorderRef.current.stop()
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop())
      setOrbState('processing')
      setCurrentTranscript('Verarbeite Audio...')
    }
  }, [orbState])

  /* ============================================================
     INITIALIZATION
     ============================================================ */
  useEffect(() => {
    // Audio player
    if (!audioPlayerRef.current) {
      audioPlayerRef.current = new Audio()
      audioPlayerRef.current.onended = () => {
        setOrbState('idle')
      }
      audioPlayerRef.current.onplay = () => {
        setOrbState('speaking')
      }
    }

    // Health check
    const initialHealthCheck = setTimeout(checkBackendHealth, 0)
    const healthInterval = setInterval(checkBackendHealth, 30000)

    // Keyboard shortcut: Space = Push-to-talk
    const handleKeyDown = (e) => {
      if (e.code === 'Space' && !e.repeat && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA' && e.target.tagName !== 'SELECT') {
        e.preventDefault()
        startRecording()
      }
    }
    const handleKeyUp = (e) => {
      if (e.code === 'Space' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA' && e.target.tagName !== 'SELECT') {
        e.preventDefault()
        stopRecording()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    window.addEventListener('keyup', handleKeyUp)

    return () => {
      clearTimeout(initialHealthCheck)
      clearInterval(healthInterval)
      window.removeEventListener('keydown', handleKeyDown)
      window.removeEventListener('keyup', handleKeyUp)
    }
  }, [checkBackendHealth, startRecording, stopRecording])

  useEffect(() => {
    return () => {
      if (audioUrlRef.current) URL.revokeObjectURL(audioUrlRef.current)
    }
  }, [])

  /* ============================================================
     ORB STATE CLASS
     ============================================================ */
  const getOrbContainerClass = () => {
    const base = 'orb-container'
    switch (orbState) {
      case 'listening': return `${base} recording`
      case 'processing': return `${base} processing`
      case 'speaking': return `${base} speaking`
      default: return base
    }
  }

  const getOrbPrompt = () => {
    switch (orbState) {
      case 'listening': return 'Lass los zum senden'
      case 'processing': return 'Verarbeite...'
      case 'speaking': return 'Nero spricht...'
      case 'error': return 'Fehler aufgetreten'
      default: return 'Halte zum Sprechen'
    }
  }

  /* ============================================================
     RENDER
     ============================================================ */
  return (
    <div id="nero-hud">

      {/* ─── HEADER ─── */}
      <header className="nero-header">
        <div className="nero-brand">
          <h1>Nero</h1>
          <span className="subtitle">Synthetic Intelligence</span>
        </div>

        <div className="header-right">
          <div className="connection-indicator" style={{ position: 'static' }}>
            <div className={`connection-dot ${!isConnected ? 'offline' : ''}`} />
            <span>{isConnected ? 'Online' : 'Offline'}</span>
          </div>
          <button
            className="settings-btn"
            onClick={() => setShowSettings(!showSettings)}
            aria-label="Einstellungen"
            id="settings-toggle"
          >
            <IconSettings />
          </button>
        </div>
      </header>

      {/* ─── CONTEXT PANEL (Left) ─── */}
      <div className="context-panel" style={{ animation: 'slide-in-left 0.6s ease-out forwards' }}>
        <div className="context-card">
          <div className="status-row">
            <div className={`status-dot ${orbState !== 'idle' ? 'active' : ''} ${orbState === 'error' ? 'error' : ''}`} />
            <span className="status-label">{CONTEXT_LABELS[orbState]}</span>
          </div>

          {currentReply ? (
            <>
              <p className="card-title">{currentReply.length > 60 ? currentReply.substring(0, 60) + '...' : currentReply}</p>
              {currentReply.length > 60 && (
                <p className="card-body">{currentReply}</p>
              )}
            </>
          ) : (
            <>
              <p className="card-title">Analyse der System-Architektur...</p>
              <p className="card-body">Verarbeitung von Echtzeit-Datenströmen und Optimierung der neuronalen Pfade.</p>
            </>
          )}

          <div className="card-divider" />
          <div className="latency-row">
            LATENZ: <span className="latency-value">{latency !== null ? ` ${latency}ms` : ' —'}</span>
          </div>

          {/* Conversation History */}
          {showHistory && conversation.length > 0 && (
            <div className="conversation-list" style={{ animation: 'fade-in 0.4s ease-out' }}>
              {conversation.map((entry, i) => (
                <div className="conversation-entry" key={i}>
                  <div className={`entry-role ${entry.role === 'user' ? 'user-role' : ''}`}>
                    {entry.role === 'user' ? 'Du' : 'Nero'} · {entry.time}
                  </div>
                  <div className="entry-text">{entry.text}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* ─── VOICE ORB (Center) ─── */}
      <div className="orb-stage">
        <div className={getOrbContainerClass()}>
          <div className="orb-ring outer" />
          <div className="orb-ring middle" />
          <div className="orb-ring inner-ring" />
          <button
            className="orb-core"
            onMouseDown={startRecording}
            onMouseUp={stopRecording}
            onTouchStart={(e) => { e.preventDefault(); startRecording() }}
            onTouchEnd={(e) => { e.preventDefault(); stopRecording() }}
            aria-label={getOrbPrompt()}
            id="voice-orb"
          />
          <span className="orb-prompt">{getOrbPrompt()}</span>
        </div>
      </div>

      {/* ─── RIGHT TOOLBAR ─── */}
      <aside className="right-toolbar">
        <button
          className={`toolbar-btn ${showHistory ? 'active' : ''}`}
          title="KI-Impulse"
          aria-label="KI-Impulse anzeigen"
          id="toolbar-sparkle"
          onClick={() => {}}
        >
          <IconSparkle />
        </button>
        <button
          className="toolbar-btn"
          title="Ideen"
          aria-label="Ideen anzeigen"
          id="toolbar-bulb"
          onClick={() => {}}
        >
          <IconBulb />
        </button>
        <button
          className="toolbar-btn"
          title="Verlauf"
          aria-label="Gesprächsverlauf anzeigen"
          id="toolbar-clock"
          onClick={() => setShowHistory(!showHistory)}
        >
          <IconClock />
        </button>
        <button
          className={`toolbar-btn ${showHistory ? 'active' : ''}`}
          title="Chat"
          aria-label="Chat öffnen"
          id="toolbar-chat"
          onClick={() => setShowHistory(!showHistory)}
        >
          <IconChat />
        </button>
      </aside>

      {/* ─── STATUS BAR (Bottom) ─── */}
      <div className={`status-bar ${orbState !== 'idle' ? 'visible' : ''}`}>
        <div className="status-chip">
          <div className={`chip-dot ${orbState === 'processing' ? 'violet' : ''}`} />
          <span>{STATE_LABELS[orbState]}</span>
        </div>
        {currentTranscript && (
          <span className="transcript-text">{currentTranscript}</span>
        )}
      </div>

      {/* ─── SETTINGS MODAL ─── */}
      {showSettings && (
        <div className="settings-overlay" onClick={(e) => { if (e.target === e.currentTarget) setShowSettings(false) }}>
          <div className="settings-modal">
            <h2>Einstellungen</h2>

            <div className="settings-group">
              <label htmlFor="setting-voice">Stimme</label>
              <select id="setting-voice" defaultValue="de-DE-ChristophNeural">
                <option value="de-DE-ChristophNeural">Christoph (Deutsch)</option>
                <option value="de-DE-KatjaNeural">Katja (Deutsch)</option>
                <option value="de-DE-ConradNeural">Conrad (Deutsch)</option>
                <option value="en-US-GuyNeural">Guy (English)</option>
              </select>
            </div>

            <div className="settings-group">
              <label htmlFor="setting-backend">Backend URL</label>
              <input
                type="text"
                id="setting-backend"
                value={backendUrl}
                onChange={(event) => setBackendUrl(event.target.value.replace(/\/$/, ''))}
              />
            </div>

            <div className="settings-group">
              <label htmlFor="setting-model">LLM Modell</label>
              <select id="setting-model" defaultValue="qwen2.5-1.5b">
                <option value="qwen2.5-1.5b">Qwen 2.5 1.5B Instruct</option>
                <option value="qwen2.5-3b">Qwen 2.5 3B Instruct</option>
              </select>
            </div>

            <div className="settings-actions">
              <button className="btn-ghost" onClick={() => setShowSettings(false)}>Schließen</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
