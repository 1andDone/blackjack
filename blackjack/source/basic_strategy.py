## Basic Strategy (source: https://wizardofodds.com/games/blackjack/strategy/4-decks/)
# H  : hit
# S  : stand
# Dh : double if allowed, otherwise hit
# Ds : double if allowed, otherwise stand
# P  : split
# Ph : split if double after split allowed, otherwise hit
# Rh : surrender if allowed, otherwise hit
# Rs : surrender if allowed, otherwise stand
# Rp : surrender if allowed, otherwise split

# player's hand (y-axis) vs. dealer up card (x-axis)

h17_hard_array = [
    # 2      3       4       5       6       7       8       9      10       J       Q       K       A
    ['H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],   # 4
    ['H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],   # 5
    ['H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],   # 6
    ['H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],   # 7
    ['H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],   # 8
    ['H',	'Dh',	'Dh',	'Dh',	'Dh',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],   # 9
    ['Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'H',	'H',	'H',	'H',	'H'],   # 10
    ['Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh'],  # 11
    ['H',	'H',	'S',	'S',	'S',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],   # 12
    ['S',	'S',	'S',	'S',	'S',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],   # 13
    ['S',	'S',	'S',	'S',	'S',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],   # 14
    ['S',	'S',	'S',	'S',	'S',	'H',	'H',	'H',	'Rh',	'Rh',	'Rh',	'Rh',	'Rh'],  # 15
    ['S',	'S',	'S',	'S',	'S',	'H',	'H',	'Rh',	'Rh',	'Rh',	'Rh',	'Rh',	'Rh'],  # 16
    ['S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'Rs'],  # 17
    ['S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S'],   # 18
    ['S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S'],   # 19
    ['S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S'],   # 20
    ['S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S']    # 21
]


h17_soft_array = [
    # 2      3       4       5       6       7       8       9      10       J       Q       K       A
    ['H',	'H',	'H',	'Dh',	'Dh',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],  # 13
    ['H',	'H',	'H',	'Dh',	'Dh',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],  # 14
    ['H',	'H',	'Dh',	'Dh',	'Dh',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],  # 15
    ['H',	'H',	'Dh',	'Dh',	'Dh',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],  # 16
    ['H',	'Dh',	'Dh',	'Dh',	'Dh',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],  # 17
    ['Ds',	'Ds',	'Ds',	'Ds',	'Ds',	'S',	'S',	'H',	'H',	'H',	'H',	'H',	'H'],  # 18
    ['S',	'S',	'S',	'S',	'Ds',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S'],  # 19
    ['S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S'],  # 20
    ['S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S']   # 21
]


h17_pair_array = [
    # 2      3       4       5       6       7       8       9      10       J       Q       K       A
    ['Ph',	'Ph',	'P',	'P',	'P',	'P',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],   # 2
    ['Ph',	'Ph',	'P',	'P',	'P',	'P',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],   # 3
    ['H',	'H',	'H',	'Ph',	'Ph',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],   # 4
    ['Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'H',	'H',	'H',	'H',	'H'],   # 5
    ['Ph',	'P',	'P',	'P',	'P',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],   # 6
    ['P',	'P',	'P',	'P',	'P',	'P',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],   # 7
    ['P',	'P',	'P',	'P',	'P',	'P',	'P',	'P',	'P',	'P',	'P',	'P',	'Rp'],  # 8
    ['P',	'P',	'P',	'P',	'P',	'S',	'P',	'P',	'S',	'S',	'S',	'S',	'S'],   # 9
    ['S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S'],   # 10
    ['S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S'],   # J
    ['S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S'],   # Q
    ['S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S'],   # K
    ['P',	'P',	'P',	'P',	'P',	'P',	'P',	'P',	'P',	'P',	'P',	'P',	'P']    # A
]


s17_hard_array = [
    # 2      3       4       5       6       7       8       9      10       J       Q       K       A
    ['H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],   # 4
    ['H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],   # 5
    ['H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],   # 6
    ['H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],   # 7
    ['H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],   # 8
    ['H',	'Dh',	'Dh',	'Dh',	'Dh',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],   # 9
    ['Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'H',	'H',	'H',	'H',	'H'],   # 10
    ['Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'H'],   # 11
    ['H',	'H',	'S',	'S',	'S',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],   # 12
    ['S',	'S',	'S',	'S',	'S',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],   # 13
    ['S',	'S',	'S',	'S',	'S',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],   # 14
    ['S',	'S',	'S',	'S',	'S',	'H',	'H',	'H',	'Rh',	'Rh',	'Rh',	'Rh',	'H'],   # 15
    ['S',	'S',	'S',	'S',	'S',	'H',	'H',	'Rh',	'Rh',	'Rh',	'Rh',	'Rh',	'Rh'],  # 16
    ['S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S'],   # 17
    ['S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S'],   # 18
    ['S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S'],   # 19
    ['S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S'],   # 20
    ['S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S']    # 21
]


s17_soft_array = [
    # 2      3       4       5       6       7       8       9      10       J       Q       K       A
    ['H',	'H',	'H',	'Dh',	'Dh',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],  # 13
    ['H',	'H',	'H',	'Dh',	'Dh',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],  # 14
    ['H',	'H',	'Dh',	'Dh',	'Dh',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],  # 15
    ['H',	'H',	'Dh',	'Dh',	'Dh',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],  # 16
    ['H',	'Dh',	'Dh',	'Dh',	'Dh',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],  # 17
    ['S',	'Ds',	'Ds',	'Ds',	'Ds',	'S',	'S',	'H',	'H',	'H',	'H',	'H',	'H'],  # 18
    ['S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S'],  # 19
    ['S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S'],  # 20
    ['S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S']   # 21
]


s17_pair_array = [
    # 2      3       4       5       6       7       8       9      10       J       Q       K       A
    ['Ph',	'Ph',	'P',	'P',	'P',	'P',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],  # 2
    ['Ph',	'Ph',	'P',	'P',	'P',	'P',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],  # 3
    ['H',	'H',	'H',	'Ph',	'Ph',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],  # 4
    ['Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'Dh',	'H',	'H',	'H',	'H',	'H'],  # 5
    ['Ph',	'P',	'P',	'P',	'P',	'H',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],  # 6
    ['P',	'P',	'P',	'P',	'P',	'P',	'H',	'H',	'H',	'H',	'H',	'H',	'H'],  # 7
    ['P',	'P',	'P',	'P',	'P',	'P',	'P',	'P',	'P',	'P',	'P',	'P',	'P'],  # 8
    ['P',	'P',	'P',	'P',	'P',	'S',	'P',	'P',	'S',	'S',	'S',	'S',	'S'],  # 9
    ['S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S'],  # 10
    ['S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S'],  # J
    ['S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S'],  # Q
    ['S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S',	'S'],  # K
    ['P',	'P',	'P',	'P',	'P',	'P',	'P',	'P',	'P',	'P',	'P',	'P',	'P']   # A
]

cards_list = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

# dealer hits on soft 17
h17_hard = {}
for row_ix, i in enumerate(range(4, 22)):
    h17_hard[i] = {}
    for col_ix, j in enumerate(cards_list):
        h17_hard[i][j] = h17_hard_array[row_ix][col_ix]


h17_soft = {}
for row_ix, i in enumerate(range(13, 22)):
    h17_soft[i] = {}
    for col_ix, j in enumerate(cards_list):
        h17_soft[i][j] = h17_soft_array[row_ix][col_ix]


h17_pair = {}
for row_ix, i in enumerate(cards_list):
    h17_pair[i] = {}
    for col_ix, j in enumerate(cards_list):
        h17_pair[i][j] = h17_pair_array[row_ix][col_ix]


# dealer stands on soft 17
s17_hard = {}
for row_ix, i in enumerate(range(4, 22)):
    s17_hard[i] = {}
    for col_ix, j in enumerate(cards_list):
        s17_hard[i][j] = s17_hard_array[row_ix][col_ix]


s17_soft = {}
for row_ix, i in enumerate(range(13, 22)):
    s17_soft[i] = {}
    for col_ix, j in enumerate(cards_list):
        s17_soft[i][j] = s17_soft_array[row_ix][col_ix]


s17_pair = {}
for row_ix, i in enumerate(cards_list):
    s17_pair[i] = {}
    for col_ix, j in enumerate(cards_list):
        s17_pair[i][j] = s17_pair_array[row_ix][col_ix]