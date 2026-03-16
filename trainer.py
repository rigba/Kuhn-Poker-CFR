import random
from tqdm import tqdm
from Node import Node
from rules import KuhnRules


class CFRTrainer:
    def __init__(self):
        self.node_map: dict[str, Node] = {}

    def train(self, iterations: int) -> float:
        cards = [1, 2, 3]
        util = 0.0

        for _ in tqdm(range(iterations), desc="Training CFR..."):
            random.shuffle(cards)
            util += self.cfr(cards, "", 1.0, 1.0)

        return util / iterations

    def cfr(self, cards: list[int], history: str, p0: float, p1: float) -> float:
        plays = len(history)
        player = plays % 2
        opponent = 1 - player
        is_player_card_higher = cards[player] > cards[opponent]

        if plays > 1:
            terminal_pass = history[-1:] == "p"
            double_bet = history[-2:] == "bb"

            if terminal_pass:
                if history == "pp":
                    return 1 if is_player_card_higher else -1
                return 1
            elif double_bet:
                return 2 if is_player_card_higher else -2

        info_set = f"{cards[player]}{history}"
        node = self.node_map.get(info_set)
        if node is None:
            node = Node(info_set=info_set)
            self.node_map[info_set] = node

        strategy = node.get_strategy(p0 if player == 0 else p1)
        util = [0.0, 0.0]
        node_util = 0.0

        for action in range(2):
            next_history = history + KuhnRules.action_to_char(action)
            util[action] = (
                -self.cfr(cards, next_history, p0 * strategy[action], p1)
                if player == 0
                else -self.cfr(cards, next_history, p0, p1 * strategy[action])
            )
            node_util += strategy[action] * util[action]

        for action in range(2):
            regret = util[action] - node_util
            node.regret_sum[action] += (p1 if player == 0 else p0) * regret

        return node_util

    def get_average_strategy(self, info_set: str) -> list[float]:
        return self.node_map[info_set].get_avg_strategy()

    def print_strategies(self) -> None:
        for node in self.node_map.values():
            print(node)