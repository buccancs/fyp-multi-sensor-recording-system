"""
Shimmer library import utilities with proper fallback handling.

This module provides a clean way to import the pyshimmer library without
using hacky sys.path manipulation.
"""

import logging
from pathlib import Path


def _import_shimmer():
    """Import shimmer libraries with proper fallback handling."""
    # Try to import pyshimmer from the standard library path first
    try:
        from pyshimmer import DEFAULT_BAUDRATE, DataPacket, ShimmerBluetooth
        from serial import Serial

        return Serial, ShimmerBluetooth, DataPacket, DEFAULT_BAUDRATE, True
    except ImportError:
        # Try to add the Android app libs path temporarily and cleanly
        android_libs_path = (
            Path(__file__).parent.parent.parent / "AndroidApp" / "libs" / "pyshimmer"
        )

        if android_libs_path.exists():
            import sys

            # Store original path to restore later
            original_path = sys.path.copy()
            try:
                sys.path.insert(0, str(android_libs_path))
                from pyshimmer import DEFAULT_BAUDRATE, DataPacket, ShimmerBluetooth
                from serial import Serial

                return Serial, ShimmerBluetooth, DataPacket, DEFAULT_BAUDRATE, True
            except ImportError as e:
                logging.warning(
                    f"PyShimmer library not available even with Android libs path: {e}"
                )
            finally:
                # Restore original path
                sys.path = original_path
        else:
            logging.warning(
                "PyShimmer library not available and Android libs path not found"
            )

        # Provide fallback classes if pyshimmer is not available
        class Serial:
            """Fallback Serial class when pyshimmer is not available."""

            def __init__(self, *args, **kwargs):
                pass

        class ShimmerBluetooth:
            """Fallback ShimmerBluetooth class when pyshimmer is not available."""

            def __init__(self, *args, **kwargs):
                pass

        class DataPacket:
            """Fallback DataPacket class when pyshimmer is not available."""

            def __init__(self, *args, **kwargs):
                pass

        return Serial, ShimmerBluetooth, DataPacket, 115200, False


# Import all shimmer classes and constants
Serial, ShimmerBluetooth, DataPacket, DEFAULT_BAUDRATE, PYSHIMMER_AVAILABLE = (
    _import_shimmer()
)
