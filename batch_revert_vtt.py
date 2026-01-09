import os
import sys
import glob
import subprocess

def batch_revert_vtt(fixed_dir, vtt_dir):
    # Check if directories exist
    if not os.path.isdir(fixed_dir):
        print(f"Error: Fixed directory {fixed_dir} not found.")
        return
    if not os.path.isdir(vtt_dir):
        print(f"Error: VTT directory {vtt_dir} not found.")
        return

    # Find all _fixed.txt files in the fixed_dir
    fixed_files = glob.glob(os.path.join(fixed_dir, "*_fixed.txt"))
    
    if not fixed_files:
        print(f"No _fixed.txt files found in {fixed_dir}")
        return

    print(f"Found {len(fixed_files)} _fixed.txt files in {fixed_dir}")

    # Get the directory where this script is located to find revert_vtt.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    revert_vtt_script = os.path.join(script_dir, "revert_vtt.py")

    if not os.path.exists(revert_vtt_script):
        print(f"Error: revert_vtt.py not found at {revert_vtt_script}")
        return

    for fixed_file in fixed_files:
        # Infer basename from _fixed.txt filename
        # example: video1_fixed.txt -> video1
        filename = os.path.basename(fixed_file)
        if not filename.endswith("_fixed.txt"):
            continue
            
        basename = filename[:-10] # remove "_fixed.txt"
        
        # Expected paths
        strip_file = os.path.join(fixed_dir, f"{basename}_strip.txt")
        vtt_file = os.path.join(vtt_dir, f"{basename}.vtt")
        
        # Check existence
        if not os.path.exists(strip_file):
            print(f"Warning: Strip file {strip_file} not found. Skipping {basename}...")
            continue
            
        if not os.path.exists(vtt_file):
            print(f"Warning: VTT file {vtt_file} not found. Skipping {basename}...")
            continue
            
        # Output check (revert_vtt.py saves to {basename}_fixed.vtt in CWD)
        # We will run subprocess with cwd=vtt_dir, so output will be in vtt_dir
        output_vtt = os.path.join(vtt_dir, f"{basename}_fixed.vtt")
        
        if os.path.exists(output_vtt):
            print(f"Skip: {output_vtt} already exists.")
            continue
            
        print(f"Processing: {basename}")
        
        try:
            # Run revert_vtt.py as a subprocess
            # Usage: python revert_vtt.py <original_vtt> <fixed_txt> [strip_txt]
            
            # Use absolute paths
            vtt_abs_path = os.path.abspath(vtt_file)
            fixed_abs_path = os.path.abspath(fixed_file)
            strip_abs_path = os.path.abspath(strip_file)
            
            cmd = [
                sys.executable,
                revert_vtt_script,
                vtt_abs_path,
                fixed_abs_path,
                strip_abs_path
            ]
            
            result = subprocess.run(
                cmd,
                cwd=vtt_dir, # execute in vtt directory so output is saved there
                capture_output=False,
                check=False
            )
            
            if result.returncode != 0:
                print(f"Error processing {basename}. Exit code: {result.returncode}.")
                
        except Exception as e:
            print(f"Unexpected error processing {basename}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python batch_revert_vtt.py <fixed_dir> <vtt_dir>")
    else:
        fixed_dir = sys.argv[1]
        vtt_dir = sys.argv[2]
        batch_revert_vtt(fixed_dir, vtt_dir)
