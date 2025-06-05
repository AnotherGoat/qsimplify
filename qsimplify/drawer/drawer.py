from io import BytesIO

import graphviz
from graphviz import Digraph
from matplotlib import pyplot
from qiskit import QuantumCircuit

from qsimplify.model import EdgeName, GateName, GraphEdge, GraphNode, QuantumGraph
from qsimplify.utils import setup_logger

_RED = "#EF9A9A"
_DARK_RED = "#B71C1C"
_GREEN = "#A5D6A7"
_DARK_GREEN = "#1B5E20"
_BLUE = "#90CAF9"
_DARK_BLUE = "#0D47A1"
_ORANGE = "#FFCC80"
_PURPLE = "#CE93D8"
_GRAY = "#EEEEEE"
_DARK_GRAY = "#424242"


class Drawer:
    """Class capable of drawing quantum graphs and circuits."""

    def __init__(self, view: bool = False) -> None:
        """Create a new drawer."""
        self._logger = setup_logger("Drawer")
        self.view = view

    def save_circuit_png(self, circuit: QuantumCircuit, file_name: str) -> None:
        """Save a Qiskit circuit to a png file."""
        self._logger.info("Saving circuit to file %s.png", file_name)

        figure = circuit.draw("mpl")
        figure.savefig(f"{file_name}.png")

    @staticmethod
    def save_circuit_to_buffer(circuit: QuantumCircuit) -> BytesIO:
        """Create a buffer with a Qiskit circuit image."""
        figure = circuit.draw(output="mpl")
        buffer = BytesIO()
        figure.savefig(buffer, format="png", bbox_inches="tight")
        pyplot.close(figure)
        buffer.seek(0)
        return buffer

    def save_graph_png(self, graph: QuantumGraph, file_name: str) -> None:
        """Save a quantum graph to a png file."""
        self._logger.info("Saving graph to file %s.png", file_name)
        self._save_graph(graph, file_name, "png", dpi=str(150))

    def save_graph_svg(self, graph: QuantumGraph, file_name: str) -> None:
        """Save a quantum graph to a svg file."""
        self._logger.info("Saving graph to file %s.svg", file_name)
        self._save_graph(graph, file_name, "svg")

    def save_graph_to_buffer(self, graph: QuantumGraph, extension: str, **kwargs: str) -> BytesIO:
        """Create a buffer with a quantum graph image."""
        image = graphviz.Digraph(format=extension)
        image.attr(scale=str(2.5), nodesep=str(0.75), splines="ortho", **kwargs)

        self._draw_nodes(graph, image)
        self._draw_edges(graph, image)

        data = image.pipe(engine="neato")
        buffer = BytesIO(data)
        buffer.seek(0)
        return buffer

    def _save_graph(
        self, graph: QuantumGraph, file_name: str, extension: str, **kwargs: str
    ) -> None:
        image = graphviz.Digraph(format=extension)
        image.attr(scale=str(2.5), nodesep=str(0.75), splines="ortho", **kwargs)

        self._draw_nodes(graph, image)
        self._draw_edges(graph, image)

        image.render(
            f"{file_name}.gv",
            outfile=f"{file_name}.{extension}",
            engine="neato",
            view=self.view,
        )

    def _draw_nodes(self, graph: QuantumGraph, image: Digraph) -> None:
        for node in graph:
            x, y = self._find_draw_position(graph, node)

            settings = {
                "label": self._find_node_label(node),
                "fillcolor": self._find_node_color(node),
                "style": "filled",
                "shape": "circle",
                "width": str(1.5),
                "pos": f"{x},{y}!",
            }

            image.node(str(node.position), **settings)

    @staticmethod
    def _find_draw_position(graph: QuantumGraph, node: GraphNode) -> tuple[int, int]:
        return node.position.column, graph.height - node.position.row - 1

    @staticmethod
    def _find_node_label(node: GraphNode) -> str:
        match node.name:
            case GateName.RX | GateName.RY | GateName.RZ:
                top_label = f"{node.name.name}({node.angle:.3f})"
            case GateName.MEASURE:
                top_label = f"M({node.bit})"
            case _:
                top_label = f"{node.name.name}"

        return f"{top_label}\n{node.position}"

    @staticmethod
    def _find_node_color(node: GraphNode) -> str:
        match node.name:
            case GateName.ID:
                return "white"
            case GateName.H | GateName.CH:
                return _RED
            case GateName.X | GateName.RX | GateName.SX | GateName.CX | GateName.CCX:
                return _BLUE
            case GateName.Y | GateName.RY | GateName.SY | GateName.CY:
                return _ORANGE
            case (
                GateName.Z
                | GateName.P
                | GateName.RZ
                | GateName.S
                | GateName.SDG
                | GateName.T
                | GateName.TDG
                | GateName.CZ
                | GateName.CP
                | GateName.CCZ
            ):
                return _GREEN
            case GateName.SWAP | GateName.CSWAP:
                return _PURPLE
            case _:
                return _GRAY

    def _draw_edges(self, graph: QuantumGraph, image: Digraph) -> None:
        for edge in graph.iter_edges():
            if edge.start.name != GateName.CZ and edge.name == EdgeName.WORKS_WITH:
                continue

            settings = {
                "taillabel": edge.name.value.replace("_", " "),
                "fontcolor": self._find_edge_color(edge),
                "labeldistance": str(2.0),
                "style": "dashed",
                "color": self._find_edge_color(edge),
            }

            image.edge(str(edge.start.position), str(edge.end.position), **settings)

    @staticmethod
    def _find_edge_color(edge: GraphEdge) -> str:
        match edge.name:
            case EdgeName.LEFT | EdgeName.RIGHT:
                return _DARK_GRAY
            case EdgeName.SWAPS_WITH:
                return _DARK_RED
            case EdgeName.TARGETS | EdgeName.CONTROLLED_BY:
                return _DARK_BLUE
            case EdgeName.WORKS_WITH:
                return _DARK_GREEN

        return _DARK_GRAY
