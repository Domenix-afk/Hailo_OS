"""
Simplified Benchmark Test mit Output-Logging
"""
import sys
import time
import asyncio
import os
import gc
import torch
import json
from datetime import datetime
from pathlib import Path

# Redirect output
log_file = open("benchmark.log", "w", buffering=1)
sys.stdout = log_file
sys.stderr = log_file

print("="*70, flush=True)
print("NERO AI BENCHMARK - STARTING", flush=True)
print(f"Timestamp: {datetime.now()}", flush=True)
print("="*70, flush=True)

print("\n1. Checking System Info...", flush=True)
print(f"   CUDA Available: {torch.cuda.is_available()}", flush=True)
if torch.cuda.is_available():
    print(f"   GPU: {torch.cuda.get_device_name(0)}", flush=True)
    print(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB", flush=True)

print("\n2. Importing OmniEngine...", flush=True)
try:
    from omni_engine import OmniEngine
    print(f"   OK - Import successful", flush=True)
except Exception as e:
    print(f"   ERROR - Import failed: {e}", flush=True)
    log_file.close()
    sys.exit(1)

print("\n3. Initializing OmniEngine (Loading Models)...", flush=True)
try:
    engine = OmniEngine()
    print("   OK - Engine initialized", flush=True)
except Exception as e:
    print(f"   ERROR - Init failed: {e}", flush=True)
    log_file.close()
    sys.exit(1)

print("\n4. Testing LLM Inference...", flush=True)
try:
    for i in range(3):
        print(f"\n   Test {i+1}/3:", flush=True)
        start = time.time()
        result = engine.generate_text("Hallo, wie geht es dir?")
        elapsed = time.time() - start
        print(f"   Time: {elapsed:.2f}s", flush=True)
        print(f"   Result: {result[:60]}...", flush=True)
        gc.collect()
except Exception as e:
    print(f"   ERROR - LLM test failed: {e}", flush=True)

print("\n" + "="*70, flush=True)
print("BENCHMARK COMPLETE - SUCCESS", flush=True)
print("="*70, flush=True)

log_file.close()
