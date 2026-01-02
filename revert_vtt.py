import webvtt
import sys
import os

def revert_vtt(original_vtt_path, fixed_txt_path):
    if not os.path.exists(original_vtt_path):
        print(f"Error: VTT file {original_vtt_path} not found.")
        return
    if not os.path.exists(fixed_txt_path):
        print(f"Error: Text file {fixed_txt_path} not found.")
        return

    # Determine output filename based on original VTT basename
    # Expected behavior: input.vtt -> input_fixed.vtt using text from input_fixed.txt
    # However, user might pass any text file. 
    # Let's make the output file name {original_basename}_fixed.vtt
    basename = os.path.splitext(os.path.basename(original_vtt_path))[0]
    output_vtt_path = f"{basename}_fixed.vtt"

    # Read fixed text
    try:
        with open(fixed_txt_path, 'r', encoding='utf-8') as f:
            # Read lines, strip whitespace from ends, ignore completely empty lines
            fixed_lines = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Error reading text file: {e}")
        return

    # Read original VTT
    try:
        vtt = webvtt.read(original_vtt_path)
    except Exception as e:
        print(f"Error reading VTT file: {e}")
        return

    if len(vtt) != len(fixed_lines):
        print(f"Warning: Line count mismatch. VTT has {len(vtt)} captions, Fixed text has {len(fixed_lines)} lines.")
        print("Proceeding with mapping as far as possible...")

    # Update captions
    count = min(len(vtt), len(fixed_lines))
    for i in range(count):
        vtt[i].text = fixed_lines[i]

    # If vtt has more lines, they remain unchanged (or empty? better leave unchanged)
    # If fixed text has more lines, they are ignored (as there are no timestamps)

    vtt.save(output_vtt_path)
    print(f"Saved to {output_vtt_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python revert_vtt.py <original_vtt> <fixed_txt>")
    else:
        revert_vtt(sys.argv[1], sys.argv[2])
