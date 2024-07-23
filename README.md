# calculateM

Small codebase that does the following:
1. reads in a text file that encodes a gridworld environment (containing an Agent, Coins, Walls, and Shutdown-Delay Buttons);
2. processes this gridworld into a graph where vertices correspond to non-obstacle objects (coins, SD buttons) and edge values correspond to the length the shortest direct path connecting two objects; and
3. runs a form of depth-limited search on variations of this graph, taking into account time until shutdown and already-visited objects, in order to get the maximum number of coins that can be collected conditional on each trajectory length.

This repo also contains additional code:
1. in `directM.py` for running the above process on a pre-parsed grid (taking episode length and grid array as input);
2. in `generateGrids.py` for randomly generating a number of gridworlds that fit adjustable specifications.
