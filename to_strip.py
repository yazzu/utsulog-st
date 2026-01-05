import webvtt
import sys
import os

def to_chunk(vtt_file):
    if not os.path.exists(vtt_file):
        print(f"Error: File {vtt_file} not found.")
        return

    basename = os.path.splitext(os.path.basename(vtt_file))[0]
    output_file = f"{basename}_strip.txt"

    text_lines = []
    
    # Read VTT file
    try:
        for caption in webvtt.read(vtt_file):
            # Clean up text: remove newlines within a caption if necessary, 
            # but usually just stripping whitespace is enough.
            text = caption.text.strip()
            if text:
                text_lines.append(text)
    except Exception as e:
        print(f"Error reading VTT file: {e}")
        return

    # Add line numbers
    numbered_lines = []
    for i, line in enumerate(text_lines):
        numbered_lines.append(f"{i+1:04d}-{line}")

    # Chunking
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(numbered_lines))

    print(f"Created {output_file} with {len(numbered_lines)} lines.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python to_strip.py <vtt_file>")
    else:
        vtt_file = sys.argv[1]
        to_chunk(vtt_file)
