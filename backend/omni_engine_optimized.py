"""
Optimized Nero AI Engine
Performance, Memory, and Reliability Improvements
"""

import os
import asyncio
import time
import tempfile
import unicodedata
import re
import io
import logging
from typing import Optional, Tuple
from functools import lru_cache

import certifi
import torch
import gc
from faster_whisper import WhisperModel
from transformers import AutoModelForCausalLM, AutoTokenizer

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(name)s] %(message)s')
logger = logging.getLogger(__name__)

# Environment setup
os.environ.setdefault("SSL_CERT_FILE", certifi.where())
os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())
os.environ['TOKENIZERS_PARALLELISM'] = 'false'  # Prevent tokenizer warnings

try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False


class OmniEngine:
    """Optimized Nero AI Engine with caching, memory management, and error handling."""
    
    # Class-level settings for optimization
    CACHE_SIZE = 128  # LRU cache size
    STT_BEAM_SIZE = 3  # Reduced from 5 for speed (quality trade-off acceptable)
    LLM_MAX_TOKENS = 120  # Reduced from 150 for faster responses
    TEXT_CHUNK_SIZE = 400  # Reduced from 500 for stability
    GARBAGE_COLLECT_INTERVAL = 5  # GC every 5 requests
    
    def __init__(self, enable_gpu: bool = True, enable_logging: bool = True):
        """Initialize the Nero AI Engine with optimizations.
        
        Args:
            enable_gpu: Use GPU if available (default: True)
            enable_logging: Enable detailed logging (default: True)
        """
        self.enable_logging = enable_logging
        self.enable_gpu = enable_gpu and torch.cuda.is_available()
        self.request_count = 0
        
        logger.info(f"Initializing Nero Engine (GPU: {self.enable_gpu})")
        
        self.device = "cuda" if self.enable_gpu else "cpu"
        logger.info(f"Using device: {self.device}")
        
        # 1. STT: Faster Whisper (optimized)
        logger.info("Loading Whisper STT model...")
        start = time.time()
        self.stt_model = WhisperModel(
            "tiny",
            device=self.device,
            compute_type="float16" if self.enable_gpu else "int8",
            cpu_threads=4,  # Use 4 CPU threads for better performance
            num_workers=2,
        )
        logger.info(f"STT loaded in {time.time()-start:.2f}s")
        
        # 2. LLM: Qwen2.5 (optimized)
        logger.info("Loading Qwen2.5 LLM model...")
        start = time.time()
        model_id = "Qwen/Qwen2.5-1.5B-Instruct"
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.llm_model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if self.enable_gpu else torch.float32,
            device_map="auto" if self.enable_gpu else None,
        )
        
        # Enable evaluation mode for inference (no gradients)
        self.llm_model.eval()
        logger.info(f"LLM loaded in {time.time()-start:.2f}s")
        
        # 3. TTS settings (optimized)
        self.tts_voice = "de-DE-AmalaNeural"  # Use known-working voice by default
        
        # System prompt (optimized for brevity)
        self.system_prompt = {
            "role": "system",
            "content": (
                "Du bist Nero, eine hilfsbereite KI. "
                "Antworte auf Deutsch, kurz und prägnant."
            ),
        }
        self.history = [self.system_prompt]
        self.max_history = 8  # Reduced from 12 for faster processing
        
        logger.info("Nero Engine initialized successfully")
    
    @lru_cache(maxsize=CACHE_SIZE)
    def _cached_normalize_text(self, text: str) -> str:
        """Cached text normalization."""
        # Clean whitespace
        text = " ".join(text.split())
        if not text:
            return "Ich habe gerade keine Antwort."
        
        # Quick replacements
        text = text.translate(str.maketrans({
            '"': '"', '"': '"',
            ''': "'", ''': "'"
        }))
        
        # Remove multiple punctuation
        text = re.sub(r'([!?.])(?=\1)', '', text)
        
        # Remove control characters more efficiently
        text = ''.join(ch for ch in text if unicodedata.category(ch)[0] != 'C')
        
        # Normalize unicode
        text = unicodedata.normalize('NFKD', text)
        
        return text.strip()
    
    def transcribe_audio(self, audio_file_path: str) -> str:
        """Optimized STT with memory cleanup."""
        try:
            segments, _ = self.stt_model.transcribe(
                audio_file_path,
                beam_size=self.STT_BEAM_SIZE,
                language="de",
                condition_on_previous_text=False,  # Disable for speed
            )
            text = " ".join(seg.text for seg in segments)
            result = text.strip()
            logger.info(f"STT result: {result[:50]}...")
            return result
        except Exception as e:
            logger.error(f"STT error: {e}")
            return ""
    
    def generate_text(self, prompt_text: str) -> str:
        """Optimized LLM generation."""
        try:
            # Add to history
            self.history.append({"role": "user", "content": prompt_text})
            self.history = [self.system_prompt] + self.history[-self.max_history:]
            
            # Tokenize
            chat_text = self.tokenizer.apply_chat_template(
                self.history,
                tokenize=False,
                add_generation_prompt=True,
            )
            model_inputs = self.tokenizer(
                [chat_text],
                return_tensors="pt",
                truncation=True,
                max_length=512,
            ).to(self.device)
            
            # Generate with optimized parameters
            with torch.no_grad():  # No gradients needed
                generated_ids = self.llm_model.generate(
                    **model_inputs,
                    max_new_tokens=self.LLM_MAX_TOKENS,
                    min_length=10,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    top_k=50,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    use_cache=True,  # Enable KV cache for speed
                )
            
            # Decode
            generated_ids = [
                output_ids[len(input_ids):]
                for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            
            response = self.tokenizer.batch_decode(
                generated_ids,
                skip_special_tokens=True
            )[0].strip()
            
            if not response:
                response = "Ich bin bereit, dir zu helfen."
            
            # Add to history
            self.history.append({"role": "assistant", "content": response})
            
            logger.info(f"LLM result: {response[:50]}...")
            
            # Periodic garbage collection
            self.request_count += 1
            if self.request_count % self.GARBAGE_COLLECT_INTERVAL == 0:
                gc.collect()
                if self.enable_gpu:
                    torch.cuda.empty_cache()
            
            return response
        
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return "Entschuldigung, ich hatte einen Fehler."
    
    async def text_to_speech(
        self,
        text: str,
        output_file_path: str,
        retry_count: int = 2,
        timeout: float = 20.0
    ) -> None:
        """Optimized TTS with better error handling and timeouts.
        
        Args:
            text: Text to convert to speech
            output_file_path: Output file path
            retry_count: Number of retries
            timeout: Timeout in seconds
        """
        text = self._cached_normalize_text(text)
        
        # Try gTTS first (most reliable and fast)
        if HAS_GTTS:
            for attempt in range(retry_count):
                try:
                    tts = gTTS(text=text, lang='de', slow=False)
                    tts.save(output_file_path)
                    
                    # Verify
                    if os.path.getsize(output_file_path) > 1000:
                        logger.info(f"TTS success via gTTS ({os.path.getsize(output_file_path)} bytes)")
                        return
                    
                except Exception as e:
                    logger.warning(f"gTTS attempt {attempt + 1} failed: {e}")
                    if attempt < retry_count - 1:
                        await asyncio.sleep(1.0)
        
        # Fallback to Edge TTS
        if HAS_EDGE_TTS:
            try:
                communicate = edge_tts.Communicate(text, self.tts_voice)
                await asyncio.wait_for(
                    communicate.save(output_file_path),
                    timeout=timeout
                )
                logger.info(f"TTS success via Edge TTS ({os.path.getsize(output_file_path)} bytes)")
                return
            except Exception as e:
                logger.warning(f"Edge TTS failed: {e}")
        
        # Both failed - create empty audio placeholder
        logger.error("TTS failed - creating silence placeholder")
        # Create a simple silence placeholder
        import wave
        with wave.open(output_file_path, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframesraw(b'\x00' * 32000)
    
    async def process_audio(
        self,
        input_audio_path: str,
        output_audio_path: str
    ) -> Tuple[str, bool]:
        """Run the optimized full pipeline: STT -> LLM -> TTS.
        
        Args:
            input_audio_path: Input audio file
            output_audio_path: Output audio file
        
        Returns:
            Tuple of (response_text, success)
        """
        try:
            logger.info("Starting audio processing pipeline")
            
            # 1. STT
            user_text = self.transcribe_audio(input_audio_path)
            if not user_text:
                logger.warning("STT returned empty text")
                return "Ich habe dich nicht verstanden.", False
            
            # 2. LLM
            ai_text = self.generate_text(user_text)
            if not ai_text:
                logger.warning("LLM returned empty text")
                return "Ich konnte keine Antwort generieren.", False
            
            # 3. TTS
            await self.text_to_speech(ai_text, output_audio_path)
            
            logger.info("Audio processing pipeline completed successfully")
            return ai_text, True
        
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            return f"Fehler: {str(e)}", False
    
    def cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up resources")
        gc.collect()
        if self.enable_gpu:
            torch.cuda.empty_cache()


if __name__ == "__main__":
    engine = OmniEngine()
    logger.info("Engine test initialized. Ready.")
