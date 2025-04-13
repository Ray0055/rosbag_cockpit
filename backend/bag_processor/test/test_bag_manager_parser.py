import pytest
from ..bag_manager.parser import RosbagParser

@pytest.fixture
def bag_parser():
    """Fixture to create an instance of RosbagParser."""
    return RosbagParser()

def test_scan_directory():
    """
    Test the scan_directory method of RosbagParser.

    Args:
        directory_path: Path to the directory to scan.
        recursive: Whether to scan recursively.
    """
    # Create an instance of RosbagParser
    parser = RosbagParser()

    directory_path = "path/to/test/directory"  # Replace with actual test directory
    metadata_list = parser.scan_directory(directory_path, recursive=True)
    assert len(metadata_list) == 0, "directory does not exits"

    directory_path = "/home/driverless/rosbag_cockpit/backend/bag_processor/test/test_examples/rosbags/"
    metadata_list = parser.scan_directory(directory_path, recursive=True)
    assert len(metadata_list) > 0,  "metadata found in the directory"

