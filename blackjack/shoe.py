from collections import Counter
import random
from blackjack.enums import CardCountingSystem
from blackjack.source.card_counting_systems import COUNT_VALUES, INITIAL_COUNTS
from blackjack.source.remaining_decks import REMAINING_CARDS_TO_DECKS


class Shoe:
    """
    Represents a shoe of cards.

    """
    def __init__(self, shoe_size: int, penetration: float = 0.75):
        """
        Parameters
        ----------
        shoe_size
            Number of decks used during a blackjack game
        penetration
            The percentage of the shoe that is dealt
            before the shoe is re-shuffled

        """
        if not 1 <= shoe_size <= 8 :
            raise ValueError('Shoe size must be between 1 and 8 decks.')

        self._shoe_size = shoe_size
        self._cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4 * self._shoe_size
        self._total_cards = len(self._cards)
        self._cut_card_location = self._total_cards - int(penetration * self._total_cards)
        self._seen_cards: Counter[str] = Counter()

    @property
    def cards(self) -> list[str]:
        return self._cards

    def burn_card(self) -> None:
        card = self._cards.pop()

    def deal_card(self, seen: bool = True) -> str:
        card = self._cards.pop()
        if seen:
            self.add_to_seen_cards(card=card)
        return card
    
    def shuffle(self) -> None:
        random.shuffle(self._cards)
        self.burn_card()

    def add_to_seen_cards(self, card: str) -> None:
        key = '10-J-Q-K' if card in {'10', 'J', 'Q', 'K'} else card
        self._seen_cards[key] += 1

    @property
    def seen_cards(self) -> dict[str, int]:
        return self._seen_cards

    @property
    def remaining_decks(self) -> float | int:
        return REMAINING_CARDS_TO_DECKS[len(self._cards)]

    @property
    def cut_card_reached(self) -> bool:
        return len(self._cards) <= self._cut_card_location

    def running_count(self, card_counting_system: CardCountingSystem) -> float | int:
        running_count = sum(COUNT_VALUES[card_counting_system][card] * count for card, count in self._seen_cards.items())
        if card_counting_system == CardCountingSystem.KO:
            return running_count + INITIAL_COUNTS[card_counting_system] * (self._shoe_size - 1)
        return running_count

    def true_count(self, card_counting_system: CardCountingSystem) -> float | int:
        result = round(self.running_count(card_counting_system=card_counting_system) / self.remaining_decks, 0)
        return 0 if result == 0 else result
