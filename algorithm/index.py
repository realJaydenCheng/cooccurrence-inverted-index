from typing import Iterable, Optional

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


class InvertedIndex:
    def __init__(self, client: Elasticsearch):
        self.client = client
        self.index: Optional[str] = None
        self.property: Optional[str] = None

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
        if mappings is None:
            mappings = InvertedIndex._default_mapping
            self.client.create(
                index=name, mappings=mappings
            )
        self.index = name
        self.property = property_

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
        bulk(
            self.client,
            self._bulk_active(data)
        )
