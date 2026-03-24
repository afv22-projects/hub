import datetime
from typing import Any, ClassVar

from sqlalchemy_history import make_versioned
from sqlalchemy_history.plugins import PropertyModTrackerPlugin

from hub.reflect.enums import HistoryOperation
from hub.reflect.schemas import HistoryEntry

# Initialize versioning before any model using this mixin is defined
make_versioned(user_cls=None, plugins=[PropertyModTrackerPlugin()])  # type: ignore


class VersionedMixin:

    __versioned__ = {}

    # This is set by sqlalchemy-history
    versions: ClassVar[list[Any]]

    # This doesn't configure what fields are actually tracked, but it
    # does make dynamically accessing them much easier
    versioned_fields: ClassVar[list[str]]

    def get_history(self) -> list[HistoryEntry]:
        history: list[HistoryEntry] = []
        for version in self.versions:
            operation = HistoryOperation(version.operation_type)
            issued_at: datetime.datetime = version.transaction.issued_at
            timestamp = (issued_at.isoformat() + "Z") if issued_at else ""

            if operation == HistoryOperation.INSERT:
                # Include initial state for creation
                changes: dict[str, str | None] = {}
                for field in self.versioned_fields:
                    val = getattr(version, field, None)
                    changes[field] = str(val) if val is not None else None
                history.append(
                    HistoryEntry(
                        timestamp=timestamp,
                        operation=operation,
                        changes=changes,
                    )
                )
            else:
                # For updates, only include changed fields
                changes = {}
                for field in self.versioned_fields:
                    mod_flag = getattr(version, f"{field}_mod", False)
                    if mod_flag:
                        new_val = getattr(version, field, None)
                        changes[field] = str(new_val) if new_val is not None else None

                if changes:
                    history.append(
                        HistoryEntry(
                            timestamp=timestamp,
                            operation=operation,
                            changes=changes,
                        )
                    )

        return history
