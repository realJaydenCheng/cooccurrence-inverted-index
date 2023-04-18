from typing import Iterable, Optional

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


class InvertedIndex:
    def __init__(self, client: Elasticsearch):
        self.client = client
        self.index: str = "co_occ_test"
        self.property: Optional[str] = None

    def __repr__(self) -> str:
        return f"Invert Index Instance {id(self):x} {self.client} {self.index}"

    _default_mapping = {
        "properties": {
            "content": {
                "type": "text",
                "analyzer": "ik_smart",
            }
        }
    }

    def set_index(
            self,
            name: str = "co_occ_test",
            property_: str = "content",
            mappings=None,
    ):
        report = None
        if mappings is None:
            mappings = InvertedIndex._default_mapping
            report = self.client.indices.create(
                index=name, mappings=mappings
            )
        self.index = name
        self.property = property_
        return report

    def _bulk_active(self, data: Iterable):
        for content in data:
            doc = {
                "_index": self.index,
                "_source": {
                    self.property: str(content)
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
            raise_on_error = False,
        )
        return report

    def delete_index_and_data(self):
        report = self.client.indices.delete(index=self.index)
        self.index = None
        self.client = None
        return report
