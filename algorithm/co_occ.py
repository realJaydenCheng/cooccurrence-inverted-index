import abc
import functools
from collections import defaultdict
from copy import deepcopy
from itertools import combinations
from typing import Sequence

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
        self.nodes: dict[str, int] = defaultdict(int)
        self.edges: dict[frozenset[str], int] = defaultdict(int)

    @abc.abstractmethod
    def get_network(self, query: dict) -> tuple[dict[str, int], dict[frozenset[str], int]]: ...


class IterConstructor(NetworkConstructor):
    @functools.wraps(NetworkConstructor.__init__)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_network(self, query: dict) -> tuple[dict[str, int], dict[frozenset[str], int]]:
        # 在es中搜索符合条件的文档，并得到每个文档的内容
        response = self.client.search(
            index=self.index, query=query, size=10000
        )
        contents = [doc['_source'][self.field] for doc in response['hits']['hits']]

        # 遍历文档构建共现矩阵
        co_occurrence_matrix: dict[frozenset[str], int] = defaultdict(int)
        for content in contents:
            # 使用 _analyze API 对文档进行分词
            analyze_response = self.client.indices.analyze(
                text=content, analyzer=DEFAULT_ANALYZER,
            )
            tokens = [token_info['token'] for token_info in analyze_response['tokens']]
            for token1, token2 in combinations(tokens, 2):
                if token1 == token2:
                    continue
                # 逐个计数
                co_occurrence_matrix[frozenset((token1, token2))] += 1
                self.nodes[token1] += 1
                self.nodes[token2] += 1

        # 构建返回值
        for token_pair, count in co_occurrence_matrix.items():
            edge = frozenset(token_pair)
            self.edges[edge] = count

        return self.nodes, self.edges


def _extract_word_buckets(
        es_response: dict,
        agg: str = DEFAULT_AGG_NAME,
) -> list[dict]:
    return es_response['aggregations'][agg]['buckets']


def _construct_query(
        base_query: dict,
        target_words: Sequence[str],
        field: str = DEFAULT_FIELD,
) -> dict:
    query = deepcopy(base_query)
    query['bool'] = query.get('bool', {})

    wildcard_queries = [
        {
            'wildcard': {
                field: f"*{word}*"
            }
        } for word in target_words
    ]
    try:
        query['bool']['must'].extend(wildcard_queries)
    except KeyError:
        query['bool']['must'] = wildcard_queries

    return query


class RecursionConstructor(NetworkConstructor):
    @functools.wraps(NetworkConstructor.__init__)
    def __init__(self,
                 agg: dict = DEFAULT_AGG,
                 agg_name: str = DEFAULT_AGG_NAME,
                 depth: int = DEFAULT_DEPTH,
                 *args, **kwargs
                 ):
        super().__init__(*args, **kwargs)
        self.agg = agg
        self.agg_name = agg_name
        super().__init__(*args, **kwargs)
        self.depth = depth

    def _get_words(
            self,
            base_query: dict,
            target_words: Sequence[str],
            depth: int = DEFAULT_DEPTH,
            agg: dict = DEFAULT_AGG,
            agg_name: str = DEFAULT_AGG_NAME,
    ) -> None:
        """递归构造词共现网络，结果存储至self.nodes与self.edges中。

        """
        # 结束递归
        if depth <= 0:
            return

        # 查询共现词
        query = _construct_query(base_query, target_words)
        response = self.client.search(
            index=self.index, query=query, aggs=agg, size=0
        )

        # 递归构造共现网络
        for bucket in _extract_word_buckets(response, agg=agg_name):
            self._get_words(base_query, [bucket['key']], depth-1, agg, agg_name)
            self.nodes[bucket["key"]] += bucket["doc_count"]
            edge = frozenset((bucket["key"], " ".join(target_words)))
            if bucket["doc_count"] > self.edges[edge]:
                self.edges[edge] = bucket["doc_count"]

    def get_network(self, query: dict) -> tuple[dict[str, int], dict[frozenset[str], int]]:
        response = self.client.search(
            index=self.index, query=query, aggs=self.agg, size=0
        )
        top_words = [
            bucket["key"] for bucket
            in _extract_word_buckets(response)
        ]
        for word in top_words:
            self._get_words(query, [word], self.depth, self.agg, self.agg_name)
        return self.nodes, self.edges
