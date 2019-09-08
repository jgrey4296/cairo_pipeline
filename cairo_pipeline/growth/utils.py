
def get_node_neighbourhood(d, node, loc=None):
    assert(isinstance(node, Node))
    if loc is None:
        loc = node.loc
    bbox_raw = node.get_delta_bbox()
    bbox = np.array([loc - bbox_raw,
                     loc + bbox_raw])
    logging.debug("Neighbourhood of ({},{}) -> bbox {}".format(loc[0], loc[1], bbox))
    matches = d.qtree.intersect(bbox.flatten())
    assert(all([x in d.allNodes for x in matches]))
    match_nodes = [d.allNodes[x] for x in matches]
    assert(len(matches) == len(match_nodes))
    return match_nodes

def filter_frontier_to_boundary(d):
    """ verify the distances of the frontier to the centre """
    logging.debug("Checking {} frontiers are at boundary".format(len(d.frontier)))
    #distance check all nodes in the frontier
    assert(all([x in d.allNodes for x in d.frontier]))
    nodesFromIDs = [d.allNodes[x] for x in d.frontier]
    distances = [x.distance_to(constants.CENTRE) for x in nodesFromIDs]
    paired = zip(d.frontier, distances)
    logging.debug("Distances: {}".format(distances))
    #filter the frontier:
    d.frontier = deque([x for x, y in paired if y < constants.HYPHAE_CIRC])
    result = bool(d.frontier)
    logging.debug("Frontier: {}".format(result))
    return result

def backtrack_random(d):
    randNode = choice(list(d.allNodes.values()))
    if randNode.open() and random() < randNode.backtrack_likelihood:
        randNode.perpendicular = True
        d.frontier.append(randNode.id)

def backtrack_from_branch(d):
    """ occasionally backtrack from a branch point: """
    if bool(d.branchPoints):
        rndBranch = choice(d.branchPoints)
        rndBranchNode = d.allNodes[rndBranch]
    if random() >= rndBranchNode.backtrack_likelihood:
        return
    length_of_branch = rndBranchNode.distance
    if length_of_branch < 2:
        return
    branchPoint = randrange(1,length_of_branch)
    currentNodeID = rndBranch
    for x in range(branchPoint):
        currentNodeID = d.graph.predecessors(currentNodeID)[0]

    assert(currentNodeID in d.allNodes)
    potentialNode = d.allNodes[currentNodeID]
    if potentialNode.open() and len(d.frontier) < constants.MAX_FRONTIER_NODES:
        potentialNode.perpendicular = True
    d.frontier.append(currentNodeID)

def determine_new_point(d, node):
    """
    Given a node, calculate a next node location
    """
    assert(isinstance(node, Node))
    predecessorIDs = d.graph.predecessors(node.id)
    if node.perpendicular is True and len(predecessorIDs) > 0:
        #get the norm, rotate 90 degrees
        assert(all([x in d.allNodes for x in predecessorIDs]))
        predecessor = d.allNodes[predecessorIDs[0]]
        normalized = predecessor.get_normal(node)
        direction = choice([[[0, -1], [1, 0]], [[0, 1], [-1, 0]]])
        perpendicular = normalized.dot(direction)
        newPoint = node.loc + (perpendicular * (2*node.d))
    elif len(predecessorIDs) == 0:
        #no predecessor, pick a random direction
        logging.debug("No predecessor, picking random direction")
        #todo: rotate around the point
        newPoint = node.move()
    else:
        logging.debug("Extending vector")
        #create a vector out of the pair / Alt: move -> d(p, x) < d(n, x)
        assert(predecessorIDs[0] in d.allNodes)
        predecessor = d.allNodes[predecessorIDs[0]]
        normalized = predecessor.get_normal(node)
        newPoint = node.move(normalized)
        if random() < node.wiggle_chance:
            newPoint = utils.math.rotatePoint(newPoint, node.loc,
                                              radMin=-(node.wiggle_amnt + node.wiggle_variance),
                                              radMax=(node.wiggle_amnt + node.wiggle_variance))

    return newPoint

def maybe_branch(d, point, focusNode):
    """ Split branch based on split chance """
    assert(isinstance(focusNode, Node))
    if (not focusNode.perpendicular) and focusNode.able_to_branch() and random() < focusNode.split_chance:
        logging.debug("Branching")
        #branch
        s1 = utils.math.rotatePoint(point, focusNode.loc,
                                    radMin=-(focusNode.split_angle + focusNode.split_variance),
                                    radMax=-(focusNode.split_angle - focusNode.split_variance))
        s2 = utils.math.rotatePoint(point, focusNode.loc,
                                    radMin=focusNode.split_angle - focusNode.split_variance,
                                    radMax=focusNode.split_angle + focusNode.split_variance)
        #todo: figure out whats going on here
        if len(s1.shape) == 2:
            s1 = choice(s1)
        if len(s2.shape) == 2:
            s2 = choice(s2)
            newPositions = [s1, s2]
            decay = focusNode.size_decay
            distance_from_branch = 0
        elif focusNode.perpendicular:
            logging.debug("Perpendicular Branching")
            #go perpendicular, with a new branch
            newPositions = [point]
            decay = 0.0
            distance_from_branch = 0
        else:
            logging.debug("Extending")
            #extend the new branch
            newPositions = [point]
            decay = 0.0
            distance_from_branch = focusNode.distance + 1
        return (newPositions, decay, distance_from_branch)

def positions_collide(d, positions, focusNode):
    """
    See if the positions specified are too close to any existing nodes
    """
    assert(isinstance(positions, list))
    assert(isinstance(focusNode, Node))
    bbox_delta = focusNode.d + focusNode.delta
    for pos in positions:
        neighbours = [x for newPos in positions for x in d.get_node_neighbourhood(focusNode,
                                                                                     loc=pos)
                      if x.id is not focusNode.id]
        fNodeDist = focusNode.distance_to(pos)
        distances = [x.distance_to(pos) for x in neighbours]
        too_close = [x for x in distances if x < fNodeDist or x < bbox_delta]
        if bool(too_close):
            logging.debug("There are {} collision,  not adding a new node".format(len(neighbours)))
            focusNode.attempt()
            if focusNode.open() and len(d.frontier) < constants.MAX_FRONTIER_NODES:
                d.frontier.append(focusNode.id)
                return True

    distances_to_other_new_pos = [utils.math.get_distance(pos,x) for x in positions if all(x != pos)]
    if any([x < fNodeDist for x in distances_to_other_new_pos]):
        return True
    return False

def get_branch_point(d, nodeID):
    """ skip down the successor chain until finding a branch """
    currentID = nodeID
    successors = d.graph.successors(currentID)
    while len(successors) == 1:
        currentID = successors[0]
        successors = d.graph.successors(currentID)
    return currentID

def get_path(d, nodeID):
    """ get all nodes from the current to the next branch """
    path = []
    successors = d.graph.successors(nodeID)
    while len(successors) == 1:
        path.append(successors[0])
        successors = d.graph.successors(successors[0])
    return path

def grow_suitable_nodes(d, newPositions, decay, distance_from_branch, focusNode):
    """
    Create new nodes,  storing any branch points,  and linking the edge to its parent
    """
    newNodes = [d.create_node(x, focusNode.d - decay,
                                 distance=distance_from_branch, priorNode=focusNode) \
                for x in newPositions]
    #add the nodes to the graph:
    for x in newNodes:
        d.graph.add_edge(focusNode.id, x.id)
    #add branch points to the store:
    if len(newNodes) > 1:
        d.branchPoints.append(focusNode.id)

def grow(d, node=None):
    """ Grow a single node out """
    logging.debug("Growing")
    #pick a frontier node
    if isinstance(node, Node):
        focusNodeID = node.id
    elif node is not None:
        focusNodeID = node
    else:
        focusNodeID = d.frontier.popleft()
    assert(focusNodeID in d.allNodes)
    focusNode = d.allNodes[focusNodeID]
    success = False
    while not success and focusNode.open():
        newPoint = d.determine_new_point(focusNode)
        newPositions, decay, distance_from_branch = d.maybe_branch(newPoint, focusNode)
        if not d.positions_collide(newPositions, focusNode):
            d.grow_suitable_nodes(newPositions, decay, distance_from_branch, focusNode)
            focusNode.force_open()
            success = True
        else:
            focusNode.attempt()

def grow_frontier(d):
    """ Grow every node in the frontier in a single step  """
    current_frontier = d.frontier
    d.frontier = deque()
    for node in current_frontier:
        d.grow(node)
        for x in range(constants.backtrack_attempts):
            d.backtrack_from_branch()
            d.backtrack_random()

def inc_time_steps(d):
    d.time_steps.append(set())
