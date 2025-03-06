class ErrorResponseDTO:
    def __init__(self, status, error, missing_fields=None, invalid_fields=None):
        self.status = status
        self.error = error
        self.missing_fields = missing_fields
        self.invalid_fields = invalid_fields
        self.data = None

class SuccessResponseDTO:
    def __init__(self, status, data, message=None):
        self.status = status
        self.message = message
        self.data = data


class CreatePostDTO(SuccessResponseDTO):
    def __init__(self, status, data, message=None):
        super().__init__(status, data, message)
        self.created_at = data['created_at']

