from typing import TypeVar

import frontmatter
from dropbox import Dropbox
from dropbox.exceptions import ApiError
from dropbox.files import FileMetadata, ListFolderResult, WriteMode

from mdorm.models.markdown_model import MarkdownModel
from .generic import GenericFiles, File

T = TypeVar("T", bound=MarkdownModel)


class DropboxFiles(GenericFiles):

    def __init__(
        self,
        access_token: str,
        root_path: str = "/mdorm",
    ) -> None:
        self.dbx = Dropbox(access_token)
        self.root_path = root_path.rstrip("/")

    def _get_path(self, Model: type[T], title: str) -> str:
        return f"{self.root_path}/{Model.__name__}/{title}.md"

    def _get_dir_path(self, Model: type[T]) -> str:
        return f"{self.root_path}/{Model.__name__}"

    def exists(self, Model: type[T], title: str) -> bool:
        try:
            self.dbx.files_get_metadata(self._get_path(Model, title))
            return True
        except Exception:
            return False

    def read(self, Model: type[T], title: str) -> T:
        path = self._get_path(Model, title)
        metadata, response = self.dbx.files_download(path)  # type: ignore[misc]
        content = response.content.decode("utf-8")
        post = frontmatter.loads(content)
        mtime = metadata.server_modified.timestamp()
        return self._load_object(Model, post, title, mtime)

    def list_files(self, Model: type[T]) -> list[File]:
        dir_path = self._get_dir_path(Model)
        try:
            result: ListFolderResult = self.dbx.files_list_folder(dir_path)  # type: ignore[assignment]
        except ApiError:
            return []

        files: list[File] = []
        while True:
            for entry in result.entries:
                if isinstance(entry, FileMetadata) and entry.name.endswith(".md"):
                    title = entry.name[:-3]  # Remove .md extension
                    mtime = entry.server_modified.timestamp()
                    files.append(File(title=title, mtime=mtime))

            if not result.has_more:
                break
            result = self.dbx.files_list_folder_continue(result.cursor)  # type: ignore[assignment]

        return files

    def write(self, obj: MarkdownModel) -> float:
        path = self._get_path(obj.__class__, obj.title)
        post = self._dump_object(obj)
        content = frontmatter.dumps(post).encode("utf-8")
        metadata = self.dbx.files_upload(
            content,
            path,
            mode=WriteMode.overwrite,
        )
        if metadata is None:
            raise RuntimeError(f"Failed to upload file: {path}")
        return metadata.server_modified.timestamp()

    def delete(self, Model: type[MarkdownModel], title: str) -> None:
        path = self._get_path(Model, title)
        self.dbx.files_delete_v2(path)
