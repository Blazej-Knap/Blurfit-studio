import os
import subprocess
import sys
import json

# Add root folder to path so blurfit_studio can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from blurfit_studio.core import video_worker

def generate_test_video(path, duration=3, width=640, height=360, fps=30):
    """Generates a dummy video using FFmpeg's testsrc filter."""
    print(f"Generating dummy test video ({width}x{height}, {duration}s) at: {path}")
    cmd = [
        video_worker.get_ffmpeg_path("ffmpeg"), "-y",
        "-f", "lavfi",
        "-i", f"testsrc=duration={duration}:size={width}x{height}:rate={fps}",
        "-pix_fmt", "yuv420p",
        path
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
    print("Dummy test video generated successfully.")

def run_tests():
    sample_file = "test_sample.mp4"
    blur_out = "test_out_blur.mp4"
    crop_out = "test_out_crop.mp4"
    
    try:
        # 1. Generate test video
        generate_test_video(sample_file, duration=3, width=640, height=360, fps=30)
        
        # 2. Test metadata extraction
        print("\n--- Test 1: Testing get_video_metadata ---")
        metadata = video_worker.get_video_metadata(sample_file)
        print("Extracted Metadata:")
        print(json.dumps(metadata, indent=2))
        
        assert metadata["width"] == 640, f"Expected width 640, got {metadata['width']}"
        assert metadata["height"] == 360, f"Expected height 360, got {metadata['height']}"
        assert abs(metadata["duration"] - 3.0) < 0.1, f"Expected duration near 3.0, got {metadata['duration']}"
        assert abs(metadata["fps"] - 30.0) < 0.1, f"Expected fps near 30, got {metadata['fps']}"
        print("SUCCESS: get_video_metadata tests passed!")
        
        # 3. Test calculation of target dimensions
        print("\n--- Test 2: Testing calculate_target_dimensions ---")
        # 9:16 target for a 640x360 horizontal video.
        # Max dimension is 640.
        # Since target_ratio = 9/16 < 1.0, target_height = 640, target_width = 640 * 9/16 = 360.
        w_out, h_out = video_worker.calculate_target_dimensions(640, 360, "9:16")
        print(f"9:16 target for 640x360 input: {w_out}x{h_out}")
        assert w_out == 360, f"Expected width 360, got {w_out}"
        assert h_out == 640, f"Expected height 640, got {h_out}"
        
        # 1:1 target.
        w_out_sq, h_out_sq = video_worker.calculate_target_dimensions(640, 360, "1:1")
        print(f"1:1 target for 640x360 input: {w_out_sq}x{h_out_sq}")
        assert w_out_sq == 640, f"Expected width 640, got {w_out_sq}"
        assert h_out_sq == 640, f"Expected height 640, got {h_out_sq}"
        print("SUCCESS: calculate_target_dimensions tests passed!")
        
        # 4. Test FFmpeg VideoProcessingThread execution for Blur Mode
        print("\n--- Test 3: Testing VideoProcessingThread - Blur Mode ---")
        if os.path.exists(blur_out):
            os.remove(blur_out)
            
        thread = video_worker.VideoProcessingThread(
            input_path=sample_file,
            output_path=blur_out,
            target_ratio_str="9:16",
            mode="blur",
            blur_strength=40,
            metadata=metadata,
            crop_position=30
        )
        
        progress_records = []
        thread.progress_changed.connect(lambda p: progress_records.append(p))
        
        # We run the thread synchronously in the test context by calling run() directly
        print("Running thread.run() synchronously...")
        thread.run()
        
        assert os.path.exists(blur_out), "Output blur video file was not created!"
        print(f"Output blur video created successfully ({os.path.getsize(blur_out)} bytes).")
        print(f"Progress signals emitted: {progress_records}")
        assert len(progress_records) > 0, "No progress signals were emitted!"
        print("SUCCESS: Blur mode rendering tests passed!")
        
        # 5. Test FFmpeg VideoProcessingThread execution for Crop Mode
        print("\n--- Test 4: Testing VideoProcessingThread - Crop Mode ---")
        if os.path.exists(crop_out):
            os.remove(crop_out)
            
        thread_crop = video_worker.VideoProcessingThread(
            input_path=sample_file,
            output_path=crop_out,
            target_ratio_str="1:1",
            mode="crop",
            blur_strength=0,
            metadata=metadata,
            crop_position=20
        )
        
        progress_records_crop = []
        thread_crop.progress_changed.connect(lambda p: progress_records_crop.append(p))
        
        print("Running thread_crop.run() synchronously...")
        thread_crop.run()
        
        assert os.path.exists(crop_out), "Output crop video file was not created!"
        print(f"Output crop video created successfully ({os.path.getsize(crop_out)} bytes).")
        print(f"Progress signals emitted: {progress_records_crop}")
        assert len(progress_records_crop) > 0, "No progress signals were emitted!"
        print("SUCCESS: Crop mode rendering tests passed!")
        
        print("\n=============================================")
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=============================================")
        
    except Exception as e:
        print(f"\nTEST RUN FAILED: {str(e)}")
        sys.exit(1)
        
    finally:
        # Cleanup
        print("\nCleaning up temporary test files...")
        for file in [sample_file, blur_out, crop_out]:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    print(f"Removed: {file}")
                except Exception as ex:
                    print(f"Failed to remove {file}: {ex}")

if __name__ == "__main__":
    run_tests()
