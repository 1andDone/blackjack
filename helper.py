import card_values as cv

def count_hand(hand):
    """
    Returns the soft and hard totals for a given hand

    Parameters
    ----------
    hand : list
        List of string card elements (i.e. '2', '3', 'J', 'Q')

    Returns
    -------
    return : tuple

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
        soft_total += 11 + ((num_aces - 1) * 1)
        hard_total += num_aces * 1

    return soft_total, hard_total


def max_count_hand(hand):
    """
    Determines the maximum count of a hand

    Parameters
    ----------
    hand : list
        List of string card elements (i.e. '2', '3', 'J', 'Q')

    Returns
    -------
    return : integer

    """
    soft_total, hard_total = count_hand(hand)

    if soft_total <= 21 and hard_total <= 21:
        total = max(soft_total, hard_total)
    elif soft_total <= 21:
        total = soft_total
    else:
        total = hard_total

    return total


def splittable(hand):
    """
    Determines if a hand is splittable or not

    Parameters
    ----------
    hand : list
        List of string card elements (i.e. '2', '3', 'J', 'Q')

    Returns
    -------
    return : boolean

    """
    if len(hand) == 2 and hand[0] == hand[1]:
        return True
    return False


