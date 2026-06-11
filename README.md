# Hailo_OS

Kurze Beschreibung
------------------
Hailo_OS ist ein kleines Optimierungs- und Demo-Projekt mit einem Python-basierten Backend und einer React/Vite-Frontend-Instanz. Das Repository enthält Benchmark- und Testskripte, Docker-Setups sowie Startskripte für verschiedene Plattformen.

Projektstruktur (Kurz)
----------------------
- `backend/` — Python-Server, Benchmarks und Tests (z. B. `main.py`, `main_optimized.py`, `run_benchmark.py`).
- `frontend/` — Web-Frontend basierend auf Vite/React (Quellcode in `frontend/src`).
- `docker-compose.yml`, `Dockerfile` — Container-Setups.
- Startskripte: `start.bat`, `start.sh`, `Start_Nero.bat`.

Voraussetzungen
--------------
- Python 3.8+ (empfohlen 3.10+)
- pip
- Node.js 16+ / npm oder yarn (für das Frontend)
- Optional: Docker & Docker Compose

Schnellstart — Backend
-----------------------
1. Virtuelle Umgebung anlegen (Windows / macOS / Linux):

```bash
python -m venv .venv
source .venv/bin/activate  # macOS / Linux
.venv\Scripts\activate     # Windows (PowerShell)
```

2. Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

3. Backend starten (Beispiel):

```bash
python backend/main.py
# oder: python backend/main_optimized.py
```

Schnellstart — Frontend
------------------------
1. In das Frontend-Verzeichnis wechseln:

```bash
cd frontend
```

2. Abhängigkeiten installieren und Entwicklungsserver starten:

```bash
npm install
npm run dev    # Vite dev server
```

Docker
------
Mit Docker Compose kann das Projekt (sofern konfiguriert) gebaut und gestartet werden:

```bash
docker-compose up --build
```

Tests & Benchmarks
------------------
- Benchmarks: `backend/run_benchmark.py` oder die vorhandenen Benchmark-Skripte im `backend/`-Ordner.
- Tests: vorhandene `test_*.py`-Skripte im `backend/`-Ordner; mit `pytest` ausführen, falls installiert.

Nützliche Hinweise
------------------
- Es gibt mehrere Startskripte im Projektstamm (`start.bat`, `start.sh`) für schnelle lokale Abläufe.
- Die Dateien `main_optimized.py` und `omni_engine_optimized.py` sind optimierte Varianten von Kernkomponenten.

Contributing
------------
Issues, Verbesserungen oder Fragen bitte als Pull Request oder Issue im Repo anlegen.

Kontakt
-------
Bei Rückfragen oder zur Abstimmung von Änderungen gern Bescheid geben.
