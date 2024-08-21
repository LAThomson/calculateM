import pickle
import argparse
import os

import torch

from tqdm import tqdm

from utils import parseEnv, gridArrayToTensor, gridTensorToArray

CHANNELS = 7

def parseGridToTensor(filePath: str) -> torch.Tensor:
    """Reads a gridworld from a text file and returns its state tensor.

    Converts from a text representation of a gridworld to a tensor representation
    with dimensions [numChannels, height, width]; the width and height are determined
    by the contents of the file, while the channels represent encodings of
    different objects in the gridworld (must be decided beforehand - see
    `utils.gridArrayToTensor` method for explanation of state tensor).

    Parameters
    ----------
    filePath : str
        The path to the gridworld to be parsed.

    Returns
    -------
    gridTensor : torch.Tensor
        The state tensor that represents the input gridworld.
    """

    # read the file and parse the gridworld
    epLen, grid = parseEnv(filePath)

    # convert the grid from list form to tensor form
    gridTensor = gridArrayToTensor(grid, epLen)

    return gridTensor

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--data", type=str, default="./generatedEnvironments/seed_10_EASY_x1000")

if __name__ == "__main__":

    args = parser.parse_args()

    datasetPath = args.data

    dataPath = os.path.join(datasetPath, "grids")

    dataset = []
    for fileName in tqdm(os.listdir(dataPath), "Converting to Tensors"):
        gridTensor = parseGridToTensor(os.path.join(dataPath, fileName))
        dataset.append(gridTensor)
    
    outputPath = os.path.join(dataPath, "..", "dataset.pickle")
    with open(outputPath, "wb") as out:
        pickle.dump(dataset, out)
