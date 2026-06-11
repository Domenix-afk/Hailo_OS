/**
 * Optimized Nero AI Frontend
 * Performance, UX, and Reliability Improvements
 */

import { useState, useRef, useEffect, useCallback, useMemo } from 'react'
import './index.css'

/* ============================================================
   SVG ICONS (Memoized)
   ============================================================ */
const IconSettings = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="3" />
    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
  </svg>
)

const IconChat = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
    <line x1="8" y1="9" x2="16" y2="9" />
    <line x1="8" y1="13" x2="12" y2="13" />
  </svg>
)

const IconClock = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10" />
    <polyline points="12 6 12 12 16 14" />
  </svg>
)

/* ============================================================
   STATE CONSTANTS
   ============================================================ */
const STATE_LABELS = {
  idle: 'BEREIT',
  listening: 'ZUHÖREN',
  processing: 'VERARBEITEN',
  speaking: 'SPRICHT',
  error: 'VERBINDUNGSFEHLER',
}

const STATE_COLORS = {
  idle: '#00D9FF',
  listening: '#FF00FF',
  processing: '#FFFF00',
  speaking: '#00FF00',
  error: '#FF0000',
}

/* ============================================================
   UTILITIES
   ============================================================ */
const decodeBase64Utf8 = (value) => {
  try {
    const bytes = Uint8Array.from(atob(value), char => char.charCodeAt(0))
    return new TextDecoder().decode(bytes)
  } catch (e) {
    console.error('Decode error:', e)
    return ''
  }
}

const formatTime = (ms) => {
  if (ms < 1000) return `${Math.round(ms)}ms`
  return `${(ms / 1000).toFixed(1)}s`
}

/* ============================================================
   MAIN APP COMPONENT
   ============================================================ */
function App() {
  // ---- Core State ----
  const [orbState, setOrbState] = useState('idle')
  const [isConnected, setIsConnected] = useState(false)
  const [latency, setLatency] = useState(null)
  const [showSettings, setShowSettings] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const [backendUrl, setBackendUrl] = useState(localStorage.getItem('backendUrl') || 'http://localhost:8000')
  
  // ---- Conversation ----
  const [conversation, setConversation] = useState([])
  const [currentReply, setCurrentReply] = useState('')
  
  // ---- Refs ----
  const mediaRecorderRef = useRef(null)
  const audioChunksRef = useRef([])
  const audioPlayerRef = useRef(null)
  const audioUrlRef = useRef(null)
  const abortControllerRef = useRef(null)
  
  // ---- Optimization: Memoized values ----
  const orbColor = useMemo(() => STATE_COLORS[orbState] || '#00D9FF', [orbState])
  const orbLabel = useMemo(() => STATE_LABELS[orbState] || 'ERROR', [orbState])
  
  /* ============================================================
     BACKEND HEALTH CHECK (Optimized)
     ============================================================ */
  const checkBackendHealth = useCallback(async () => {
    try {
      // Use AbortSignal for timeout
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 2000)
      
      const res = await fetch(`${backendUrl}/api/health`, {
        signal: controller.signal,
        cache: 'no-cache'
      })
      
      clearTimeout(timeoutId)
      setIsConnected(res.ok)
    } catch (err) {
      setIsConnected(false)
      console.debug('Health check failed:', err.message)
    }
  }, [backendUrl])
  
  /* ============================================================
     AUDIO BACKEND COMMUNICATION (Optimized)
     ============================================================ */
  const sendAudioToBackend = useCallback(async (blob) => {
    if (!blob || blob.size === 0) {
      setOrbState('error')
      setCurrentReply('Audio ist leer.')
      setTimeout(() => setOrbState('idle'), 2000)
      return
    }
    
    const startTime = performance.now()
    const formData = new FormData()
    formData.append('audio', blob, 'user_audio.webm')
    
    // Create abort controller for this request
    abortControllerRef.current = new AbortController()
    
    try {
      const response = await fetch(`${backendUrl}/api/voice`, {
        method: 'POST',
        body: formData,
        signal: abortControllerRef.current.signal,
      })
      
      const processingTime = performance.now() - startTime
      setLatency(Math.round(processingTime))
      
      if (response.ok) {
        // Decode text from header
        const encodedReply = response.headers.get('X-Nero-Text-B64')
        let decodedReply = ''
        if (encodedReply) {
          decodedReply = decodeBase64Utf8(encodedReply)
        }
        setCurrentReply(decodedReply)
        
        // Add to conversation (limited history)
        setConversation(prev => {
          const newConv = [...prev]
          if (decodedReply) {
            newConv.push({
              role: 'nero',
              text: decodedReply,
              time: new Date().toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })
            })
          }
          // Keep last 20 entries for performance
          return newConv.slice(-20)
        })
        
        // Play audio response
        const audioBlob = await response.blob()
        if (audioUrlRef.current) URL.revokeObjectURL(audioUrlRef.current)
        audioUrlRef.current = URL.createObjectURL(audioBlob)
        audioPlayerRef.current.src = audioUrlRef.current
        audioPlayerRef.current.play().catch(err => {
          console.warn('Audio playback failed:', err)
          setOrbState('idle')
        })
      } else {
        const errorText = await response.text()
        setOrbState('error')
        setCurrentReply(`Server Fehler: ${response.status}`)
        setTimeout(() => setOrbState('idle'), 3000)
      }
    } catch (err) {
      if (err.name === 'AbortError') {
        console.debug('Request aborted')
        return
      }
      console.error('Backend error:', err)
      setOrbState('error')
      setCurrentReply('Server nicht erreichbar.')
      setIsConnected(false)
      setTimeout(() => setOrbState('idle'), 3000)
    } finally {
      abortControllerRef.current = null
    }
  }, [backendUrl])
  
  /* ============================================================
     AUDIO RECORDING (Optimized)
     ============================================================ */
  const startRecording = useCallback(async () => {
    // Prevent multiple recordings
    if (orbState !== 'idle' && orbState !== 'error') return
    
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        }
      })
      
      // Use optimal settings
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: 'audio/webm',
        audioBitsPerSecond: 128000, // Balanced quality/size
      })
      
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
      
      mediaRecorderRef.current.onerror = (event) => {
        console.error('Recording error:', event.error)
        setOrbState('error')
        setCurrentReply('Aufnahmefehler.')
        setTimeout(() => setOrbState('idle'), 2000)
      }
      
      mediaRecorderRef.current.start()
      setOrbState('listening')
      setCurrentReply('')
    } catch (err) {
      console.error('Microphone error:', err)
      setOrbState('error')
      setCurrentReply('Mikrofon nicht verfügbar.')
      setTimeout(() => setOrbState('idle'), 2000)
    }
  }, [orbState, sendAudioToBackend])
  
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && orbState === 'listening') {
      mediaRecorderRef.current.stop()
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop())
      setOrbState('processing')
      setCurrentReply('Verarbeite...')
    }
  }, [orbState])
  
  /* ============================================================
     EFFECTS - Setup and Cleanup
     ============================================================ */
  useEffect(() => {
    // Initialize audio player
    if (!audioPlayerRef.current) {
      audioPlayerRef.current = new Audio()
      audioPlayerRef.current.onended = () => setOrbState('idle')
      audioPlayerRef.current.onplay = () => setOrbState('speaking')
      audioPlayerRef.current.onerror = () => {
        console.error('Audio error')
        setOrbState('idle')
      }
    }
    
    // Initial health check
    checkBackendHealth()
    const healthInterval = setInterval(checkBackendHealth, 20000) // Check every 20s
    
    // Keyboard shortcuts
    const handleKeyDown = (e) => {
      if (e.code === 'Space' && !e.repeat) {
        const tag = e.target.tagName
        if (tag !== 'INPUT' && tag !== 'TEXTAREA' && tag !== 'SELECT') {
          e.preventDefault()
          startRecording()
        }
      }
    }
    
    const handleKeyUp = (e) => {
      if (e.code === 'Space') {
        const tag = e.target.tagName
        if (tag !== 'INPUT' && tag !== 'TEXTAREA' && tag !== 'SELECT') {
          e.preventDefault()
          stopRecording()
        }
      }
    }
    
    window.addEventListener('keydown', handleKeyDown)
    window.addEventListener('keyup', handleKeyUp)
    
    return () => {
      clearInterval(healthInterval)
      window.removeEventListener('keydown', handleKeyDown)
      window.removeEventListener('keyup', handleKeyUp)
      // Cancel any pending requests
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [checkBackendHealth, startRecording, stopRecording])
  
  useEffect(() => {
    // Cleanup audio URLs on unmount
    return () => {
      if (audioUrlRef.current) {
        URL.revokeObjectURL(audioUrlRef.current)
      }
    }
  }, [])
  
  /* ============================================================
     SAVE SETTINGS
     ============================================================ */
  const handleBackendUrlChange = useCallback((newUrl) => {
    setBackendUrl(newUrl)
    localStorage.setItem('backendUrl', newUrl)
    checkBackendHealth()
  }, [checkBackendHealth])
  
  /* ============================================================
     RENDER
     ============================================================ */
  return (
    <div className="app">
      {/* ORB INTERFACE */}
      <div className="orb-section">
        <div className="orb-container" data-state={orbState}>
          <div className="orb" style={{ borderColor: orbColor }}>
            <div className="orb-inner" style={{ backgroundColor: orbColor + '33' }}></div>
          </div>
          <button
            className="orb-button"
            onMouseDown={startRecording}
            onMouseUp={stopRecording}
            onTouchStart={startRecording}
            onTouchEnd={stopRecording}
            disabled={orbState === 'processing' || orbState === 'speaking'}
            style={{ '--orb-color': orbColor }}
          >
            {orbLabel}
          </button>
        </div>
        
        <p className="orb-prompt">
          {orbState === 'listening' ? 'Lass los zum senden' : 'SPACE zum Sprechen'}
        </p>
        
        {latency && (
          <p className="latency">Antwortzeit: {formatTime(latency)}</p>
        )}
      </div>
      
      {/* RESPONSE DISPLAY */}
      <div className="response-section">
        {currentReply && (
          <div className="response-box">
            <p>{currentReply}</p>
          </div>
        )}
        <audio
          ref={audioPlayerRef}
          style={{ display: 'none' }}
          preload="auto"
        />
      </div>
      
      {/* STATUS AND CONTROLS */}
      <div className="footer">
        <div className="status">
          <span className={`status-dot ${isConnected ? 'connected' : 'disconnected'}`}></span>
          <span>{isConnected ? 'Verbunden' : 'Getrennt'}</span>
        </div>
        
        <button
          className="footer-button"
          onClick={() => setShowHistory(!showHistory)}
          title="Verlauf"
        >
          <IconChat />
        </button>
        
        <button
          className="footer-button"
          onClick={() => setShowSettings(!showSettings)}
          title="Einstellungen"
        >
          <IconSettings />
        </button>
      </div>
      
      {/* HISTORY PANEL */}
      {showHistory && (
        <div className="panel history-panel">
          <h3>Verlauf ({conversation.length})</h3>
          <div className="history-list">
            {conversation.length === 0 ? (
              <p className="empty">Keine Einträge</p>
            ) : (
              conversation.map((msg, i) => (
                <div key={i} className="history-item">
                  <span className="time">{msg.time}</span>
                  <p>{msg.text}</p>
                </div>
              ))
            )}
          </div>
          <button className="close-button" onClick={() => setShowHistory(false)}>
            Schließen
          </button>
        </div>
      )}
      
      {/* SETTINGS PANEL */}
      {showSettings && (
        <div className="panel settings-panel">
          <h3>Einstellungen</h3>
          <div className="setting-group">
            <label>Backend URL:</label>
            <input
              type="text"
              value={backendUrl}
              onChange={(e) => handleBackendUrlChange(e.target.value)}
              placeholder="http://localhost:8000"
            />
          </div>
          <button className="close-button" onClick={() => setShowSettings(false)}>
            Schließen
          </button>
        </div>
      )}
    </div>
  )
}

export default App
