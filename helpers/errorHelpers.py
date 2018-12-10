
class NoRecordsReceived(Exception):
    def __init__(self, message, invocation):
        self.message = message
        self.invocation = invocation


class InvalidExecutionType(Exception):
    def __init__(self, message):
        self.message = message
