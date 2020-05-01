import card_values as cv

def count_hand(hand):
    """
    Returns the soft and hard totals for a given hand.

    Parameters
    ----------
    hand : list of str
        List of string card elements

    Returns
    -------
    tuple of int
        Soft and hard totals for a given hand

    """
    non_aces = [card for card in hand if card != 'A']

    # hard values
    hard_total = 0
    for card in non_aces:
        hard_total += cv.card_values[card]

    # possible soft values
    aces = [card for card in hand if card == 'A']
    num_aces = len(aces)

    soft_total = hard_total

    # if there are multiple aces, only one can be valued at 11
    if num_aces > 0:
        soft_total += 11 + (num_aces - 1)
        hard_total += num_aces

    return soft_total, hard_total


def max_count_hand(hand):
    """
    Determines the maximum count of a hand, while trying not to
    exceed 21. If both the soft and hard totals exceed 21, the hard
    total is reported.

    Parameters
    ----------
    hand : list of str
        List of string card elements

    Returns
    -------
    int
        Maximum count of a hand, while trying not exceed 21

    """
    soft_total, hard_total = count_hand(hand)

    if soft_total <= 21 and hard_total <= 21:
        return max(soft_total, hard_total)
    elif soft_total <= 21:
        return soft_total
    else:
        return hard_total


def splittable(rules, hand):
    """
    Determines if a hand is splittable or not.

    Parameters
    ----------
    rules : HouseRules
        HouseRules class instance
    hand : list of str
        List of string card elements

    Returns
    -------
    bool
        True if hand is splittable, false otherwise

    """
    if len(hand) == 2:
        if hand[0] == hand[1]:
            return True
        if rules.split_unlike_tens:
            if hand[0] == 'A' or hand[1] == 'A':
                return False
            if cv.card_values[hand[0]] == 10 and cv.card_values[hand[1]] == 10:
                return True
    return False
