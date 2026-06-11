# Nero – Synthetic Intelligence Framework
**Systemdokumentation & Architektur**

Nero ist ein fortschrittliches KI-System, das auf einem React-Frontend (Vite) und einem FastAPI-Python-Backend basiert. Es implementiert eine "Omni-Live-Interface" Architektur, bei der Sprache (STT), Sprachverarbeitung (LLM) und Sprachausgabe (TTS) nahtlos ineinandergreifen.

---

## 1. Systemarchitektur

Das Projekt ist in zwei Hauptkomponenten unterteilt:

- **Frontend** (`/frontend`): Ein React-basiertes, hochgradig visuelles HUD (Heads-Up Display) im "Minimalist-Glassmorphic" Design.
- **Backend** (`/backend`): Ein Python-Service, der die komplexe Audioverarbeitung, Transkription und Texterstellung orchestriert.

### Architektur-Fluss (Omni Engine)
1. **User spricht** in das Frontend-Mikrofon (Push-To-Talk).
2. Das **Frontend** streamt/sendet die aufgenommene Audio-Datei (.webm) an den Backend-Endpunkt `/api/voice`.
3. Das **Backend** verarbeitet die Audiodaten in drei Schritten (Omni-Pipeline):
   - **STT (Speech-to-Text)** via Faster Whisper (tiny model).
   - **LLM (Large Language Model)** via Qwen2.5-1.5B-Instruct zur Generierung der Antwort.
   - **TTS (Text-to-Speech)** via Edge TTS für die dynamische Sprachsynthese.
4. Das **Backend** antwortet mit der generierten Audio-Datei (.mp3) und fügt den transkribierten Text in den Response-Header (`X-Nero-Text`) ein.
5. Das **Frontend** spielt die Antwort ab und visualisiert sie.

---

## 2. Frontend (`/frontend`)

Das Frontend ist mit **React 19**, **Vite** und **TailwindCSS 4** gebaut.

### Design-System
Basierend auf der `DESIGN.md` Spezifikation nutzt das Frontend ein immersives Fullscreen-Design:
- **Typografie**: Geist (für saubere, große Texte) und JetBrains Mono (für Labels, Status und Latenzen).
- **Farbpalette**: Deep Space Black (`#050505`) als Hintergrund, mit leuchtenden Cyan- (`#00dbe7`) und Violett- (`#dcb8ff`) Akzenten (Neon-Glow-Effekte).
- **Glassmorphism**: Panels nutzen `backdrop-filter: blur(24px)` und stark reduzierte Weiß-Transparenzen, um "schwebende" UI-Fragmente zu erzeugen.

### Hauptkomponenten (`App.jsx`)
- **Voice Orb (`.orb-core`)**: Das zentrale Element der Interaktion. Reagiert auf Benutzereingaben und visualisiert Backend-Zustände durch CSS-Keyframe-Animationen (`breathe`, `pulse`, `spin`, `speak`).
- **Context Panel**: Zeigt den Systemstatus, den aktuellen Kontext (Generierte Textantwort) sowie die Gesprächshistorie der letzten 10 Einträge.
- **Right Toolbar**: Vertikales Menü mit Icon-Buttons (Einstellungen, Historie, etc.).
- **Header & Status Bar**: Zeigt das Nero-Branding, Verbindungsstatus (Heartbeat an `/api/health`) und Latenz-Tracking.

### Frontend States (`orbState`)
- `idle`: System ist bereit, Orb "atmet".
- `listening`: Mikrofon nimmt auf, roter/violetter Pulse.
- `processing`: Audio wurde an Backend gesendet, STT/LLM arbeitet, Orb dreht sich.
- `speaking`: Audio-Response wird abgespielt, Orb pulsiert organisch zur Sprache.
- `error`: Verbindungs- oder Hardwarefehler, rote UI-Elemente.

---

## 3. Backend (`/backend`)

Das Backend läuft als **FastAPI** Service und lädt alle KI-Modelle einmalig beim Start in den Grafikspeicher (VRAM), um eine latenzfreie Verarbeitung zu garantieren.

### Kern-Dateien
- **`main.py`**: Definiert die API-Routen, CORS-Regeln und wickelt den Datei-Upload (Audio) ab.
- **`omni_engine.py`**: Enthält die Kern-Klasse `OmniEngine`, die die STT -> LLM -> TTS Pipeline orchestriert.

### KI-Komponenten
1. **Faster Whisper (STT)**: 
   - Konfiguriert auf "tiny", generiert Transkripte extrem schnell.
   - Nutzt INT8/FP16 je nach Hardware.
2. **Qwen 2.5 1.5B Instruct (LLM)**:
   - Ein sehr schnelles, instruktionsbasiertes Modell für dialogische Antworten.
   - Der System-Prompt zwingt Nero zu prägnanten, deutschen Antworten ("Du bist Nero, eine fortschrittliche...").
   - Gesprächsverlauf (`self.history`) wird pro Session im RAM gehalten.
3. **Edge TTS (TTS)**:
   - Nutzt die Microsoft Edge Voice API (Standard: `de-DE-ChristophNeural`).
   - Keine lokalen VRAM-Kosten für TTS.

---

## 4. Setup & Deployment

### Voraussetzungen
- **Node.js** (für das Frontend)
- **Python 3.10+** (für das Backend)
- **FFmpeg** (im Systempfad, wird für Whisper STT benötigt)
- Empfohlen: NVIDIA GPU für schnelle Whisper- und Qwen-Inferenz.

### Starten des Systems
Es gibt ein mitgeliefertes Batch-Skript für Windows-Nutzer: `Start_Nero.bat`
Dieses Skript:
1. Startet das Python-Backend im VENV (`main.py` auf Port 8000).
2. Startet den Vite Dev-Server für das Frontend (Port 5173).
3. Öffnet automatisch den Browser auf `http://localhost:5173`.

Alternativ manueller Start:
```bash
# Backend
cd backend
venv\Scripts\activate
uvicorn main:app --reload

# Frontend
cd frontend
npm run dev
```

---

## 5. Erweiterungsmöglichkeiten & Roadmap

- **LLM Streaming**: Aktuell wartet das Backend, bis die gesamte LLM-Antwort generiert ist, bevor es TTS startet. Eine Optimierung wäre das Streaming von Token-Chunks direkt in die TTS-Engine (z.B. Satz-basiertes TTS-Streaming), um die Latenz weiter zu senken.
- **Wissensdatenbank (RAG)**: Anbindung einer lokalen Vektor-Datenbank, damit Nero auf lokale Systemdateien oder Unternehmensdaten zugreifen kann.
- **Voice Wake-Word**: Implementierung eines lokalen Wake-Word-Detectors (z.B. Porcupine), um die Push-To-Talk Taste überflüssig zu machen.
- **State-Persistenz**: Die `self.history` im Backend geht bei Neustart verloren. Eine Anbindung an SQLite oder Redis könnte User-Sessions persistieren.
