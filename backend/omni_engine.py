import os
import asyncio
import time
import tempfile
import unicodedata
import re
import io

import certifi
import torch
from faster_whisper import WhisperModel
from transformers import AutoModelForCausalLM, AutoTokenizer

os.environ.setdefault("SSL_CERT_FILE", certifi.where())
os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())

import edge_tts

try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False


class OmniEngine:
    def __init__(self):
        print("Initializing Omni Engine...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # 1. STT: Faster Whisper (tiny model for low latency).
        print("Loading Whisper STT...")
        self.stt_model = WhisperModel(
            "tiny",
            device=self.device,
            compute_type="float16" if self.device == "cuda" else "int8",
        )

        # 2. LLM: Qwen2.5 1.5B Instruct.
        print("Loading Qwen2.5 LLM...")
        model_id = "Qwen/Qwen2.5-1.5B-Instruct"
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.llm_model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto",
        )

        # 3. TTS settings.
        self.tts_voice = "de-DE-ChristophNeural"
        self.tts_voices_fallback = [
            "de-DE-KerstenNeural",
            "de-DE-AmalaNeural",
            "de-AT-JonasNeural",
            "de-CH-LeniNeural",
        ]
        self.tts_rate = "+10%"  # Slightly faster speech
        self.tts_pitch = "+5%"  # Slightly higher pitch

        self.system_prompt = {
            "role": "system",
            "content": (
                "Du bist Nero, eine fortschrittliche, hilfsbereite und sehr menschlich wirkende KI. "
                "Antworte immer auf Deutsch. Halte deine Antworten kurz und prägnant, wie in einem echten Gespräch."
            ),
        }
        self.history = [self.system_prompt]

        print("Omni Engine Ready!")

    def transcribe_audio(self, audio_file_path):
        """Convert speech to text."""
        segments, _info = self.stt_model.transcribe(audio_file_path, beam_size=5, language="de")
        text = " ".join(segment.text for segment in segments)
        return text.strip()

    def generate_text(self, prompt_text):
        """Generate an LLM response."""
        self.history.append({"role": "user", "content": prompt_text})
        self.history = [self.system_prompt] + self.history[-12:]

        chat_text = self.tokenizer.apply_chat_template(
            self.history,
            tokenize=False,
            add_generation_prompt=True,
        )
        model_inputs = self.tokenizer([chat_text], return_tensors="pt").to(self.device)

        with torch.inference_mode():
            generated_ids = self.llm_model.generate(
                **model_inputs,
                max_new_tokens=150,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        generated_ids = [
            output_ids[len(input_ids):]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
        if not response:
            response = "Ich habe gerade keine passende Antwort generiert."

        self.history.append({"role": "assistant", "content": response})
        return response

    def _normalize_text_for_tts(self, text):
        """Normalize text for TTS: remove special chars, fix encoding issues."""
        # Clean up whitespace
        text = " ".join(text.split())
        if not text:
            text = "Ich habe gerade keine passende Antwort generiert."
        
        # Remove/replace problematic characters
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace("'", "'").replace("'", "'")
        
        # Remove multiple punctuation
        text = re.sub(r'([!?.])(?=\1)', '', text)
        
        # Keep only safe characters for TTS
        # Remove control characters
        text = ''.join(ch for ch in text if unicodedata.category(ch)[0] != 'C')
        
        # Normalize unicode
        text = unicodedata.normalize('NFKD', text)
        
        return text.strip()

    def _split_text_into_chunks(self, text, max_length=500):
        """Split text into chunks for TTS (edge-tts has limits)."""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Split by sentences first
        sentences = re.split(r'([.!?]+)', text)
        
        for i in range(0, len(sentences), 2):
            sentence = sentences[i] + (sentences[i+1] if i+1 < len(sentences) else "")
            
            if len(current_chunk) + len(sentence) <= max_length:
                current_chunk += sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

    async def text_to_speech(self, text, output_file_path, retry_count=2):
        """Convert text to speech with multiple TTS engines for reliability.
        
        Strategy:
        1. Try gTTS (Google TTS) first - most reliable
        2. Fall back to Edge TTS with working voices
        
        Features:
        - Text normalization for compatibility
        - Automatic retries with exponential backoff
        - Multiple engine and voice fallbacks
        """
        text = self._normalize_text_for_tts(text)
        
        # Try gTTS first (most reliable)
        if HAS_GTTS:
            print(f"  TTS: Attempting Google TTS (gTTS)...")
            for attempt in range(retry_count):
                try:
                    print(f"    Attempt {attempt + 1}/{retry_count}...", end="", flush=True)
                    
                    tts = gTTS(text=text, lang='de', slow=False)
                    tts.save(output_file_path)
                    
                    # Verify file
                    if os.path.exists(output_file_path) and os.path.getsize(output_file_path) > 1000:
                        print(f" SUCCESS ({os.path.getsize(output_file_path)} bytes)")
                        return
                    else:
                        raise Exception("Generated audio too small")
                
                except Exception as e:
                    print(f" FAILED: {e}")
                    if attempt < retry_count - 1:
                        await asyncio.sleep(2 ** attempt)
                    continue
        
        # Fall back to Edge TTS with known working voices
        if HAS_EDGE_TTS:
            print(f"  TTS: Attempting Edge TTS (fallback)...")
            
            # Only use voices that work reliably
            edge_tts_voices = [
                "de-DE-AmalaNeural",  # Known to work
                "de-DE-KerstenNeural",
                "de-AT-JonasNeural",
            ]
            
            for voice_idx, voice in enumerate(edge_tts_voices):
                print(f"    Voice {voice_idx + 1}/{len(edge_tts_voices)}: {voice}")
                
                for attempt in range(retry_count):
                    try:
                        print(f"      Attempt {attempt + 1}/{retry_count}...", end="", flush=True)
                        
                        communicate = edge_tts.Communicate(text, voice)
                        await asyncio.wait_for(
                            communicate.save(output_file_path),
                            timeout=30.0
                        )
                        
                        # Verify file
                        if os.path.exists(output_file_path) and os.path.getsize(output_file_path) > 1000:
                            print(f" SUCCESS ({os.path.getsize(output_file_path)} bytes)")
                            return
                        else:
                            raise Exception("Generated audio too small")
                    
                    except asyncio.TimeoutError:
                        print(f" TIMEOUT")
                        if attempt < retry_count - 1:
                            await asyncio.sleep(2 ** attempt)
                    
                    except Exception as e:
                        print(f" FAILED: {e}")
                        if attempt < retry_count - 1:
                            await asyncio.sleep(2 ** attempt)
                        continue
        
        # All methods failed
        raise Exception(
            f"TTS failed: gTTS available={HAS_GTTS}, Edge TTS available={HAS_EDGE_TTS}. "
            "Please install gTTS (pip install gTTS) or ensure Edge TTS network access."
        )

    async def process_audio(self, input_audio_path, output_audio_path):
        """Run the full Omni pipeline: STT -> LLM -> TTS."""
        print("Transcribing...")
        user_text = self.transcribe_audio(input_audio_path)
        print(f"User: {user_text}")

        if not user_text:
            return "Ich habe leider nichts verstanden.", False

        print("Thinking...")
        ai_text = self.generate_text(user_text)
        print(f"Nero: {ai_text}")

        print("Speaking...")
        await self.text_to_speech(ai_text, output_audio_path)
        return ai_text, True


if __name__ == "__main__":
    engine = OmniEngine()
    print("Test initialized. Ready.")
