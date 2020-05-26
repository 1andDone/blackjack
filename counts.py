# Balanced Card Counting Systems: Hi-Lo, Hi-Opt I, Hi-Opt II, Omega II, Halves, Zen Count
# Unbalanced Card Counting Systems: KO

hi_lo = {'Hi-Lo': {
    2: 1,
    3: 1,
    4: 1,
    5: 1,
    6: 1,
    7: 0,
    8: 0,
    9: 0,
    10: -1,
    11: -1,
    12: -1,
    13: -1,
    1: -1
}}

hi_opt_1 = {'Hi-Opt I': {
    2: 0,
    3: 1,
    4: 1,
    5: 1,
    6: 1,
    7: 0,
    8: 0,
    9: 0,
    10: -1,
    11: -1,
    12: -1,
    13: -1,
    1: 0
}}

hi_opt_2 = {'Hi-Opt II': {
    2: 1,
    3: 1,
    4: 2,
    5: 2,
    6: 1,
    7: 1,
    8: 0,
    9: 0,
    10: -2,
    11: -2,
    12: -2,
    13: -2,
    1: 0
}}

omega_2 = {'Omega II': {
    2: 1,
    3: 1,
    4: 2,
    5: 2,
    6: 2,
    7: 1,
    8: 0,
    9: -1,
    10: -2,
    11: -2,
    12: -2,
    13: -2,
    1: 0
}}

halves = {'Halves': {
    2: 0.5,
    3: 1,
    4: 1,
    5: 1.5,
    6: 1,
    7: 0.5,
    8: 0,
    9: -0.5,
    10: -1,
    11: -1,
    12: -1,
    13: -1,
    1: -1
}}

zen_count = {'Zen Count': {
    2: 1,
    3: 1,
    4: 2,
    5: 2,
    6: 2,
    7: 1,
    8: 0,
    9: 0,
    10: -2,
    11: -2,
    12: -2,
    13: -2,
    1: -1
}}

ko = {'KO': {
    2: 1,
    3: 1,
    4: 1,
    5: 1,
    6: 1,
    7: 1,
    8: 0,
    9: 0,
    10: -1,
    11: -1,
    12: -1,
    13: -1,
    1: -1
}}

# create a nested dictionary
count_dict = {}
for d in [hi_lo, hi_opt_1, hi_opt_2, omega_2, halves, zen_count, ko]:
    for k, v in d.items():
        count_dict[k] = v
