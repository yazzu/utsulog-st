import os
import sys
import glob
import subprocess

def batch_to_vtt(target_dir):
    if not os.path.isdir(target_dir):
        print(f"Error: Directory {target_dir} not found.")
        return

    # Find all mp3 files in the target directory
    mp3_files = glob.glob(os.path.join(target_dir, "*.mp3"))
    
    if not mp3_files:
        print(f"No mp3 files found in {target_dir}")
        return

    print(f"Found {len(mp3_files)} mp3 files in {target_dir}")

    # Get the directory where this script is located to find to_vtt.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    to_vtt_script = os.path.join(script_dir, "to_vtt.py")

    if not os.path.exists(to_vtt_script):
        print(f"Error: to_vtt.py not found at {to_vtt_script}")
        return

    for mp3_file in mp3_files:
        basename = os.path.splitext(os.path.basename(mp3_file))[0]
        # vtt file is expected in the same directory as mp3
        vtt_file = os.path.join(os.path.dirname(mp3_file), f"{basename}.vtt")

        if os.path.exists(vtt_file):
            print(f"Skip: {vtt_file} already exists.")
            continue

        print(f"Processing: {mp3_file}")
        
        try:
            # Run to_vtt.py as a subprocess
            # We pass the absolute path of the mp3 file
            # cwd is set to the mp3 directory so to_vtt.py outputs there (as per its logic)
            # Actually to_vtt.py logic: output_file = f"{basename}.vtt". 
            # If we run it from a different dir, it might save in CWD.
            # to_vtt.py uses:
            # basename = os.path.splitext(os.path.basename(mp3_file))[0]
            # output_file = f"{basename}.vtt"
            # It saves to current working directory.
            # So we should set cwd to the directory of the mp3 file.
            
            mp3_dir = os.path.dirname(mp3_file)
            mp3_abs_path = os.path.abspath(mp3_file)
            
            result = subprocess.run(
                [sys.executable, to_vtt_script, mp3_abs_path],
                cwd=mp3_dir,
                capture_output=False, # Let stdout/stderr go to console
                check=False # Don't raise exception on non-zero exit code immediately
            )

            if result.returncode != 0:
                print(f"Error processing {mp3_file}. Exit code: {result.returncode}. Skipping...")
            
        except Exception as e:
            print(f"Unexpected error processing {mp3_file}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python batch_to_vtt.py <directory>")
    else:
        target_dir = sys.argv[1]
        batch_to_vtt(target_dir)
