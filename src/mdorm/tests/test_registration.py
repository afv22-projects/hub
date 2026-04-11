import tempfile
from pathlib import Path
from typing import Annotated

from mdorm import LocalFiles, MarkdownModel, MDorm
from mdorm.fields import IntegerSpec, SectionSpec


class SampleModel(MarkdownModel):
    count: Annotated[int, IntegerSpec()]


class SampleModelWithSections(MarkdownModel):
    count: Annotated[int, IntegerSpec()]
    notes: Annotated[str, SectionSpec()] = ""


class TestRegistration:
    def test_model_registered(self):
        """Verify SampleModel is in the registry."""
        assert "SampleModel" in MarkdownModel._registry
        assert MarkdownModel._registry["SampleModel"] is SampleModel

    def test_init_creates_table(self):
        """Verify MDorm() creates a table with correct columns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            files = LocalFiles(Path(tmpdir))
            db = MDorm(files)

            assert "SampleModel" in db.cache.metadata.tables
            table = db.cache.metadata.tables["SampleModel"]

            column_names = {col.name for col in table.columns}
            assert column_names == {
                "title",
                "content",
                "mtime",
                "count",
            }

    def test_init_creates_table_with_section_fields(self):
        """Verify MDorm() creates columns for SectionSpec fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            files = LocalFiles(Path(tmpdir))
            db = MDorm(files)

            assert "SampleModelWithSections" in db.cache.metadata.tables
            table = db.cache.metadata.tables["SampleModelWithSections"]

            column_names = {col.name for col in table.columns}
            assert column_names == {
                "title",
                "content",
                "mtime",
                "count",
                "notes",
            }

    def test_table_is_usable(self):
        """Verify the created table can be used for insert/select."""
        with tempfile.TemporaryDirectory() as tmpdir:
            files = LocalFiles(Path(tmpdir))
            db = MDorm(files)

            obj = SampleModel(
                title="test",
                content="",
                mtime=0.0,
                count=42,
            )
            db.create(SampleModel, obj)

            result = db.get_or_none(SampleModel, "test")
            assert result is not None
            assert result.title == "test"
            assert result.count == 42

    def test_loads_markdown_files(self):
        """Verify MDorm() loads markdown files from disk into the database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_dir = Path(tmpdir) / "SampleModel"
            model_dir.mkdir()

            md_file = model_dir / "item1.md"
            md_file.write_text(
                """---
count: 99
---
# Content here
"""
            )

            files = LocalFiles(Path(tmpdir))
            db = MDorm(files)
            result = db.get_or_none(SampleModel, "item1")
            assert result is not None
            assert result.title == "item1"
            assert result.count == 99
            assert result.content == "# Content here"

    def test_loads_markdown_files_with_sections(self):
        """Verify MDorm() loads section fields from markdown files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_dir = Path(tmpdir) / "SampleModelWithSections"
            model_dir.mkdir()

            md_file = model_dir / "item1.md"
            md_file.write_text(
                """---
count: 99
---
# Content here

<!-- section: notes -->
These are my notes.
"""
            )

            files = LocalFiles(Path(tmpdir))
            db = MDorm(files)
            result = db.get_or_none(SampleModelWithSections, "item1")
            assert result is not None
            assert result.title == "item1"
            assert result.count == 99
            assert result.content == "# Content here"
            assert result.notes == "These are my notes."
