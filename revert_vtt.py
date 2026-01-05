import webvtt
import sys
import os
import re

def parse_tagged_file(path):
    """
    Parses a file with lines like '[L0001] Text content'
    Returns a dictionary mapping 'L0001' -> 'Text content'
    """
    mapping = {}
    # Matches 0001-... or 123-...
    # We capture the content after the tag.
    pattern = re.compile(r"^(\d+)\-(.*)")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.rstrip('\n') # Remove newline char
                if not line:
                    continue
                match = pattern.match(line)
                if match:
                    tag = match.group(1)
                    content = match.group(2)
                    mapping[tag] = content
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return None
    return mapping

def revert_vtt(original_vtt_path, fixed_txt_path, strip_txt_path=None):
    if not os.path.exists(original_vtt_path):
        print(f"Error: VTT file {original_vtt_path} not found.")
        return
    if not os.path.exists(fixed_txt_path):
        print(f"Error: Text file {fixed_txt_path} not found.")
        return

    basename = os.path.splitext(os.path.basename(original_vtt_path))[0]
    output_vtt_path = f"{basename}_fixed.vtt"

    # Infer strip path if not provided
    if not strip_txt_path:
        strip_txt_path = f"{basename}_strip.txt"
    
    strip_map = {}
    if os.path.exists(strip_txt_path):
        strip_map = parse_tagged_file(strip_txt_path)
        if strip_map is None: return # Error reading
    else:
        print(f"Warning: Strip file {strip_txt_path} not found. Cannot restore missing lines correctly.")

    fixed_map = parse_tagged_file(fixed_txt_path)
    if fixed_map is None: return

    # Read original VTT
    try:
        vtt = webvtt.read(original_vtt_path)
    except Exception as e:
        print(f"Error reading VTT file: {e}")
        return

    updated_count = 0
    restored_count = 0
    skipped_count = 0
    
    # We must match the index logic of to_strip.py
    # to_strip.py increments index for every non-empty stripped caption
    original_strip_index = 0
    
    for caption in vtt:
        original_text_stripped = caption.text.strip()
        
        if not original_text_stripped:
            # Skipped in to_strip workflow
            continue
            
        original_strip_index += 1
        tag = f"{original_strip_index:04d}"
        
        if tag in fixed_map:
            # Update with fixed text
            caption.text = fixed_map[tag]
            updated_count += 1
        elif tag in strip_map:
            # Restore from strip map (original stripped text)
            print(f"Line {tag} missing in fixed text. Restored from original strip file.")
            caption.text = strip_map[tag]
            restored_count += 1
        else:
            # Not in fixed, not in strip. 
            # This implies the strip file provided doesn't match the VTT or something is wrong.
            skipped_count += 1

    vtt.save(output_vtt_path)
    print(f"Saved to {output_vtt_path}")
    print(f"Total processed indices: {original_strip_index}")
    print(f"Updated lines: {updated_count}")
    print(f"Restored lines: {restored_count}")
    print(f"Skipped/Unchanged lines: {skipped_count}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python revert_vtt.py <original_vtt> <fixed_txt> [strip_txt]")
    else:
        strip_arg = sys.argv[3] if len(sys.argv) > 3 else None
        revert_vtt(sys.argv[1], sys.argv[2], strip_arg)
