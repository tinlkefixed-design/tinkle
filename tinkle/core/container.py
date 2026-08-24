from .audit import AuditLog
from .events import EventBus
from .export import DataService
from .jobs import JobQueue
from .projects import ProjectService
from .state import StateStore
from .tasks import TaskService
from tinkle.memory.service import MemoryService
from tinkle.security.policy import RateLimiter, SecurityPolicy
from tinkle.privacy import PrivacyService
from tinkle.observer.engine import TinkleObserver
from tinkle.integration.engine import IntegrationCoordinator

events = EventBus()
audit = AuditLog(events)
state = StateStore()
tasks = TaskService(events)
projects = ProjectService()
jobs = JobQueue()
memory = MemoryService("./data/tinkle_memory.db")
privacy = PrivacyService()
observer = TinkleObserver()
data = DataService(projects, tasks, audit, memory)
security_policy = SecurityPolicy()
from .config import settings
rate_limiter = RateLimiter(security_policy, enabled=settings.env.lower() == "production")

# Phase 28: one shared coordinator wires the existing core boundaries together.
