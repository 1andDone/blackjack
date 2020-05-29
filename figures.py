import numpy as np
import matplotlib.pyplot as plt


def format_title(
        name, plot_name, shoe_size, penetration, blackjack_payout,
        count_strategy, play_strategy, bet_strategy, bet_spread,
        initial_bankroll, min_bet, simulations
):
    """
    Formats the title of a plot.

    Parameters
    ----------
    name : str
        Name of the player
    plot_name : str
        Name of the plot
    shoe_size : int
        Number of decks used during a blackjack game
    penetration : float
        Percentage of shoe played before the deck is re-shuffled
    blackjack_payout : float
        Payout for a player receiving a natural blackjack
    count_strategy : str
        Name of the card counting strategy used by the player
    play_strategy : str
        Name of the play strategy used by the player
    bet_strategy : str
        Name of the bet strategy used by the player
    bet_spread : float
        Ratio of maximum bet to minimum bet
    initial_bankroll : float
        Amount of money a player starts out with when sitting down at a table
    min_bet : float
        Minimum amount of money a player is willing to wager when playing a hand
    simulations : int
        Number of shoes played

    Returns
    -------
    str
        Formatted plot title

    """
    title = ('{name} {plot_name}\n' +
             '{shoe_size} Decks, {penetration}% Deck Penetration, {blackjack_payout} Blackjack Payout\n' +
             '{count_strategy}{play_strategy}{bet_strategy}{bet_spread}\n' +
             '{initial_bankroll} Initial Bankroll, {min_bet} Minimum Bet\n' +
             '{simulations} Shoe Simulations').format(
        name="'" + name + "'",
        plot_name=plot_name,
        shoe_size=shoe_size,
        penetration=int(penetration * 100) if (penetration * 100) - int(penetration * 100) == 0 else penetration * 100,
        blackjack_payout=blackjack_payout,
        count_strategy="'" + count_strategy + "'" + ' Card Counting System, ' if count_strategy is not None else '',
        play_strategy='Basic Strategy' if play_strategy == 'Basic' else play_strategy,
        bet_strategy=', ' + bet_strategy + ' Bet' if bet_strategy == 'Flat' else '',
        bet_spread=', 1-' + str(int(bet_spread) if bet_spread - int(bet_spread) == 0 else bet_spread) +
        ' Bet Spread' if bet_strategy == 'Spread' else '',
        initial_bankroll='\${:.2f}'.format(int(initial_bankroll)) if initial_bankroll - int(initial_bankroll) == 0
        else '\${:.2f}'.format(initial_bankroll),
        min_bet='\${:.2f}'.format(int(min_bet)) if min_bet - int(min_bet) == 0 else '\${:.2f}'.format(min_bet),
        simulations=simulations)

    return title


def net_winnings_figure(
        count, net_winnings, name, shoe_size, penetration,
        blackjack_payout, count_strategy, play_strategy, bet_strategy,
        bet_spread, initial_bankroll, min_bet, simulations
):
    """
    Creates two sub-plots based on the player's counting strategy. The top sub-plot shows
    the individual net winnings of a player at each running or true count at which
    they played a hand. The bottom sub-plot shows the cumulative net winnings of a player
    as the running or true count increases.

    Parameters
    ----------
    count : array_like
        Current running or true count based on the player's counting strategy
    net_winnings : array_like
        Amount of money a player has won or lost since starting
    name : str
        Name of the player
    shoe_size : int
        Number of decks used during a blackjack game
    penetration : float
        Percentage of shoe played before the deck is re-shuffled
    blackjack_payout : float
        Payout for a player receiving a natural blackjack
    count_strategy : str
        Name of the card counting strategy used by the player
    play_strategy : str
        Name of the play strategy used by the player
    bet_strategy : str
        Name of the bet strategy used by the player
    bet_spread : float
        Ratio of maximum bet to minimum bet
    initial_bankroll : float
        Amount of money a player starts out with when sitting down at a table
    min_bet : float
        Minimum amount of money a player is willing to wager when playing a hand
    simulations : int
        Number of shoes played

    """
    balanced_card_counting_systems = ['Hi-Lo', 'Hi-Opt I', 'Hi-Opt II', 'Omega II', 'Halves', 'Zen Count']

    # format width to be 80% of true count precision
    width = 0.8

    fig, (ax1, ax2) = plt.subplots(
                                nrows=2,
                                ncols=1,
                                sharex=True,
                                gridspec_kw={'hspace': 0.1},
                                figsize=(12, 9)
    )

    ax1.set_title(
        format_title(
            name=name,
            plot_name='Net Winnings',
            shoe_size=shoe_size,
            penetration=penetration,
            blackjack_payout=blackjack_payout,
            count_strategy=count_strategy,
            play_strategy=play_strategy,
            bet_strategy=bet_strategy,
            bet_spread=bet_spread,
            initial_bankroll=initial_bankroll,
            min_bet=min_bet,
            simulations=simulations
        )
    )

    ax1.bar(x=count[net_winnings > 0], height=net_winnings[net_winnings > 0] / simulations, color='b', width=width)
    ax1.bar(x=count[net_winnings < 0], height=net_winnings[net_winnings < 0] / simulations, color='r', width=width)
    ax1.set_ylabel('Net Winnings Per Shoe ($)')
    ax1.grid()

    ax2.plot(count, np.cumsum(net_winnings), color='k')
    ax2.set_ylabel('Cumulative Net Winnings ($)')
    ax2.set_xlabel(str(count_strategy) + ' True Count' if count_strategy in balanced_card_counting_systems else
                   str(count_strategy) + ' Running Count')
    ax2.grid()

    plt.show()



