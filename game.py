import random

from rules import KuhnRules


class KuhnGame:
    def __init__(self, trainer, human_first: bool = True):
        self.trainer = trainer
        self.who_is_first = 0 if human_first else 1
        self.player_card = 0
        self.bot_card = 0
        self.history = ""
        self.current_player = self.who_is_first

    def deal(self) -> None:
        cards = [1, 2, 3]
        random.shuffle(cards)
        self.player_card = cards[0]
        self.bot_card = cards[1]
        self.history = ""
        self.current_player = self.who_is_first

    def bot_action(self) -> int:
        info_set = f"{self.bot_card}{self.history}"
        strategy = self.trainer.get_average_strategy(info_set)
        return self.sample_action(strategy)

    @staticmethod
    def sample_action(strategy: list[float]) -> int:
        r = random.random()
        cumulative = 0.0
        for action, prob in enumerate(strategy):
            cumulative += prob
            if r < cumulative:
                return action
        return len(strategy) - 1

    def apply_action(self, action: int) -> None:
        self.history += KuhnRules.action_to_char(action)
        self.current_player = 1 - self.current_player

    def is_terminal(self) -> bool:
        return KuhnRules.is_terminal(self.history)

    def payout(self) -> int:
        return KuhnRules.payout(
            self.history,
            self.player_card,
            self.bot_card,
            self.who_is_first,
        )