from typing import Iterable, Optional

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from .utils import *


class InvertedIndex:
    def __init__(self, client: Elasticsearch):
        self.client = client
        self.index: str = DEFAULT_INDEX
        self.field: Optional[str] = None

    def __repr__(self) -> str:
        return f"Invert Index Instance {id(self):x} {self.client} {self.index}"

    def set_index(
            self,
            name: str = DEFAULT_INDEX,
            field: str = DEFAULT_FIELD,
            mappings=None,
    ):
        report = None
        if mappings is None:
            report = self.client.indices.create(
                index=name, mappings=DEFAULT_MAPPING
            )
        self.index = name
        self.field = field
        return report

    def _bulk_active(self, data: Iterable):
        for content in data:
            doc = {
                "_index": self.index,
                "_source": {
                    self.field: str(content)
                },
            }
            yield doc

    def index_data(
            self,
            data: Iterable[str],
    ):
        report = bulk(
            self.client,
            self._bulk_active(data),
            raise_on_error=False,
        )
        return report

    def delete_index_and_data(self):
        report = self.client.indices.delete(index=self.index)
        self.index = None
        self.client = None
        return report
