ticket_prices = {"london": "$799", "paris": "$899", "tokyo": "$1400", "berlin": "$499"}

danger_levels = {"london": "3", "paris": "5", "tokyo": "1", "berlin": "4"}

def get_ticket_price(destination_city):
    print(f"Price tool called for city {destination_city}")
    price = ticket_prices.get(destination_city.lower(), "Unknown ticket price")
    return f"The price of a ticket to {destination_city} is {price}"

    # There's a particular dictionary structure that's required to describe our function:

def get_danger_level(destination_city):
    print(f"Danger level tool called for city {destination_city}")
    danger = danger_levels.get(destination_city.lower(), "Unknown danger level")
    return f"The danger level of {destination_city} is {danger}"

    # There's a particular dictionary structure that's required to describe our function:

price_function = {
    "name": "get_ticket_price",
    "description": "Get the price of a return ticket to the destination city.",
    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {
                "type": "string",
                "description": "The city that the customer wants to travel to",
            },
        },
        "required": ["destination_city"],
        "additionalProperties": False
    }
}

danger_level_function = {
    "name": "get_danger_level",
    "description": "Get the danger level of a destination city.",
    "parameters": {
        "type": "object",
        "properties": {
            "destination_city": {
                "type": "string",
                "description": "The city that the customer wants to travel to",
            },
        },
        "required": ["destination_city"],
        "additionalProperties": False
    }
}

tools = [{"type": "function", "function": price_function}, {"type": "function", "function": danger_level_function}]