from uuid import UUID
from .errors import ProjectNotFoundError
from .schemas import Project, ProjectCreate

class ProjectService:
    def __init__(self) -> None:
        self._projects: dict[UUID, Project] = {}

    def create(self, data: ProjectCreate, owner: str) -> Project:
        project = Project(name=data.name, owner=owner)
        self._projects[project.id] = project
        return project

    def get(self, project_id: UUID, owner: str) -> Project:
        project = self._projects.get(project_id)
        if project is None or project.owner != owner:
            raise ProjectNotFoundError(str(project_id))
        return project

    def delete(self, project_id: UUID, owner: str) -> None:
        self.get(project_id, owner)
        del self._projects[project_id]

    def all_for(self, owner: str) -> list[Project]:
        return [p for p in self._projects.values() if p.owner == owner]
