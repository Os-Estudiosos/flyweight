"""Armazenamento compartilhado das bibliotecas JS/CSS dos relatórios (Flyweight).

Antes, cada relatório HTML carregava a sua própria cópia do Plotly (~4,8 MB) e do
CSS. Agora cada biblioteca é enviada UMA vez para um storage (S3, GCS, Azure Blob,
pasta servida pelo Nginx...) e os relatórios só guardam a URL dela.

  Flyweight (estado intrínseco) -> arquivo da biblioteca no storage, imutável
  Referência ao flyweight       -> URL usada no <script src> / <link href>
  Fábrica                       -> SharedAssetStore.url_for()
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, Protocol

# Um ano + "immutable": o navegador nem revalida, porque o arquivo de uma URL nunca muda.
IMMUTABLE_CACHE = "public, max-age=31536000, immutable"


@dataclass(frozen=True)
class Asset:
    """Biblioteca estática usada por todos os relatórios (estado intrínseco)."""

    name: str
    version: str
    content: bytes = field(repr=False)
    content_type: str = "text/javascript"

    @cached_property
    def key(self) -> str:
        """Caminho no storage com o hash do conteúdo.

        Se o conteúdo mudar, a chave (e a URL) muda: o arquivo publicado nunca é
        sobrescrito. É isso que garante a imutabilidade do flyweight.
        """
        digest = hashlib.sha256(self.content).hexdigest()[:12]
        ext = "css" if self.content_type == "text/css" else "js"
        return f"libs/{self.name}-{self.version}.{digest}.{ext}"


class Storage(Protocol):
    def exists(self, key: str) -> bool: ...
    def put(self, key: str, data: bytes, content_type: str, cache_control: str) -> None: ...
    def public_url(self, key: str) -> str: ...


class LocalStorage:
    """Pasta local servida como arquivos estáticos (desenvolvimento e demo)."""

    def __init__(self, root: Path, base_url: str) -> None:
        self.root = Path(root)
        self.base_url = base_url.rstrip("/")

    def exists(self, key: str) -> bool:
        return (self.root / key).is_file()

    def put(self, key: str, data: bytes, content_type: str, cache_control: str) -> None:
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def public_url(self, key: str) -> str:
        return f"{self.base_url}/{key}"


class S3Storage:
    """Bucket S3 (ou compatível) servido por uma CDN. Requer boto3."""

    def __init__(self, bucket: str, base_url: str, client: Any = None) -> None:
        if client is None:
            import boto3

            client = boto3.client("s3")
        self._s3 = client
        self.bucket = bucket
        self.base_url = base_url.rstrip("/")

    def exists(self, key: str) -> bool:
        from botocore.exceptions import ClientError

        try:
            self._s3.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as exc:
            if exc.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound"):
                return False
            raise

    def put(self, key: str, data: bytes, content_type: str, cache_control: str) -> None:
        self._s3.put_object(
            Bucket=self.bucket, Key=key, Body=data, ContentType=content_type, CacheControl=cache_control
        )

    def public_url(self, key: str) -> str:
        return f"{self.base_url}/{key}"


class SharedAssetStore:
    """Fábrica de flyweights: devolve a URL da cópia compartilhada de um asset,
    enviando-o para o storage somente se ele ainda não existir lá."""

    def __init__(self, storage: Storage) -> None:
        self._storage = storage
        self._urls: dict[str, str] = {}  # pool em memória: chave no storage -> URL pública
        self.uploads = 0
        self.reused = 0

    def url_for(self, asset: Asset) -> str:
        url = self._urls.get(asset.key)
        if url is not None:
            self.reused += 1
            return url
        if not self._storage.exists(asset.key):
            self._storage.put(asset.key, asset.content, asset.content_type, IMMUTABLE_CACHE)
            self.uploads += 1
        url = self._urls[asset.key] = self._storage.public_url(asset.key)
        return url
