from counts import count_dict


class CountingStrategy(object):
    """
    CountingStrategy is an object that represents the card counting strategy used by
    a player at the table in order to make informed betting decisions.

    """
    def __init__(self, cards):
        """
        Parameters
        ----------
        cards : Cards
            Cards class instance
        """
        self.cards = cards
        running_count_dict = {}
        for strategy in ['Hi-Lo', 'Hi-Opt I', 'Hi-Opt II', 'Omega II', 'Halves', 'Zen Count']:
            running_count_dict[strategy] = 0
        self.running_count_dict = running_count_dict

    def update_running_count(self):
        for strategy in ['Hi-Lo', 'Hi-Opt I', 'Hi-Opt II', 'Omega II', 'Halves', 'Zen Count']:
            for card in self.cards.get_visible_cards():
                self.running_count_dict[strategy] += count_dict[strategy].get(card)

    def running_count(self, strategy):
        if strategy not in ['Hi-Lo', 'Hi-Opt I', 'Hi-Opt II', 'Omega II', 'Halves', 'Zen Count']:
            raise ValueError('Strategy must be "Hi-Lo", "Hi-Opt I", "Hi-Opt II", "Omega II", "Halves", or "Zen Count".')
        return self.running_count_dict[strategy]

    def true_count(self, strategy, accuracy=0.5):
        if strategy not in ['Hi-Lo', 'Omega II', 'Halves', 'Zen Count']:
            raise ValueError('Strategy must be "Hi-Lo", "Omega II", "Halves", or "Zen Count".')
        if accuracy not in [0.1, 0.5, 1]:
            raise ValueError('Accuracy of true count must be to the nearest 0.1, 0.5, or 1.')
        if accuracy == 0.1:
            return round(self.running_count(strategy=strategy)/self.cards.remaining_decks(), 1)
        elif accuracy == 0.5:
            return round((self.running_count(strategy=strategy)/self.cards.remaining_decks()) * 2, 0)/2
        else:
            return round(self.running_count(strategy=strategy)/self.cards.remaining_decks(), 0)