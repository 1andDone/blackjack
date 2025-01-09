from typing import Any
from blackjack.enums import CardCountingSystem


HI_LO_VALUES = {
    '2': 1,
    '3': 1,
    '4': 1,
    '5': 1,
    '6': 1,
    '7': 0,
    '8': 0,
    '9': 0,
    '10-J-Q-K': -1,
    'A': -1,
}


HI_OPT_I_VALUES = {
    '2': 0,
    '3': 1,
    '4': 1,
    '5': 1,
    '6': 1,
    '7': 0,
    '8': 0,
    '9': 0,
    '10-J-Q-K': -1,
    'A': 0,
}


HI_OPT_II_VALUES = {
    '2': 1,
    '3': 1,
    '4': 2,
    '5': 2,
    '6': 1,
    '7': 1,
    '8': 0,
    '9': 0,
    '10-J-Q-K': -2,
    'A': 0,
}


OMEGA_II_VALUES = {
    '2': 1,
    '3': 1,
    '4': 2,
    '5': 2,
    '6': 2,
    '7': 1,
    '8': 0,
    '9': -1,
    '10-J-Q-K': -2,
    'A': 0,
}


HALVES_VALUES = {
    '2': 0.5,
    '3': 1,
    '4': 1,
    '5': 1.5,
    '6': 1,
    '7': 0.5,
    '8': 0,
    '9': -0.5,
    '10-J-Q-K': -1,
    'A': -1,
}


ZEN_COUNT_VALUES = {
    '2': 1,
    '3': 1,
    '4': 2,
    '5': 2,
    '6': 2,
    '7': 1,
    '8': 0,
    '9': 0,
    '10-J-Q-K': -2,
    'A': -1,
}


KO_VALUES = {
    '2': 1,
    '3': 1,
    '4': 1,
    '5': 1,
    '6': 1,
    '7': 1,
    '8': 0,
    '9': 0,
    '10-J-Q-K': -1,
    'A': -1,
}


# balanced card counting systems: Hi-Lo, Hi-Opt I, Hi-Opt II, Omega II, Halves, Zen Count
# unbalanced card counting systems: KO
COUNT_VALUES: dict[CardCountingSystem, dict[str, Any]] = {
    CardCountingSystem.HI_LO: HI_LO_VALUES,
    CardCountingSystem.HI_OPT_I: HI_OPT_I_VALUES,
    CardCountingSystem.HI_OPT_II: HI_OPT_II_VALUES,
    CardCountingSystem.OMEGA_II: OMEGA_II_VALUES,
    CardCountingSystem.HALVES: HALVES_VALUES,
    CardCountingSystem.ZEN_COUNT: ZEN_COUNT_VALUES,
    CardCountingSystem.KO: KO_VALUES
}


# balanced card counting systems begin at a running count equal to 0
# unbalanced card counting systems (KO) begin at a running count equal to -4 * (shoe size - 1)
# the additional (shoe size - 1) factor for KO is added when used
INITIAL_COUNTS = {
    CardCountingSystem.KO: -4
}
