import webvtt
import sys
import os

def to_chunk(vtt_file, lines_per_chunk=30):
    if not os.path.exists(vtt_file):
        print(f"Error: File {vtt_file} not found.")
        return

    basename = os.path.splitext(os.path.basename(vtt_file))[0]
    output_file = f"{basename}_chunks.txt"

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

    # Chunking
    with open(output_file, 'w', encoding='utf-8') as f:
        for i in range(0, len(text_lines), lines_per_chunk):
            chunk = text_lines[i:i + lines_per_chunk]
            f.write('\n'.join(chunk) + '\n\n') # Add extra newline between chunks

    print(f"Created {output_file} with {len(text_lines)} lines.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python to_chunk.py <vtt_file> [lines_per_chunk]")
    else:
        vtt_file = sys.argv[1]
        lines_per_chunk = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        to_chunk(vtt_file, lines_per_chunk)
