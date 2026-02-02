import os
import sys
import glob
import subprocess

def batch_to_strip(from_dir, to_dir):
    # Check if from_dir exists
    if not os.path.isdir(from_dir):
        print(f"Error: Source directory {from_dir} not found.")
        return

    # Create to_dir if it doesn't exist
    if not os.path.exists(to_dir):
        try:
            os.makedirs(to_dir)
            print(f"Created output directory: {to_dir}")
        except OSError as e:
            print(f"Error creating directory {to_dir}: {e}")
            return

    # Find all vtt files in the from_dir
    vtt_files = glob.glob(os.path.join(from_dir, "*.vtt"))
    
    if not vtt_files:
        print(f"No vtt files found in {from_dir}")
        return

    print(f"Found {len(vtt_files)} vtt files in {from_dir}")

    # Get the directory where this script is located to find to_strip.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    to_strip_script = os.path.join(script_dir, "to_strip.py")

    if not os.path.exists(to_strip_script):
        print(f"Error: to_strip.py not found at {to_strip_script}")
        return

    for vtt_file in vtt_files:
        basename = os.path.splitext(os.path.basename(vtt_file))[0]
        # output file name check (to_strip.py generates {basename}_strip.txt)
        output_filename = f"{basename}_strip.txt"
        output_file_path = os.path.join(to_dir, output_filename)

        if os.path.exists(output_file_path):
            print(f"Skip: {output_file_path} already exists.")
            continue

        print(f"Processing: {vtt_file}")
        
        try:
            # Run to_strip.py as a subprocess
            # Pass absolute path of vtt file and output file
            vtt_abs_path = os.path.abspath(vtt_file)
            output_abs_path = os.path.abspath(output_file_path)
            
            result = subprocess.run(
                [sys.executable, to_strip_script, vtt_abs_path, output_abs_path],
                capture_output=False,
                check=False
            )

            if result.returncode != 0:
                print(f"Error processing {vtt_file}. Exit code: {result.returncode}. Skipping...")
            
        except Exception as e:
            print(f"Unexpected error processing {vtt_file}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python batch_to_strip.py <from_dir> <to_dir>")
    else:
        from_dir = sys.argv[1]
        to_dir = sys.argv[2]
        batch_to_strip(from_dir, to_dir)
