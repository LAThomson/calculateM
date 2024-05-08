from classes import Object, AStarNode, DLSNode

import numpy as np

import re
import heapq
import queue
import itertools
import copy

MAXDIST = 10e9

def parseEnv(filepath: str) -> (int, list):
    """Parses the given environment text file.

    Parameters
    ----------
    filepath : str
        The filepath of the environment to be parsed.
    
    Returns
    -------
    epLen : int
        The standard duration of the environment episode if no delay buttons are pressed.
    grid : list
        A 2D array containing the grid information in the format [<col1>, <col2>, etc.]
        ('A' for agent location,
         'C<v>' for a coin of value <v>,
         'SD<t>' for a shutdown button of time <t>,
         '#' for a wall, and '.' for an empty tile).
    """

    # parse the information in the given filepath
    with open(filepath, "r") as file:
        
        # init vars for episode length and for grid
        epLen = None
        grid = []

        # read first line for episode length
        epLen = int(file.readline())

        # read remaining lines into grid format
        for line in file.readlines():
            grid.append(line.split())
        
        # get the transpose of the grid, so first index denotes column
        grid = np.array(grid).T.tolist()
        
        return (epLen, grid)

def findAll(target: str, grid: list) -> list:
    """Takes a grid and a target object and finds all locations where that object appears.

    Parameters
    ----------
    target : str
        The string identifier of the target object (e.g. 'A' for agent, 'SD' for shutdown delay button, etc.).
    grid : list
        The grid in which to search for the target object.
    
    Returns
    -------
    locsAndVals : list
        A list containing Object instances.
    """
    
    # initialise the list to contain the locations
    locsAndVals = []

    # iterate through the grid, checking each tile
    for x, col in enumerate(grid):
        for y, tile in enumerate(col):
            if re.match(f"^{target}", tile):
                value = re.sub(f"{target}", "", tile)
                if value == "":
                    value = 0
                else:
                    value = int(value)
                locsAndVals.append(Object(target, x, y, value))

    return locsAndVals

def getManhattanDist(start: (int, int), end: (int, int)) -> int:
    """Gets the Manhattan distance between two tiles in the grid.
    """

    return abs(end[0] - start[0]) + abs(end[1] - start[1])

def getFreeNeighbours(tile: (int, int), grid: list) -> list:
    """Gets all the free (not wall) neighbours of tile in grid.
    
    Parameters
    ----------
    tile : (int, int)
        The tile whose neighbours are being found.
    grid : list
        The grid being used as a reference for information about walls / size.
    
    Returns
    -------
    neighbours : list
        A list of neighbouring tiles that are free to move to.
    """

    # initialise list
    neighbours = []

    # iterate neighbours of tile
    for neighbour in [(tile[0], tile[1]-1), (tile[0]+1, tile[1]), (tile[0], tile[1]+1), (tile[0]-1, tile[1])]:
        # check if tile in grid is free
        try:
            isWall = grid[neighbour[0]][neighbour[1]]
        except IndexError:
            # if neighbour outside grid, ignore
            continue
        else:
            # only add to neighbours if isWall == 0
            if isWall == 0:
                neighbours.append(neighbour)
    
    return neighbours

def aStarSearch(start: (int, int), end: (int, int), binGrid: list, heuristicFn) -> (int, list):
    """Carries out the A* search algorithm on the given grid.

    Parameters
    ----------
    start : (int, int)
        Location of the search's start tile.
    end : (int, int)
        Location of the goal of the search.
    binGrid : list
        Binary grid (1s for walls, 0s otherwise) in which to carry out the search.
    heuristicFn : (int, int) -> (int, int) -> int
        The heuristic function with which to calculate h.
    
    Returns
    -------
    distance : int
        The distance (i.e. cost) of the shortest path found by the algorithm.
    path : list
        List of tile coordinates that make up the shortest path.
    """

    # first, initialise the neighbouring nodes priority queue to contain just the start
    pq = []
    heapq.heappush(pq, AStarNode(None, start, 0, heuristicFn(start, end)))

    # also intialise empty set for visited nodes (contains just coordinates)
    visited = set()

    # main search loop
    while pq:
        
        # pop top Node off of queue
        currentNode = heapq.heappop(pq)

        # add it to visited
        visited.add(currentNode.loc)

        # check if it's the goal
        if currentNode.loc == end:
            
            # if it's the goal, return the path up until now and the Node's path cost
            distance = currentNode.g
            path = []
            tracker = currentNode
            while tracker != None:
                path.insert(0, tracker.loc)
                tracker = tracker.parent
            
            return (distance, path)
        
        # if it isn't the goal, explore its neighbours
        else:
            neighbours = getFreeNeighbours(currentNode.loc, binGrid)
            for neighbour in neighbours:
                
                # skip if already visited
                if neighbour in visited:
                    continue
                
                # otherwise, add a new Node for the neighbour to the pq
                else:
                    parent = currentNode
                    loc = neighbour
                    g = parent.g + 1
                    h = heuristicFn(loc, end)
                    heapq.heappush(pq, AStarNode(parent, loc, g, h))

    # if code reaches this point, no path found, so raise error
    print(f"Warning: no path could be found between {start} and {end}.")
    print("Distance will be set to MAXDIST as precaution.")
    return (MAXDIST, [])

def getDist(start: (int, int), end: (int, int), grid: list) -> int:
    """Finds the length of the shortest path (found using A*) from start to end in the given grid.

    Parameters
    ----------
    start : (int, int)
        The grid coordinates of the start point.
    end : (int, int)
        The grid coordinates of the end point.
    grid : list
        The grid in which to calculate the distance.
    
    Returns
    -------
    distance : int
        The distance in steps from the start point to the end point, taking walls into account.
    """

    # first, convert the grid provided to a binary grid representing walls (1) and not walls (0)
    # note, we are treating any object (e.g. wall, SD button, coin) not at `start` or `end` as a wall
    #   - this ensures that the shortest path found doesn't go through any other objects that could
    #     change the trajectory length or number of coins collected.
    binGrid = [[(0 if (tile=="." or tile=="A") else 1) for tile in col] for col in grid]
    binGrid[start[0]][start[1]] = 0
    binGrid[end[0]][end[1]] = 0
    
    # now, take this binary grid and run A* search on it
    (distance, path) = aStarSearch(start, end, binGrid, getManhattanDist)

    return distance

def convertToGraph(grid: list) -> dict:
    """Converts a given grid the corresponding object graph, represented using an adjacency matrix.

    Takes a given gridworld environment and converts it into a graph in which vertices
    are non-obstacle object tiles (e.g. SD buttons and coins) and edge values represent
    the number of steps required to get from one object to the other without interacting
    with any other objects on the way (if this isn't possible, edge value = MAXDIST).

    Parameters
    ----------
    grid : list
        The grid to be converted.
    
    Returns
    -------
    adjMatrix : dict
        A nested dictionary representing all the edge costs between objects.
    """

    # first find all the relevant non-obstacle objects in the grid
    nonObstacles = [x for target in ["A", "C", "SD"] for x in findAll(target, grid)]

    # now initialise the adjacency matrix dictionary and populate it using getDist
    adjMatrix = {source: {target: 0 for target in nonObstacles} for source in nonObstacles}
    for i, source in enumerate(nonObstacles):
        for target in nonObstacles[(i+1):]:
            dist = getDist(source.loc(), target.loc(), grid)
            adjMatrix[source][target] = dist
            adjMatrix[target][source] = dist

    return adjMatrix

def omitFromGrid(grid: list, visited: frozenset) -> list:
    """Replaces instances of visited objects in the given grid with empty spaces.

    This simulates what the gridworld environment would look like after the agent
    has already interacted with some of the objects in the environment (e.g. after
    picking up a coin, that coin object is no longer there).

    Parameters
    ----------
    grid : list
        2D array encoding the initial grid environment (nothing visited).
    visited : frozenset
        A frozenset of objects that are to be erased from the initial grid.
    
    Returns
    -------
    alteredGrid : list
        2D array representing the environment after the objects have been removed.
    """

    # create a copy of the initial grid
    alteredGrid = copy.deepcopy(grid)

    # loop over the list of visited objects
    for obj in visited:
        # access the object's location in the grid and place an empty tile (".")
        alteredGrid[obj.x][obj.y] = "."

    return alteredGrid

def getMScores(grid: list, defaultLimit : int, quiet: bool = False) -> dict:
    """Finds all values of m for the given grid using a variant of depth-limited search.

    This form of depth-limited search is used to solve for the maximum number
    of coins that can be collected for each trajectory length in a particular grid.
    It treats the time until shutdown as the depth limit, not exploring any nodes
    which cost more than this limit. The limit can be extended by SD buttons.

    Parameters
    ----------
    grid : list
        A 2D array representing a gridworld environment.
    defaultLimit : int
        The default time until shutdown in the environment.
    quiet : bool, default = False
        Flag for whether or not to suppress informative console outputs.

    Returns
    -------
    mScores : dict
        A dictionary indexed by trajectory length containing the max score for that length
        and a path (list) of objects that gives you this max score.
    """

    # first, convert the grid into an initial graph where nothing has been explored
    initialGraph = convertToGraph(grid)

    # next, create a dictionary which keeps track of graphs for all configurations of visited objects
    nonObstacles = [x for target in ["A", "C", "SD"] for x in findAll(target, grid)]
    objectPowerset = [frozenset(x) for i in range(len(nonObstacles) + 1) for x in itertools.combinations(nonObstacles, i)]
    graphs = {s: None for s in objectPowerset}

    # and add the initialGraph to the entry for the empty set (i.e. nothing explored)
    graphs[frozenset()] = initialGraph

    # initialise the FIFO queue for nodes with just the start node
    q = queue.Queue()
    q.put(DLSNode(None, findAll("A", grid)[0], 0, defaultLimit, 0))

    # initialise a dictionary for the different possible trajectory lengths
    mScores = {}

    if not quiet:
        print("\n ----- SEARCH UPDATES -----\n")

    # repeat until the queue is empty
    while not q.empty():
        
        # pop top node off of queue
        currentNode = q.get()

        # compare this node against the current max for this trajectory length
        try:
            (maxScore, maxPath) = mScores[currentNode.getTrajLen()]
        except KeyError:
            # if no current max for this length exists, add to dict
            if not quiet:
                print(f"   *** NEW TRAJECTORY LENGTH FOUND [{currentNode.getTrajLen()}] with a score of {currentNode.score}")
                print(f"       Cost = {currentNode.cost}; Budget = {currentNode.budget}; Path = {currentNode.getPath()}")
                print()
            mScores[currentNode.getTrajLen()] = (currentNode.score, currentNode.getPath())
        else:
            # if max exists, replace node only if current node is better
            if currentNode.score > maxScore:
                if not quiet:
                    print(f"   (+) [{currentNode.getTrajLen()}] HAS A NEW MAX with a score of {currentNode.score} (prev. {maxScore})")
                    print(f"       Cost = {currentNode.cost}; Budget = {currentNode.budget}; Path = {currentNode.getPath()}")
                    print()
                mScores[currentNode.getTrajLen()] = (currentNode.score, currentNode.getPath())

        # explore neighbouring nodes, excluding paths to already-visited objects
        # and any paths that exceed the budget with the next step cost
        for neighbour in list(initialGraph.keys()):
            
            # access, or create if doesn't exist, the altered graph for this node's visited objects
            alteredGraph = graphs[currentNode.getVisited()]
            if alteredGraph == None:
                alteredGraph = convertToGraph(omitFromGrid(grid, currentNode.getVisited()))
                graphs[currentNode.getVisited()] = alteredGraph

            # ignore neighbour if already visited on this path, or
            # if the step to neighbour can't be made in the remaining time before shutdown
            if (neighbour in currentNode.getPath()) or (alteredGraph[currentNode.obj][neighbour] > currentNode.budget):
                continue
            else:
                # otherwise, add a new node to the queue
                parent = currentNode
                obj = neighbour
                cost = currentNode.cost + alteredGraph[currentNode.obj][neighbour]
                budget = currentNode.budget - alteredGraph[currentNode.obj][neighbour]
                if neighbour.identifier == "SD":
                    budget += neighbour.value
                score = currentNode.score
                if neighbour.identifier == "C":
                    score += neighbour.value
                q.put(DLSNode(parent, obj, cost, budget, score))
    
    # once the queue is empty, all possible paths that could be taken before
    # shutdown have been explored, so just return the mScores dictionary
    return mScores
