from typing import TYPE_CHECKING, ClassVar, TypeVar

from pydantic import BaseModel, ConfigDict, create_model

from .fields import FieldSpec, get_field_spec


class MarkdownModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    content: str = ""
    mtime: float = 0.0  # Initialized as stale to force a fetch

    # Registry for discovering inheritor classes on startup
    _registry: ClassVar[dict[str, type["MarkdownModel"]]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if getattr(cls, "__abstract__", False):
            return
        cls._registry[cls.__name__] = cls

    @classmethod
    def get_field_specs(cls) -> dict[str, FieldSpec]:
        """Get all Field instances for this model's fields."""
        result = {}
        for name, info in cls.model_fields.items():
            if name in ("title", "content", "mtime"):
                continue
            spec = get_field_spec(info.metadata)
            if spec:
                result[name] = spec
        return result

    @classmethod
    def section_fields(cls) -> set[str]:
        """Get names of fields stored in the markdown body."""
        return {name for name, spec in cls.get_field_specs().items() if spec.in_body}

    @classmethod
    def frontmatter_fields(cls) -> set[str]:
        """Get names of fields stored in frontmatter."""
        return {
            name for name, spec in cls.get_field_specs().items() if not spec.in_body
        }

    @classmethod
    def relation_fields(cls) -> dict[str, str]:
        """Get relation fields with their target models."""
        return {
            name: spec.target_model
            for name, spec in cls.get_field_specs().items()
            if spec.target_model is not None
        }


T = TypeVar("T", bound=MarkdownModel)


if TYPE_CHECKING:

    class Patch(BaseModel): ...

    class Response(BaseModel): ...

    class Request(BaseModel): ...

else:

    class Patch:
        _registry: dict[str, type[BaseModel]] = {}

        def __class_getitem__(cls, model_cls: type[T]) -> type[BaseModel]:
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

            patch_model = create_model(f"{name}Patch", **fields)
            cls._registry[name] = patch_model
            return patch_model

    class Response:
        _registry: dict[str, type[BaseModel]] = {}

        def __class_getitem__(cls, model_cls: type[T]) -> type[BaseModel]:
            name = model_cls.__name__
            if name in cls._registry:
                return cls._registry[name]

            fields = {}
            for f_name, f_info in model_cls.model_fields.items():
                if f_name == "mtime":
                    continue
                fields[f_name] = (f_info.annotation, f_info.default)

            response_model = create_model(f"{name}Response", **fields)
            cls._registry[name] = response_model
            return response_model

    class Request:
        _registry: dict[str, type[BaseModel]] = {}

        def __class_getitem__(cls, model_cls: type[T]) -> type[BaseModel]:
            name = model_cls.__name__
            if name in cls._registry:
                return cls._registry[name]

            fields = {}
            for f_name, f_info in model_cls.model_fields.items():
                if f_name == "mtime":
                    continue
                fields[f_name] = (f_info.annotation, f_info.default)

            request_model = create_model(f"{name}Request", **fields)
            cls._registry[name] = request_model
            return request_model
