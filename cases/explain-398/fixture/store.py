from contextlib import contextmanager
from copy import deepcopy


class Rejected(Exception):
    pass


class MemoryStore:
    """Single-threaded teaching store; no database or external calls."""
    def __init__(self):
        self.parents = {}
        self.codes = {}
        self.sessions = {}
        self.carts = {}
        self.serial = 0
        self.fail_commit = False

    def fresh(self, prefix):
        self.serial += 1
        return f"{prefix}-{self.serial}"

    @contextmanager
    def transaction(self):
        before = deepcopy((self.parents, self.codes, self.sessions))
        try:
            yield self
            if self.fail_commit:
                raise RuntimeError("commit failed")
        except Exception:
            self.parents, self.codes, self.sessions = before
            raise
        # Normal context exit is the commit boundary in this synthetic store.

    def lock_parent(self, parent_id):
        return self.parents.get(parent_id)

    def lock_code(self, code):
        return self.codes.get(code)

    def register(self, code, user_id, now):
        self.codes[code]["used"] = True
        session_id = self.fresh("session")
        self.sessions[session_id] = {"user": user_id, "expires": now + 60}
        return session_id

    def purge_expired(self, now):
        for key in list(self.sessions):
            if self.sessions[key]["expires"] <= now:
                del self.sessions[key]
