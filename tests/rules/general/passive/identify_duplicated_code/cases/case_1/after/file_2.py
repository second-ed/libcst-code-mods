def process_b(table, item) -> None:
    result = table.clean(item)
    save(result, limit=50)
