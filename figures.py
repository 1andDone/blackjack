import matplotlib.pyplot as plt

# TODO make plot size bigger -- figsize
# TODO plot distribution of end bankroll amounts
# TODO run simulations and make plots for more than one player
# TODO Make titles automatic
# TODO create graphics for every player

# figure 1
plt.figure()
plt.bar(x=true_count[net_winnings > 0], height=net_winnings[net_winnings > 0]/simulations, color='b', width=0.2)
plt.bar(x=true_count[net_winnings < 0], height=net_winnings[net_winnings < 0]/simulations, color='r', width=0.2)
plt.xlabel('Hi-Lo True count')
plt.ylabel('Net Winnings per Shoe (Dollars)')
plt.title('Player vs. Dealer Bar Plot: \n'
          'Shoe Size 6, 75% Deck Penetration, \n'
          'Variable $10, ' + str(r.blackjack_payout) + ' Blackjack Payout, \n' +
          str(simulations) + ' Shoe Simulations')
plt.grid()
plt.show()

# figure 2
plt.figure()
plt.plot(true_count, np.cumsum(net_winnings)/simulations)
plt.xlabel('Hi-Lo True Count')
plt.ylabel('Net Winnings per Shoe (Dollars)')
plt.title('Player vs. Dealer Cumulative Sum: \n'
          'Shoe Size 6, 75% Deck Penetration, \n'
          'Variable $10, ' + str(r.blackjack_payout) + ' Blackjack Payout, \n' +
          str(simulations) + ' Shoe Simulations')
plt.grid()
plt.show()

# figure 3
plt.figure()
plt.plot(true_count[num_hands > 10000],
         (player_natural_blackjack[num_hands > 10000] +
          player_showdown_win[num_hands > 10000] +
          dealer_bust[num_hands > 10000]) /
         (num_hands[num_hands > 10000] - push[num_hands > 10000]))
plt.xlabel('Hi-Lo True Count')
plt.ylabel('Player Win Percentage')
plt.title('Player vs. Dealer Win Percentage: \n'
          'Shoe Size 6, 75% Deck Penetration, \n'
          'Variable $10, ' + str(r.blackjack_payout) + ' Blackjack Payout, \n' +
          str(simulations) + ' Shoe Simulations')
plt.grid(axis='y')
plt.show()

# figure 4
plt.figure()
x = [1, 2, 3, 4, 5, 6, 7, 8]
y = [np.sum(player_natural_blackjack + player_showdown_win + dealer_bust)/np.sum(num_hands),
     np.sum(dealer_natural_blackjack + dealer_showdown_win + player_bust + player_surrender)/np.sum(num_hands),
     np.sum(push)/np.sum(num_hands),
     np.sum(dealer_bust)/np.sum(num_hands),
     np.sum(player_bust)/np.sum(num_hands),
     np.sum(player_surrender)/np.sum(num_hands),
     np.sum(dealer_natural_blackjack)/np.sum(num_hands),
     np.sum(player_natural_blackjack)/np.sum(num_hands)]
plt.bar(x=x, height=y, width=0.2, color='b')
plt.xticks([1, 2, 3, 4, 5, 6, 7, 8], ['Player Win', 'Dealer Win', 'Push', 'Dealer Bust', 'Player Bust', 'Surrender',
                                      'Dealer Natural', 'Player Natural'])
plt.ylabel('Percentage')
plt.title('Overall Winning Percentages for Player vs. Dealer over \n' +
          str(simulations) + ' Shoe Simulations')
for i in range(len(y)):
    plt.annotate('{:.2%}'.format(y[i]), xy=(x[i] - 0.1, y[i] + 0.005))
plt.grid(axis='y')
plt.show()