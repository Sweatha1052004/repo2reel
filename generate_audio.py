import os
import logging
import tempfile
import subprocess
import platform
from typing import Optional
import requests
import time

logger = logging.getLogger(__name__)

class AudioGenerator:
    """Generate audio from text using CPU-optimized text-to-speech"""
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.tts_engine = self._initialize_tts_engine()
        logger.info(f"Initialized AudioGenerator with engine: {self.tts_engine}")
    
    def _initialize_tts_engine(self) -> str:
        """Initialize the best available TTS engine"""
        # Try different TTS engines in order of preference
        
        # Check for system TTS (Windows SAPI, macOS say, Linux espeak)
        system = platform.system().lower()
        
        if system == "windows":
            try:
                import win32com.client
                return "sapi"
            except ImportError:
                pass
        elif system == "darwin":  # macOS
            try:
                subprocess.run(["say", "--version"], capture_output=True, check=True)
                return "say"
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
        elif system == "linux":
            # Check for espeak or festival
            try:
                subprocess.run(["espeak", "--version"], capture_output=True, check=True)
                return "espeak"
            except (subprocess.CalledProcessError, FileNotFoundError):
                try:
                    subprocess.run(["festival", "--version"], capture_output=True, check=True)
                    return "festival"
                except (subprocess.CalledProcessError, FileNotFoundError):
                    pass
        
        # Try Python TTS libraries
        try:
            import pyttsx3
            return "pyttsx3"
        except ImportError:
            pass
        
        try:
            from gtts import gTTS
            return "gtts"
        except ImportError:
            pass
        
        return "edge_tts"  # Free Microsoft Edge TTS as final fallback
    
    def generate_audio(self, text: str, session_id: str) -> str:
        """Generate audio file from text"""
        try:
            # Clean and prepare text
            text = self._clean_text_for_tts(text)
            
            output_file = os.path.join(self.temp_dir, f'repo2reel_{session_id}_audio.wav')
            
            if self.tts_engine == "sapi":
                return self._generate_with_sapi(text, output_file)
            elif self.tts_engine == "say":
                return self._generate_with_say(text, output_file)
            elif self.tts_engine == "espeak":
                return self._generate_with_espeak(text, output_file)
            elif self.tts_engine == "festival":
                return self._generate_with_festival(text, output_file)
            elif self.tts_engine == "pyttsx3":
                return self._generate_with_pyttsx3(text, output_file)
            elif self.tts_engine == "gtts":
                return self._generate_with_gtts(text, output_file)
            else:
                return self._generate_with_edge_tts(text, output_file)
                
        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            # Try fallback method
            return self._generate_fallback_audio(text, session_id)
    
    def _clean_text_for_tts(self, text: str) -> str:
        """Clean text for better TTS output"""
        # Remove timing markers
        import re
        text = re.sub(r'\[[\d:.-]+\]', '', text)
        
        # Remove markdown formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
        text = re.sub(r'`(.*?)`', r'\1', text)        # Code
        
        # Clean up multiple spaces and newlines
        text = re.sub(r'\n+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Ensure proper sentence ending
        text = text.strip()
        if text and not text.endswith('.'):
            text += '.'
        
        return text
    
    def _generate_with_sapi(self, text: str, output_file: str) -> str:
        """Generate audio using Windows SAPI"""
        try:
            import win32com.client
            
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            voices = speaker.GetVoices()
            
            # Try to find a good voice
            for voice in voices:
                voice_desc = voice.GetDescription().lower()
                if any(name in voice_desc for name in ["david", "mark", "zira", "hazel"]):
                    speaker.Voice = voice
                    break
            
            # Set speech rate (slower for better comprehension)
            speaker.Rate = 0  # Normal rate
            
            # Save to WAV file
            wav_format = win32com.client.Dispatch("SAPI.SpAudioFormat")
            wav_format.Type = 34  # SAFT22kHz16BitMono
            
            file_stream = win32com.client.Dispatch("SAPI.SpFileStream")
            file_stream.Open(output_file, 3)  # Write mode
            file_stream.Format = wav_format
            
            speaker.AudioOutputStream = file_stream
            speaker.Speak(text)
            
            file_stream.Close()
            
            logger.info(f"Generated audio with SAPI: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"SAPI TTS error: {e}")
            raise
    
    def _generate_with_say(self, text: str, output_file: str) -> str:
        """Generate audio using macOS say command"""
        try:
            # Use macOS say command with output to file
            subprocess.run([
                "say", 
                "-v", "Alex",  # Use Alex voice
                "-r", "180",   # Words per minute
                "-o", output_file.replace('.wav', '.aiff'),  # say outputs AIFF
                text
            ], check=True)
            
            # Convert AIFF to WAV using ffmpeg if available
            aiff_file = output_file.replace('.wav', '.aiff')
            try:
                subprocess.run([
                    "ffmpeg", "-i", aiff_file, "-y", output_file
                ], check=True, capture_output=True)
                os.remove(aiff_file)  # Clean up AIFF file
            except (subprocess.CalledProcessError, FileNotFoundError):
                # If ffmpeg not available, return AIFF file
                return aiff_file
            
            logger.info(f"Generated audio with say: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"macOS say TTS error: {e}")
            raise
    
    def _generate_with_espeak(self, text: str, output_file: str) -> str:
        """Generate audio using espeak"""
        try:
            subprocess.run([
                "espeak",
                "-v", "en+m3",  # English male voice
                "-s", "160",     # Speed (words per minute)
                "-a", "80",      # Amplitude
                "-w", output_file,  # Write to file
                text
            ], check=True)
            
            logger.info(f"Generated audio with espeak: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"espeak TTS error: {e}")
            raise
    
    def _generate_with_festival(self, text: str, output_file: str) -> str:
        """Generate audio using Festival TTS"""
        try:
            # Create temporary text file
            text_file = output_file.replace('.wav', '.txt')
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            # Generate speech with Festival
            subprocess.run([
                "text2wave",
                text_file,
                "-o", output_file
            ], check=True)
            
            # Clean up text file
            os.remove(text_file)
            
            logger.info(f"Generated audio with Festival: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Festival TTS error: {e}")
            raise
    
    def _generate_with_pyttsx3(self, text: str, output_file: str) -> str:
        """Generate audio using pyttsx3 (cross-platform TTS)"""
        try:
            import pyttsx3
            
            engine = pyttsx3.init()
            
            # Configure voice properties
            voices = engine.getProperty('voices')
            if voices:
                # Try to find a male voice or any clear voice
                for voice in voices:
                    if 'male' in voice.name.lower() or 'david' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
                    elif 'zira' in voice.name.lower() or 'alex' in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        break
            
            # Set speech rate (words per minute)
            engine.setProperty('rate', 160)
            
            # Set volume
            engine.setProperty('volume', 0.9)
            
            # Save to file
            engine.save_to_file(text, output_file)
            engine.runAndWait()
            
            logger.info(f"Generated audio with pyttsx3: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"pyttsx3 TTS error: {e}")
            raise
    
    def _generate_with_gtts(self, text: str, output_file: str) -> str:
        """Generate audio using Google Text-to-Speech"""
        try:
            from gtts import gTTS
            
            # Create gTTS object
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save to MP3 first
            mp3_file = output_file.replace('.wav', '.mp3')
            tts.save(mp3_file)
            
            # Convert MP3 to WAV using ffmpeg if available
            try:
                subprocess.run([
                    "ffmpeg", "-i", mp3_file, "-ar", "44100", "-ac", "1", "-y", output_file
                ], check=True, capture_output=True)
                os.remove(mp3_file)  # Clean up MP3 file
                logger.info(f"Generated audio with gTTS (converted to WAV): {output_file}")
                return output_file
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Return MP3 file if conversion fails
                logger.info(f"Generated audio with gTTS (MP3): {mp3_file}")
                return mp3_file
                
        except Exception as e:
            logger.error(f"gTTS error: {e}")
            raise
    
    def _generate_with_edge_tts(self, text: str, output_file: str) -> str:
        """Generate audio using Microsoft Edge TTS (free)"""
        try:
            # Try to use edge-tts library
            try:
                import edge_tts
                import asyncio
                
                async def generate_speech():
                    voice = "en-US-AriaNeural"  # Default voice
                    communicate = edge_tts.Communicate(text, voice)
                    await communicate.save(output_file)
                
                asyncio.run(generate_speech())
                logger.info(f"Generated audio with Edge TTS: {output_file}")
                return output_file
                
            except ImportError:
                # Try command line edge-tts
                mp3_file = output_file.replace('.wav', '.mp3')
                result = subprocess.run([
                    "edge-tts",
                    "--text", text,
                    "--write-media", mp3_file,
                    "--voice", "en-US-AriaNeural"
                ], capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    # Convert to WAV if ffmpeg available
                    try:
                        subprocess.run([
                            "ffmpeg", "-i", mp3_file, "-ar", "44100", "-ac", "1", "-y", output_file
                        ], check=True, capture_output=True)
                        os.remove(mp3_file)
                        return output_file
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        return mp3_file
                else:
                    raise Exception(f"Edge TTS command failed: {result.stderr}")
                    
        except Exception as e:
            logger.error(f"Edge TTS error: {e}")
            raise
    
    def _generate_fallback_audio(self, text: str, session_id: str) -> str:
        """Generate a silent audio file as ultimate fallback"""
        try:
            output_file = os.path.join(self.temp_dir, f'repo2reel_{session_id}_audio_silent.wav')
            
            # Try to create a short silent audio file using ffmpeg
            try:
                duration = min(len(text.split()) * 0.5, 180)  # Estimate duration
                subprocess.run([
                    "ffmpeg", "-f", "lavfi", 
                    "-i", f"anullsrc=duration={duration}:sample_rate=44100:channel_layout=mono",
                    "-y", output_file
                ], check=True, capture_output=True)
                
                logger.warning(f"Generated silent audio fallback: {output_file}")
                return output_file
                
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Create a minimal WAV file manually
                import wave
                import struct
                
                sample_rate = 44100
                duration = min(len(text.split()) * 0.5, 180)
                frames = int(duration * sample_rate)
                
                with wave.open(output_file, 'w') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(sample_rate)
                    
                    # Write silent frames
                    for _ in range(frames):
                        wav_file.writeframes(struct.pack('<h', 0))
                
                logger.warning(f"Generated manual silent audio: {output_file}")
                return output_file
                
        except Exception as e:
            logger.error(f"Fallback audio generation failed: {e}")
            raise Exception("Could not generate audio file")

def generate_audio_from_text(text: str, session_id: str) -> str:
    """Main function to generate audio from text"""
    try:
        generator = AudioGenerator()
        return generator.generate_audio(text, session_id)
    except Exception as e:
        logger.error(f"Failed to generate audio: {e}")
        raise
