from operation import SessionOperation
from store import MemoryStore
from web import Controller, Cookies, Dispatcher, SessionAuth


def build():
    store, cookies = MemoryStore(), Cookies()
    operation = SessionOperation(store)
    controller = Controller(operation, store, cookies)
    auth = SessionAuth(store)
    dispatcher = Dispatcher({
        "exchange": controller.exchange,
        "cart": lambda request: auth.call(request, controller.cart),
    })
    return store, cookies, operation, dispatcher
