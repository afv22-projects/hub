from typing import TypeVar, TYPE_CHECKING

from pydantic import BaseModel, create_model

from .markdown_model import MarkdownModel

T = TypeVar("T", bound=MarkdownModel)


class RequestBase(BaseModel):
    """Base class for all Request types."""

    title: str


if TYPE_CHECKING:

    class Request(RequestBase):
        title: str
        content: str = ""

else:

    class Request:
        _registry: dict[str, type[RequestBase]] = {}

        def __class_getitem__(cls, model_cls: type[T]) -> type[RequestBase]:
            name = model_cls.__name__
            if name in cls._registry:
                return cls._registry[name]

            fields = {}
            for f_name, f_info in model_cls.model_fields.items():
                if f_name == "mtime":
                    continue
                fields[f_name] = (f_info.annotation, f_info.default)

            request_model = create_model(
                f"{name}Request", __base__=RequestBase, **fields
            )
            cls._registry[name] = request_model
            return request_model
