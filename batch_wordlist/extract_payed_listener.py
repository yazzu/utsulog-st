#!/usr/bin/env python3
"""
Extract paid listeners from chat logs.

This script reads JSON files from chat_logs_processed directory,
extracts authorName from paid_message and sponsorships_gift_purchase_announcement,
and outputs the unique list to paid_listener.txt.
"""

import os
import sys
import json
import glob
import re


def contains_non_ascii(s):
    """Check if string contains non-ASCII characters (e.g., Japanese)."""
    return any(ord(c) > 127 for c in s)


def clean_author_name(name):
    """
    Clean author name by removing trailing symbols/alphanumeric characters
    if the name contains non-ASCII characters.
    
    Args:
        name: Author name to clean
    
    Returns:
        Cleaned author name
    """
    # Remove @ prefix if present
    if name.startswith('@'):
        name = name[1:]
    
    # If name contains non-ASCII (Japanese) characters,
    # remove trailing symbols and alphanumeric characters
    if contains_non_ascii(name):
        # Remove trailing pattern: symbols followed by alphanumeric, or just symbols
        # Pattern matches: -xy1z, _123, .abc, etc. at the end
        name = re.sub(r'[-_.\s]+[a-zA-Z0-9]+$', '', name)
        # Also remove trailing symbols only
        name = re.sub(r'[-_.\s]+$', '', name)
    
    return name


def extract_payed_listener(
    input_dir='/mnt/f/Dev/utsulog/chat_logs/chat_logs_processed',
    output_file='paid_listener.txt'
):
    """
    Extract paid listener names from chat logs.

    Args:
        input_dir: Path to the directory containing JSON files
        output_file: Path to output the extracted listener names
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Target message types
    target_types = {'paid_message', 'sponsorships_gift_purchase_announcement'}
    
    # Check if input directory exists
    if not os.path.isdir(input_dir):
        print(f"Error: Input directory {input_dir} not found.")
        return False
    
    # Find all JSON files
    json_files = glob.glob(os.path.join(input_dir, '*.json'))
    if not json_files:
        print(f"Error: No JSON files found in {input_dir}")
        return False
    
    print(f"Found {len(json_files)} JSON files.")
    
    # Set to store unique author names
    author_names = set()
    
    # Process each JSON file
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        obj = json.loads(line)
                        message_type = obj.get('message_type', '')
                        
                        if message_type in target_types:
                            author_name = obj.get('authorName', '')
                            if author_name:
                                # Clean the author name
                                author_name = clean_author_name(author_name)
                                if author_name:  # Only add if not empty after cleaning
                                    author_names.add(author_name)
                    
                    except json.JSONDecodeError:
                        # Skip invalid JSON lines
                        continue
        
        except Exception as e:
            print(f"Warning: Failed to process {json_file}: {e}")
            continue
    
    if not author_names:
        print("Warning: No paid listeners found.")
    
    # Sort and deduplicate (already unique from set)
    sorted_names = sorted(author_names)
    
    # Save the results
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for name in sorted_names:
                f.write(name + '\n')
        
        print(f"Saved {len(sorted_names)} unique paid listener names to {output_file}")
        return True
    
    except Exception as e:
        print(f"Error writing output file: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Default usage
        extract_payed_listener()
    elif len(sys.argv) == 2:
        extract_payed_listener(sys.argv[1])
    elif len(sys.argv) == 3:
        extract_payed_listener(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python extract_payed_listener.py [input_dir] [output_file]")
        print("  Default: python extract_payed_listener.py /mnt/f/Dev/utsulog/chat_logs/chat_logs_processed paid_listener.txt")
