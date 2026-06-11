"""
Dedicated TTS Test - Test the improved Text-to-Speech system
"""
import asyncio
import os
import sys
from pathlib import Path
from omni_engine import OmniEngine

async def test_tts():
    print("="*70)
    print("TTS (Text-to-Speech) TEST SUITE")
    print("="*70)
    
    # Initialize engine
    print("\n1. Initializing OmniEngine...")
    try:
        engine = OmniEngine()
        print("   OK - Engine initialized")
    except Exception as e:
        print(f"   ERROR - Failed to initialize: {e}")
        return False
    
    # Test cases with different text lengths and complexities
    test_cases = [
        ("Test 1: Short simple", "Hallo, wie geht es dir?"),
        ("Test 2: Medium text", "Guten Tag. Mein Name ist Nero und ich bin ein KI-Assistent. Ich kann dir heute helfen."),
        ("Test 3: Longer text", "Willkommen zu unserem KI-System! Ich bin Nero, eine fortschrittliche, hilfsbereite und sehr menschlich wirkende KI. Ich antworte immer auf Deutsch und halte meine Antworten kurz und prägnant, wie in einem echten Gespräch."),
        ("Test 4: With numbers", "Heute ist der 10. Juni 2026, es ist 16 Uhr und 30 Minuten."),
        ("Test 5: With special chars", "Das ist... toll! Wirklich? Ja, absolut!"),
    ]
    
    success_count = 0
    fail_count = 0
    
    for test_name, test_text in test_cases:
        print(f"\n{test_name}")
        print(f"  Text: '{test_text}'")
        
        output_file = f"tts_output_{len(test_cases) - fail_count}.mp3"
        
        try:
            print(f"  Generating audio...", end="", flush=True)
            await engine.text_to_speech(test_text, output_file)
            
            # Check if file was created and has content
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                if file_size > 1000:  # At least 1KB
                    print(f" SUCCESS ({file_size} bytes)")
                    success_count += 1
                    print(f"  Output file: {output_file}")
                    # Don't delete - keep for manual verification
                else:
                    print(f" ERROR - File too small ({file_size} bytes)")
                    fail_count += 1
                    os.remove(output_file)
            else:
                print(f" ERROR - No file created")
                fail_count += 1
        
        except Exception as e:
            print(f" ERROR - {e}")
            fail_count += 1
            if os.path.exists(output_file):
                os.remove(output_file)
        
        # Wait between requests
        await asyncio.sleep(1)
    
    print("\n" + "="*70)
    print(f"RESULTS: {success_count} passed, {fail_count} failed")
    print("="*70)
    
    return fail_count == 0

async def main():
    success = await test_tts()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
