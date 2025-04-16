import os
import pytest
from vinery.dependency_graph import DependencyGraph
import networkx as nx


@pytest.fixture
def graph(tmp_path):
    # Create a fake folder structure with dependency config files
    (tmp_path / "A").mkdir()
    (tmp_path / "B").mkdir()
    (tmp_path / "C").mkdir()
    (tmp_path / "C/D").mkdir()  # Nested folder

    # Create dependency files
    (tmp_path / "A" / "_deps.conf").write_text("")        # A has no dependencies
    (tmp_path / "B" / "_deps.conf").write_text("#commentlikeandsubscribe\nA\n")     # B depends on A
    (tmp_path / "C" / "_deps.conf").write_text("/A\nB/\n//")  # C depends on A and B
    (tmp_path / "C/D" / "_deps.conf").write_text("A\nC\n")  # D depends on A and C (and, indirectly, B)

    # Return the DependencyGraph instance
    return DependencyGraph().from_library(str(tmp_path))


def test_graph_addition(graph):
    g1 = DependencyGraph() + graph

    # g1 should now contain graph's nodes and edges
    assert set(g1.nodes) == set(graph.nodes)
    assert set(g1.edges) == set(graph.edges)


def test_graph_subtraction(graph):
    # Subtracting some nodes from the graph should remove them and the respective edges
    g1 = graph - DependencyGraph().from_nodes({"A", "B"})
    # g1 should not contain A and B
    assert set(g1.nodes) == {"C", "C/D"}
    assert set(g1.edges) == {("C", "C/D")}

    # Two equal graphs should result in an empty graph
    g2 = graph.copy() - graph
    # g2 should be empty
    assert set(g2.nodes) == set()
    assert set(g2.edges) == set()

    # Subtracting to an empty graph should have no effect
    g3 = DependencyGraph() - graph
    # g should be empty
    assert set(g3.nodes) == set()
    assert set(g3.edges) == set()

    # Subtracting an empty graph should have no effect
    g4 = graph - DependencyGraph()
    # g4 should be the same as graph
    assert set(g4.nodes) == set(graph.nodes)
    assert set(g4.edges) == set(graph.edges)


def test_dependency_graph_ignores_line_comments(graph):
    # Assertions
    assert isinstance(graph, DependencyGraph)
    assert "#commentlikeandsubscribe" not in set(graph.nodes)


def test_dependency_graph_ignores_trailing_and_leading_slashes(graph):
    # Assertions
    assert isinstance(graph, DependencyGraph)
    assert "/A" not in set(graph.nodes)
    assert "B/" not in set(graph.nodes)
    assert "//" not in set(graph.nodes)
    assert "A" in set(graph.nodes)
    assert "B" in set(graph.nodes)


def test_dependency_graph_mirrors_the_file_structure(graph, tmp_path):
    """
    Test that build_dependency_graph correctly constructs the dependency graph.
    """
    # Assertions
    assert isinstance(graph, DependencyGraph)
    assert set(graph.nodes) == {"A", "B", "C", "C/D"}  # All nodes exist
    # Also, a node's name consists of the relative path from the tmp_path
    assert set(graph.edges) == {
        ("A", "B"),
        ("A", "C"),
        ("A", "C/D"),
        ("B", "C"),
        ("C", "C/D")
    }  # Correct dependencies


def test_save_graph_png_file_exists(graph, tmp_path):
    graph.save_to_png(target_directory=str(tmp_path))
    assert os.path.isfile(os.path.join(str(tmp_path), "graph.png"))


def test_find_all_dependencies(graph):
    # Test when starting from 'A'
    dependencies_a = graph.find_all_dependencies('A')
    assert dependencies_a == {'A'}  # A has no dependencies, just itself

    # Test when starting from 'B'
    dependencies_b = graph.find_all_dependencies('B')
    assert dependencies_b == {'A', 'B'}  # B depends on A only

    # Test when starting from 'C'
    dependencies_c = graph.find_all_dependencies('C')
    assert dependencies_c == {'A', 'B', 'C'}  # C depends on A and B

    # Test when starting from 'C/D'
    dependencies_d = graph.find_all_dependencies('C/D')
    assert dependencies_d == {'A', 'B', 'C', 'C/D'}  # D depends on all nodes, even B (indirectly)


def test_wsubgraph(graph):
    """Test that wsubgraph creates a correct writable subgraph."""
    subset_of_nodes = {"A", "B", "C"}  

    # Generate the writable subgraph
    subgraph = graph.wsubgraph(subset_of_nodes)

    # Check that only the selected nodes are present
    assert set(subgraph.nodes) == subset_of_nodes, \
        f"Expected nodes {subset_of_nodes}, but got {set(subgraph.nodes)}"

    # Check that edges are correctly retained (only within selected nodes)
    expected_edges = [(u, v) for u, v in graph.edges if u in subset_of_nodes and v in subset_of_nodes]
    assert set(subgraph.edges) == set(expected_edges), \
        f"Expected edges {expected_edges}, but got {set(subgraph.edges)}"

    # Ensure that the returned subgraph is a completely new instance, not a view
    assert subgraph is not graph, "wsubgraph() should return a new instance, not a view"

    # Ensure modifications to the subgraph do not affect the original graph
    subgraph.add_node("X")
    assert "X" not in graph.nodes, "Modifying the subgraph should not affect the original graph"


def test_from_nodes_wsubgraph(graph):
    """
    Test the from_nodes_wsubgraph function.
    Works with
    """

    # Test for 'A', which should only return node A (no dependencies)
    new_graph_a = graph.from_nodes_wsubgraph(['A'])
    assert sorted(new_graph_a.nodes) == ['A']
    assert list(new_graph_a.edges) == []  # No edges in the subgraph for A
    
    # Test for 'B', which should return a subgraph with nodes A, and B
    new_graph_b = graph.from_nodes_wsubgraph({'B'})
    assert sorted(new_graph_b.nodes) == sorted(['A', 'B'])
    assert ('A', 'B') in new_graph_b.edges  # Edge from A to B should be present

    # Test for ('C', 'A'), which should return a subgraph with nodes A, B, and C
    new_graph_c = graph.from_nodes_wsubgraph(('C', 'A'))
    assert sorted(new_graph_c.nodes) == sorted(['A', 'B', 'C'])
    assert ('A', 'B') in new_graph_c.edges  # Edge from A to C should be present
    assert ('A', 'C') in new_graph_c.edges  # Edge from A to C should be present
    assert ('B', 'C') in new_graph_c.edges  # Edge from A to C should be present

    # Test for 'D', which should return all nodes
    new_graph_d = graph.from_nodes_wsubgraph(['C/D'])
    assert sorted(graph.nodes) == sorted(new_graph_d.nodes)
    assert sorted(graph.edges) == sorted(new_graph_d.edges)


def test_sorting(graph):
    """Test normal topological sorting (root to leaves)."""
    result = graph.sorted_list()
    assert all(result.index(u) < result.index(v) for u, v in graph.edges), \
        f"Result {result} is not a valid topological order."


def test_sorting_reversed(graph):
    """Test reverse topological sorting (leaves to root)."""
    result = graph.sorted_list(reverse=True)
    assert all(result.index(u) > result.index(v) for u, v in graph.edges), \
        f"Result {result} is not a valid topological order"
