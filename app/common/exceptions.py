"""Custom exceptions for the application."""


class BaseAppException(Exception):
    """Base exception for all application errors."""

    def __init__(
        self,
        message: str,
        user_message: str = "Something went wrong. Please try again later.",
    ):
        self.message = message
        self.user_message = user_message
        super().__init__(self.message)


# External service errors (API calls, network issues)
class ExternalServiceError(BaseAppException):
    """Exception raised when external service calls fail."""

    def __init__(
        self,
        message: str = "External service error",
        user_message: str = "External service error. Please try again later.",
    ):
        super().__init__(message=message, user_message=user_message)


class InstagramAPIError(ExternalServiceError):
    """Exception raised when Instagram API calls fail."""

    def __init__(self, message: str = "Instagram API error"):
        super().__init__(
            message=message,
            user_message="Failed to download content from Instagram. Please try again later.",
        )


class TikTokAPIError(ExternalServiceError):
    """Exception raised when TikTok API calls fail."""

    def __init__(self, message: str = "TikTok API error"):
        super().__init__(
            message=message,
            user_message="Failed to download video from TikTok. Please try again later.",
        )


# Internal application errors (business logic, validation)
class InternalAppError(BaseAppException):
    """Exception raised when internal application logic fails."""

    def __init__(self, message: str = "Internal application error"):
        super().__init__(
            message=message,
            user_message="Something went wrong. Please try again later.",
        )


class RollProcessingError(InternalAppError):
    """Exception raised when roll processing fails."""

    def __init__(self, message: str = "Roll processing failed"):
        super().__init__(
            message=message,
            user_message="Failed to process dice roll command. Please try again.",
        )


class InputValidationError(InternalAppError):
    """Exception raised when input validation fails."""

    def __init__(self, message: str = "Input validation failed"):
        super().__init__(
            message=message,
            user_message="Invalid command format. Please check the syntax.",
        )
