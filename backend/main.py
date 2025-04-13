#!/usr/bin/env python3
"""
Main entry point for the Cockpit ROS Bag Database Manager.

This script provides command line interface for managing ROS bag files
and their metadata in the SQLite database.
"""

import argparse
import os
import sys

from bag_processor.bag_manager.parser import RosbagParser
from bag_processor.database import DatabaseManager


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Cockpit ROS Bag Database Manager")

    parser.add_argument(
        "--db",
        type=str,
        default=DatabaseManager.DEFAULT_DB_PATH,
        help="Path to the SQLite database file",
    )

    # Add mutually exclusive group for processing options
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--bag", type=str, help="Process a single ROS bag file")
    group.add_argument("--dir", type=str, help="Process all ROS bag files in a directory")

    parser.add_argument(
        "--recursive",
        action="store_true",
        default=True,
        help="Recursively process subdirectories (default: True)",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Print database statistics after processing",
    )

    return parser.parse_args()


def main():
    """Main entry point for the script."""
    args = parse_args()

    # Initialize database manager
    db_manager = DatabaseManager(args.db)

    # Initialize parser
    parser = RosbagParser()

    print(f"Using database: {args.db}")
    try:
        if args.bag:
            # Process a single bag file
            if not os.path.exists(args.bag):
                print(f"Error: Bag file does not exist: {args.bag}")
                return 1

            print(f"Processing bag file: {args.bag}")
            metadata = parser.parse_bag_folder(args.bag)
            if metadata:
                db_manager.insert_rosbag_metadata(metadata)
                print(f"Successfully processed bag file: {args.bag}")
            else:
                print(f"Failed to process bag file: {args.bag}")

        elif args.dir:
            # Process a directory of bag files
            if not os.path.isdir(args.dir):
                print(f"Error: Directory does not exist: {args.dir}")
                return 1

            print(f"Processing bag files in directory: {args.dir}")
            print(f"Recursive search: {args.recursive}")

            metadata_list = parser.scan_directory(args.dir, args.recursive)
            print(f"Found {len(metadata_list)} bag files")

            for metadata in metadata_list:
                db_manager.insert_rosbag_metadata(metadata)

            print(f"Successfully processed {len(metadata_list)} bag files")

        if args.stats:
            db_manager.get_database_stats()

    finally:
        db_manager.close_db()

    return 0


if __name__ == "__main__":
    sys.exit(main())
