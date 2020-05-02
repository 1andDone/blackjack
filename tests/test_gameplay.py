import pytest
from gameplay import players_place_bets
from table import Table
from house_rules import HouseRules
from player import Player
from cards import Cards
from counting_strategy import CountingStrategy


def test_players_place_bets():
    cards = Cards(shoe_size=6)
    cards.shuffle()
    counting_strategy = CountingStrategy(cards=cards)
    table = Table()
    rules = HouseRules(min_bet=10, max_bet=500)
    players = [
                Player(
                    name='Amount bet below table minimum',
                    rules=rules,
                    bankroll=20,
                    min_bet=10
                ),
                Player(
                    name='Amount bet within constraints',
                    rules=rules,
                    bankroll=20,
                    min_bet=10
                ),
                Player(
                    name='Amount bet is greater than available funds',
                    rules=rules,
                    bankroll=2000,
                    min_bet=500
                )
    ]

    for p in players:
        table.add_player(player=p)
        if p.get_name() == 'Amount bet below table minimum':
            p.set_bankroll(amount=5)
            assert p.get_bankroll() == 5
            assert p.get_bankroll() < rules.min_bet
        if p.get_name() == 'Amount bet within constraints':
            assert rules.min_bet <= p.get_min_bet() <= rules.max_bet
        if p.get_name() == 'Amount bet is greater than available funds':
            p.set_bankroll(amount=490)
            assert p.get_bankroll() == 490
            assert p.get_min_bet() > p.get_bankroll()
            assert rules.min_bet <= p.get_bankroll() <= rules.max_bet

    players_place_bets(table=table, rules=rules, counting_strategy=counting_strategy)

    for p in players:
        if p.get_name() == 'Amount bet below table minimum':
            assert p.get_bankroll() == 5  # bankroll unchanged
            assert p not in table.get_players()  # player removed from table
        if p.get_name() == 'Amount bet within constraints':
            assert p.get_bankroll() == 10  # bankroll went down by 10
            assert p in table.get_players()  # player still at table
        if p.get_name() == 'Amount bet is greater than available funds':
            assert p.get_bankroll() == 0  # player bet entire bankroll
            assert p in table.get_players()  # player still at table


