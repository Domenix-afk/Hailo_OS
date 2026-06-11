"""
Comprehensive Benchmark Test Suite für Nero AI Framework
Testet alle Komponenten mit detaillierten Metriken und Statistiken
"""

import time
import asyncio
import os
import gc
import psutil
import torch
import json
import statistics
from datetime import datetime
from pathlib import Path
from omni_engine import OmniEngine
import wave
import struct
import math
import unicodedata

class BenchmarkSuite:
    def __init__(self):
        self.engine = None
        self.results = {}
        self.system_info = self._get_system_info()
        self.test_audio_path = "temp_benchmark_input.wav"
        self.output_audio_path = "temp_benchmark_output.mp3"
        self.process = psutil.Process()
        
    def _get_system_info(self):
        """Sammelt System- und Hardware-Informationen"""
        info = {
            "timestamp": datetime.now().isoformat(),
            "cpu_count": psutil.cpu_count(logical=False),
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "ram_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
            "cuda_available": torch.cuda.is_available(),
        }
        if torch.cuda.is_available():
            info["cuda_device"] = torch.cuda.get_device_name(0)
            info["cuda_memory_total_gb"] = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2)
        return info
    
    def _create_test_audio(self, duration=3.0, frequency=440.0):
        """Erstellt ein Test-Audio-File (Sinuswelle)"""
        print(f"  → Generiere Test-Audio ({duration}s @ {frequency}Hz)...")
        sample_rate = 16000
        with wave.open(self.test_audio_path, 'w') as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(sample_rate)
            for i in range(int(sample_rate * duration)):
                value = int(32767.0 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
                f.writeframesraw(struct.pack('<h', value))
        print(f"    ✓ Audio erstellt: {self.test_audio_path}")
    
    def _measure_memory(self):
        """Misst aktuellen RAM- und GPU-Speicherverbrauch"""
        memory = {
            "ram_mb": round(self.process.memory_info().rss / (1024**2), 2),
            "ram_percent": round(self.process.memory_percent(), 2)
        }
        if torch.cuda.is_available():
            memory["gpu_allocated_mb"] = round(torch.cuda.memory_allocated() / (1024**2), 2)
            memory["gpu_cached_mb"] = round(torch.cuda.memory_reserved() / (1024**2), 2)
            memory["gpu_total_mb"] = round(torch.cuda.get_device_properties(0).total_memory / (1024**2), 2)
        return memory
    
    async def benchmark_model_loading(self, iterations=3):
        """Testet das Laden der Modelle"""
        print("\n" + "="*60)
        print("1️⃣ MODEL LOADING BENCHMARK")
        print("="*60)
        
        times = []
        for i in range(iterations):
            print(f"\n  Lauf {i+1}/{iterations}...")
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            start_time = time.time()
            engine = OmniEngine()
            elapsed = time.time() - start_time
            times.append(elapsed)
            
            memory = self._measure_memory()
            print(f"    Zeit: {elapsed:.2f}s")
            print(f"    RAM: {memory['ram_mb']}MB ({memory['ram_percent']}%)")
            if 'gpu_allocated_mb' in memory:
                print(f"    GPU: {memory['gpu_allocated_mb']}MB / {memory['gpu_total_mb']}MB")
            
            if i == 0:
                self.engine = engine
        
        self.results['model_loading'] = {
            'times': times,
            'min': min(times),
            'max': max(times),
            'mean': statistics.mean(times),
            'stdev': statistics.stdev(times) if len(times) > 1 else 0,
            'memory_after': self._measure_memory()
        }
        
        print(f"\n  📊 Ergebnisse:")
        print(f"    Min: {self.results['model_loading']['min']:.2f}s")
        print(f"    Max: {self.results['model_loading']['max']:.2f}s")
        print(f"    Durchschnitt: {self.results['model_loading']['mean']:.2f}s")
        print(f"    Std Dev: {self.results['model_loading']['stdev']:.2f}s")
    
    async def benchmark_stt(self, iterations=3):
        """Testet Speech-to-Text Funktion"""
        print("\n" + "="*60)
        print("2️⃣ SPEECH-TO-TEXT (STT) BENCHMARK")
        print("="*60)
        
        if not self.engine:
            self.engine = OmniEngine()
        
        self._create_test_audio(duration=3.0)
        
        times = []
        for i in range(iterations):
            print(f"\n  Lauf {i+1}/{iterations}...")
            gc.collect()
            
            start_time = time.time()
            result = self.engine.transcribe_audio(self.test_audio_path)
            elapsed = time.time() - start_time
            times.append(elapsed)
            
            print(f"    Zeit: {elapsed:.2f}s")
            print(f"    Result: '{result}'")
            print(f"    Speicher: {self._measure_memory()['ram_mb']}MB")
        
        self.results['stt'] = {
            'times': times,
            'min': min(times),
            'max': max(times),
            'mean': statistics.mean(times),
            'stdev': statistics.stdev(times) if len(times) > 1 else 0,
            'input_duration_sec': 3.0
        }
        
        print(f"\n  📊 Ergebnisse:")
        print(f"    Min: {self.results['stt']['min']:.2f}s")
        print(f"    Max: {self.results['stt']['max']:.2f}s")
        print(f"    Durchschnitt: {self.results['stt']['mean']:.2f}s")
        print(f"    RTF (Real-Time Factor): {self.results['stt']['mean']/3.0:.2f}x")
    
    async def benchmark_llm(self, iterations=3):
        """Testet Language Model Generierung"""
        print("\n" + "="*60)
        print("3️⃣ LANGUAGE MODEL (LLM) BENCHMARK")
        print("="*60)
        
        if not self.engine:
            self.engine = OmniEngine()
        
        test_prompts = [
            "Erzähle mir einen kurzen Witz über KI.",
            "Was ist Machine Learning?",
            "Beschreibe in drei Sätzen, was Künstliche Intelligenz ist."
        ]
        
        times = []
        word_counts = []
        
        for prompt_idx in range(min(len(test_prompts), iterations)):
            print(f"\n  Lauf {prompt_idx+1}/{iterations}: '{test_prompts[prompt_idx]}'")
            
            # Reset history
            self.engine.history = [self.engine.system_prompt]
            gc.collect()
            
            start_time = time.time()
            response = self.engine.generate_text(test_prompts[prompt_idx])
            elapsed = time.time() - start_time
            times.append(elapsed)
            
            word_count = len(response.split())
            word_counts.append(word_count)
            
            throughput = word_count / elapsed if elapsed > 0 else 0
            
            print(f"    Zeit: {elapsed:.2f}s")
            print(f"    Wörter: {word_count}")
            print(f"    Durchsatz: {throughput:.2f} W/s")
            print(f"    Response: {response[:80]}...")
        
        self.results['llm'] = {
            'times': times,
            'word_counts': word_counts,
            'min_time': min(times),
            'max_time': max(times),
            'mean_time': statistics.mean(times),
            'stdev_time': statistics.stdev(times) if len(times) > 1 else 0,
            'throughput': statistics.mean([wc/t for wc, t in zip(word_counts, times) if t > 0])
        }
        
        print(f"\n  📊 Ergebnisse:")
        print(f"    Min Zeit: {self.results['llm']['min_time']:.2f}s")
        print(f"    Max Zeit: {self.results['llm']['max_time']:.2f}s")
        print(f"    Durchschnittliche Zeit: {self.results['llm']['mean_time']:.2f}s")
        print(f"    Ø Wörter pro Sekunde: {self.results['llm']['throughput']:.2f} W/s")
    
    async def benchmark_tts(self, iterations=3):
        """Testet Text-to-Speech Funktion"""
        print("\n" + "="*60)
        print("4️⃣ TEXT-TO-SPEECH (TTS) BENCHMARK")
        print("="*60)
        
        if not self.engine:
            self.engine = OmniEngine()
        
        test_texts = [
            "Das ist ein Test.",
            "Willkommen bei Nero, deinem KI-Assistenten.",
            "Machine Learning ist eine faszinierende Technologie."
        ]
        
        times = []
        
        for text_idx in range(min(len(test_texts), iterations)):
            text = test_texts[text_idx]
            output_file = f"temp_benchmark_tts_{text_idx}.mp3"
            
            print(f"\n  Lauf {text_idx+1}/{iterations}: '{text}'")
            
            # Normalize text
            safe_text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
            if not safe_text.strip():
                safe_text = "Test"
            
            gc.collect()
            
            start_time = time.time()
            try:
                await self.engine.text_to_speech(safe_text, output_file)
                elapsed = time.time() - start_time
                times.append(elapsed)
                
                file_size = os.path.getsize(output_file) / (1024**2)
                print(f"    Zeit: {elapsed:.2f}s")
                print(f"    Dateigröße: {file_size:.2f}MB")
                
                os.remove(output_file)
            except Exception as e:
                print(f"    ❌ Fehler: {e}")
        
        if times:
            self.results['tts'] = {
                'times': times,
                'min': min(times),
                'max': max(times),
                'mean': statistics.mean(times),
                'stdev': statistics.stdev(times) if len(times) > 1 else 0,
            }
            
            print(f"\n  📊 Ergebnisse:")
            print(f"    Min: {self.results['tts']['min']:.2f}s")
            print(f"    Max: {self.results['tts']['max']:.2f}s")
            print(f"    Durchschnitt: {self.results['tts']['mean']:.2f}s")
    
    async def benchmark_end_to_end(self, iterations=2):
        """Testet die komplette Pipeline"""
        print("\n" + "="*60)
        print("5️⃣ END-TO-END PIPELINE BENCHMARK")
        print("="*60)
        
        if not self.engine:
            self.engine = OmniEngine()
        
        self._create_test_audio(duration=2.0)
        
        times = []
        
        for i in range(iterations):
            print(f"\n  Lauf {i+1}/{iterations}...")
            
            # Reset history
            self.engine.history = [self.engine.system_prompt]
            gc.collect()
            
            output_file = f"temp_e2e_output_{i}.mp3"
            
            start_time = time.time()
            try:
                await self.engine.process_audio(self.test_audio_path, output_file)
                elapsed = time.time() - start_time
                times.append(elapsed)
                
                print(f"    Zeit: {elapsed:.2f}s")
                
                if os.path.exists(output_file):
                    os.remove(output_file)
            except Exception as e:
                print(f"    ❌ Fehler: {e}")
        
        if times:
            self.results['e2e'] = {
                'times': times,
                'min': min(times),
                'max': max(times),
                'mean': statistics.mean(times),
                'stdev': statistics.stdev(times) if len(times) > 1 else 0,
            }
            
            print(f"\n  📊 Ergebnisse:")
            print(f"    Min: {self.results['e2e']['min']:.2f}s")
            print(f"    Max: {self.results['e2e']['max']:.2f}s")
            print(f"    Durchschnitt: {self.results['e2e']['mean']:.2f}s")
    
    async def benchmark_stress_test(self):
        """Stress-Test: Mehrere aufeinanderfolgende Verarbeitungen"""
        print("\n" + "="*60)
        print("6️⃣ STRESS TEST (10 aufeinanderfolgende Aufrufe)")
        print("="*60)
        
        if not self.engine:
            self.engine = OmniEngine()
        
        prompts = [
            "Hallo", "Wer bist du?", "Erkläre KI", "Witz",
            "Dankeschön", "Auf Wiedersehen", "Test 1", "Test 2", "Test 3", "Final"
        ]
        
        times = []
        start_total = time.time()
        
        for idx, prompt in enumerate(prompts):
            print(f"  {idx+1}/10: '{prompt}'", end="", flush=True)
            
            self.engine.history = [self.engine.system_prompt]
            
            start = time.time()
            try:
                response = self.engine.generate_text(prompt)
                elapsed = time.time() - start
                times.append(elapsed)
                print(f" ✓ ({elapsed:.2f}s)")
            except Exception as e:
                print(f" ❌ ({e})")
        
        total_time = time.time() - start_total
        
        self.results['stress_test'] = {
            'times': times,
            'total_time': total_time,
            'avg_time': statistics.mean(times) if times else 0,
            'requests_per_second': len(times) / total_time if total_time > 0 else 0
        }
        
        print(f"\n  📊 Ergebnisse:")
        print(f"    Gesamtzeit: {total_time:.2f}s")
        print(f"    Ø Zeit pro Anfrage: {self.results['stress_test']['avg_time']:.2f}s")
        print(f"    Anfragen/Sekunde: {self.results['stress_test']['requests_per_second']:.2f}")
    
    def generate_report(self):
        """Erstellt einen detaillierten Benchmark-Report"""
        print("\n" + "="*60)
        print("📋 BENCHMARK REPORT GENERIERUNG")
        print("="*60)
        
        report = {
            "system_info": self.system_info,
            "benchmark_results": self.results,
            "summary": {
                "model_loading_avg": round(self.results.get('model_loading', {}).get('mean', 0), 2),
                "stt_avg": round(self.results.get('stt', {}).get('mean', 0), 2),
                "llm_throughput": round(self.results.get('llm', {}).get('throughput', 0), 2),
                "tts_avg": round(self.results.get('tts', {}).get('mean', 0), 2),
                "e2e_avg": round(self.results.get('e2e', {}).get('mean', 0), 2),
            }
        }
        
        # Save JSON report
        report_file = f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"  ✓ JSON Report: {report_file}")
        
        # Save TXT report
        txt_file = report_file.replace('.json', '.txt')
        with open(txt_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write("NERO AI FRAMEWORK - COMPREHENSIVE BENCHMARK REPORT\n")
            f.write("="*70 + "\n\n")
            
            f.write("SYSTEM INFORMATION\n")
            f.write("-"*70 + "\n")
            for key, value in self.system_info.items():
                f.write(f"  {key}: {value}\n")
            
            f.write("\n\nBENCHMARK RESULTS\n")
            f.write("-"*70 + "\n")
            
            if 'model_loading' in self.results:
                f.write("\n1. Model Loading\n")
                r = self.results['model_loading']
                f.write(f"   Min: {r['min']:.2f}s\n")
                f.write(f"   Max: {r['max']:.2f}s\n")
                f.write(f"   Mean: {r['mean']:.2f}s\n")
                f.write(f"   StdDev: {r['stdev']:.2f}s\n")
            
            if 'stt' in self.results:
                f.write("\n2. Speech-to-Text\n")
                r = self.results['stt']
                f.write(f"   Mean Time: {r['mean']:.2f}s\n")
                f.write(f"   Real-Time Factor: {r['mean']/3.0:.2f}x\n")
            
            if 'llm' in self.results:
                f.write("\n3. Language Model\n")
                r = self.results['llm']
                f.write(f"   Mean Time: {r['mean_time']:.2f}s\n")
                f.write(f"   Throughput: {r['throughput']:.2f} words/sec\n")
            
            if 'tts' in self.results:
                f.write("\n4. Text-to-Speech\n")
                r = self.results['tts']
                f.write(f"   Mean Time: {r['mean']:.2f}s\n")
            
            if 'e2e' in self.results:
                f.write("\n5. End-to-End Pipeline\n")
                r = self.results['e2e']
                f.write(f"   Mean Time: {r['mean']:.2f}s\n")
            
            if 'stress_test' in self.results:
                f.write("\n6. Stress Test (10 Requests)\n")
                r = self.results['stress_test']
                f.write(f"   Total Time: {r['total_time']:.2f}s\n")
                f.write(f"   Avg per Request: {r['avg_time']:.2f}s\n")
                f.write(f"   Requests/sec: {r['requests_per_second']:.2f}\n")
            
            f.write("\n" + "="*70 + "\n")
        
        print(f"  ✓ Text Report: {txt_file}")
        
        # Print summary to console
        print("\n  ZUSAMMENFASSUNG:")
        for key, value in report['summary'].items():
            print(f"    {key}: {value}")
    
    async def run_full_benchmark(self):
        """Führt alle Benchmarks aus"""
        print("\n")
        print("╔" + "="*58 + "╗")
        print("║" + " "*58 + "║")
        print("║" + "  🚀 NERO AI COMPREHENSIVE BENCHMARK SUITE 🚀".center(58) + "║")
        print("║" + " "*58 + "║")
        print("╚" + "="*58 + "╝")
        
        try:
            await self.benchmark_model_loading(iterations=2)
            await self.benchmark_stt(iterations=2)
            await self.benchmark_llm(iterations=3)
            await self.benchmark_tts(iterations=2)
            await self.benchmark_end_to_end(iterations=2)
            await self.benchmark_stress_test()
            
            self.generate_report()
            
            print("\n" + "="*60)
            print("✅ BENCHMARK ERFOLGREICH ABGESCHLOSSEN!")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"\n❌ Fehler während des Benchmarks: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Cleanup
            if os.path.exists(self.test_audio_path):
                os.remove(self.test_audio_path)

async def main():
    suite = BenchmarkSuite()
    await suite.run_full_benchmark()

if __name__ == "__main__":
    asyncio.run(main())
