class KuhnRules:
    TERMINAL_HISTORIES = {"pp", "bp", "pbp", "bb", "pbb"}

    @staticmethod
    def is_terminal(history: str) -> bool:
        return history in KuhnRules.TERMINAL_HISTORIES

    @staticmethod
    def card_to_name(card: int) -> str:
        return {1: "Jack", 2: "Queen", 3: "King"}.get(card, "Invalid card")

    @staticmethod
    def action_to_char(action: int) -> str:
        return {0: "p", 1: "b"}[action]

    @staticmethod
    def action_to_name(action: int) -> str:
        return {0: "Pass", 1: "Bet"}[action]

    @staticmethod
    def char_to_action(action: str) -> int:
        return {"p": 0, "b": 1}[action.lower()]

    @staticmethod
    def payout(history: str, player_card: int, bot_card: int, who_is_first: int) -> int:
        is_player_card_higher = player_card > bot_card

        if history == "pp":
            return 1 if is_player_card_higher else -1
        if history in ("bb", "pbb"):
            return 2 if is_player_card_higher else -2
        if history == "bp":
            return 1 if who_is_first == 0 else -1
        if history == "pbp":
            return -1 if who_is_first == 0 else 1

        raise ValueError(f"Invalid terminal history: {history}")