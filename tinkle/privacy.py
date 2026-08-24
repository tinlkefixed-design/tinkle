from dataclasses import dataclass
from threading import RLock

@dataclass(frozen=True)
class PrivacySettings:
    store_data: bool = True
    allow_cloud_models: bool = True
    local_only: bool = False
    allow_delete: bool = True
    allow_export: bool = True

class PrivacyService:
    def __init__(self) -> None:
        self._settings: dict[str, PrivacySettings] = {}
        self._lock = RLock()

    def get(self, owner: str) -> PrivacySettings:
        with self._lock:
            return self._settings.get(owner, PrivacySettings())

    def update(self, owner: str, **changes) -> PrivacySettings:
        current = self.get(owner)
        updated = PrivacySettings(**{**current.__dict__, **changes})
        if updated.local_only:
            updated = PrivacySettings(**{**updated.__dict__, "allow_cloud_models": False})
        with self._lock:
            self._settings[owner] = updated
        return updated
