def validate_request(data):
    if not data:
        return "Missing JSON body"

    if "text" not in data:
        return "Missing 'text' field"

    if not isinstance(data["text"], str):
        return "'text' must be a string"

    if len(data["text"].strip()) == 0:
        return "'text' cannot be empty"

    return None
