import numpy as np
import matplotlib.pyplot as plt

def format_title(player_name, plot_name, shoe_size, count_strategy, play_strategy, blackjack_payout,
                 penetration, initial_bankroll, bet_strategy, min_bet, bet_spread, simulations):
    """
    """
    title = ('{player_name} {plot_name}\n' +
             '{shoe_size} Decks, {penetration}% Deck Penetration, {blackjack_payout} Blackjack Payout,\n' +
             '{count_strategy}{play_strategy} Play Strategy,\n' +
             '{initial_bankroll} Initial Bankroll,\n' +
             '{bet_strategy}{min_bet} Minimum Bet{bet_spread}\n' +
             '{simulations} Shoe Simulations').format(
        player_name=player_name,
        plot_name=plot_name,
        shoe_size=shoe_size,
        count_strategy=count_strategy + ' Count Strategy, ' if count_strategy is not None else '',
        play_strategy=play_strategy,
        blackjack_payout=blackjack_payout,
        penetration=int(penetration * 100) if (penetration * 100) - int(penetration * 100) == 0 else penetration * 100,
        initial_bankroll='$' + str(int(initial_bankroll)) if initial_bankroll - int(initial_bankroll) == 0
                                else str(initial_bankroll),
        bet_strategy=bet_strategy + ' Bet Strategy, ' if bet_strategy == 'Flat' else '',
        min_bet='$' + str(int(min_bet)) if min_bet - int(min_bet) == 0 else str(min_bet),
        bet_spread=', 1-' + str(int(bet_spread) if bet_spread - int(bet_spread) == 0
                                else bet_spread) + ' Bet Spread,' if bet_strategy == 'Variable' else '',
        simulations=simulations)

    return title


def net_winnings_per_shoe(count, count_accuracy, net_winnings, count_strategy, play_strategy, player_name,
                          shoe_size, blackjack_payout, penetration, initial_bankroll, bet_strategy,
                          min_bet, bet_spread, simulations):
    """
    """
    # format width to be 80% of count accuracy
    if count_accuracy == 0.1:
        width = 0.08
    elif count_accuracy == 0.5:
        width = 0.4
    else:
        width = 0.8

    plt.figure(figsize=(16, 12))
    plt.bar(x=count[net_winnings > 0], height=net_winnings[net_winnings > 0] / simulations, color='b', width=width)
    plt.bar(x=count[net_winnings < 0], height=net_winnings[net_winnings < 0] / simulations, color='r', width=width)
    plt.xlabel(str(count_strategy) + ' count')
    plt.ylabel('Net Winnings per Shoe ($)')
    plt.title(
        format_title(
            player_name=player_name,
            plot_name='Net Winnings per Shoe',
            shoe_size=shoe_size,
            count_strategy=count_strategy,
            play_strategy=play_strategy,
            blackjack_payout=blackjack_payout,
            penetration=penetration,
            initial_bankroll=initial_bankroll,
            bet_strategy=bet_strategy,
            min_bet=min_bet,
            bet_spread=bet_spread,
            simulations=simulations,
        )
    )
    plt.grid()
    plt.show()


def cumulative_net_winnings_per_shoe(count, net_winnings, count_strategy, play_strategy, player_name, shoe_size,
                                     blackjack_payout, penetration, initial_bankroll, bet_strategy, min_bet,
                                     bet_spread, simulations):
    """
    """
    plt.figure(figsize=(16, 12))
    plt.plot(count, np.cumsum(net_winnings) / simulations)
    plt.xlabel(str(count_strategy) + ' count')
    plt.ylabel('Net Winnings per Shoe ($)')
    plt.title(
        format_title(
                player_name=player_name,
                plot_name='Cumulative Net Winnings per Shoe',
                shoe_size=shoe_size,
                count_strategy=count_strategy,
                play_strategy=play_strategy,
                blackjack_payout=blackjack_payout,
                penetration=penetration,
                initial_bankroll=initial_bankroll,
                bet_strategy=bet_strategy,
                min_bet=min_bet,
                bet_spread=bet_spread,
                simulations=simulations,
        )
    )
    plt.grid()
    plt.show()


def bankroll_growth(ending_bankroll, shoe, count_strategy, play_strategy,
                    player_name, shoe_size, blackjack_payout, penetration, initial_bankroll,
                    bet_strategy, min_bet, bet_spread, simulations):
    """
    """
    plt.figure(figsize=(16, 12))
    plt.plot(shoe, ending_bankroll)
    plt.xlabel('Number of Shoes Played')
    plt.ylabel('Bankroll ($)')
    plt.xlim(0, max(shoe) + 0.01 * max(shoe))
    plt.ylim(0, max(ending_bankroll) + 0.01 * max(ending_bankroll))
    plt.title(
        format_title(
            player_name=player_name,
            plot_name='Bankroll Growth',
            shoe_size=shoe_size,
            count_strategy=count_strategy,
            play_strategy=play_strategy,
            blackjack_payout=blackjack_payout,
            penetration=penetration,
            initial_bankroll=initial_bankroll,
            bet_strategy=bet_strategy,
            min_bet=min_bet,
            bet_spread=bet_spread,
            simulations=simulations,
        )
    )
    plt.grid()
    plt.show()


def bankroll_end_of_shoe(ending_bankroll, ending_bankroll_count, count_strategy, play_strategy,
                         player_name, shoe_size, blackjack_payout, penetration, initial_bankroll,
                         bet_strategy, min_bet, bet_spread, simulations):
    """
    """
    plt.figure(figsize=(16, 12))
    plt.plot(ending_bankroll, ending_bankroll_count)
    plt.xlabel('Bankroll ($)')
    plt.ylabel('Number of Occurrences')
    plt.ylim(0, max(ending_bankroll_count) + 0.01 * max(ending_bankroll_count))
    plt.title(
        format_title(
            player_name=player_name,
            plot_name='Ending Bankroll for Each Shoe Played',
            shoe_size=shoe_size,
            count_strategy=count_strategy,
            play_strategy=play_strategy,
            blackjack_payout=blackjack_payout,
            penetration=penetration,
            initial_bankroll=initial_bankroll,
            bet_strategy=bet_strategy,
            min_bet=min_bet,
            bet_spread=bet_spread,
            simulations=simulations,
        )
    )
    plt.grid()
    plt.show()

