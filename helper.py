import card_values as cv


def count_hand(hand):
    """
    Returns the maximum hard or soft total for a given hand and indicates
    whether or not the hand is soft.

    Parameters
    ----------
    hand : list of str
        List of string card elements

    Returns
    -------
    tuple of int, bool
        Maximum hard or soft total for a given hand and an indicator
        of whether or not it is a soft hand

    """
    total = 0
    soft_hand = False
    for card in hand:
        total += cv.card_values[card]

    if 'A' in hand and total < 12:
        total += 10
        soft_hand = True

    return total, soft_hand


def add_card_to_total(total, soft_hand, card):
    """
    Returns the maximum hard or soft total for a given hand when a card is added
    to a previously computed total and indicates whether or not the hand is soft.

    Parameters
    ----------
    total : int
        Maximum hard or soft total for a hand computed previously
    soft_hand : bool
        True if the previously computed hand is soft, false if hard
    card : str
        String card element

    Returns
    -------
    tuple of int, bool
        Maximum hard or soft total for a given hand and an indicator
        of whether or not it is a soft hand

    """
    total = total + cv.card_values[card]
    if card == 'A' and total < 12:  # total less than 12 implies that no Ace is in hand (so long as hand length >= 2)
        total += 10
        soft_hand = True
    elif soft_hand and total > 21:
        total -= 10
        soft_hand = False
    return total, soft_hand


def splittable(rules, hand, num_hands=1):
    """
    Determines if a hand is splittable or not.

    Parameters
    ----------
    rules : HouseRules
        HouseRules class instance
    hand : list of str
        List of string card elements
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
            if all(x in ['10', 'J', 'Q', 'K'] for x in hand):
                return True
    return False
