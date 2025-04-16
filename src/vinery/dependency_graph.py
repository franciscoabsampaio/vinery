from __future__ import annotations
from collections import deque
import matplotlib.pyplot as plt
import networkx as nx
import os
from vinery.io import DIRECTORIES, echo, read_deps_conf


class DependencyGraph(nx.DiGraph):
    def __add__(self, other: DependencyGraph) -> DependencyGraph:
        """
        Adds nodes and edges from another graph.
        """
        new = self.copy()
        new.add_nodes_from(other.nodes)
        new.add_edges_from(other.edges)
        return new
    

    def __sub__(self, other: DependencyGraph) -> DependencyGraph:
        """
        Subtracts nodes and edges from the current graph.
        """
        new = self.copy()
        new.remove_nodes_from(other.nodes)
        new.remove_edges_from(other.edges)
        return new


    def from_library(self, path_to_library: str) -> DependencyGraph:
        """
        Scans all subfolders in the path_to_library directory and builds a dependency graph.
        Folders MUST contain a file named '_deps.conf' with a list of dependencies.
        """
        for (root, _, files) in os.walk(path_to_library, topdown=True):
            if "_deps.conf" in files:
                plan_name = root.split(path_to_library)[-1].strip("/")
                self.add_node(plan_name)

                for dependency in read_deps_conf(root):
                    self.add_edge(dependency, plan_name)
        
        return self


    def from_node(self, node: str) -> DependencyGraph:
        """
        Function to create a new DependencyGraph object from a single node.
        """
        self.add_node(node)
        return self


    def from_nodes(self, nodes: set[str]) -> DependencyGraph:
        """
        Function to create a new DependencyGraph object from a single node.
        """
        self.add_nodes_from(nodes)
        return self
    
    
    def wsubgraph(self, nodes: set[str]) -> DependencyGraph:
        """
        'w' stands for writable.
        Whereas subgraph() creates a Graph view,
        wsubgraph() creates a completely new DependencyGraph object.
        """
        wsubgraph = DependencyGraph().from_nodes(nodes)

        for u, v in self.edges:
            if u in nodes and v in nodes:
                wsubgraph.add_edge(u, v)

        return wsubgraph
    

    def find_all_dependencies(self, node: str, visited: set = None) -> set:
        """
        Utility function to find all dependencies (parent nodes) recursively
        """

        if visited is None:
            visited = set()

        # Add the current node to the visited set
        visited.add(node)

        # Recursively find all dependencies (parents) of the current node
        for parent in self.predecessors(node):
            if parent not in visited:
                visited = self.find_all_dependencies(parent, visited)

        return visited
    

    def from_nodes_wsubgraph(self, nodes: tuple[str]) -> DependencyGraph:
        """
        Function to create a new DependencyGraph object from a subgraph,
        given any number of nodes - which the wsubgraph must include.
        """
        # Get all dependencies (parents) for each node
        from itertools import chain
        dependencies = set(
            chain.from_iterable(
                self.find_all_dependencies(node) for node in nodes
            )
        )

        return self.wsubgraph(dependencies)


    def save_to_png(self, target_directory: str = DIRECTORIES["output"]) -> None:
        plt.figure(figsize=(8, 5))
        nx.draw(self, with_labels=True, node_color="lightblue", edge_color="gray", arrowsize=20)
        plt.savefig(os.path.join(target_directory, "graph.png"), dpi=300)

        echo(f"graph.png was saved to {target_directory}.", log_level="INFO")


    def sorted_list(self, reverse: bool = False) -> list[str]:
        """
        Returns a list of nodes, sorted using Kahn's algorithm.
        By default, the list is sorted from the root to the leaves, by level.
        If reverse=True, the list is sorted from the leaves to the root.
        """
        # Compute in/out-degree (number of incoming/outgoing edges for each node)
        # to start processing root nodes (no incoming) or leaf nodes (no outgoing)
        # depending on traversal direction
        degree = {
            node: (
                self.in_degree(node)
                if not reverse
                else self.out_degree(node)
            ) for node in self.nodes
        }

        # Start with root nodes (in-degree 0) if forward, or leaf nodes (out-degree 0) if reversed
        queue = deque([node for node in self.nodes if degree[node] == 0])

        sorted_nodes = []
        while queue:
            node = queue.popleft()  # Process the next available node
            sorted_nodes.append(node)

            # Get the node's relative
            relatives = self.predecessors(node) if reverse else self.successors(node)

            for relative in relatives:
                degree[relative] -= 1  # Reduce the in-degree (or out-degree for reverse)
                
                # If the node's relative now has no remaining dependencies,
                # add the relative to the queue
                if degree[relative] == 0:
                    queue.append(relative)

        return sorted_nodes
