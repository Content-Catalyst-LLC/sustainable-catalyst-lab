"""SQLite transaction contexts with deterministic connection ownership."""
import sqlite3

class ClosingConnection(sqlite3.Connection):
    """Retain native commit/rollback semantics, then release the descriptor."""
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()
