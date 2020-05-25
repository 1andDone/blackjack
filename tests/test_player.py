import pytest
from player import Player
from house_rules import HouseRules


@pytest.fixture
def setup_player():
    r = HouseRules(bet_limits=[10, 500])
    p = Player(
            name='Player 1',
            rules=r,
            bankroll=100,
            min_bet=10
    )
    return p


class TestPlayer(object):

    @pytest.mark.parametrize('name, expected',
                             [
                                 ('Player 1', 'Player 1'),  # string name
                                 (1, TypeError)  # non-string name
                             ])
    def test_name(self, name, expected):
        """
        Tests the name parameter of the __init__ method.

        """
        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(TypeError):
                Player(
                    name=name,
                    rules=HouseRules(bet_limits=[10, 500]),
                    bankroll=100,
                    min_bet=10
                )

        else:
            p = Player(
                    name=name,
                    rules=HouseRules(bet_limits=[10, 500]),
                    bankroll=100,
                    min_bet=10
                )
            assert p.get_name() == expected

    @pytest.mark.parametrize('bankroll, expected',
                             [
                                 (5, ValueError),  # bankroll is less than rules and/or players min bet
                                 (1000, 1000)
                             ])
    def test_bankroll(self, bankroll, expected):
        """
        Tests the bankroll parameter of the __init__ method.

        """
        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(ValueError):
                Player(
                    name='Player 1',
                    rules=HouseRules(bet_limits=[10, 500]),
                    bankroll=bankroll,
                    min_bet=10
                )

        else:
            p = Player(
                    name='Player 1',
                    rules=HouseRules(bet_limits=[10, 500]),
                    bankroll=bankroll,
                    min_bet=10
                )
            assert p.get_bankroll() == expected

    @pytest.mark.parametrize('min_bet, expected',
                             [
                                 (5, ValueError),  # min bet is less than rules allow
                                 (505, ValueError),  # min bet is greater than rules allow
                                 (10, 10)
                             ])
    def test_min_bet(self, min_bet, expected):
        """
        Tests the min_bet parameter of the __init__ method.

        """
        r = HouseRules(bet_limits=[10, 500])

        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(ValueError):
                Player(
                    name='Player 1',
                    rules=r,
                    bankroll=100,
                    min_bet=min_bet
                )

        else:
            p = Player(
                    name='Player 1',
                    rules=r,
                    bankroll=100,
                    min_bet=min_bet
                )
            assert p.get_min_bet() == expected

    @pytest.mark.parametrize('bet_spread, expected',
                             [
                                 (0.5, ValueError),  # bet spread less than 1
                                 (10, 10),
                                 (50, ValueError)  # bet spread greater than rules max bet/player min bet
                             ])
    def test_bet_spread(self, bet_spread, expected):
        """
        Tests the bet_spread parameter of the __init__ method.

        """
        r = HouseRules(bet_limits=[10, 500])

        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(ValueError):
                Player(
                    name='Player 1',
                    rules=r,
                    bankroll=100,
                    min_bet=20,
                    bet_count_amount=[(1, 20), (2, 50)],
                    bet_spread=bet_spread,
                    bet_strategy='Spread',
                    count_strategy='Hi-Lo',
                    true_count_accuracy=0.5
                )

        else:
            p = Player(
                    name='Player 1',
                    rules=r,
                    bankroll=100,
                    min_bet=20,
                    bet_count_amount=[(1, 20), (2, 50)],
                    bet_spread=bet_spread,
                    bet_strategy='Spread',
                    count_strategy='Hi-Lo',
                    true_count_accuracy=0.5
            )
            assert p.get_bet_spread() == expected

    @pytest.mark.parametrize('bet_count_amount, expected',
                             [
                                 ([(1, 10), (2, 50)], {1: 10, 2: 50}),
                                 ([(1, 10), (2, 50.56339)], {1: 10, 2: 50.56}),  # rounded
                                 ([(1, 15), (2, 50)], ValueError),  # first amount is greater than minimum bet
                                 ([(1, 10), (2, 105)], ValueError),  # last amount exceeds minimum bet * bet spread
                                 ([(2, 50), (1, 10)], ValueError),  # counts out of order
                                 ([(1, 50), (2, 10)], ValueError)  # amounts out of order
                             ])
    def test_bet_count_amount(self, bet_count_amount, expected):
        """
        Tests the bet_count_amount of the __init__ method.

        """
        r = HouseRules(bet_limits=[10, 500])

        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(ValueError):
                Player(
                    name='Player 1',
                    rules=r,
                    bankroll=100,
                    min_bet=10,
                    bet_count_amount=bet_count_amount,
                    bet_spread=10,
                    bet_strategy='Spread',
                    count_strategy='Hi-Lo',
                    true_count_accuracy=0.5
                )

        else:
            p = Player(
                    name='Player 1',
                    rules=r,
                    bankroll=100,
                    min_bet=10,
                    bet_count_amount=bet_count_amount,
                    bet_spread=10,
                    bet_strategy='Spread',
                    count_strategy='Hi-Lo',
                    true_count_accuracy=0.5
            )
            assert p.bet_scale == expected

    @pytest.mark.parametrize('bet_strategy, count_strategy, true_count_accuracy, expected',
                             [
                                 ('Spread', 'Hi-Lo', 1, 1),
                                 ('Spread', 'Hi-Lo', 0.5, 0.5),
                                 ('Spread', 'Hi-Lo', 0.1, 0.1),
                                 ('Spread', 'Hi-Lo', None, ValueError),
                                 ('Spread', 'KO', None, None),
                                 ('Spread', 'KO', 1, ValueError),
                                 ('Flat', None, None, None),
                                 ('Flat', None, 0.5, ValueError)
                             ])
    def test_true_count_accuracy(self, bet_strategy, count_strategy, true_count_accuracy, expected):
        """
        Tests the true_count_accuracy of the __init__ method.

        """
        r = HouseRules(bet_limits=[10, 500])

        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(ValueError):
                Player(
                    name='Player 1',
                    rules=r,
                    bankroll=100,
                    min_bet=10,
                    bet_count_amount=[(1, 10), (2, 50)],
                    bet_spread=10,
                    bet_strategy=bet_strategy,
                    count_strategy=count_strategy,
                    true_count_accuracy=true_count_accuracy
                )

        else:
            p = Player(
                    name='Player 1',
                    rules=r,
                    bankroll=100,
                    min_bet=10,
                    bet_count_amount=[(1, 10), (2, 50)],
                    bet_spread=10,
                    bet_strategy=bet_strategy,
                    count_strategy=count_strategy,
                    true_count_accuracy=true_count_accuracy
            )
            assert p.get_true_count_accuracy() == expected

    @pytest.mark.parametrize('count_strategy, back_counting, back_counting_entry_exit, expected',
                             [
                                 ('Hi-Lo', True, [1, 2], [1, 2]),
                                 ('Hi-Lo', True, [2.2, -1.7], [2.2, -1.7]),
                                 ('Hi-Lo', True, [1, 2, 3], ValueError),  # entry/exit needs to be a list of length 2
                                 ('Hi-Lo', True, ['6', '5'], ValueError),  # entry/exit needs to be int or float
                                 ('Hi-Lo', False, [1, 2], ValueError),  # no back counting
                                 ('Hi-Lo', True, None, ValueError),  # no back counting
                                 (None, True, [1, 2], ValueError)  # back counting requires a count strategy
                             ])
    def test_back_counting_entry_exit(self, count_strategy, back_counting, back_counting_entry_exit, expected):
        """
        Tests the back_counting of the __init__ method.

        """
        r = HouseRules(bet_limits=[10, 500])

        if type(expected) == type and issubclass(expected, Exception):
            with pytest.raises(ValueError):
                Player(
                    name='Player 1',
                    rules=r,
                    bankroll=100,
                    min_bet=10,
                    bet_count_amount=[(1, 10), (2, 50)],
                    bet_spread=10,
                    bet_strategy='Spread',
                    count_strategy=count_strategy,
                    true_count_accuracy=0.5,
                    back_counting=back_counting,
                    back_counting_entry_exit=back_counting_entry_exit
                )

        else:
            p = Player(
                    name='Player 1',
                    rules=r,
                    bankroll=100,
                    min_bet=10,
                    bet_count_amount=[(1, 10), (2, 50)],
                    bet_spread=10,
                    bet_strategy='Spread',
                    count_strategy=count_strategy,
                    true_count_accuracy=0.5,
                    back_counting=back_counting,
                    back_counting_entry_exit=back_counting_entry_exit
            )
            assert p.get_back_counting_entry_exit() == expected

    def test_create_hand(self, setup_player):
        """
        Tests the create_hand method.

        """
        p = setup_player
        assert p.get_hands_dict() == {}
        p.create_hand()
        assert p.get_hands_dict() == {
            1: {
                    'busted': False,
                    'double down': False,
                    'hand': [],
                    'insurance': False,
                    'natural blackjack': False,
                    'split': False,
                    'stand': False,
                    'surrender': False
            }
        }

    def test_insurance(self, setup_player):
        """
        Tests the insurance method.

        """
        p = setup_player
        p.create_hand()
        assert p.get_insurance() is False
        p.insurance()
        assert p.get_insurance() is True

    def test_hit(self, setup_player):
        """
        Tests the hit method.

        """
        p = setup_player
        p.create_hand()
        assert p.get_hand(key=1) == []
        p.hit(key=1, new_card='K')
        p.hit(key=1, new_card='7')
        assert p.get_hand(key=1) == ['K', '7']

    def test_split(self, setup_player):
        """
        Tests the split method.

        """
        p = setup_player
        p.create_hand()
        p.hit(key=1, new_card='A')
        p.hit(key=1, new_card='A')
        assert p.get_hand(key=1) == ['A', 'A']
        p.split(key=1, new_key=2)
        for key in [1, 2]:
            assert p.get_hand(key=key) == ['A']

    def test_double_down(self, setup_player):
        """
        Tests the double_down method.

        """
        p = setup_player
        p.create_hand()
        p.hit(key=1, new_card='6')
        p.hit(key=1, new_card='4')
        assert p.get_double_down(key=1) is False
        p.double_down(key=1, new_card='A')
        assert p.get_double_down(key=1) is True

    @pytest.mark.parametrize('hand, num_hands, expected',
                             [
                                 (['8'], 1, 'H'),  # hand of length 1
                                 (['8', '8'], 1, 'P'),  # number of hands is less than max hands
                                 (['8', '8'], 4, 'Rh'),  # number of hands is not less than max hands
                                 (['A', '7'], 1, 'H'),  # soft total
                                 (['8', 'J'], 1, 'S'),  # hard total
                                 (['J', '6', 'K'], 1, 'B')  # busted
                             ])
    def test_decision(self, setup_player, hand, num_hands, expected):
        """
        Tests the decision method.

        """
        p = setup_player
        decision = p.decision(
                        hand=hand,
                        dealer_up_card='J',
                        num_hands=num_hands
        )
        assert decision == expected

