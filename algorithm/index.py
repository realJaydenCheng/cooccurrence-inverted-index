from typing import Iterable, Optional

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from .utils import *


class InvertedIndex:
    """基于Elasticsearch的倒排索引

    Attributes
    ----------
    client: Elasticsearch
        Elasticsearch客户端实例。
    index: str
        在Elasticsearch中具体的索引名称。
    field: str
        在索引中用于分析的字段名称。

    Methods
    -------
    set_index(name: str = DEFAULT_INDEX, field: str = DEFAULT_FIELD, mappings=None):
        设置类的属性。
    index_data(data: Iterable[str]):
        将数据填充到类属性中。
    delete_index_and_data():
        删除类属性中的数据。
    """
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
        return report
