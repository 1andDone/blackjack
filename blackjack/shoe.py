from collections import Counter
import random
from blackjack.enums import CardCountingSystem
from blackjack.source.card_counting_systems import COUNT_VALUES, INITIAL_COUNTS


class Shoe:
    """
    Represents a shoe of cards.

    """
    def __init__(self, shoe_size: int):
        """
        Parameters
        ----------
        shoe_size
            Number of decks used during a blackjack game

        """
        if not 1 <= shoe_size <= 8 :
            raise ValueError('Shoe size must be between 1 and 8 decks.')

        self._shoe_size = shoe_size
        self._cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4 * self._shoe_size
        self._total_cards = len(self._cards)
        self._seen_cards: Counter[str] = Counter()

    @property
    def cards(self) -> list[str]:
        return self._cards

    def burn_card(self, seen: bool = False) -> None:
        card = self._cards.pop()
        if seen:
            self.add_to_seen_cards(card=card)

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
        ratio = len(self._cards) / 52
        if ratio >= 0.75:
            return round(ratio, 0)
        if 0.25 < ratio < 0.75:
            return 0.5
        return 0.25

    def cut_card_reached(self, penetration: float) -> bool:
        used_cards = self._total_cards - len(self._cards)
        return (used_cards / self._total_cards) >= penetration

    def running_count(self, card_counting_system: CardCountingSystem) -> float | int:
        running_count = sum(COUNT_VALUES[card_counting_system][card] * self._seen_cards[card] for card in self._seen_cards)
        starting_count = INITIAL_COUNTS[card_counting_system] * (self._shoe_size - 1)
        return running_count + starting_count

    def true_count(self, card_counting_system: CardCountingSystem) -> float | int:
        if card_counting_system == CardCountingSystem.KO:
            raise ValueError('"true_count" is only applicable for balanced card counting systems.')
        result = round(self.running_count(card_counting_system=card_counting_system) / self.remaining_decks, 0)
        return 0 if result == 0 else result
