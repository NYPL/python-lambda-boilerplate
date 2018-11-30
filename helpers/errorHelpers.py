class NoRecordsRecieved(Exception):
    def __init__(self, message, invocation):
        self.message = message
        self.invocation = invocation
