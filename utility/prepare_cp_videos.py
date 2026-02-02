#!/usr/bin/env python3
"""
Script to copy video files from samba network folder to VIDEOFILES_DIR.

This script:
1. Copies *.mp4 files from /mnt/miniutsuro/utsulog-data/videofiles
2. Destination: VIDEOFILES_DIR environment variable
3. Skips files that already exist in the destination
"""

import os
import sys
import glob
import shutil
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Source and destination paths
SOURCE_DIR = '/mnt/miniutsuro/utsulog-data/videofiles'
DEST_DIR = os.environ.get('VIDEOFILES_DIR', '/app/videofiles')


def copy_videos(source_dir: str, dest_dir: str, dry_run: bool = False) -> tuple[int, int, int]:
    """
    Copy MP4 video files from source directory to destination directory.
    
    Args:
        source_dir: Source directory path
        dest_dir: Destination directory path
        dry_run: If True, only show what would be done without actually copying
    
    Returns:
        tuple: (copied_count, skipped_count, error_count)
    """
    copied_count = 0
    skipped_count = 0
    error_count = 0
    
    # Check if source directory exists
    if not os.path.isdir(source_dir):
        logger.error(f"Source directory not found: {source_dir}")
        return copied_count, skipped_count, error_count
    
    # Create destination directory if it doesn't exist
    if not dry_run:
        os.makedirs(dest_dir, exist_ok=True)
    
    # Find all MP4 files in source directory
    mp4_pattern = os.path.join(source_dir, '*.mp4')
    mp4_files = glob.glob(mp4_pattern)
    
    if not mp4_files:
        logger.warning(f"No MP4 files found in {source_dir}")
        return copied_count, skipped_count, error_count
    
    logger.info(f"Found {len(mp4_files)} MP4 files in {source_dir}")
    
    for source_file in sorted(mp4_files):
        basename = os.path.basename(source_file)
        dest_file = os.path.join(dest_dir, basename)
        
        # Skip if file already exists in destination
        if os.path.exists(dest_file):
            logger.info(f"Skip (exists): {basename}")
            skipped_count += 1
            continue
        
        if dry_run:
            logger.info(f"[DRY RUN] Would copy: {basename}")
            copied_count += 1
        else:
            try:
                logger.info(f"Copying: {basename}")
                shutil.copy2(source_file, dest_file)
                logger.info(f"Copied: {basename}")
                copied_count += 1
            except (OSError, IOError) as e:
                logger.error(f"Error copying {basename}: {e}")
                error_count += 1
    
    return copied_count, skipped_count, error_count


def main():
    """Main function."""
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv
    
    if dry_run:
        logger.info("=== DRY RUN MODE (no files will be copied) ===")
    
    logger.info(f"Source: {SOURCE_DIR}")
    logger.info(f"Destination: {DEST_DIR}")
    
    copied, skipped, errors = copy_videos(SOURCE_DIR, DEST_DIR, dry_run=dry_run)
    
    logger.info("=" * 50)
    logger.info("Summary:")
    logger.info(f"  Copied:  {copied}")
    logger.info(f"  Skipped: {skipped}")
    logger.info(f"  Errors:  {errors}")
    
    if errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
