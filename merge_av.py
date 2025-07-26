import os
import logging
import subprocess
import tempfile

logger = logging.getLogger(__name__)

class AudioVideoMerger:
    """Merge audio and video files using CPU-optimized processing"""
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        logger.info("Initialized AudioVideoMerger")
    
    def merge_audio_video(self, video_file: str, audio_file: str, session_id: str) -> str:
        """Merge audio and video files into final output"""
        try:
            if not os.path.exists(video_file):
                raise FileNotFoundError(f"Video file not found: {video_file}")
            
            if not os.path.exists(audio_file):
                logger.warning(f"Audio file not found: {audio_file}, returning video without audio")
                return video_file
            
            output_file = os.path.join(self.temp_dir, f'repo2reel_{session_id}_final.mp4')
            
            logger.info(f"Merging video: {video_file} with audio: {audio_file}")
            
            # Use ffmpeg to merge audio and video
            success = self._merge_with_ffmpeg(video_file, audio_file, output_file)
            
            if success and os.path.exists(output_file):
                # Verify the output file is valid
                if self._verify_video_file(output_file):
                    logger.info(f"Successfully merged audio and video: {output_file}")
                    return output_file
                else:
                    logger.warning("Merged video verification failed, returning original video")
                    return video_file
            else:
                # Fallback: return video without audio if merge fails
                logger.warning("Audio merge failed, returning video without audio")
                return video_file
                
        except Exception as e:
            logger.error(f"Error merging audio and video: {e}")
            # Return video file as fallback
            return video_file
    
    def _merge_with_ffmpeg(self, video_file: str, audio_file: str, output_file: str) -> bool:
        """Merge files using ffmpeg"""
        try:
            # Get video and audio durations
            video_duration = self._get_video_duration(video_file)
            audio_duration = self._get_audio_duration(audio_file)
            
            if video_duration is None or audio_duration is None:
                logger.warning("Could not determine file durations, using simple merge")
                return self._simple_merge(video_file, audio_file, output_file)
            
            # Determine which approach to use based on duration difference
            duration_diff = abs(video_duration - audio_duration)
            
            if duration_diff < 3.0:  # Less than 3 seconds difference
                return self._simple_merge(video_file, audio_file, output_file)
            elif video_duration > audio_duration:
                return self._merge_with_audio_loop(video_file, audio_file, output_file, video_duration)
            else:
                return self._merge_with_video_speed_adjust(video_file, audio_file, output_file, audio_duration)
                
        except Exception as e:
            logger.error(f"ffmpeg merge error: {e}")
            return False
    
    def _simple_merge(self, video_file: str, audio_file: str, output_file: str) -> bool:
        """Simple merge without duration adjustments"""
        try:
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-i', audio_file,
                '-c:v', 'copy',      # Copy video stream without re-encoding
                '-c:a', 'aac',       # Encode audio to AAC
                '-map', '0:v:0',     # Map first video stream
                '-map', '1:a:0',     # Map first audio stream
                '-shortest',         # Stop at shortest stream
                '-avoid_negative_ts', 'make_zero',  # Handle timing issues
                '-y',               # Overwrite output
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("Simple merge completed successfully")
                return True
            else:
                logger.error(f"Simple merge failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Simple merge error: {e}")
            return False
    
    def _merge_with_audio_loop(self, video_file: str, audio_file: str, output_file: str, target_duration: float) -> bool:
        """Merge with audio looping to match video duration"""
        try:
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-stream_loop', '-1',    # Loop audio indefinitely
                '-i', audio_file,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-t', str(target_duration),  # Stop at video duration
                '-avoid_negative_ts', 'make_zero',
                '-y',
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("Audio loop merge completed successfully")
                return True
            else:
                logger.error(f"Audio loop merge failed: {result.stderr}")
                # Try fallback without looping
                return self._simple_merge(video_file, audio_file, output_file)
                
        except Exception as e:
            logger.error(f"Audio loop merge error: {e}")
            return False
    
    def _merge_with_video_speed_adjust(self, video_file: str, audio_file: str, output_file: str, target_duration: float) -> bool:
        """Merge with video speed adjustment to match audio duration"""
        try:
            # Calculate speed factor
            video_duration = self._get_video_duration(video_file)
            if video_duration is None:
                return self._simple_merge(video_file, audio_file, output_file)
            
            speed_factor = video_duration / target_duration
            
            # Limit speed adjustment to reasonable range
            if speed_factor < 0.5 or speed_factor > 2.0:
                logger.warning(f"Speed factor {speed_factor} is extreme, using simple merge")
                return self._simple_merge(video_file, audio_file, output_file)
            
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-i', audio_file,
                '-filter_complex', f'[0:v]setpts=PTS/{speed_factor}[v]',
                '-map', '[v]',
                '-map', '1:a:0',
                '-c:a', 'aac',
                '-avoid_negative_ts', 'make_zero',
                '-y',
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info(f"Video speed adjust merge completed (factor: {speed_factor})")
                return True
            else:
                logger.error(f"Video speed adjust merge failed: {result.stderr}")
                return self._simple_merge(video_file, audio_file, output_file)
                
        except Exception as e:
            logger.error(f"Video speed adjust merge error: {e}")
            return False
    
    def _get_video_duration(self, video_file: str) -> float:
        """Get video duration in seconds"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                video_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and result.stdout.strip():
                duration = float(result.stdout.strip())
                logger.debug(f"Video duration: {duration} seconds")
                return duration
            else:
                logger.error(f"Failed to get video duration: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting video duration: {e}")
            return None
    
    def _get_audio_duration(self, audio_file: str) -> float:
        """Get audio duration in seconds"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                audio_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and result.stdout.strip():
                duration = float(result.stdout.strip())
                logger.debug(f"Audio duration: {duration} seconds")
                return duration
            else:
                logger.error(f"Failed to get audio duration: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting audio duration: {e}")
            return None
    
    def _verify_video_file(self, video_file: str) -> bool:
        """Verify that the video file is valid"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-show_entries', 'format=duration',
                video_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Error verifying video file: {e}")
            return False
    
    def add_background_music(self, video_file: str, music_file: str, session_id: str, volume: float = 0.2) -> str:
        """Add background music to video (optional feature)"""
        try:
            if not os.path.exists(music_file):
                logger.warning(f"Background music file not found: {music_file}")
                return video_file
            
            output_file = os.path.join(self.temp_dir, f'repo2reel_{session_id}_with_music.mp4')
            
            cmd = [
                'ffmpeg',
                '-i', video_file,
                '-i', music_file,
                '-filter_complex', f'[1:a]volume={volume}[music];[0:a][music]amix=inputs=2[audio]',
                '-map', '0:v',
                '-map', '[audio]',
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-shortest',
                '-y',
                output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                logger.info("Background music added successfully")
                return output_file
            else:
                logger.error(f"Failed to add background music: {result.stderr}")
                return video_file
                
        except Exception as e:
            logger.error(f"Error adding background music: {e}")
            return video_file

def merge_audio_video(video_file: str, audio_file: str, session_id: str) -> str:
    """Main function to merge audio and video"""
    try:
        merger = AudioVideoMerger()
        return merger.merge_audio_video(video_file, audio_file, session_id)
    except Exception as e:
        logger.error(f"Failed to merge audio and video: {e}")
        # Return video file as fallback
        return video_file
