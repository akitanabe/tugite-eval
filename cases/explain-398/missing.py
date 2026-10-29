from provider_adapter import exchange_ticket


def exchange(request, cookies):
    session_id = exchange_ticket(request["ticket"], request["cookies"].get("binding"))
    cookies.session(session_id)
    return {"status": 204}


def cart(request, repository):
    return repository.cart_for(request["user"])


ROUTES = {"exchange": exchange, "cart": cart}
