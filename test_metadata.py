#!/usr/bin/env python3
"""
Simple test script for metadata extraction.

This demonstrates the metadata extraction functionality without requiring
a full test framework setup.
"""

import sys
from pathlib import Path

# Add src to path so we can import rommer modules
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from rommer.extractor import MetadataExtractor


def test_metadata_extraction():
    """Test metadata extraction with various ROM titles."""

    extractor = MetadataExtractor()

    # Test cases with expected metadata
    test_cases = [
        {
            'title': 'Metal Gear Solid (USA) (Disc 1) (Rev 1)',
            'expected': {
                'primary_region': 'USA',
                'revision': 'Rev 1',
                'disc_info': 'Disc 1',
                'status': 'Production',
                'category': 'Games',
            }
        },
        {
            'title': 'Super Mario 64 (Europe) (En,Fr,De)',
            'expected': {
                'primary_region': 'Europe',
                'languages': ['En', 'Fr', 'De'],
                'category': 'Games',
            }
        },
        {
            'title': 'Sonic the Hedgehog (USA, Europe) (Beta)',
            'expected': {
                'regions': ['USA', 'Europe'],
                'status': 'Beta',
            }
        },
        {
            'title': 'Final Fantasy VII (USA) (Disc 1) (v1.1) [!]',
            'expected': {
                'primary_region': 'USA',
                'version': 'v1.1',
                'disc_info': 'Disc 1',
                'dump_status': 'verified',
            }
        },
        {
            'title': 'Legend of Zelda, The - Ocarina of Time (USA) (Demo)',
            'expected': {
                'primary_region': 'USA',
                'category': 'Demo',
            }
        },
        {
            'title': 'Pokemon Red Version (USA) (SLUS-00123)',
            'expected': {
                'primary_region': 'USA',
                'product_code': 'SLUS-00123',
            }
        },
        {
            'title': 'Gran Turismo (USA) (v1.2) (PAL)',
            'expected': {
                'primary_region': 'USA',
                'version': 'v1.2',
                'video_standard': 'PAL',
            }
        },
    ]

    print("Testing metadata extraction...")
    print("=" * 70)

    all_passed = True
    for i, test in enumerate(test_cases, 1):
        title = test['title']
        expected = test['expected']

        print(f"\nTest {i}: {title}")
        print("-" * 70)

        metadata = extractor.extract_metadata(title)

        # Check expected fields
        passed = True
        for key, expected_value in expected.items():
            actual_value = metadata.get(key)
            match = actual_value == expected_value

            status = "✓" if match else "✗"
            print(f"  {status} {key}: {actual_value} {'==' if match else '!='} {expected_value}")

            if not match:
                passed = False
                all_passed = False

        # Show other extracted fields
        print(f"\n  Additional metadata:")
        for key, value in metadata.items():
            if key not in expected and value:
                print(f"    {key}: {value}")

    print("\n" + "=" * 70)
    if all_passed:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(test_metadata_extraction())
