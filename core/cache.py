import hashlib
from collections import OrderedDict

class LRUCache:
    """
    Простой in-memory LRU-кэш для хранения результатов анонимизации текста.
    Значительно ускоряет работу при повторяющихся блоках текста (например, в диалогах с LLM).
    """
    def __init__(self, capacity: int = 1024):
        self.capacity = capacity
        self.cache: OrderedDict[str, str] = OrderedDict()
        
    def _hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def get(self, text: str) -> str | None:
        key = self._hash(text)
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None

    def put(self, text: str, masked_text: str) -> None:
        key = self._hash(text)
        self.cache[key] = masked_text
        self.cache.move_to_end(key)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
