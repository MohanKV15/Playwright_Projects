import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Union

logger = logging.getLogger(__name__)


class DataReader:
    """Utility class for loading test data from JSON files."""

    @staticmethod
    def load_json(file_path: Union[str, Path]) -> Any:
        """Loads and returns parsed data from a JSON file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Test data JSON file not found at: {path}")

        logger.info(f"Loading test data JSON: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def get_test_cases(json_path: Union[str, Path], key: str) -> List[Dict[str, Any]]:
        """Extracts a specific test case list from a JSON file."""
        data = DataReader.load_json(json_path)
        if key not in data:
            raise KeyError(f"Key '{key}' not found in test data JSON file: {json_path}")
        return data[key]
