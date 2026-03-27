from typing import TypeVar, TYPE_CHECKING

from pydantic import BaseModel, create_model

from .markdown_model import MarkdownModel

T = TypeVar("T", bound=MarkdownModel)


class PatchBase(BaseModel):
    """Base class for all Patch types."""

    pass


if TYPE_CHECKING:

    class Patch(PatchBase):
        title: str
        content: str = ""

else:

    class Patch:
        _registry: dict[str, type[PatchBase]] = {}

        def __class_getitem__(cls, model_cls: type[T]) -> type[PatchBase]:
            name = model_cls.__name__
            if name in cls._registry:
                return cls._registry[name]

            fields = {}
            for f_name, f_info in model_cls.model_fields.items():
                if f_name == "mtime":
                    continue
                annotation = (
                    f_info.annotation if f_info.annotation is not None else type(None)
                )
                fields[f_name] = (annotation | None, None)

            patch_model = create_model(f"{name}Patch", __base__=PatchBase, **fields)
            cls._registry[name] = patch_model
            return patch_model
