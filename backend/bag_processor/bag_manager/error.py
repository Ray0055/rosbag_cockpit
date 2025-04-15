class BagPlayBackError(Exception):
    """Exception raised for errors in the bag playback process."""

    def __init__(self, message: str, error_code: int):
        super().__init__(message)
        self.message = message
        self.error_code = 1000

    def __str__(self):
        return f"BagPlayBackError {self.error_code}: {self.message}"


class BagPlaybackBusyError(BagPlayBackError):
    """Exception raised when a bag playback is already in progress."""

    def __init__(self, message: str = "A bag is being played now. ", error_code: int = 1001):
        super().__init__(message, error_code)
