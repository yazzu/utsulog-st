import os
import sys
import glob
import subprocess
import logging


# Valid log levels
# DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = "batch_generate_content.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def batch_generate_content(from_dir):
    # Check if from_dir exists
    if not os.path.isdir(from_dir):
        logging.error(f"Error: Directory {from_dir} not found.")
        return

    # Find all _strip.txt files in the from_dir
    strip_files = glob.glob(os.path.join(from_dir, "*_strip.txt"))
    
    if not strip_files:
        logging.warning(f"No _strip.txt files found in {from_dir}")
        return

    logging.info(f"Found {len(strip_files)} _strip.txt files in {from_dir}")

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    generate_content_script = os.path.join(script_dir, "generate_content.py")
    system_instruction_file = os.path.join(script_dir, "system_instruction.txt")
    wordlist_file = os.path.join(script_dir, "wordlist.txt")

    if not os.path.exists(generate_content_script):
        logging.error(f"Error: generate_content.py not found at {generate_content_script}")
        return

    for input_file in strip_files:
        logging.info(f"Processing: {input_file}")
        try:
            # Run generate_content.py as a subprocess
            cmd = [
                sys.executable, 
                generate_content_script, 
                input_file,
                system_instruction_file,
                wordlist_file
            ]
            
            logging.info(f"Starting process for {input_file}")
            
            try:
                # Use Popen to capture output in real-time
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, # Redirect stderr to stdout
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )

                # Read output line by line and log it
                for line in process.stdout:
                    line = line.strip()
                    if line:
                        logging.info(f"[{os.path.basename(input_file)}] {line}")

                # Wait for process to complete
                return_code = process.wait()

                if return_code != 0:
                    logging.error(f"Error processing {input_file}. Exit code: {return_code}.")
                    if return_code == 75:
                       logging.warning("  (Timeout occurred, skipping file)")
                else:
                    logging.info(f"Successfully processed {input_file}")

            except Exception as e:
                logging.error(f"Error executing subprocess for {input_file}: {e}")
            
        except Exception as e:
            logging.error(f"Unexpected error processing {input_file}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python batch_generate_content.py <target_dir>")
    else:
        target_dir = sys.argv[1]
        batch_generate_content(target_dir)
