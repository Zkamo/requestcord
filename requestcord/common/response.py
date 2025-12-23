from typing import Any, Optional


class APIResponse:
    __slots__ = ("success", "status_code", "data", "error")

    def __init__(
        self,
        *,
        success: bool,
        status_code: int,
        data: Any = None,
        error: Optional[str] = None
    ):
        self.success = success
        self.status_code = status_code
        self.data = data
        self.error = error

    @classmethod
    def from_http_response(cls, response, data: Any = None):
        return cls(
            success=200 <= response.status < 300,
            status_code=response.status,
            data=data,
            error=None if response.status < 400 else response.reason
        )

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "status_code": self.status_code,
            "data": self.data,
            "error": self.error
        }

    def json(self) -> dict:
        return self.to_dict()