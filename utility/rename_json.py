#!/usr/bin/env python3
"""
Script to rename JSON files based on actualStartTime from videos.ndjson.

This script:
1. Reads videos/videos.ndjson
2. Extracts video_id from video_url
3. Globs the json directory
4. Renames JSON files:
   - Before format: {publishedAt}_[{video_id}]_{sanitized_title}_vtt.json
   - After format: {actualStartTime}_[{video_id}]_{sanitized_title}_vtt.json
"""

import os
import sys
import json
import glob
import re
from datetime import datetime


def extract_video_id(video_url: str) -> str | None:
    """
    Extract video_id from YouTube video URL.
    
    Supports formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/v/VIDEO_ID
    """
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/v/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, video_url)
        if match:
            return match.group(1)
    return None


def parse_datetime_to_format(datetime_str: str) -> str | None:
    """
    Ensure datetime string is in YYYYMMDDHHMMSS format.
    Also supports ISO 8601 parsing as fallback.
    """
    if not datetime_str:
        return None

    # Check if already in generic 14-digit format
    if re.fullmatch(r'\d{14}', datetime_str):
        return datetime_str

    try:
        # Handle ISO 8601 format with 'Z' or timezone
        if datetime_str.endswith('Z'):
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        else:
            dt = datetime.fromisoformat(datetime_str)
        return dt.strftime('%Y%m%d%H%M%S')
    except ValueError:
        return None


def load_videos_ndjson(ndjson_path: str) -> dict:
    """
    Load videos.ndjson and create a mapping of video_id to actualStartTime.
    
    Returns:
        dict: {video_id: formatted_actualStartTime}
    """
    video_map = {}
    
    if not os.path.exists(ndjson_path):
        print(f"Error: {ndjson_path} not found.")
        return video_map
    
    with open(ndjson_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                video_data = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse line {line_num}: {e}")
                continue
            
            video_url = video_data.get('video_url')
            actual_start_time = video_data.get('actualStartTime')
            
            if not video_url:
                print(f"Warning: Line {line_num} missing 'video_url'")
                continue
            
            if not actual_start_time:
                print(f"Warning: Line {line_num} missing 'actualStartTime'")
                continue
            
            video_id = extract_video_id(video_url)
            if not video_id:
                print(f"Warning: Could not extract video_id from URL: {video_url}")
                continue
            
            formatted_time = parse_datetime_to_format(actual_start_time)
            if not formatted_time:
                print(f"Warning: Could not parse actualStartTime: {actual_start_time}")
                continue
            
            video_map[video_id] = formatted_time
    
    print(f"Loaded {len(video_map)} videos from {ndjson_path}")
    return video_map


def rename_json_files(json_dir: str, video_map: dict, dry_run: bool = False):
    """
    Rename JSON files in the json directory based on video_map.
    
    File format:
    - Before: {publishedAt}_[{video_id}]_{sanitized_title}_vtt.json
    - After:  {actualStartTime}_[{video_id}]_{sanitized_title}_vtt.json
    """
    if not os.path.isdir(json_dir):
        print(f"Error: Directory {json_dir} not found.")
        return
    
    # Pattern to match: {timestamp}_[{video_id}]_{rest}_vtt.json
    pattern = re.compile(r'^(\d{14})_\[([a-zA-Z0-9_-]{11})\]_(.+)_vtt\.json$')
    
    json_files = glob.glob(os.path.join(json_dir, '*_vtt.json'))
    
    if not json_files:
        print(f"No *_vtt.json files found in {json_dir}")
        return
    
    print(f"Found {len(json_files)} JSON files in {json_dir}")
    
    renamed_count = 0
    skipped_count = 0
    error_count = 0
    
    for json_file in sorted(json_files):
        basename = os.path.basename(json_file)
        match = pattern.match(basename)
        
        if not match:
            print(f"Skip: {basename} does not match expected format")
            skipped_count += 1
            continue
        
        current_timestamp = match.group(1)
        video_id = match.group(2)
        rest = match.group(3)
        
        if video_id not in video_map:
            print(f"Skip: No actualStartTime found for video_id [{video_id}]")
            skipped_count += 1
            continue
        
        new_timestamp = video_map[video_id]
        
        if current_timestamp == new_timestamp:
            print(f"Skip: {basename} already has correct timestamp")
            skipped_count += 1
            continue
        
        new_basename = f"{new_timestamp}_[{video_id}]_{rest}_vtt.json"
        new_filepath = os.path.join(json_dir, new_basename)
        
        if os.path.exists(new_filepath):
            print(f"Error: Target file already exists: {new_basename}")
            error_count += 1
            continue
        
        if dry_run:
            print(f"[DRY RUN] Would rename:\n  {basename}\n  -> {new_basename}")
        else:
            try:
                os.rename(json_file, new_filepath)
                print(f"Renamed:\n  {basename}\n  -> {new_basename}")
                renamed_count += 1
            except OSError as e:
                print(f"Error renaming {basename}: {e}")
                error_count += 1
    
    print(f"\nSummary:")
    print(f"  Renamed: {renamed_count}")
    print(f"  Skipped: {skipped_count}")
    print(f"  Errors:  {error_count}")


def main():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    ndjson_path = os.path.join(script_dir, 'videos', 'videos.ndjson')
    json_dir = os.path.join(script_dir, 'json')
    
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv
    
    if dry_run:
        print("=== DRY RUN MODE (no files will be renamed) ===\n")
    
    # Load video data
    video_map = load_videos_ndjson(ndjson_path)
    
    if not video_map:
        print("No videos loaded. Exiting.")
        sys.exit(1)
    
    # Rename files
    rename_json_files(json_dir, video_map, dry_run=dry_run)


if __name__ == "__main__":
    main()
