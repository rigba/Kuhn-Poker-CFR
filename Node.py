from constants import NUM_ACTIONS 

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