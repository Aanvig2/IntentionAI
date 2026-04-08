package financial

default allow := false

allow if {
    input.action in input.token.allowed_actions
    ticker_allowed
    qty_within_limit
    destination_allowed
}

ticker_allowed if {
    "*" in input.token.ticker_scope
}

ticker_allowed if {
    input.ticker in input.token.ticker_scope
}

qty_within_limit if {
    input.token.max_qty == 0
}

qty_within_limit if {
    input.qty <= input.token.max_qty
}

destination_allowed if {
    input.action != "SEND_DATA"
}

destination_allowed if {
    input.action == "SEND_DATA"
    input.destination == input.token.destination_scope
}

# violations (set)
violation contains "action_not_permitted" if {
    not input.action in input.token.allowed_actions
}

violation contains "ticker_out_of_scope" if {
    not ticker_allowed
}

violation contains "qty_exceeded" if {
    not qty_within_limit
}

violation contains "unauthorized_destination" if {
    input.action == "SEND_DATA"
    input.destination != input.token.destination_scope
}