import weakref


class Node(object):
    def __init__(self, name, data):
        self.edges = []
        self.outgoing_edges = []
        self.incoming_edges = []
        self._depends_on = set()
        self.name = name
        self.data = data

    def has_edge(self, other_edge):
        for edge in self.edges:
            if other_edge == edge:
                return True
        return False

    def has_incoming_edges(self):
        return any(edge.is_incoming_edge(self) for edge in self.edges)

    def has_outgoing_edges(self):
        return any(edge.is_outgoing_edge(self) for edge in self.edges)

    def add_dependency(self, node):
        self._depends_on.add(node)

    def get_dependencies(self):
        return self._depends_on

    def depends_on(self, node):
        return node in self._depends_on

    def is_dependency_for(self, node):
        return node.depends_on(self)

    def repath(self):
        # TODO Recache all incoming and outgoing references after an
        #      edge is removed
        pass

    def add_edge(self, edge):
        if self.has_edge(edge):
            raise Exception("An edge {} already exists!".format(edge))
        self.edges.append(edge)
        if edge.from_node == self:
            self.outgoing_edges.append(weakref.ref(edge))
        else:
            self.incoming_edges.append(weakref.ref(edge))

    def __str__(self):
        return self.name

    def __lt__(self, other):
        if self == other:
            return False
        return self.depends_on(other)

    def __gt__(self, other):
        if self == other:
            return False
        return self.is_dependency_for(other)


class Edge(object):
    def __init__(self, from_node, to_node):
        self.from_node = from_node
        self.to_node = to_node

    @property
    def start(self):
        return self.from_node

    @property
    def end(self):
        return self.to_node

    def connected_to_node(self, node):
        if self.from_node == node or self.to_node == node:
            return True
        return False

    def is_outgoing_edge(self, node):
        if not self.connected_to_node(node):
            raise Exception("This edge {} is not connected to this "
                            "node {}".format(self, node))
        if self.from_node == node:
            return True

    def is_incoming_edge(self, node):
        if not self.connected_to_node(node):
            raise Exception("This edge {} is not connected to this "
                            "node {}".format(self, node))
        if self.to_node == node:
            return True

    def __eq__(self, other):
        if self.from_node == other.from_node and self.to_node == other.to_node:
            return True
        if self.from_node == other.to_node and self.to_node == other.from_node:
            return True
        return False

    def __str__(self):
        return "Edge <From: {} To: {}>".format(self.start, self.end)


class DirectedGraph(object):
    def __init__(self):
        self.nodes = {}
        self.paths = []
        self._cache_dirty = True

    def add_node(self, node):
        if node.name in self.nodes:
            raise Exception("A node named '{}' already exists in this "
                            "graph".format(node.name))
        self.nodes[node.name] = node

    def add_edge(self, from_node_key, to_node_key):
        if from_node_key == to_node_key:
            raise Exception("No Nodes may have have self-referential cycles!")
        from_node = self.nodes[from_node_key]
        to_node = self.nodes[to_node_key]

        new_edge = Edge(from_node, to_node)
        from_node.add_edge(new_edge)
        to_node.add_edge(new_edge)

    def get_node(self, key):
        return self.nodes.get(key)

    def dump(self):
        self.find_paths()
        for key, node in self.nodes.items():
            print(node.name)
            print('-' * 80)
            print("Edges:")
            for edge_ref in node.outgoing_edges:
                edge = edge_ref()
                print("{} -> {}".format(node.name, edge.to_node.name))
            print('-' * 80)
            print("Depends on: {}".format(', '.join(
                  [str(x) for x in node._depends_on])))
            print()

    def find_paths(self):
        if not self._cache_dirty:
            return self.paths

        paths = []
        root_nodes = []
        for key, node in self.nodes.items():
            if node.has_incoming_edges():
                continue
            root_nodes.append(node)

        # Each node is the root of its own tree, DFS for each tree
        # in graph
        for node in root_nodes:
            node_stack = [(node, [])]
            current_path = None
            while len(node_stack) > 0:
                current_node, current_path = node_stack.pop()
                current_path.append(current_node)
                for prev_node in current_path:
                    if prev_node == current_node:
                        continue
                    prev_node.add_dependency(current_node)

                if len(current_node.outgoing_edges) == 0:
                    if current_path:
                        paths.append(current_path)
                    continue
                for edge_ref in current_node.outgoing_edges:
                    # You have to call a weakref to "dereference" it
                    edge = edge_ref()
                    if edge.to_node in current_path:
                        self.dump()
                        raise Exception("Cycle detected!")
                    node_stack.append((edge.to_node, current_path.copy()))

        self.paths = paths
        return self.paths

    def create_plan(self):
        # It's not strictly sufficient to sort these by
        # dependency ordering. You actually have to compare each node
        # to each node, i.e. do NOT switch this to sorted(...)
        # I entertained trying to merge the paths together, but I think
        # this is actually more efficient. You really only look at each
        # node once, whereas with the paths there's really nothing stopping
        # any given node from being in *every* valid path
        self.find_paths()
        nodes = list(self.nodes.values())
        nodes_to_insert = nodes.copy()
        index_of_node = -1
        for node in nodes_to_insert:
            highest_idx = 0
            for i in range(len(nodes)):
                if node == nodes[i]:
                    index_of_node = i
                if node < nodes[i]:
                    if i > highest_idx:
                        highest_idx = i

            if highest_idx + 1 > index_of_node:
                nodes.insert(highest_idx + 1, node)
                nodes.remove(node)
        return nodes



def example():
    graph = DirectedGraph()
    graph.add_node(Node('a', {}))
    graph.add_node(Node('b', {}))
    graph.add_node(Node('c', {}))
    graph.add_node(Node('d', {}))
    graph.add_node(Node('e', {}))
    graph.add_node(Node('f', {}))
    graph.add_node(Node('g', {}))
    graph.add_edge('a', 'b')
    graph.add_edge('a', 'd')
    graph.add_edge('b', 'd')
    graph.add_edge('c', 'a')
    graph.add_edge('f', 'g')
    graph.add_edge('f', 'a')
    graph.add_edge('f', 'b')
    graph.add_edge('g', 'd')
    graph.dump()
    print()
    print("Paths:")
    print('-' * 80)
    for path in graph.find_paths():
        print([x.name for x in path])
    plan = ", ".join([x.name for x in graph.create_plan()])
    print("Dependency ordering: {}".format(plan))
