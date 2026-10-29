# Synthetic WebView-like session

Teaching code only; Python standard library, no database, SDK, API or network. Inspect statically.
`app.build()` wires the supplied paths. `SessionOperation.prepare(binding, now)` returns a challenge id;
`issue(challenge, user, now)` returns a code. A caller supplies these and the binding cookie to the exchange route,
then supplies the issued session cookie to the cart route. The real app/WebView transport and binding-cookie
installation are not provided. No security adequacy or production concurrency guarantee is claimed.
`lock_*` are lookups in this single-threaded memory model, not real locks. Normal transaction context exit
commits; an exception rolls back parent/code/session maps. The id counter is deliberately outside rollback.
Requests are dictionaries with `now` and `cookies`; exchange also has `parent` and `code`. Use well-shaped
requests when explaining the main path. Unexpected exceptions and missing route keys propagate.
