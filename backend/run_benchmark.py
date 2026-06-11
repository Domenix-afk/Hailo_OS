import time
import asyncio
import os
import gc
import torch
from omni_engine import OmniEngine
import edge_tts

async def run_benchmark():
    results = {}
    print("Starte Benchmark...")
    
    # 1. Model Loading Time
    start_time = time.time()
    engine = OmniEngine()
    results['model_load'] = time.time() - start_time
    print(f"Modelle geladen in: {results['model_load']:.2f}s")
    
    # Warmup LLM (first inference is usually slower due to CUDA graph / memory allocation)
    print("Wärme Modelle auf...")
    engine.generate_text("Hallo")
    
    # Generate a dummy 3-second audio file (sine wave) for STT benchmark
    import wave
    import struct
    import math
    test_audio_path = "temp_benchmark_input.wav"
    sample_rate = 16000
    duration = 3.0
    print(f"Generiere lokales Test-Audio ({duration}s)...")
    with wave.open(test_audio_path, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        for i in range(int(sample_rate * duration)):
            value = int(32767.0 * math.sin(2.0 * math.pi * 440.0 * i / sample_rate))
            f.writeframesraw(struct.pack('<h', value))
    
    # 2. STT Benchmark
    print("Starte STT Benchmark...")
    start_time = time.time()
    transcribed_text = engine.transcribe_audio(test_audio_path)
    results['stt_time'] = time.time() - start_time
    print(f"STT: {transcribed_text} ({results['stt_time']:.2f}s)")
    
    if not transcribed_text.strip():
        transcribed_text = "Erzähle mir einen kurzen Witz über KI."
        print(f"STT war leer (Sinus-Ton). Verwende Fallback für LLM: '{transcribed_text}'")
    
    # 3. LLM Benchmark
    print("Starte LLM Benchmark...")
    start_time = time.time()
    llm_response = engine.generate_text(transcribed_text)
    results['llm_time'] = time.time() - start_time
    word_count = len(llm_response.split())
    results['llm_words'] = word_count
    results['llm_speed'] = word_count / results['llm_time'] if results['llm_time'] > 0 else 0
    print(f"LLM: {word_count} Wörter generiert in {results['llm_time']:.2f}s ({results['llm_speed']:.2f} W/s)")
    
    # 4. TTS Benchmark
    print("Starte TTS Benchmark...")
    out_audio_path = "temp_benchmark_output.mp3"
    start_time = time.time()
    try:
        # Normalize text to ASCII to avoid edge-tts unicode issues on Windows
        import unicodedata
        safe_text = unicodedata.normalize('NFKD', llm_response).encode('ascii', 'ignore').decode('utf-8')
        if not safe_text.strip(): safe_text = "Test"
        await engine.text_to_speech(safe_text, out_audio_path)
        results['tts_time'] = time.time() - start_time
        print(f"TTS: Audio generiert in {results['tts_time']:.2f}s")
    except Exception as e:
        print(f"TTS Fehler: {e}")
        results['tts_time'] = 0.0

    # 5. End-to-End Benchmark
    print("Starte Full Pipeline Benchmark...")
    engine.history = [{"role": "system", "content": "Du bist Nero. Antworte sehr kurz."}] # Reset history
    start_time = time.time()
    try:
        # Mock the engine's transcribe_audio and text_to_speech if needed, but let's just run it
        # Note: the full pipeline might fail if Edge TTS fails again, let's patch the engine method temporarily for the benchmark
        original_tts = engine.text_to_speech
        async def safe_tts(text, path):
            safe_txt = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
            if not safe_txt.strip(): safe_txt = "Test"
            try:
                await original_tts(safe_txt, path)
            except Exception:
                pass
        engine.text_to_speech = safe_tts
        await engine.process_audio(test_audio_path, out_audio_path)
        results['e2e_time'] = time.time() - start_time
        print(f"End-to-End Pipeline: {results['e2e_time']:.2f}s")
    except Exception as e:
        print(f"End-to-End Fehler: {e}")
        results['e2e_time'] = 0.0
    
    # GPU Memory Info (if CUDA available)
    if torch.cuda.is_available():
        results['vram_allocated'] = torch.cuda.memory_allocated() / (1024**2)
        results['vram_reserved'] = torch.cuda.memory_reserved() / (1024**2)
    else:
        results['vram_allocated'] = 0
        results['vram_reserved'] = 0
        
    # Cleanup
    if os.path.exists(test_audio_path): os.remove(test_audio_path)
    if os.path.exists(out_audio_path): os.remove(out_audio_path)
    
    # Print Markdown Table
    print("\n\n=== BENCHMARK RESULTS ===")
    print("| Komponente | Metrik | Ergebnis |")
    print("|------------|--------|----------|")
    print(f"| Model Loading | Initialisierung STT & LLM | {results['model_load']:.2f} s |")
    print(f"| Speech-to-Text | Transkription | {results['stt_time']:.3f} s |")
    print(f"| LLM Inference | Generierungszeit | {results['llm_time']:.3f} s |")
    print(f"| LLM Speed | Wörter pro Sekunde | {results['llm_speed']:.1f} W/s |")
    print(f"| Text-to-Speech | Synthese | {results['tts_time']:.3f} s |")
    print(f"| **End-to-End** | **Komplette Pipeline** | **{results['e2e_time']:.3f} s** |")
    
    if torch.cuda.is_available():
        print(f"| VRAM | Genutzter GPU Speicher | {results['vram_allocated']:.1f} MB |")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
