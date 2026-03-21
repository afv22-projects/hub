import tempfile
from pathlib import Path
from typing import Annotated

import pytest

from src.mdorm import MarkdownModel
from src.mdorm.fields import BooleanSpec, RelationToOne, SectionSpec
from src.mdorm.file_manager import FileManager


class Article(MarkdownModel):
    draft: Annotated[bool, BooleanSpec()]


class ArticleWithSections(MarkdownModel):
    draft: Annotated[bool, BooleanSpec()]
    notes: Annotated[str, SectionSpec()] = ""
    summary: Annotated[str, SectionSpec()] = ""


class Author(MarkdownModel):
    bio: Annotated[str, SectionSpec()] = ""


class Recipe(MarkdownModel):
    author: Annotated[str, RelationToOne("Author")]


class TestParseContent:
    """Tests for the _parse_content static method."""

    def test_parse_empty_content(self):
        """Verify empty string returns empty content."""
        result = FileManager._parse_content("")
        assert result == {"content": ""}

    def test_parse_body_only(self):
        """Verify content without sections goes to content."""
        result = FileManager._parse_content("Just some text.")
        assert result == {"content": "Just some text."}

    def test_parse_single_section(self):
        """Verify single section is parsed correctly."""
        content = "<!-- section: notes -->\nSome notes here."
        result = FileManager._parse_content(content)
        assert result["content"] == ""
        assert result["notes"] == "Some notes here."

    def test_parse_multiple_sections(self):
        """Verify multiple sections are parsed correctly."""
        content = """<!-- section: summary -->
First section.

<!-- section: notes -->
Second section."""
        result = FileManager._parse_content(content)
        assert result["content"] == ""
        assert result["summary"] == "First section."
        assert result["notes"] == "Second section."

    def test_parse_body_and_sections(self):
        """Verify preamble content goes to content with sections after."""
        content = """Preamble text.

<!-- section: notes -->
SectionSpec content."""
        result = FileManager._parse_content(content)
        assert result["content"] == "Preamble text."
        assert result["notes"] == "SectionSpec content."

    def test_parse_preserves_markdown_in_sections(self):
        """Verify markdown headers inside sections are preserved."""
        content = """<!-- section: notes -->
## A Header
Some **bold** text.

### Another header
More content."""
        result = FileManager._parse_content(content)
        assert "## A Header" in result["notes"]
        assert "### Another header" in result["notes"]
        assert "**bold**" in result["notes"]

    def test_parse_strips_whitespace(self):
        """Verify leading/trailing whitespace is stripped from sections."""
        content = """<!-- section: notes -->

  Content with whitespace

"""
        result = FileManager._parse_content(content)
        assert result["notes"] == "Content with whitespace"


class TestDumpContent:
    """Tests for the _dump_content static method."""

    def test_dump_body_only(self):
        """Verify dumping model with only content (no section fields)."""
        article = Article(
            title="test",
            content="Hello world",
            draft=False,
        )
        result = FileManager._dump_content(article)
        assert result == "Hello world"

    def test_dump_with_sections(self):
        """Verify dumping model with section fields includes markers."""
        article = ArticleWithSections(
            title="test",
            content="Preamble",
            draft=False,
            notes="Some notes.",
        )
        result = FileManager._dump_content(article)
        assert "Preamble" in result
        assert "<!-- section: notes -->" in result
        assert "Some notes." in result

    def test_dump_multiple_sections(self):
        """Verify dumping multiple section fields preserves all."""
        article = ArticleWithSections(
            title="test",
            content="",
            draft=False,
            summary="A summary.",
            notes="Some notes.",
        )
        result = FileManager._dump_content(article)
        assert "<!-- section: summary -->" in result
        assert "A summary." in result
        assert "<!-- section: notes -->" in result
        assert "Some notes." in result


class TestSectionsRoundTrip:
    """Tests for reading and writing sections through FileManager."""

    def test_read_file_with_sections(self):
        """Verify reading a file with section markers parses them into fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_dir = Path(tmpdir) / "ArticleWithSections"
            model_dir.mkdir()

            md_file = model_dir / "post.md"
            md_file.write_text(
                """---
draft: true
---
Introduction here.

<!-- section: summary -->
This is the summary.

<!-- section: notes -->
## Important
Some notes.
"""
            )

            fm = FileManager(Path(tmpdir))
            result = fm.read(ArticleWithSections, "post")

            assert result.content == "Introduction here."
            assert result.summary == "This is the summary."
            assert "## Important" in result.notes
            assert "Some notes." in result.notes

    def test_write_file_with_sections(self):
        """Verify writing a model with section fields creates proper markers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fm = FileManager(Path(tmpdir))

            article = ArticleWithSections(
                title="new",
                content="Main content",
                notes="My notes here.",
                draft=False,
            )
            fm.write(article)

            # Read back and verify
            result = fm.read(ArticleWithSections, "new")
            assert result.content == "Main content"
            assert result.notes == "My notes here."

    def test_sections_roundtrip(self):
        """Verify section fields survive a write then read cycle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fm = FileManager(Path(tmpdir))

            original = ArticleWithSections(
                title="roundtrip",
                content="Body text",
                summary="Brief summary.",
                notes="## Header\nDetailed notes.",
                draft=True,
            )
            fm.write(original)
            result = fm.read(ArticleWithSections, "roundtrip")

            assert result.content == original.content
            assert result.summary == original.summary
            assert result.notes == original.notes
            assert result.title == original.title
            assert result.draft == original.draft

    def test_read_all_with_sections(self):
        """Verify read_all correctly parses section fields from multiple files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_dir = Path(tmpdir) / "ArticleWithSections"
            model_dir.mkdir()

            (model_dir / "first").write_text(
                """---
draft: false
---
<!-- section: notes -->
First notes
"""
            )
            (model_dir / "second").write_text(
                """---
draft: true
---
Body content

<!-- section: summary -->
Second summary
"""
            )

            fm = FileManager(Path(tmpdir))
            results = fm.read_all(ArticleWithSections)

            first = next(r for r in results if r.title == "first")
            second = next(r for r in results if r.title == "second")

            assert first.notes == "First notes"
            assert first.content == ""
            assert second.summary == "Second summary"
            assert second.content == "Body content"

    def test_section_default_value(self):
        """Verify section fields use default when not in markdown."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_dir = Path(tmpdir) / "ArticleWithSections"
            model_dir.mkdir()

            md_file = model_dir / "post.md"
            md_file.write_text(
                """---
draft: false
---
Just body content.
"""
            )

            fm = FileManager(Path(tmpdir))
            result = fm.read(ArticleWithSections, "post")

            assert result.content == "Just body content."
            assert result.notes == ""  # Default value
            assert result.summary == ""  # Default value


class TestRead:
    def test_read_loads_file(self):
        """Verify read() loads a markdown file and returns the model."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_dir = Path(tmpdir) / "Article"
            model_dir.mkdir()

            md_file = model_dir / "post.md"
            md_file.write_text(
                """---
draft: true
---
This is the body.
"""
            )

            fm = FileManager(Path(tmpdir))
            result = fm.read(Article, "post")

            assert result.title == "post"
            assert result.draft is True
            assert result.content == "This is the body."

    def test_read_nonexistent_raises(self):
        """Verify read() raises FileNotFoundError for missing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fm = FileManager(Path(tmpdir))

            with pytest.raises(FileNotFoundError):
                fm.read(Article, "missing")


class TestReadAll:
    def test_read_all_loads_all_files(self):
        """Verify read_all() loads all markdown files for a model."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_dir = Path(tmpdir) / "Article"
            model_dir.mkdir()

            (model_dir / "first.md").write_text(
                """---
draft: false
---
Content 1
"""
            )
            (model_dir / "second.md").write_text(
                """---
draft: true
---
Content 2
"""
            )

            fm = FileManager(Path(tmpdir))
            results = fm.read_all(Article)

            assert len(results) == 2
            titles = {r.title for r in results}
            assert titles == {"first", "second"}

    def test_read_all_empty_directory(self):
        """Verify read_all() returns empty list when no files exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fm = FileManager(Path(tmpdir))
            results = fm.read_all(Article)
            assert results == []


class TestWrite:
    def test_write_creates_file(self):
        """Verify write() creates a new markdown file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fm = FileManager(Path(tmpdir))

            article = Article(title="new", content="Body text", draft=False)
            fm.write(article)

            file_path = Path(tmpdir) / "Article" / "new.md"
            assert file_path.exists()

            result = fm.read(Article, "new")
            assert result.title == "new"
            assert result.draft is False
            assert result.content == "Body text"

    def test_write_overwrites_existing(self):
        """Verify write() overwrites an existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_dir = Path(tmpdir) / "Article"
            model_dir.mkdir()

            (model_dir / "existing").write_text(
                """---
draft: true
---
Old content
"""
            )

            fm = FileManager(Path(tmpdir))
            updated = Article(
                title="existing",
                content="New content",
                draft=False,
            )
            fm.write(updated)

            result = fm.read(Article, "existing")
            assert result.title == "existing"
            assert result.draft is False
            assert result.content == "New content"

    def test_write_excludes_section_fields_from_frontmatter(self):
        """Verify section fields are not written to YAML frontmatter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fm = FileManager(Path(tmpdir))

            article = ArticleWithSections(
                title="new",
                content="Body",
                draft=False,
                notes="My notes",
                summary="My summary",
            )
            fm.write(article)

            # Read raw file and verify frontmatter doesn't have section fields
            file_path = Path(tmpdir) / "ArticleWithSections" / "new.md"
            raw_content = file_path.read_text()

            # SectionSpec fields should be in body, not frontmatter
            assert "notes: My notes" not in raw_content
            assert "summary: My summary" not in raw_content
            assert "<!-- section: notes -->" in raw_content
            assert "<!-- section: summary -->" in raw_content


class TestDelete:
    def test_delete_removes_file(self):
        """Verify delete() removes the markdown file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_dir = Path(tmpdir) / "Article"
            model_dir.mkdir()

            file_path = model_dir / "to_delete.md"
            file_path.write_text(
                """---
draft: false
---
"""
            )

            fm = FileManager(Path(tmpdir))
            fm.delete(Article, "to_delete")

            assert not file_path.exists()

    def test_delete_nonexistent_raises(self):
        """Verify delete() raises FileNotFoundError for missing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fm = FileManager(Path(tmpdir))

            with pytest.raises(FileNotFoundError):
                fm.delete(Article, "missing")


class TestRelationToOne:
    """Tests for RelationToOne field parsing and serialization."""

    def test_read_parses_wiki_link(self):
        """Verify read() parses wiki link syntax and extracts the title."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_dir = Path(tmpdir) / "Recipe"
            model_dir.mkdir()

            md_file = model_dir / "pasta.md"
            md_file.write_text(
                """---
author: "[[Author/John Smith]]"
---
A delicious pasta recipe.
"""
            )

            fm = FileManager(Path(tmpdir))
            result = fm.read(Recipe, "pasta")

            assert result.author == "John Smith"

    def test_read_validates_model_type(self):
        """Verify read() raises ValueError when model type doesn't match."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_dir = Path(tmpdir) / "Recipe"
            model_dir.mkdir()

            md_file = model_dir / "pasta.md"
            md_file.write_text(
                """---
author: "[[WrongModel/John Smith]]"
---
Content.
"""
            )

            fm = FileManager(Path(tmpdir))
            with pytest.raises(ValueError) as exc_info:
                fm.read(Recipe, "pasta")

            assert "Expected [[Author/...]]" in str(exc_info.value)
            assert "found [[WrongModel/...]]" in str(exc_info.value)

    def test_read_all_parses_wiki_links(self):
        """Verify read_all() parses wiki links in all files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_dir = Path(tmpdir) / "Recipe"
            model_dir.mkdir()

            (model_dir / "pasta.md").write_text(
                """---
author: "[[Author/John Smith]]"
---
Pasta recipe.
"""
            )
            (model_dir / "soup.md").write_text(
                """---
author: "[[Author/Jane Doe]]"
---
Soup recipe.
"""
            )

            fm = FileManager(Path(tmpdir))
            results = fm.read_all(Recipe)

            authors = {r.title: r.author for r in results}
            assert authors["pasta"] == "John Smith"
            assert authors["soup"] == "Jane Doe"

    def test_relation_field_missing_in_file(self):
        """Verify read() handles missing relation field gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            model_dir = Path(tmpdir) / "Recipe"
            model_dir.mkdir()

            md_file = model_dir / "pasta.md"
            md_file.write_text(
                """---
---
No author specified.
"""
            )

            fm = FileManager(Path(tmpdir))
            # This should raise a validation error from Pydantic
            # since author is required (no default)
            with pytest.raises(Exception):
                fm.read(Recipe, "pasta")

    def test_write_serializes_wiki_link(self):
        """Verify write() converts title to wiki link format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fm = FileManager(Path(tmpdir))

            recipe = Recipe(
                title="pasta",
                content="A delicious pasta recipe.",
                author="John Smith",
            )
            fm.write(recipe)

            # Read raw file and verify wiki link format
            md_file = Path(tmpdir) / "Recipe" / "pasta.md"
            raw_content = md_file.read_text()
            assert "[[Author/John Smith]]" in raw_content

    def test_write_then_read_roundtrip(self):
        """Verify write then read preserves the relation field."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fm = FileManager(Path(tmpdir))

            recipe = Recipe(
                title="soup",
                content="A warm soup recipe.",
                author="Jane Doe",
            )
            fm.write(recipe)

            result = fm.read(Recipe, "soup")
            assert result.author == "Jane Doe"
            assert result.content == "A warm soup recipe."

    def test_write_overwrites_relation_field(self):
        """Verify write() updates relation field in existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fm = FileManager(Path(tmpdir))

            # Create initial recipe
            recipe = Recipe(
                title="pasta",
                content="Pasta recipe.",
                author="John Smith",
            )
            fm.write(recipe)

            # Update with different author
            updated = Recipe(
                title="pasta",
                content="Pasta recipe.",
                author="Jane Doe",
            )
            fm.write(updated)

            # Verify update
            result = fm.read(Recipe, "pasta")
            assert result.author == "Jane Doe"

            # Verify raw file
            md_file = Path(tmpdir) / "Recipe" / "pasta.md"
            raw_content = md_file.read_text()
            assert "[[Author/Jane Doe]]" in raw_content
            assert "John Smith" not in raw_content
