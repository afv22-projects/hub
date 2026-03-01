from typing import Any, ClassVar


class VersionedMixin:

    __versioned__ = {}

    versions: ClassVar[list[Any]]
    versioned_fields: ClassVar[list[str]]
