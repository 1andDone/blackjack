import numpy as np
import matplotlib.pyplot as plt


def format_title(name, plot_name, shoe_size, penetration, blackjack_payout,
                 count_strategy, play_strategy, bet_strategy, bet_spread,
                 initial_bankroll, min_bet, simulations):
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
        name=name,
        plot_name=plot_name,
        shoe_size=shoe_size,
        penetration=int(penetration * 100) if (penetration * 100) - int(penetration * 100) == 0 else penetration * 100,
        blackjack_payout=blackjack_payout,
        count_strategy=count_strategy + ' Count, ' if count_strategy is not None else '',
        play_strategy='Basic Strategy' if play_strategy == 'Basic' else play_strategy,
        bet_strategy=', ' + bet_strategy + ' Bet' if bet_strategy == 'Flat' else '',
        bet_spread=', 1-' + str(int(bet_spread) if bet_spread - int(bet_spread) == 0
                                else bet_spread) + ' Bet Spread' if bet_strategy == 'Variable' else '',
        initial_bankroll='\${:.2f}'.format(int(initial_bankroll)) if initial_bankroll - int(initial_bankroll) == 0
        else '\${:.2f}'.format(initial_bankroll),
        min_bet='\${:.2f}'.format(int(min_bet)) if min_bet - int(min_bet) == 0 else '\${:.2f}'.format(min_bet),
        simulations=simulations)

    return title


def net_winnings_per_shoe(count, count_accuracy, net_winnings, name, shoe_size, penetration,
                          blackjack_payout, count_strategy, play_strategy, bet_strategy,
                          bet_spread, initial_bankroll, min_bet, simulations):
    """
    Creates a plot based on the player's counting strategy of their individual net winnings
    for each true or running count value they played a hand during.

    Parameters
    ----------
    count : float
        Current true or running count based on the player's counting strategy
    count_accuracy : float
        Accuracy of player's counting strategy
    net_winnings : float
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
    # format width to be 80% of count accuracy
    if count_accuracy == 0.1:
        width = 0.08
    elif count_accuracy == 0.5:
        width = 0.4
    else:
        width = 0.8

    plt.figure(figsize=(12, 9))
    plt.bar(x=count[net_winnings > 0], height=net_winnings[net_winnings > 0] / simulations, color='b', width=width)
    plt.bar(x=count[net_winnings < 0], height=net_winnings[net_winnings < 0] / simulations, color='r', width=width)
    plt.xlabel(str(count_strategy) + ' Count')
    plt.ylabel('Net Winnings Per Shoe ($)')
    plt.title(
        format_title(
            name=name,
            plot_name='Net Winnings Per Shoe',
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
    plt.grid()
    plt.show()


def cumulative_net_winnings_per_shoe(count, net_winnings, name, shoe_size, penetration,
                                     blackjack_payout, count_strategy, play_strategy,
                                     bet_strategy, bet_spread, initial_bankroll,
                                     min_bet, simulations):
    """
    Creates a plot based on the player's counting strategy of their individual cumulative
    net winnings over each true or running count value they played a hand during.

    Parameters
    ----------
    count : float
        Current true or running count based on the player's counting strategy
    net_winnings : float
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
    plt.figure(figsize=(12, 9))
    plt.plot(count, np.cumsum(net_winnings) / simulations)
    plt.xlabel(str(count_strategy) + ' Count')
    plt.ylabel('Net Winnings Per Shoe')
    plt.title(
        format_title(
                name=name,
                plot_name='Cumulative Net Winnings per Shoe',
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
    plt.grid()
    plt.show()


def bankroll_growth(bankroll, shoe_num, name, shoe_size, penetration, blackjack_payout, count_strategy,
                    play_strategy, bet_strategy, bet_spread, initial_bankroll, min_bet, simulations):
    """
    Creates a plot of a player's bankroll growth over the course of many shoe simulations.

    Parameters
    ----------
    bankroll : float
        Amount of money a player currently has
    shoe_num : int
        Current shoe number
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
    plt.figure(figsize=(12, 9))
    plt.plot(shoe_num, bankroll)
    plt.xlabel('Number of Shoes Played')
    plt.ylabel('Bankroll ($)')
    plt.xlim(0, max(shoe_num) + 0.01 * max(shoe_num))
    plt.title(
        format_title(
            name=name,
            plot_name='Bankroll Growth',
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
    plt.grid()
    plt.show()

