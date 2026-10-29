from store import Rejected


class Cookies:
    def __init__(self):
        self.issued = []
        self.fail = False

    def session(self, session_id):
        if self.fail:
            raise RuntimeError("cookie failed")
        self.issued.append(("session", session_id))


class Controller:
    def __init__(self, operation, store, cookies):
        self.operation, self.store, self.cookies = operation, store, cookies

    def exchange(self, request):
        session_id = self.operation.exchange(
            request["parent"], request["code"], request["cookies"].get("binding"), request["now"]
        )
        self.cookies.session(session_id)
        return {"status": 204}

    def cart(self, request):
        return {"status": 200, "cart": self.store.carts.get(request["user"], [])}


class SessionAuth:
    def __init__(self, store):
        self.store = store

    def call(self, request, next_handler):
        session = self.store.sessions.get(request["cookies"].get("session"))
        if not session or session["expires"] <= request["now"]:
            raise Rejected("unauthenticated")
        authenticated = dict(request, user=session["user"])
        return next_handler(authenticated)


class Dispatcher:
    def __init__(self, routes):
        self.routes = routes

    def dispatch(self, name, request):
        handler = self.routes[name]
        try:
            return handler(request)
        except Rejected as error:
            return {"status": 403, "reason": str(error)}
