from enum import Enum

import pytest

from mdorm.fields import EnumSpec


class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class TestEnumSpec:
    def setup_method(self):
        self.spec = EnumSpec(Status)

    def test_serialize_returns_enum_value(self):
        assert self.spec.serialize(Status.ACTIVE, "status") == "active"
        assert self.spec.serialize(Status.INACTIVE, "status") == "inactive"
        assert self.spec.serialize(Status.PENDING, "status") == "pending"

    def test_deserialize_returns_enum_member(self):
        assert self.spec.deserialize("active", "status") == Status.ACTIVE
        assert self.spec.deserialize("inactive", "status") == Status.INACTIVE
        assert self.spec.deserialize("pending", "status") == Status.PENDING

    def test_deserialize_invalid_value_raises(self):
        with pytest.raises(ValueError):
            self.spec.deserialize("unknown", "status")

    def test_roundtrip(self):
        for member in Status:
            serialized = self.spec.serialize(member, "status")
            deserialized = self.spec.deserialize(serialized, "status")
            assert deserialized == member
