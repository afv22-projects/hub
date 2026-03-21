from enum import Enum

import pytest

from mdorm.fields import EnumSpec, ListSpec, ListSectionSpec


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


class TestListSpec:
    def setup_method(self):
        self.spec = ListSpec()

    def test_serialize_returns_comma_separated_string(self):
        assert self.spec.serialize(["a", "b", "c"], "tags") == "a, b, c"

    def test_serialize_empty_list(self):
        assert self.spec.serialize([], "tags") == ""

    def test_deserialize_parses_comma_separated_string(self):
        assert self.spec.deserialize("a, b, c", "tags") == ["a", "b", "c"]

    def test_deserialize_handles_no_spaces(self):
        assert self.spec.deserialize("a,b,c", "tags") == ["a", "b", "c"]

    def test_deserialize_empty_string(self):
        assert self.spec.deserialize("", "tags") == []

    def test_roundtrip(self):
        values = ["item1", "item2", "item3"]
        serialized = self.spec.serialize(values, "tags")
        deserialized = self.spec.deserialize(serialized, "tags")
        assert deserialized == values


class TestListSectionSpec:
    def setup_method(self):
        self.spec = ListSectionSpec()

    def test_serialize_creates_bullet_list(self):
        result = self.spec.serialize(["a", "b", "c"], "items")
        assert "<!-- section: items -->" in result
        assert "- a" in result
        assert "- b" in result
        assert "- c" in result

    def test_serialize_empty_list(self):
        result = self.spec.serialize([], "items")
        assert "<!-- section: items -->" in result

    def test_deserialize_parses_bullet_list(self):
        content = "- first\n- second\n- third"
        assert self.spec.deserialize(content, "items") == ["first", "second", "third"]

    def test_deserialize_handles_whitespace(self):
        content = "  - first  \n- second\n  - third  "
        assert self.spec.deserialize(content, "items") == ["first", "second", "third"]

    def test_deserialize_empty_string(self):
        assert self.spec.deserialize("", "items") == []

    def test_deserialize_skips_blank_lines(self):
        content = "- first\n\n- second\n\n- third"
        assert self.spec.deserialize(content, "items") == ["first", "second", "third"]

    def test_roundtrip(self):
        values = ["item1", "item2", "item3"]
        serialized = self.spec.serialize(values, "items")
        # Extract the content after the section marker
        content = serialized.split("\n\n", 1)[1]
        deserialized = self.spec.deserialize(content, "items")
        assert deserialized == values

    def test_in_body_is_true(self):
        assert self.spec.in_body is True
