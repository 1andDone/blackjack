# Only balanced counting strategies
# True count strategies: Hi-Lo, Zen card, Omega II, Halves
# Running count strategies: Hi-Opt I, Hi-Opt II

hi_lo = {
    '2': 1,
    '3': 1,
    '4': 1,
    '5': 1,
    '6': 1,
    '7': 0,
    '8': 0,
    '9': 0,
    '10': -1,
    'J': -1,
    'Q': -1,
    'K': -1,
    'A': -1
}

hi_opt_1 = {
    '2': 0,
    '3': 1,
    '4': 1,
    '5': 1,
    '6': 1,
    '7': 0,
    '8': 0,
    '9': 0,
    '10': -1,
    'J': -1,
    'Q': -1,
    'K': -1,
    'A': 0
}

hi_opt_2 = {
    '2': 1,
    '3': 1,
    '4': 2,
    '5': 2,
    '6': 1,
    '7': 1,
    '8': 0,
    '9': 0,
    '10': -2,
    'J': -2,
    'Q': -2,
    'K': -2,
    'A': 0
}

omega_2 = {
    '2': 1,
    '3': 1,
    '4': 2,
    '5': 2,
    '6': 2,
    '7': 1,
    '8': 0,
    '9': -1,
    '10': -2,
    'J': -2,
    'Q': -2,
    'K': -2,
    'A': 0
}

halves = {
    '2': 0.5,
    '3': 1,
    '4': 1,
    '5': 1.5,
    '6': 1,
    '7': 0.5,
    '8': 0,
    '9': -0.5,
    '10': -1,
    'J': -1,
    'Q': -1,
    'K': -1,
    'A': -1
}

zen_count = {
    '2': 1,
    '3': 1,
    '4': 2,
    '5': 2,
    '6': 2,
    '7': 1,
    '8': 0,
    '9': 0,
    '10': -2,
    'J': -2,
    'Q': -2,
    'K': -2,
    'A': -1
}