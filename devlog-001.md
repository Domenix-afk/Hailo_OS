# Devlog #1 – Nero Framework: First Light

**Date:** 2026-06-08

## Summary

Nero is shaping up to be a real-time synthetic intelligence interface. The core architecture is a FastAPI backend running an Omni Pipeline (STT → LLM → TTS) paired with a React/Vite frontend rendered as a glassmorphic HUD. The system processes voice input end-to-end: transcribes with Faster Whisper (tiny), generates a response with Qwen 2.5 1.5B Instruct, and speaks back via Edge TTS.

## What's Working

- **Voice Orb:** The central UI component is fully animated with CSS keyframes – breathing idle, pulsing record, spinning processing, and organic speak animation. The concentric ring system reacts to each state change.
- **Omni Pipeline:** `omni_engine.py` orchestrates the three-model chain flawlessly. Models load once into VRAM on startup and stay hot. The benchmark script (`run_benchmark.py`) measures each stage independently.
- **Push-to-Talk:** Spacebar hold-to-record with automatic release detection. Falls back gracefully on microphone denial.
- **Settings modal:** Voice selection, backend URL config, and model switching are wired up.

## Current Challenges

- **Edge TTS unicode issues on Windows:** The benchmark script had to normalize text through NFKD + ASCII stripping to avoid crashes. This needs a more robust fix.
- **LLM history is RAM-only:** A server restart wipes all conversation context. SQLite or Redis persistence would make this production-ready.
- **No wake-word detection yet:** Users must push-to-talk. Adding Porcupine or a local trigger word would make interaction truly hands-free.
- **LLM streaming:** The current implementation waits for the full LLM response before feeding TTS. Streaming tokens sentence-by-sentence into Edge TTS would cut latency significantly.

## Next Steps

1. Build a benchmarking dashboard to visualize pipeline latencies in real-time
2. Add LLM streaming + sentence-boundary TTS for sub-second response start
3. Implement a simple vector memory (RAG) so Nero can reference local documents
4. Polish the responsive layout – the HUD currently shines on desktop but needs love on mobile

## Reflection

Seeing the orb pulse from idle → listening → processing → speaking is incredibly satisfying. The visual feedback makes the AI feel alive. The next milestone is making it feel *fast* – right now the latency from "release spacebar" to "Nero starts speaking" is around 2–4 seconds depending on hardware. Getting that under 1 second will be the focus of the next sprint.
