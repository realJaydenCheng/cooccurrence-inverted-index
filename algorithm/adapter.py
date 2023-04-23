import abc

import matplotlib.pyplot as plt
import networkx as nx

from .co_occ import CoNetwork


class _NetworkAdapter(abc.ABC):
    def __init__(self, network: CoNetwork):
        self._network = network

    @abc.abstractmethod  # property
    def nodes(self): ...

    @abc.abstractmethod  # property
    def edges(self): ...


class NetworkXAdapter(_NetworkAdapter):
    def __init__(
            self,
            network: CoNetwork,
            limit: int = 30,
            reverse: bool = True,
    ):
        super().__init__(network)
        self.limit = limit
        self.reverse = reverse
        self._sorted_edges = sorted(
            self._network.edges.items(),
            key=lambda x: x[-1],
            reverse=self.reverse
        )

    @property
    def nodes(self):
        _nodes = []
        for edge in self.edges:
            _nodes.append((edge[0], {"weight": self._network.nodes[edge[0]]}))
            _nodes.append((edge[1], {"weight": self._network.nodes[edge[1]]}))
        return _nodes

    @property
    def edges(self) -> list:
        return [(*k, {"weight": v})
                for k, v in self._sorted_edges
                ][:self.limit]


def nx_draw_network(
        graph: nx.Graph,
        pos: dict,
        ax: plt.Axes = None,
        node_size_min: int = 200,
        node_size_max: int = 800,
        node_color: str = "blue",
        node_alpha: float = 0.1,
        edge_width_min: int = 2,
        edge_width_max: int = 6,
        edge_alpha: float = 0.1,
        font_size: int = 9,
        font_color: str = "black",
        font_family: str = "sans-serif"
) -> plt.Axes:
    # 设置节点的大小，根据权重调整
    _max_node = max(
        graph.nodes.data("weight"),
        key=lambda x: x[-1]
    )[-1]
    node_sizes = [
        (node_size_max - node_size_min) *
        (attr['weight'] / _max_node) +
        node_size_min
        for _, attr in graph.nodes(data=True)
    ]

    # 设置边的宽度，根据权重调整
    _max_edge = max(
        graph.edges.data("weight"),
        key=lambda x: x[-1]
    )[-1]
    edge_widths = [
        (edge_width_max - edge_width_min) *
        (attr['weight'] / _max_edge) +
        edge_width_min
        for _, _, attr in graph.edges(data=True)
    ]

    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    nx.draw_networkx_nodes(
        graph, pos, node_size=node_sizes,
        node_color=node_color, alpha=node_alpha, ax=ax
    )
    nx.draw_networkx_edges(
        graph, pos, width=edge_widths,
        alpha=edge_alpha, ax=ax
    )
    nx.draw_networkx_labels(
        graph, pos, font_size=font_size, font_color=font_color,
        font_family=font_family, ax=ax
    )

    return ax
