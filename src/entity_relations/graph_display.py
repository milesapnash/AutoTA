def print_graph(entities, relations):
    # Imported here as plotting is optional and only needed for display
    import networkx as nx
    from matplotlib import pyplot as plt

    entity_colors = {
        'class': 'skyblue',
        'abstractClass': 'lightgreen',
        'interface': 'lightcoral',
        'constructor': 'lightyellow',
        'method': 'lightpink',
        'abstractMethod': 'lightgray',
        'field': 'lightblue'
    }
    graph = nx.DiGraph()

    # Add nodes to the graph
    for entity in entities:
        graph.add_node(str(entity), entity_type=entity.type)

    # Add edges to the graph
    for relation in relations:
        graph.add_edge(str(relation.entity_from), str(relation.entity_to),
                       label=relation.relation_type)

    # Use the spring layout to position nodes
    pos = nx.spring_layout(graph, k=1, iterations=100)

    plt.figure(figsize=(12, 8))

    for node in graph.nodes:
        if 'entity_type' not in graph.nodes[node]:
            print(node)

    # Draw the nodes and edges
    node_colors = [entity_colors[graph.nodes[node]['entity_type']] for node in
                   graph.nodes]
    nx.draw(graph, pos, with_labels=True, node_size=3000,
            node_color=node_colors,
            font_size=10, font_weight="bold", arrows=True)

    # Draw the edge labels
    edge_labels = nx.get_edge_attributes(graph, 'label')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels,
                                 font_color='red', font_size=8, label_pos=0.5,
                                 rotate=False)

    # Adjust positions to avoid overlap with edge labels
    for (node, (x, y)) in pos.items():
        dx = 0.02  # Offset for x
        dy = 0.02  # Offset for y
        pos[node] = (x + dx, y + dy)

    plt.title("Entity Relation Graph")
    plt.show()
