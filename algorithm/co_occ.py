import abc
import functools
from collections import defaultdict
from itertools import combinations

from elasticsearch import Elasticsearch

from .utils import *


class NetworkConstructor(abc.ABC):
    def __init__(
            self,
            client: Elasticsearch,
            index: str = DEFAULT_INDEX,
            field: str = DEFAULT_FIELD
    ):
        self.client = client
        self.index = index
        self.field = field

    @abc.abstractmethod
    def get_network(self, query: dict) -> tuple[dict[str, int], dict[frozenset[str], int]]: ...


class IterConstructor(NetworkConstructor):
    @functools.wraps(NetworkConstructor.__init__)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @functools.wraps(NetworkConstructor.get_network)
    def get_network(self, query: dict) -> tuple[dict[str, int], dict[frozenset[str], int]]:
        nodes: dict[str, int] = defaultdict(int)
        edges: dict[frozenset[str], int] = defaultdict(int)

        # 在es中搜索符合条件的文档，并得到每个文档的内容
        response = self.client.search(
            index=self.index, query=query, size=10000
        )
        titles = [doc['_source'][self.field] for doc in response['hits']['hits']]

        # 遍历文档构建共现矩阵
        co_occurrence_matrix: dict[frozenset[str], int] = defaultdict(int)
        for title in titles:
            # 使用 _analyze API 对标题进行分词
            analyze_response = self.client.indices.analyze(
                text=title, analyzer=DEFAULT_ANALYZER,
            )
            tokens = [token_info['token'] for token_info in analyze_response['tokens']]
            for token1, token2 in combinations(tokens, 2):
                if token1 == token2:
                    continue
                # 逐个计数
                co_occurrence_matrix[frozenset((token1, token2))] += 1
                nodes[token1] += 1
                nodes[token2] += 1

        # 构建返回值
        for token_pair, count in co_occurrence_matrix.items():
            edge = frozenset(token_pair)
            edges[edge] = count

        return nodes, edges
