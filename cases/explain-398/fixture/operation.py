from store import Rejected


class SessionOperation:
    def __init__(self, store):
        self.store = store

    def prepare(self, binding, now):
        parent_id = self.store.fresh("challenge")
        self.store.parents[parent_id] = {
            "binding": binding, "expires": now + 30, "refresh_active": True
        }
        return parent_id

    def issue(self, parent_id, user_id, now):
        parent = self.store.lock_parent(parent_id)
        if not parent or parent["expires"] <= now or not parent["refresh_active"]:
            raise Rejected("inactive challenge")
        code = self.store.fresh("code")
        self.store.codes[code] = {"parent": parent_id, "user": user_id, "used": False}
        return code

    def exchange(self, parent_id, code, binding, now):
        with self.store.transaction():
            parent = self.store.lock_parent(parent_id)
            item = self.store.lock_code(code)
            if not parent or parent["expires"] <= now or not parent["refresh_active"]:
                raise Rejected("inactive challenge")
            if not item or item["parent"] != parent_id or item["used"]:
                raise Rejected("invalid code")
            if parent["binding"] != binding:
                raise Rejected("binding mismatch")
            self.store.purge_expired(now)
            session_id = self.store.register(code, item["user"], now)
        return session_id
