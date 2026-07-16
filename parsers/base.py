from abc import ABC, abstractmethod

class BaseParser(ABC):
    @staticmethod
    @abstractmethod
    def anonymize(file_bytes: bytes, anonymize_func) -> bytes:
        pass

    @staticmethod
    @abstractmethod
    def deanonymize(file_bytes: bytes, deanonymize_func) -> bytes:
        pass
