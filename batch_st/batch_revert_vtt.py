import os
import sys
import glob
import subprocess
import logging

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def batch_revert_vtt(fixed_dir, vtt_dir):
    # Check if directories exist
    if not os.path.isdir(fixed_dir):
        logging.error(f"Fixed directory {fixed_dir} not found.")
        return
    if not os.path.isdir(vtt_dir):
        logging.error(f"VTT directory {vtt_dir} not found.")
        return

    # Find all _fixed.txt files in the fixed_dir
    fixed_files = glob.glob(os.path.join(fixed_dir, "*_fixed.txt"))
    
    if not fixed_files:
        logging.info(f"No _fixed.txt files found in {fixed_dir}")
        return

    logging.info(f"Found {len(fixed_files)} _fixed.txt files in {fixed_dir}")

    # Get the directory where this script is located to find revert_vtt.py
    script_dir = os.path.dirname(os.path.abspath(__file__))
    revert_vtt_script = os.path.join(script_dir, "revert_vtt.py")

    if not os.path.exists(revert_vtt_script):
        logging.error(f"revert_vtt.py not found at {revert_vtt_script}")
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
            logging.warning(f"Strip file {strip_file} not found. Skipping {basename}...")
            continue
            
        if not os.path.exists(vtt_file):
            logging.warning(f"VTT file {vtt_file} not found. Skipping {basename}...")
            continue
            
        # Output check (revert_vtt.py saves to {basename}_fixed.vtt in CWD)
        # We will run subprocess with cwd=vtt_dir, so output will be in vtt_dir
        output_vtt = os.path.join(vtt_dir, f"{basename}_fixed.vtt")
        
        if os.path.exists(output_vtt):
            logging.info(f"Skip: {output_vtt} already exists.")
            continue
            
        logging.info(f"Processing: {basename}")
        
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
                capture_output=True, # Capture output for logging
                text=True,
                check=False
            )
            
            if result.stdout:
                logging.info(f"Output for {basename}:\n{result.stdout.strip()}")
            if result.stderr:
                logging.error(f"Error output for {basename}:\n{result.stderr.strip()}")

            if result.returncode != 0:
                logging.error(f"Error processing {basename}. Exit code: {result.returncode}.")
                
        except Exception as e:
            logging.error(f"Unexpected error processing {basename}: {e}")

if __name__ == "__main__":
    # Configure logging
    log_file = os.path.join(SCRIPT_DIR, "batch_revert_vtt.log")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )

    if len(sys.argv) < 3:
        logging.error("Usage: python batch_revert_vtt.py <fixed_dir> <vtt_dir>")
    else:
        fixed_dir = sys.argv[1]
        vtt_dir = sys.argv[2]
        batch_revert_vtt(fixed_dir, vtt_dir)
