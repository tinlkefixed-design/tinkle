class TinkleError(Exception):
    """Base exception for Tinkle."""

class TaskNotFoundError(TinkleError):
    pass

class ProjectNotFoundError(TinkleError):
    pass

class PermissionDeniedError(TinkleError):
    pass

class AuthenticationError(TinkleError):
    pass

class InvalidStateTransitionError(TinkleError):
    pass

class NoCompatibleModelError(TinkleError):
    pass
class ToolNotFoundError(TinkleError):
    pass
class ToolPermissionError(TinkleError):
    pass
class ToolValidationError(TinkleError):
    pass
class ToolExecutionError(TinkleError):
    pass
