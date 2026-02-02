import os
import sys
import glob
import subprocess

def batch_to_vtt(mp3_dir, vtt_dir):
    if not os.path.isdir(mp3_dir):
        print(f"Error: Directory {mp3_dir} not found.")
        return

    # Create output directory if it doesn't exist
    if not os.path.exists(vtt_dir):
        os.makedirs(vtt_dir)
        print(f"Created output directory: {vtt_dir}")

    # Find all mp3 files in the target directory
    mp3_files = glob.glob(os.path.join(mp3_dir, "*.mp3"))
    
    if not mp3_files:
        print(f"No mp3 files found in {mp3_dir}")
        return

    print(f"Found {len(mp3_files)} mp3 files in {mp3_dir}")

    # Get the directory where this script is located to find to_vtt.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    to_vtt_script = os.path.join(script_dir, "to_vtt.py")

    if not os.path.exists(to_vtt_script):
        print(f"Error: to_vtt.py not found at {to_vtt_script}")
        return

    for mp3_file in mp3_files:
        basename = os.path.splitext(os.path.basename(mp3_file))[0]
        # vtt file is saved to the specified vtt_directory
        vtt_file = os.path.join(vtt_dir, f"{basename}.vtt")

        if os.path.exists(vtt_file):
            print(f"Skip: {vtt_file} already exists.")
            continue

        print(f"Processing: {mp3_file} -> {vtt_file}")
        
        try:
            # Run to_vtt.py as a subprocess
            mp3_abs_path = os.path.abspath(mp3_file)
            vtt_abs_path = os.path.abspath(vtt_file)
            
            result = subprocess.run(
                [sys.executable, to_vtt_script, mp3_abs_path, vtt_abs_path],
                cwd=mp3_dir, # cwd allows to_vtt.py to access local resources if needed, though arguments are absolute
                capture_output=False,
                check=False
            )

            if result.returncode != 0:
                print(f"Error processing {mp3_file}. Exit code: {result.returncode}. Skipping...")
            
        except Exception as e:
            print(f"Unexpected error processing {mp3_file}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python batch_to_vtt.py <mp3_directory> <vtt_directory>")
    else:
        mp3_dir = sys.argv[1]
        vtt_dir = sys.argv[2]
        batch_to_vtt(mp3_dir, vtt_dir)
