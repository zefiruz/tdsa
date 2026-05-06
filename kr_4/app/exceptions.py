class CustomExceptionA(Exception):
    def __init__(self, message: str):
        self.message = message

class CustomExceptionB(Exception):
    def __init__(self, message: str):
        self.message = message