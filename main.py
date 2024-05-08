from calculateM import calculateM

GRIDPATH = "./exampleEnvironments/7x7env1.txt"

print()
mScores = calculateM(GRIDPATH, quiet=False)
print(f" ----- RESULTS: -----\n")
print(f"   Number of different trajectory lengths: {len(mScores)}")
for trajLength, (m, path) in mScores.items():
    print(f"    > m{trajLength} = {m}")
print()

# for 7x7 grid, mScores should look like:
#  Number of different trajectory lengths: 4
#   > m5 = 3
#   > m8 = 4
#   > m9 = 5
#   > m12 = 5
