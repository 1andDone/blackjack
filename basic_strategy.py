import numpy as np

# basic strategy key
# H : hit
# S : stand
# Dh : double if allowed, otherwise hit
# Ds : double if allowed, otherwise stand
# P : split
# Ph : split if double after split allowed, otherwise hit
# Rh : surrender if allowed, otherwise hit
# Rs : surrender if allowed, otherwise stand
# Rp : surrender if allowed, otherwise split
# source: https://wizardofodds.com/games/blackjack/strategy/4-decks/

# extended the above table to include soft 12 (A-A)
# this case is possible if the player does not have sufficient funds to split A-A and is forced to play the hand

# arrays of player's hand (y-axis) vs. dealers up card (x-axis)

s17_hard_array = np.array([
    ["H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["H",	"Dh",	"Dh",	"Dh",	"Dh",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"H",	"H",	"H",	"H",	"H"],
    ["Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"H"],
    ["H",	"H",	"S",	"S",	"S",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["S",	"S",	"S",	"S",	"S",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["S",	"S",	"S",	"S",	"S",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["S",	"S",	"S",	"S",	"S",	"H",	"H",	"H",	"Rh",	"Rh",	"Rh",	"Rh",	"H"],
    ["S",	"S",	"S",	"S",	"S",	"H",	"H",	"Rh",	"Rh",	"Rh",	"Rh",	"Rh",	"Rh"],
    ["S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S"],
    ["S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S"],
    ["S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S"],
    ["S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S"],
    ["S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S"]
])

s17_soft_array = np.array([
    ["H",   "H",    "H",    "H",    "H",    "H",    "H",    "H",    "H",    "H",    "H",    "H",    "H"],
    ["H",	"H",	"H",	"Dh",	"Dh",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["H",	"H",	"H",	"Dh",	"Dh",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["H",	"H",	"Dh",	"Dh",	"Dh",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["H",	"H",	"Dh",	"Dh",	"Dh",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["H",	"Dh",	"Dh",	"Dh",	"Dh",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["S",	"Ds",	"Ds",	"Ds",	"Ds",	"S",	"S",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S"],
    ["S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S"],
    ["S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S"]
])

s17_splits_array = np.array([
    ["Ph",	"Ph",	"P",	"P",	"P",	"P",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["Ph",	"Ph",	"P",	"P",	"P",	"P",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["H",	"H",	"H",	"Ph",	"Ph",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"H",	"H",	"H",	"H",	"H"],
    ["Ph",	"P",	"P",	"P",	"P",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["P",	"P",	"P",	"P",	"P",	"P",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["P",	"P",	"P",	"P",	"P",	"P",	"P",	"P",	"P",	"P",	"P",	"P",	"P"],
    ["P",	"P",	"P",	"P",	"P",	"S",	"P",	"P",	"S",	"S",	"S",	"S",	"S"],
    ["S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S"],
    ["P",	"P",	"P",	"P",	"P",	"P",	"P",	"P",	"P",	"P",	"P",	"P",	"P"]
])

h17_hard_array = np.array([
    ["H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["H",	"Dh",	"Dh",	"Dh",	"Dh",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"H",	"H",	"H",	"H",	"H"],
    ["Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh"],
    ["H",	"H",	"S",	"S",	"S",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["S",	"S",	"S",	"S",	"S",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["S",	"S",	"S",	"S",	"S",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["S",	"S",	"S",	"S",	"S",	"H",	"H",	"H",	"Rh",	"Rh",	"Rh",	"Rh",	"Rh"],
    ["S",	"S",	"S",	"S",	"S",	"H",	"H",	"Rh",	"Rh",	"Rh",	"Rh",	"Rh",	"Rh"],
    ["S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"Rs"],
    ["S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S"],
    ["S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S"],
    ["S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S"],
    ["S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S"]
])

h17_soft_array = np.array([
    ["H",   "H",    "H",    "H",    "H",    "H",    "H",    "H",    "H",    "H",    "H",    "H",    "H"],
    ["H",	"H",	"H",	"Dh",	"Dh",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["H",	"H",	"H",	"Dh",	"Dh",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["H",	"H",	"Dh",	"Dh",	"Dh",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["H",	"H",	"Dh",	"Dh",	"Dh",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["H",	"Dh",	"Dh",	"Dh",	"Dh",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["Ds",	"Ds",	"Ds",	"Ds",	"Ds",	"S",	"S",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["S",	"S",	"S",	"S",	"Ds",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S"],
    ["S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S"],
    ["S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S"]
])

h17_splits_array = np.array([
    ["Ph",	"Ph",	"P",	"P",	"P",	"P",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["Ph",	"Ph",	"P",	"P",	"P",	"P",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["H",	"H",	"H",	"Ph",	"Ph",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"Dh",	"H",	"H",	"H",	"H",	"H"],
    ["Ph",	"P",	"P",	"P",	"P",	"H",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["P",	"P",	"P",	"P",	"P",	"P",	"H",	"H",	"H",	"H",	"H",	"H",	"H"],
    ["P",	"P",	"P",	"P",	"P",	"P",	"P",	"P",	"P",	"P",	"P",	"P",	"Rp"],
    ["P",	"P",	"P",	"P",	"P",	"S",	"P",	"P",	"S",	"S",	"S",	"S",	"S"],
    ["S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S",	"S"],
    ["P",	"P",	"P",	"P",	"P",	"P",	"P",	"P",	"P",	"P",	"P",	"P",	"P"]
])

# cards list ranges from 2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K, A
cards_list = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 1]

# splits list ranges from 2, 3, 4, 5, 6, 7, 8, 9, 10 (including J, Q, K), A
splits_list = [2, 3, 4, 5, 6, 7, 8, 9, 10, 1]

# Nested Dictionaries
s17_hard = {}
for row_ix, i in enumerate(range(4, 22)):
    s17_hard[i] = {}
    for col_ix, j in enumerate(cards_list):
        s17_hard[i][j] = s17_hard_array[row_ix][col_ix]

s17_soft = {}
for row_ix, i in enumerate(range(12, 22)):
    s17_soft[i] = {}
    for col_ix, j in enumerate(cards_list):
        s17_soft[i][j] = s17_soft_array[row_ix][col_ix]

s17_splits = {}
for row_ix, i in enumerate(splits_list):
    s17_splits[i] = {}
    for col_ix, j in enumerate(cards_list):
        s17_splits[i][j] = s17_splits_array[row_ix][col_ix]

h17_hard = {}
for row_ix, i in enumerate(range(4, 22)):
    h17_hard[i] = {}
    for col_ix, j in enumerate(cards_list):
        h17_hard[i][j] = h17_hard_array[row_ix][col_ix]

h17_soft = {}
for row_ix, i in enumerate(range(12, 22)):
    h17_soft[i] = {}
    for col_ix, j in enumerate(cards_list):
        h17_soft[i][j] = h17_soft_array[row_ix][col_ix]

h17_splits = {}
for row_ix, i in enumerate(splits_list):
    h17_splits[i] = {}
    for col_ix, j in enumerate(cards_list):
        h17_splits[i][j] = h17_splits_array[row_ix][col_ix]