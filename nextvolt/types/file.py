from __future__ import annotations

from typing import Literal, TypedDict, Union
from typing_extensions import NotRequired

__all__ = ("File",)

class SizedMetadata(TypedDict):
    type: Literal["Image", "Video"]
    height: int
    width: int

class SimpleMetadata(TypedDict):
    type: Literal["File", "Text", "Audio"]

FileMetadata = Union[SizedMetadata, SimpleMetadata]

class File(TypedDict):
    _id: str
    tag: str
    size: int
    filename: str
    metadata: FileMetadata
    content_type: str

class FileMetadataPayload(TypedDict):
    type: Literal["Video", "Image", "File", "Text", "Audio"]
    height: NotRequired[int]
    width: NotRequired[int]

class FilePayload(TypedDict):
    _id: str
    tag: str
    size: int
    filename: str
    metadata: FileMetadataPayload
    content_type: str
