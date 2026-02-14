from logging.handlers import TimedRotatingFileHandler


class CustomLoggingHandler(TimedRotatingFileHandler):
    pass


db_handler: CustomLoggingHandler = CustomLoggingHandler("db")


def process(handler: CustomLoggingHandler, unrelated_type: int = 0) -> None:
    local_handler: CustomLoggingHandler = handler
    local_handler.emit(f"processing started {unrelated_type}")


class Service:
    service_handler: CustomLoggingHandler

    def __init__(self, handler: CustomLoggingHandler) -> None:
        self.service_handler = handler
        self.unrelated_type: int = 0

    def run(self) -> None:
        self.service_handler.emit(f"running {self.unrelated_type}")
