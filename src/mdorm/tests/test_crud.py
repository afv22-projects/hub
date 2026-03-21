import tempfile
from pathlib import Path
from typing import Annotated

import pytest

from src.mdorm import MarkdownModel, MDorm
from src.mdorm.fields import SectionSpec, StringSpec


class Note(MarkdownModel):
    tags: Annotated[str, StringSpec()]


class NoteWithSections(MarkdownModel):
    tags: Annotated[str, StringSpec()]
    notes: Annotated[str, SectionSpec()] = ""
    summary: Annotated[str, SectionSpec()] = ""


class TestCreate:
    def test_create_inserts_record(self):
        """Verify create() inserts a new record into the database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = MDorm(Path(tmpdir))

            note = Note(title="note1", content="Hello", tags="a,b")
            db.create(note)

            result = db.get(Note, "note1")
            assert result.title == "note1"
            assert result.content == "Hello"
            assert result.tags == "a,b"

    def test_create_duplicate_raises(self):
        """Verify create() raises an error for duplicate primary key."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = MDorm(Path(tmpdir))

            note = Note(title="note1", content="", tags="")
            db.create(note)

            with pytest.raises(Exception):
                db.create(note)


class TestUpdate:
    def test_update_modifies_record(self):
        """Verify update() modifies an existing record."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = MDorm(Path(tmpdir))

            note = Note(title="note1", content="Old", tags="")
            db.create(note)

            updated = Note(title="note1", content="New", tags="updated")
            db.update(updated)

            result = db.get(Note, "note1")
            assert result.content == "New"
            assert result.tags == "updated"

    def test_update_nonexistent_raises(self):
        """Verify update() raises an error if record doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = MDorm(Path(tmpdir))

            note = Note(title="missing", content="", tags="")
            with pytest.raises(KeyError):
                db.update(note)


class TestDelete:
    def test_delete_removes_record(self):
        """Verify delete() removes a record from the database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = MDorm(Path(tmpdir))

            note = Note(title="note1", content="", tags="")
            db.create(note)

            db.delete(Note, "note1")

            result = db.get_or_none(Note, "note1")
            assert result is None

    def test_delete_nonexistent_raises(self):
        """Verify delete() raises an error if record doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = MDorm(Path(tmpdir))

            with pytest.raises(FileNotFoundError):
                db.delete(Note, "missing")


class TestMarkdownFileSync:
    """Tests to verify that CRUD operations sync to markdown files."""

    def test_create_writes_md_file(self):
        """Verify create() writes a markdown file with frontmatter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            db = MDorm(tmppath)

            note = Note(
                title="note1",
                content="Hello world",
                tags="foo,bar",
            )
            db.create(note)

            md_file = tmppath / "Note" / "note1.md"
            assert md_file.exists()

            content = md_file.read_text()
            assert "Hello world" in content
            assert "tags: foo,bar" in content

    def test_update_modifies_md_file(self):
        """Verify update() modifies the markdown file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            db = MDorm(tmppath)

            note = Note(
                title="note1",
                content="Old content",
                tags="old",
            )
            db.create(note)

            updated = Note(
                title="note1",
                content="New content",
                tags="new",
            )
            db.update(updated)

            md_file = tmppath / "Note" / "note1.md"
            content = md_file.read_text()
            assert "New content" in content
            assert "tags: new" in content
            assert "Old" not in content

    def test_delete_removes_md_file(self):
        """Verify delete() removes the markdown file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            db = MDorm(tmppath)

            note = Note(title="note1", content="To be deleted", tags="")
            db.create(note)

            md_file = tmppath / "Note" / "note1.md"
            assert md_file.exists()

            db.delete(Note, "note1")
            assert not md_file.exists()

    def test_md_file_persists_after_db_reload(self):
        """Verify that md files created are loaded back into a fresh db."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            db = MDorm(tmppath)

            note = Note(
                title="persist",
                content="Persist me",
                tags="keep",
            )
            db.create(note)

            # Create a new db instance pointing to same directory
            db2 = MDorm(tmppath)
            result = db2.get(Note, "persist")

            assert result.content == "Persist me"
            assert result.tags == "keep"


class TestSectionsIntegration:
    """Tests for SectionSpec field functionality through the full CRUD stack."""

    def test_create_with_section_fields(self):
        """Verify create() stores section fields in both db and markdown file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            db = MDorm(tmppath)

            note = NoteWithSections(
                title="note1",
                content="Main body",
                notes="Detailed notes.",
                summary="A brief summary.",
                tags="test",
            )
            db.create(note)

            # Verify in database
            result = db.get(NoteWithSections, "note1")
            assert result.content == "Main body"
            assert result.notes == "Detailed notes."
            assert result.summary == "A brief summary."

            # Verify in markdown file
            md_file = tmppath / "NoteWithSections" / "note1.md"
            content = md_file.read_text()
            assert "<!-- section: notes -->" in content
            assert "Detailed notes." in content
            assert "<!-- section: summary -->" in content
            assert "A brief summary." in content

    def test_update_section_fields(self):
        """Verify update() modifies section fields in both db and file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            db = MDorm(tmppath)

            note = NoteWithSections(
                title="note1",
                content="Body",
                notes="Old notes.",
                tags="",
            )
            db.create(note)

            updated = NoteWithSections(
                title="note1",
                content="Body",
                notes="New notes.",
                summary="Added summary.",
                tags="",
            )
            db.update(updated)

            result = db.get(NoteWithSections, "note1")
            assert result.notes == "New notes."
            assert result.summary == "Added summary."

    def test_section_fields_persist_after_reload(self):
        """Verify section fields are loaded back from markdown files on db reload."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            db = MDorm(tmppath)

            note = NoteWithSections(
                title="persist",
                content="Body",
                notes="## Header\nPersistent notes.",
                tags="",
            )
            db.create(note)

            # Create fresh db instance
            db2 = MDorm(tmppath)
            result = db2.get(NoteWithSections, "persist")

            assert result.notes == "## Header\nPersistent notes."

    def test_section_fields_with_markdown_content(self):
        """Verify section fields can contain full markdown with headers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = MDorm(Path(tmpdir))

            note = NoteWithSections(
                title="note1",
                content="Intro paragraph.",
                notes="## First Header\nSome text.\n\n### Sub-header\nMore text.",
                tags="",
            )
            db.create(note)

            result = db.get(NoteWithSections, "note1")
            assert "## First Header" in result.notes
            assert "### Sub-header" in result.notes

    def test_empty_section_fields(self):
        """Verify model with empty section fields works correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = MDorm(Path(tmpdir))

            note = NoteWithSections(
                title="note1",
                content="Just body content",
                tags="",
                # notes and summary use default ""
            )
            db.create(note)

            result = db.get(NoteWithSections, "note1")
            assert result.content == "Just body content"
            assert result.notes == ""
            assert result.summary == ""

    def test_all_returns_section_fields(self):
        """Verify all() returns models with their section fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db = MDorm(Path(tmpdir))

            db.create(
                NoteWithSections(
                    title="note1",
                    content="Body 1",
                    notes="Notes 1",
                    tags="",
                )
            )
            db.create(
                NoteWithSections(
                    title="note2",
                    content="Body 2",
                    summary="Summary 2",
                    tags="",
                )
            )

            results = db.all(NoteWithSections)
            assert len(results) == 2

            note1 = next(n for n in results if n.title == "note1")
            note2 = next(n for n in results if n.title == "note2")

            assert note1.notes == "Notes 1"
            assert note2.summary == "Summary 2"

    def test_section_fields_excluded_from_frontmatter(self):
        """Verify section fields are not written to YAML frontmatter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            db = MDorm(tmppath)

            note = NoteWithSections(
                title="note1",
                content="Body",
                notes="My notes",
                summary="My summary",
                tags="tag1",
            )
            db.create(note)

            # Read raw file and verify frontmatter
            md_file = tmppath / "NoteWithSections" / "note1.md"
            raw_content = md_file.read_text()

            # SectionSpec fields should NOT be in frontmatter
            assert "notes: My notes" not in raw_content
            assert "summary: My summary" not in raw_content
            # Regular fields should be in frontmatter
            assert "tags: tag1" in raw_content
