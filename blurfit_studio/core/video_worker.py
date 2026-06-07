import os
import sys
import json
import subprocess
from PyQt6.QtCore import QThread, pyqtSignal

def get_ffmpeg_path(name="ffmpeg"):
    """
    Returns the path to the ffmpeg or ffprobe executable.
    Checks blurfit_studio/bin/ first (local to the package),
    and falls back to system PATH.
    """
    # Try local package path: blurfit_studio/bin/<name>(.exe)
    package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_path = os.path.join(package_dir, "bin", name)
    if sys.platform == "win32":
        local_path += ".exe"
        
    if os.path.exists(local_path):
        return local_path
        
    # Fallback to system PATH
    return name

def get_video_metadata(file_path):
    """
    Extracts metadata from a video file using ffprobe.
    Returns a dict with width, height, duration, fps, and rotation.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    # Run ffprobe to get stream and format info in JSON format
    cmd = [
        get_ffmpeg_path("ffprobe"),
        "-v", "quiet",
        "-print_format", "json",
        "-show_streams",
        "-show_format",
        file_path
    ]
    
    # Hide console window on Windows
    startupinfo = None
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0 # SW_HIDE

    result = subprocess.run(
        cmd, 
        capture_output=True, 
        text=True, 
        check=True, 
        startupinfo=startupinfo
    )
    
    data = json.loads(result.stdout)
    
    video_stream = None
    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video":
            video_stream = stream
            break
            
    if not video_stream:
        raise ValueError("No video stream found in the selected file.")
        
    # Standard dimensions
    width = int(video_stream.get("width", 0))
    height = int(video_stream.get("height", 0))
    
    # Parse rotation metadata
    rotation = 0
    # 1. Check tags
    tags = video_stream.get("tags", {})
    if "rotate" in tags:
        try:
            rotation = int(tags["rotate"])
        except ValueError:
            pass
    # 2. Check side data list
    for side_data in video_stream.get("side_data_list", []):
        if "rotation" in side_data:
            try:
                rotation = int(side_data["rotation"])
            except ValueError:
                pass
                
    # If video is rotated 90 or 270 degrees, swap width and height for visual representation
    if abs(rotation) in (90, 270):
        width, height = height, width
        
    # Parse duration
    duration = 0.0
    if "duration" in video_stream:
        try:
            duration = float(video_stream["duration"])
        except ValueError:
            pass
            
    if duration == 0.0 and "duration" in data.get("format", {}):
        try:
            duration = float(data["format"]["duration"])
        except ValueError:
            pass
            
    # Parse frame rate
    r_frame_rate = video_stream.get("r_frame_rate", "30/1")
    if "/" in r_frame_rate:
        try:
            num, den = map(int, r_frame_rate.split("/"))
            fps = num / den if den != 0 else 30.0
        except Exception:
            fps = 30.0
    else:
        try:
            fps = float(r_frame_rate)
        except ValueError:
            fps = 30.0
            
    return {
        "width": width,
        "height": height,
        "duration": duration,
        "fps": fps,
        "rotation": rotation
    }


def calculate_target_dimensions(input_width, input_height, target_ratio_str):
    """
    Calculates target width and height based on the source video size
    and the desired aspect ratio. Keeps the quality high by sizing the
    output based on the maximum input dimension.
    """
    # Parse target ratio (e.g. "9:16" -> 9/16)
    try:
        num, den = map(int, target_ratio_str.split(":"))
        target_ratio = num / den
    except Exception:
        target_ratio = 9/16
        
    box_size = max(input_width, input_height)
    
    # Target is horizontal or square
    if target_ratio >= 1.0:
        target_width = box_size
        target_height = int(round(target_width / target_ratio))
    else:
        target_height = box_size
        target_width = int(round(target_height * target_ratio))
        
    # Ensure dimensions are divisible by 2 for standard video encoders (H.264)
    target_width = (target_width // 2) * 2
    target_height = (target_height // 2) * 2
    
    return max(2, target_width), max(2, target_height)


class VideoProcessingThread(QThread):
    """
    QThread to execute FFmpeg in the background and report progress.
    """
    progress_changed = pyqtSignal(int)
    finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, input_path, output_path, target_ratio_str, mode, blur_strength, metadata, crop_position=50):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.target_ratio_str = target_ratio_str
        self.mode = mode
        self.blur_strength = blur_strength
        self.metadata = metadata
        self.crop_position = crop_position
        self.process = None
        self.is_cancelled = False

    def run(self):
        try:
            # 1. Calculate target dimensions
            w_in = self.metadata["width"]
            h_in = self.metadata["height"]
            duration = self.metadata["duration"]
            
            w_out, h_out = calculate_target_dimensions(w_in, h_in, self.target_ratio_str)
            
            # 2. Build FFmpeg command line
            cmd = [get_ffmpeg_path("ffmpeg"), "-y", "-i", self.input_path, "-progress", "pipe:1"]
            
            # Construct filters
            if self.mode == "blur":
                # Map blur strength (0-100) to boxblur radius (1 to 50)
                # Ensure it doesn't exceed target boundaries to prevent FFmpeg crashes
                max_radius = min(w_out // 2, h_out // 2) - 1
                blur_radius = min(max_radius, max(1, int(self.blur_strength * 0.5)))
                
                # Check rotation metadata. If the video has rotation tags, FFmpeg normally 
                # auto-rotates it, but we should make sure the fit/crop calculation matches.
                # Standard ffmpeg auto-rotates since v3, so we split the auto-rotated stream.
                filter_str = (
                    f"[0:v]split=2[bg][fg];"
                    f"[bg]scale=w={w_out}:h={h_out}:force_original_aspect_ratio=increase,"
                    f"crop=w={w_out}:h={h_out}:x=(iw-ow)*({self.crop_position}/100):y=(ih-oh)*({self.crop_position}/100),"
                    f"boxblur=luma_radius={blur_radius}:luma_power=2[bg_blur];"
                    f"[fg]scale=w={w_out}:h={h_out}:force_original_aspect_ratio=decrease[fg_scaled];"
                    f"[bg_blur][fg_scaled]overlay=x=(W-w)/2:y=(H-h)/2:shortest=1[outv]"
                )
            else: # "crop" / Przytnij i wypełnij
                filter_str = (
                    f"[0:v]scale=w={w_out}:h={h_out}:force_original_aspect_ratio=increase,"
                    f"crop=w={w_out}:h={h_out}:x=(iw-ow)*({self.crop_position}/100):y=(ih-oh)*({self.crop_position}/100)[outv]"
                )
                
            cmd.extend([
                "-filter_complex", filter_str,
                "-map", "[outv]",
                "-map", "0:a?", # Copy audio if present, ignore if not
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-c:a", "copy", # Copy audio stream without transcoding to keep quality and save CPU
                self.output_path
            ])
            
            # 3. Start FFmpeg subprocess
            # Configure startupinfo to hide command prompt on Windows
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0 # SW_HIDE
                
            import tempfile
            
            # Use a temporary file to capture stderr to prevent blocking the OS pipe buffers
            with tempfile.TemporaryFile(mode="w+t", encoding="utf-8", errors="replace") as stderr_file:
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=stderr_file,
                    text=True,
                    bufsize=1,
                    startupinfo=startupinfo,
                    encoding="utf-8",
                    errors="replace"
                )
                
                # Read stdout line-by-line for progress information
                while self.process.poll() is None:
                    if self.is_cancelled:
                        self.process.terminate()
                        self.error_occurred.emit("Processing was cancelled by the user.")
                        return
                        
                    line = self.process.stdout.readline()
                    if not line:
                        continue
                        
                    # Search for out_time_us (microseconds)
                    if line.startswith("out_time_us="):
                        try:
                            time_us = int(line.split("=")[1].strip())
                            current_seconds = time_us / 1_000_000.0
                            if duration > 0:
                                percentage = min(99, int((current_seconds / duration) * 100))
                                self.progress_changed.emit(percentage)
                        except Exception:
                            pass
                            
                # Wait for the process to exit completely
                self.process.wait()
                
                # Retrieve all stdout lines remaining
                stdout_data = self.process.stdout.read()
                
                # Read captured stderr log
                stderr_file.seek(0)
                stderr_data = stderr_file.read()
            
            # Check return code
            if self.process.returncode == 0 and not self.is_cancelled:
                self.progress_changed.emit(100)
                self.finished.emit(self.output_path)
            else:
                if not self.is_cancelled:
                    # Capture some stderr output for debugging
                    err_msg = stderr_data if stderr_data else "FFmpeg process failed with non-zero exit code."
                    # Extract last few lines of stderr
                    lines = err_msg.strip().split("\n")
                    short_err = "\n".join(lines[-5:]) if len(lines) > 5 else err_msg
                    self.error_occurred.emit(f"FFmpeg error:\n{short_err}")
                    
        except Exception as e:
            self.error_occurred.emit(f"An error occurred during video processing:\n{str(e)}")

    def cancel(self):
        self.is_cancelled = True
        if self.process:
            try:
                self.process.terminate()
            except Exception:
                pass
