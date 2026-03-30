from typing import TypeVar, TYPE_CHECKING

from pydantic import BaseModel, computed_field, create_model

from .markdown_model import MarkdownModel

T = TypeVar("T", bound=MarkdownModel)


class ResponseBase(BaseModel):
    """Base class for all Response types."""

    @computed_field
    @property
    def _type(self) -> str:
        """Return the name of the model class."""
        return self.__class__.__name__.removesuffix("Response")


if TYPE_CHECKING:

    class Response(ResponseBase):
        title: str
        content: str = ""

else:

    class Response:
        _registry: dict[str, type[ResponseBase]] = {}

        def __class_getitem__(cls, model_cls: type[T]) -> type[ResponseBase]:
            name = model_cls.__name__
            if name in cls._registry:
                return cls._registry[name]

            fields = {}
            for f_name, f_info in model_cls.model_fields.items():
                if f_name == "mtime":
                    continue
                fields[f_name] = (f_info.annotation, ...)

            response_model = create_model(
                f"{name}Response", __base__=ResponseBase, **fields
            )
            cls._registry[name] = response_model
            return response_model
