import random
from tqdm import tqdm

PASS, BET, NUM_ACTIONS = 0, 1, 2

class Node:
    def __init__(
        self,
        info_set: str = "",
        regret_sum: list[float] | None = None,
        strategy: list[float] | None = None,
        strategy_sum: list[float] | None = None,
    ):
        self.info_set = info_set
        self.regret_sum = regret_sum if regret_sum is not None else [0.0] * NUM_ACTIONS
        self.strategy = strategy if strategy is not None else [0.0] * NUM_ACTIONS
        self.strategy_sum = strategy_sum if strategy_sum is not None else [0.0] * NUM_ACTIONS

    def get_strategy(self, realization_weight):
        normalizing_sum = 0

        for i in range(NUM_ACTIONS):
            self.strategy[i] = self.regret_sum[i] if self.regret_sum[i] > 0 else 0
            normalizing_sum += self.strategy[i]

        for j in range(NUM_ACTIONS):
            if normalizing_sum > 0:
                self.strategy[j] /= normalizing_sum
            else:
                self.strategy[j] = 1.0 / NUM_ACTIONS
            self.strategy_sum[j] += realization_weight * self.strategy[j]
        return self.strategy

    def get_avg_strategy(self):
        avg_strategy = [0.0] * NUM_ACTIONS
        normalizing_sum = 0

        for i in range(NUM_ACTIONS):
            normalizing_sum += self.strategy_sum[i]

        for j in range(NUM_ACTIONS):
            if normalizing_sum > 0:
                avg_strategy[j] = self.strategy_sum[j] / normalizing_sum
            else:
                avg_strategy[j] = 1.0 / NUM_ACTIONS
        return avg_strategy

    def __str__(self) -> str:
        return f"{self.info_set:>4}: {self.get_avg_strategy()}"


node_map: dict[str, Node] = {}


def train(iterations: int):
    cards = [1, 2, 3]
    util = 0.0
    
    for _ in tqdm(range(iterations), desc="Training CFR..."):
        random.shuffle(cards)
        util += cfr(cards, "", 1, 1)

    print("Average Game Value" + str(util / iterations))
    for node in node_map.values():
        print(node)


def cfr(cards: list[int], history: str, p0: float, p1: float) -> float:
    plays = len(history)
    player = plays % 2  # get curr play index
    opponent = 1 - player
    is_player_card_higher = cards[player] > cards[opponent]
    # return payoff for terminal states
    if plays > 1: 
        terminal_pass = history[-1:] == "p"
        double_bet = history[-2:] == "bb"   
        if terminal_pass:
            if history == "pp":
                return 1 if is_player_card_higher else -1
            else:
                return 1
        elif double_bet:
            return 2 if is_player_card_higher else -2

    # get infoset node or create
    info_set = str(cards[player]) + history
    node = node_map.get(info_set)
    if node is None:
        node = Node()
        node.info_set = info_set
        node_map[info_set] = node

    # for each action recursively call cfr with additional history and probability
    strategy = node.get_strategy(p0 if player == 0 else p1)
    util = [0.0] * NUM_ACTIONS
    node_util = 0

    for i in range(NUM_ACTIONS):
        next_history = history + ("p" if i == 0 else "b")
        util[i] = (
            -cfr(cards, next_history, p0 * strategy[i], p1)
            if player == 0
            else -cfr(cards, next_history, p0 , p1 * strategy[i])
        )
        node_util += strategy[i] * util[i]

    # for each action compute and accumulate cfr
    for j in range(NUM_ACTIONS):
        regret = util[j] - node_util
        node.regret_sum[j] += (p1 if player == 0 else p0) * regret

    return node_util


train(1000000)
    

            

    