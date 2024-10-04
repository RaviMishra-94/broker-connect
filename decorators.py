def handle_parse_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, AttributeError, TypeError) as e:
            print(f"Caught an error while trying to parse response using {func.__name__}: {e}")

    return wrapper
