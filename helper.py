def count_hand(hand):
    """
    Returns the maximum hard or soft total for a given hand and indicates
    whether or not the hand is soft.

    Parameters
    ----------
    hand : list of int
        List of integer card elements

    Returns
    -------
    tuple of int, bool
        Maximum hard or soft total for a given hand and an indicator
        of whether or not it is a soft hand

    """
    total = 0
    soft_hand = False
    for card in hand:
        total += 10 if card >= 10 else card

    if 1 in hand and total < 12:
        total += 10
        soft_hand = True

    return total, soft_hand


def splittable(rules, hand, num_hands):
    """
    Determines if a hand is splittable or not.

    Parameters
    ----------
    rules : HouseRules
        HouseRules class instance
    hand : list of int
        List of integer card elements
    num_hands : int
        Number of hands being played by a player

    Returns
    -------
    bool
        True if hand is splittable, false otherwise

    """
    if len(hand) == 2 and num_hands < rules.max_hands:
        if hand[0] == hand[1]:
            return True
        if rules.split_unlike_tens:
            if all(card >= 10 for card in hand):
                return True
    return False
