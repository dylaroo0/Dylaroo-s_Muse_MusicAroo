# File: ai_music_assistant/plugins/base.py

from abc import ABC, abstractmethod

class Plugin(ABC):
    """
    Base class for all assistant plugins. Each must implement:
      - name: unique identifier
      - version: plugin version string
      - run(data): returns a dict of results
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique plugin name identifier"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version string"""
        pass

    @abstractmethod
    def run(self, data: dict) -> dict:
        """
        Process input data (e.g., audio bytes, MIDI bytes) and return a dictionary of results.

        Args:
            data (dict): Contains 'bytes' key with file data.
        Returns:
            dict: Analysis or error information.
        """
        pass
