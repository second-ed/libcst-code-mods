from logging.handlers import TimedRotatingFileHandler


class CustomLoggingHandler(TimedRotatingFileHandler):
    pass


custom_handler: CustomLoggingHandler = CustomLoggingHandler("db")


def process(custom_handler: CustomLoggingHandler, unrelated_type: int = 0) -> None:
    custom_handler: CustomLoggingHandler = custom_handler
    custom_handler.emit(f"processing started {unrelated_type}")


class Service:
    custom_handler: CustomLoggingHandler

    def __init__(self, custom_handler: CustomLoggingHandler) -> None:
        self.custom_handler = custom_handler
        self.unrelated_type: int = 0

    def run(self) -> None:
        self.custom_handler.emit(f"running {self.unrelated_type}")
