def process_a(obj, value) -> None:
    cleaned = obj.clean(value)
    save(cleaned, limit=10)
