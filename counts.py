import numpy as np

# Balanced Card Counting Systems: Hi-Lo, Hi-Opt I, Hi-Opt II, Omega II, Halves, Zen Count
# Unbalanced Card Counting Systems: KO

# Dictionary referencing row number of count_array
count_dict = {
    'Hi-Lo': 0,
    'Hi-Opt I': 1,
    'Hi-Opt II': 2,
    'Omega II': 3,
    'Halves': 4,
    'Zen Count': 5,
    'KO': 6
}

# Counts for each card
count_array = np.array([
    # A   2   3  4  5     6   7   8    9  10   J   Q   K
    [-1,  1,  1, 1, 1,    1,  0,  0,   0, -1, -1, -1, -1],  # Hi-Lo
    [0,   0,  1, 1, 1,    1,  0,  0,   0, -1, -1, -1, -1],  # Hi-Opt I
    [0,   1,  1, 2, 2,    1,  1,  0,   0, -2, -2, -2, -2],  # Hi-Opt II
    [0,   1,  1, 2, 2,    2,  1,  0,  -1, -2, -2, -2, -2],  # Omega II
    [-1, .5,  1, 1, 1.5,  1, .5,  0, -.5, -1, -1, -1, -1],  # Halves
    [-1,  1,  1, 2, 2,    2,  1,  0,   0, -2, -2, -2, -2],  # Zen Count
    [-1,  1,  1, 1, 1,    1,  1,  0,   0, -1, -1, -1, -1]   # KO
])

count_array = count_array.T

# # Balanced Card Counting Systems begin at a running count equal to 0
# # Unbalanced Card Counting Systems (KO) begin at a running count equal to -4 * (shoe size - 1)
# # The additional (shoe size - 1) factor will be added in counting_strategy.py
starting_count_array = np.array([0, 0, 0, 0, 0, 0, -4])
