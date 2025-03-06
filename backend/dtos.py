from typing import List, Optional


class ErrorResponseDTO:
    def __init__(
        self,
        status: int,
        message: str,
        invalid_fields: Optional[List[str]] = None,
        data: Optional[dict] = None,
    ):
        self.status = status
        self.message = message
        self.invalid_fields = invalid_fields
        self.data = data


class NotFoundErrorResponseDTO:
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message


class UnauthorizedErrorResponseDTO:
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
