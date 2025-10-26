"""
Speech transcription module using Deepgram for real-time audio-to-text.
Captures audio from system microphone and streams to Deepgram API.
"""
import threading
import time
from collections import deque
from typing import Optional, Callable
import pyaudio
from deepgram import DeepgramClient, DeepgramClientOptions, LiveTranscriptionEvents, LiveOptions
import asyncio
import config


class SpeechTranscriber:
    """Handles real-time speech transcription using Deepgram."""
    
    def __init__(self):
        """Initialize the speech transcriber."""
        self.api_key = config.DEEPGRAM_API_KEY
        self.buffer_seconds = config.TRANSCRIPTION_BUFFER_SECONDS
        self.sample_rate = config.AUDIO_SAMPLE_RATE
        self.channels = config.AUDIO_CHANNELS
        
        # Audio settings
        self.chunk_size = 1024
        self.format = pyaudio.paInt16
        
        # Transcription buffer (stores recent transcripts with timestamps)
        self.transcription_buffer = deque(maxlen=100)  # Store last 100 segments
        self.latest_transcription = ""
        self.buffer_lock = threading.Lock()

        # Track last processed segment for continuous processing
        self.last_processed_index = -1
        
        # Audio stream
        self.audio = None
        self.stream = None
        
        # Deepgram connection
        self.deepgram_client = None
        self.dg_connection = None
        
        # Threading
        self.running = False
        self.transcription_thread = None
        
        # Connection status
        self.is_connected = False
        self.connection_error = None
        
        print("\n🎤 Speech Transcriber initialized")
        print(f"Sample rate: {self.sample_rate} Hz")
        print(f"Buffer duration: {self.buffer_seconds} seconds")
    
    def start(self):
        """Start the transcription service."""
        if self.running:
            print("⚠️  Transcription already running")
            return
        
        try:
            # Initialize Deepgram client (v3 API)
            self.deepgram_client = DeepgramClient(self.api_key)
            
            # Start transcription thread
            self.running = True
            self.transcription_thread = threading.Thread(
                target=self._transcription_loop,
                daemon=True
            )
            self.transcription_thread.start()
            
            print("✅ Speech transcription started")
            
        except Exception as e:
            print(f"❌ Failed to start transcription: {e}")
            self.connection_error = str(e)
            self.running = False
    
    def stop(self):
        """Stop the transcription service."""
        if not self.running:
            return
        
        print("\n🛑 Stopping speech transcription...")
        self.running = False
        
        # Wait for thread to finish
        if self.transcription_thread:
            self.transcription_thread.join(timeout=3)
        
        # Close audio stream
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except:
                pass
        
        if self.audio:
            try:
                self.audio.terminate()
            except:
                pass
        
        # Close Deepgram connection
        if self.dg_connection:
            try:
                self.dg_connection.finish()
            except:
                pass
        
        print("✅ Speech transcription stopped")
    
    def _transcription_loop(self):
        """Main transcription loop (runs in background thread)."""
        retry_count = 0
        max_retries = 3
        
        while self.running and retry_count < max_retries:
            try:
                self._run_transcription()
                retry_count = 0  # Reset on successful run
            except Exception as e:
                retry_count += 1
                print(f"❌ Transcription error (attempt {retry_count}/{max_retries}): {e}")
                self.connection_error = str(e)
                self.is_connected = False
                
                if retry_count < max_retries and self.running:
                    print(f"⏳ Retrying in 2 seconds...")
                    time.sleep(2)
                else:
                    print("❌ Max retries reached, stopping transcription")
                    break
    
    def _run_transcription(self):
        """Run the transcription connection."""
        try:
            # Initialize PyAudio
            self.audio = pyaudio.PyAudio()
            
            # Open microphone stream
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            print("🎙️  Microphone opened successfully")
            
            # Create Deepgram connection (v3 API with asyncio)
            self._run_deepgram_streaming()
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            self.connection_error = str(e)
            self.is_connected = False
            raise
    
    def _run_deepgram_streaming(self):
        """Run Deepgram streaming using v3 API."""
        try:
            # Get the live transcription connection
            self.dg_connection = self.deepgram_client.listen.live.v("1")
            
            parent_self = self
            
            # Define event handlers
            def on_message(self_inner, result, **kwargs):
                try:
                    sentence = result.channel.alternatives[0].transcript
                    if sentence and sentence.strip():
                        with parent_self.buffer_lock:
                            timestamp = time.time()
                            parent_self.transcription_buffer.append({
                                'text': sentence,
                                'timestamp': timestamp
                            })
                            parent_self.latest_transcription = sentence
                        # Only print non-empty transcriptions
                        if len(sentence) > 3:
                            print(f"🗣️  {sentence}")
                except Exception as e:
                    print(f"⚠️  Message handler error: {e}")
            
            def on_error(self_inner, error, **kwargs):
                print(f"❌ Deepgram error: {error}")
                parent_self.connection_error = str(error)
            
            def on_close(self_inner, close, **kwargs):
                print("🔌 Deepgram connection closed")
                parent_self.is_connected = False
            
            # Register event handlers
            self.dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
            self.dg_connection.on(LiveTranscriptionEvents.Error, on_error)
            self.dg_connection.on(LiveTranscriptionEvents.Close, on_close)
            
            # Configure options
            options = LiveOptions(
                model="nova-2",
                language="en-US",
                encoding="linear16",
                sample_rate=self.sample_rate,
                channels=self.channels,
                punctuate=True,
                interim_results=False,
            )
            
            # Start the connection
            if self.dg_connection.start(options):
                self.is_connected = True
                self.connection_error = None
                print("✅ Deepgram connection established")
            else:
                raise Exception("Failed to start Deepgram connection")
            
            # Stream audio to Deepgram
            while self.running and self.is_connected:
                try:
                    data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                    self.dg_connection.send(data)
                except Exception as e:
                    print(f"⚠️  Audio stream error: {e}")
                    break
            
            # Close connection when done
            if self.dg_connection:
                self.dg_connection.finish()
            
        except Exception as e:
            print(f"❌ Streaming error: {e}")
            self.connection_error = str(e)
            self.is_connected = False
            raise
    
    def _on_close(self):
        """Handle connection close."""
        print("🔌 Deepgram connection closed")
        self.is_connected = False
    
    def get_latest_transcription(self) -> str:
        """
        Get the most recent transcription line.
        
        Returns:
            Latest transcribed text
        """
        with self.buffer_lock:
            return self.latest_transcription
    
    def get_recent_transcription(self, seconds: Optional[int] = None) -> str:
        """
        Get transcription from the last N seconds.

        Args:
            seconds: Number of seconds to retrieve (default: buffer_seconds)

        Returns:
            Combined transcription text from the specified time window
        """
        if seconds is None:
            seconds = self.buffer_seconds

        current_time = time.time()
        cutoff_time = current_time - seconds

        with self.buffer_lock:
            # Get all segments within time window
            recent_segments = [
                seg['text'] for seg in self.transcription_buffer
                if seg['timestamp'] >= cutoff_time
            ]

            return ' '.join(recent_segments)

    def get_latest_segment(self) -> Optional[dict]:
        """
        Get the most recent transcription segment with timestamp.

        Returns:
            Dictionary with 'text' and 'timestamp' keys, or None if no segments
        """
        with self.buffer_lock:
            if self.transcription_buffer:
                # Return the last segment
                return dict(self.transcription_buffer[-1])
            return None

    def get_unprocessed_segments(self) -> list:
        """
        Get all unprocessed transcription segments.

        Returns:
            List of dictionaries with 'text' and 'timestamp' keys
        """
        with self.buffer_lock:
            if not self.transcription_buffer:
                return []

            # Find segments that haven't been processed yet
            unprocessed = []
            buffer_list = list(self.transcription_buffer)

            # Start from the last processed index + 1
            start_index = self.last_processed_index + 1
            if start_index < len(buffer_list):
                for i in range(start_index, len(buffer_list)):
                    unprocessed.append(dict(buffer_list[i]))

                # Update the last processed index
                self.last_processed_index = len(buffer_list) - 1

            return unprocessed
    
    def is_ready(self) -> bool:
        """
        Check if transcription service is ready.
        
        Returns:
            True if connected and running
        """
        return self.running and self.is_connected
    
    def get_status(self) -> dict:
        """
        Get current status of transcription service.
        
        Returns:
            Status dictionary with connection info
        """
        return {
            'running': self.running,
            'connected': self.is_connected,
            'error': self.connection_error,
            'buffer_count': len(self.transcription_buffer)
        }

