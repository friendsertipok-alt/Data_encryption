import hashlib
from collections import OrderedDict
from typing import Any

class LRUCache:
    """
    Простой in-memory LRU-кэш для хранения результатов анонимизации текста.
    Значительно ускоряет работу при повторяющихся блоках текста (например, в диалогах с LLM).
    """
    def __init__(self, capacity: int = 1024):
        self.capacity = capacity
        self.cache: OrderedDict[str, str] = OrderedDict()
        
    def _hash(self, key: Any) -> str:
        if isinstance(key, tuple):
            key_str = str(key)
        else:
            key_str = str(key)
        return hashlib.sha256(key_str.encode("utf-8")).hexdigest()

    def get(self, key: Any) -> Any | None:
        hash_key = self._hash(key)
        if hash_key in self.cache:
            self.cache.move_to_end(hash_key)
            return self.cache[hash_key]
        return None

    def put(self, key: Any, masked_text: Any) -> None:
        hash_key = self._hash(key)
        self.cache[hash_key] = masked_text
        self.cache.move_to_end(hash_key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
