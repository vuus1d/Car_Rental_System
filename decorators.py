def log_action(func):

    def wrapper(*args, **kwargs):

        print(f"\n[LOG] Executing: {func.__name__}")

        result = func(*args, **kwargs)

        print(f"[LOG] Finished: {func.__name__}")

        return result

    return wrapper