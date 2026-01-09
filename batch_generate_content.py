import os
import sys
import glob
import subprocess

def batch_generate_content(from_dir):
    # Check if from_dir exists
    if not os.path.isdir(from_dir):
        print(f"Error: Directory {from_dir} not found.")
        return

    # Find all _strip.txt files in the from_dir
    strip_files = glob.glob(os.path.join(from_dir, "*_strip.txt"))
    
    if not strip_files:
        print(f"No _strip.txt files found in {from_dir}")
        return

    print(f"Found {len(strip_files)} _strip.txt files in {from_dir}")

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    generate_content_script = os.path.join(script_dir, "generate_content.py")
    system_instruction_file = os.path.join(script_dir, "system_instruction.txt")
    wordlist_file = os.path.join(script_dir, "wordlist.txt")

    if not os.path.exists(generate_content_script):
        print(f"Error: generate_content.py not found at {generate_content_script}")
        return

    for input_file in strip_files:
        print(f"Processing: {input_file}")
        try:
            # Run generate_content.py as a subprocess
            cmd = [
                sys.executable, 
                generate_content_script, 
                input_file,
                system_instruction_file,
                wordlist_file
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=False,
                check=False
            )

            if result.returncode != 0:
                print(f"Error processing {input_file}. Exit code: {result.returncode}.")
                if result.returncode == 75:
                   print("  (Timeout occurred, skipping file)")
            
        except Exception as e:
            print(f"Unexpected error processing {input_file}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python batch_generate_content.py <target_dir>")
    else:
        target_dir = sys.argv[1]
        batch_generate_content(target_dir)
