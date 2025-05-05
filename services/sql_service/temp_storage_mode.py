from enum import Enum


class DBTempStorageModes(Enum):
    FILE = "File (lower RAM usage)"
    MEMORY = "Memory (recommended)"
