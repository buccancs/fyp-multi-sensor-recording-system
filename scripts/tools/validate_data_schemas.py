#!/usr/bin/env python3
"""
Data Schema Validation Utility

This script validates data files against their schemas to ensure data integrity
and consistency across the multi-sensor recording system.

Usage:
    python validate_data_schemas.py [--session SESSION_PATH] [--schema-dir SCHEMA_DIR]
    python validate_data_schemas.py --all-sessions
    python validate_data_schemas.py --check-schema SCHEMA_FILE
"""

import argparse
import json
import jsonschema
import os
import sys
from jsonschema import ValidationError
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class DataSchemaValidator:
    """Validates data files against JSON schemas."""

    def __init__(self, schema_dir: str = "docs/schemas"):
        """Initialize validator with schema directory."""
        self.schema_dir = Path(schema_dir)
        self.schemas = {}
        self.load_schemas()

    def load_schemas(self) -> None:
        """Load all JSON schemas from the schema directory."""
        if not self.schema_dir.exists():
            print(f"Warning: Schema directory {self.schema_dir} not found")
            return

        schema_files = {
            "session_metadata": "session_metadata_schema.json",
            "session_log": "session_log_schema.json",
            "calibration_session": "calibration_session_schema.json",
            "processing_metadata": "processing_metadata_schema.json"
        }

        for schema_name, filename in schema_files.items():
            schema_path = self.schema_dir / filename
            if schema_path.exists():
                try:
                    with open(schema_path, 'r') as f:
                        self.schemas[schema_name] = json.load(f)
                    print(f"✓ Loaded schema: {schema_name}")
                except Exception as e:
                    print(f"✗ Failed to load schema {schema_name}: {e}")
            else:
                print(f"⚠ Schema file not found: {filename}")

    def validate_file(self, file_path: str, schema_name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a single file against its schema.

        Args:
            file_path: Path to the JSON file to validate
            schema_name: Name of the schema to validate against

        Returns:
            Tuple of (is_valid, error_message)
        """
        if schema_name not in self.schemas:
            return False, f"Schema '{schema_name}' not loaded"

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            return False, f"Failed to read JSON file: {e}"

        try:
            jsonschema.validate(data, self.schemas[schema_name])
            return True, None
        except ValidationError as e:
            return False, f"Validation error: {e.message}"
        except Exception as e:
            return False, f"Unexpected error: {e}"

    def validate_session(self, session_path: str) -> Dict[str, any]:
        """
        Validate all data files in a session folder.

        Args:
            session_path: Path to session folder

        Returns:
            Dictionary with validation results
        """
        session_path = Path(session_path)
        results = {
            "session_path": str(session_path),
            "valid": True,
            "files_checked": 0,
            "files_valid": 0,
            "errors": []
        }

        if not session_path.exists():
            results["valid"] = False
            results["errors"].append(f"Session path does not exist: {session_path}")
            return results

        metadata_file = session_path / "session_metadata.json"
        if metadata_file.exists():
            results["files_checked"] += 1
            is_valid, error = self.validate_file(metadata_file, "session_metadata")
            if is_valid:
                results["files_valid"] += 1
                print(f"✓ session_metadata.json")
            else:
                results["valid"] = False
                results["errors"].append(f"session_metadata.json: {error}")
                print(f"✗ session_metadata.json: {error}")
        else:
            results["errors"].append("Missing session_metadata.json")
            print("⚠ Missing session_metadata.json")

        log_files = list(session_path.glob("*_log.json"))
        for log_file in log_files:
            results["files_checked"] += 1
            is_valid, error = self.validate_file(log_file, "session_log")
            if is_valid:
                results["files_valid"] += 1
                print(f"✓ {log_file.name}")
            else:
                results["valid"] = False
                results["errors"].append(f"{log_file.name}: {error}")
                print(f"✗ {log_file.name}: {error}")

        processing_files = list(session_path.glob("**/processing_metadata.json"))
        for proc_file in processing_files:
            results["files_checked"] += 1
            is_valid, error = self.validate_file(proc_file, "processing_metadata")
            if is_valid:
                results["files_valid"] += 1
                print(f"✓ {proc_file.relative_to(session_path)}")
            else:
                results["valid"] = False
                results["errors"].append(f"{proc_file.relative_to(session_path)}: {error}")
                print(f"✗ {proc_file.relative_to(session_path)}: {error}")

        return results

    def validate_calibration_session(self, calibration_path: str) -> Dict[str, any]:
        """
        Validate calibration session data.

        Args:
            calibration_path: Path to calibration session folder

        Returns:
            Dictionary with validation results
        """
        calibration_path = Path(calibration_path)
        results = {
            "calibration_path": str(calibration_path),
            "valid": True,
            "files_checked": 0,
            "files_valid": 0,
            "errors": []
        }

        info_file = calibration_path / "session_info.json"
        if info_file.exists():
            results["files_checked"] += 1
            is_valid, error = self.validate_file(info_file, "calibration_session")
            if is_valid:
                results["files_valid"] += 1
                print(f"✓ session_info.json")
            else:
                results["valid"] = False
                results["errors"].append(f"session_info.json: {error}")
                print(f"✗ session_info.json: {error}")
        else:
            results["errors"].append("Missing session_info.json")
            print("⚠ Missing session_info.json")

        return results

    def find_all_sessions(self, base_dir: str = "PythonApp/recordings") -> List[Path]:
        """Find all session folders in the recordings directory."""
        base_path = Path(base_dir)
        sessions = []

        if base_path.exists():
            for item in base_path.iterdir():
                if item.is_dir() and ("session_" in item.name or item.name.endswith("_log.json")):
                    if (item / "session_metadata.json").exists():
                        sessions.append(item)

        return sessions

    def find_all_calibration_sessions(self, base_dir: str = "calibration_data") -> List[Path]:
        """Find all calibration session folders."""
        base_path = Path(base_dir)
        sessions = []

        if base_path.exists():
            for item in base_path.iterdir():
                if item.is_dir() and (item / "session_info.json").exists():
                    sessions.append(item)

        return sessions


def main():
    """Main entry point for the validation script."""
    parser = argparse.ArgumentParser(description="Validate data files against schemas")
    parser.add_argument("--session", help="Path to specific session to validate")
    parser.add_argument("--schema-dir", default="docs/schemas", help="Directory containing schema files")
    parser.add_argument("--all-sessions", action="store_true", help="Validate all sessions")
    parser.add_argument("--calibration", help="Path to calibration session to validate")
    parser.add_argument("--check-schema", help="Validate a specific schema file")

    args = parser.parse_args()

    validator = DataSchemaValidator(args.schema_dir)

    if args.check_schema:
        try:
            with open(args.check_schema, 'r') as f:
                schema = json.load(f)
            jsonschema.Draft7Validator.check_schema(schema)
            print(f"✓ Schema {args.check_schema} is valid")
        except Exception as e:
            print(f"✗ Schema {args.check_schema} is invalid: {e}")
            return 1

    elif args.session:
        print(f"Validating session: {args.session}")
        results = validator.validate_session(args.session)

        print(f"\nValidation Summary:")
        print(f"Files checked: {results['files_checked']}")
        print(f"Files valid: {results['files_valid']}")
        print(f"Overall valid: {'✓' if results['valid'] else '✗'}")

        if results['errors']:
            print(f"\nErrors:")
            for error in results['errors']:
                print(f"  - {error}")
            return 1

    elif args.calibration:
        print(f"Validating calibration session: {args.calibration}")
        results = validator.validate_calibration_session(args.calibration)

        print(f"\nValidation Summary:")
        print(f"Files checked: {results['files_checked']}")
        print(f"Files valid: {results['files_valid']}")
        print(f"Overall valid: {'✓' if results['valid'] else '✗'}")

        if results['errors']:
            print(f"\nErrors:")
            for error in results['errors']:
                print(f"  - {error}")
            return 1

    elif args.all_sessions:
        print("Finding all sessions...")
        sessions = validator.find_all_sessions()
        calibration_sessions = validator.find_all_calibration_sessions()

        print(f"Found {len(sessions)} recording sessions and {len(calibration_sessions)} calibration sessions")

        total_valid = 0
        total_sessions = len(sessions) + len(calibration_sessions)

        for session in sessions:
            print(f"\n--- Validating {session.name} ---")
            results = validator.validate_session(session)
            if results['valid']:
                total_valid += 1

        for calib_session in calibration_sessions:
            print(f"\n--- Validating calibration {calib_session.name} ---")
            results = validator.validate_calibration_session(calib_session)
            if results['valid']:
                total_valid += 1

        print(f"\n=== Overall Summary ===")
        print(f"Total sessions: {total_sessions}")
        print(f"Valid sessions: {total_valid}")
        print(f"Success rate: {total_valid/total_sessions*100:.1f}%" if total_sessions > 0 else "No sessions found")

        if total_valid < total_sessions:
            return 1

    else:
        print("No validation target specified. Use --help for options.")
        return 1

    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nValidation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)