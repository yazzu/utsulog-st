#!/usr/bin/env python3
"""
Merge wordlist files.

This script reads word files from:
- game_title.txt
- paid_listener.txt
- dictionary/*.txt

And outputs a merged, sorted, and deduplicated wordlist to wordlist.txt.
"""

import os
import glob


def merge_wordlist(
    dictionary_dir='dictionary',
    output_file='wordlist.txt'
):
    """
    Merge word files and output a sorted, unique wordlist.

    Args:
        game_title_file: Path to game_title.txt
        paid_listener_file: Path to paid_listener.txt
        dictionary_dir: Path to dictionary directory
        output_file: Path to output wordlist file
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Set to store unique words
    words = set()
    
    # Get the script directory for relative paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Helper function to resolve path
    def resolve_path(path):
        if os.path.isabs(path):
            return path
        return os.path.join(script_dir, path)
    
    # Read dictionary/*.txt
    dictionary_path = resolve_path(dictionary_dir)
    if os.path.isdir(dictionary_path):
        txt_files = glob.glob(os.path.join(dictionary_path, '*.txt'))
        print(f"Found {len(txt_files)} dictionary files.")
        
        for txt_file in txt_files:
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            words.add(line)
            except Exception as e:
                print(f"Warning: Failed to read {txt_file}: {e}")
    else:
        print(f"Warning: Dictionary directory {dictionary_path} not found, skipping.")
    
    if not words:
        print("Warning: No words found.")
        return False
    
    # Sort and deduplicate (already unique from set)
    sorted_words = sorted(words)
    
    # Save the results
    output_path = resolve_path(output_file)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for word in sorted_words:
                f.write(word + '\n')
        
        print(f"Saved {len(sorted_words)} unique words to {output_path}")
        return True
    
    except Exception as e:
        print(f"Error writing output file: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 1:
        # Default usage
        merge_wordlist()
    elif len(sys.argv) == 2:
        merge_wordlist(output_file=sys.argv[1])
    elif len(sys.argv) == 3:
        merge_wordlist(
            dictionary_dir=sys.argv[1]
        )
    elif len(sys.argv) == 4:
        merge_wordlist(
            dictionary_dir=sys.argv[1],
            output_file=sys.argv[2]
        )
    else:
        print("Usage: python merge_wordlist.py [output_file]")
        print("       python merge_wordlist.py <dictionary_dir> <output_file>")
        print("  Default: python merge_wordlist.py")
