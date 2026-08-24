from .audit import AuditLog
from .projects import ProjectService
from .schemas import ExportResponse
from .tasks import TaskService

class DataService:
    def __init__(self, projects: ProjectService, tasks: TaskService, audit: AuditLog, memory=None) -> None:
        self.projects = projects
        self.tasks = tasks
        self.audit = audit
        self.memory = memory

    def export_owner(self, owner: str) -> dict:
        result = ExportResponse(
            owner=owner,
            projects=self.projects.all_for(owner),
            tasks=self.tasks.all_for(owner),
            audit_log=[e for e in self.audit.entries if e.actor == owner],
        ).model_dump()
        result["memory"] = self.memory.export_owner(owner) if self.memory else []
        return result

    def delete_owner(self, owner: str) -> None:
        for project in self.projects.all_for(owner):
            self.projects.delete(project.id, owner)
        self.tasks.delete_for(owner)
        if self.memory:
            self.memory.delete_owner(owner)
