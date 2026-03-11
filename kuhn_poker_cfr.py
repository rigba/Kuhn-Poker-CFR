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


print("Welcome to a Kuhn Poker CFR Implementation")

iterations = -1

while True:
    try:
        iterations = int(input("How many iterations would you like to train on? (Recommendation: At least >100000 to reach approximately Nash Equillibrium): "))
        if iterations < 0:
            print("Please enter a non-negative integer.")
            continue
        break
    except ValueError:
        print("Please enter a valid integer.")

train(iterations)

response = ""

def card_no_as_royal(no):
    match no:
        case 1:
            return "Jack"
        case 2:
            return "Queen"
        case 3:
            return "King"
        case _:
            return "Invalid card"
        
def action_to_pass_bet(no, natural_language: bool):
    match no:
        case 0:
            return  "Pass" if natural_language else "p"
        case 1:
            return "Bet" if natural_language else "b"
        case _:
            return "Invalid Action"
        
def action_acronym_to_action_no(str):
    if str == "p":
        return 0
    if str == "b":
        return 1
    return -1
        
def pass_or_bet_input():
    while True:
        response = input("Would you like to pass or bet? P/B: ").upper()
        if response not in ("P", "B"):
            print("Please enter Pass(P) or Bet(B)")
            continue
        return response
            
def get_bot_action(strategy: list[float]): # map mixed strategy dist to action
    r = random.random()
    a: int = 0
    cumulative_probability: float = 0
    
    while(a < NUM_ACTIONS - 1):
        cumulative_probability += strategy[a]
        if (r < cumulative_probability):
            break
        a += 1
    
    return a

def is_terminal(history: str):
    return history in ["pp", "bp", "pbp", "bb"]

def get_payout(history: str, player_card: int, bot_card: int, who_is_first: int) -> int:
    is_player_card_higher = player_card > bot_card

    if history == "pp":
        return 1 if is_player_card_higher else -1
    elif history == "bb":
        return 2 if is_player_card_higher else -2
    elif history == "bp":
        return 1 if who_is_first == 0 else -1
    elif history == "pbp":
        return -1 if who_is_first == 0 else 1
    else:
        raise ValueError(f"Invalid terminal history: {history}")

while True:
    try:
        response = input("Would you like to play against the learnt strategy? Y/N: ")
        if response != "Y" and response != "N":
            print("Please enter Yes(Y) or No(N)")
            continue
        break
    except ValueError:
        print("Please enter Yes(Y) or No(N)")
        
if response == "N":
    print("Very well, thankyou for checking out my project!")
else:
    play_again = True
    player_tally = 0
    bot_tally = 0
    who_is_first = 0 # 0 human, 1 bot
    while play_again:
        cards = [1, 2, 3]
        random.shuffle(cards)
        player_card = cards[0]
        bot_card = cards[1]
        history = ""
        current_player = 0 if who_is_first == 0 else 1
        
        if who_is_first == 0:
            print("You are first! You drew a " + card_no_as_royal(player_card))
        else:
            print("You are second! You drew a " + card_no_as_royal(player_card))
            
        
        while not is_terminal(history):
            if current_player == 0:
                action = action_acronym_to_action_no(pass_or_bet_input().lower())
            else:
                action = get_bot_action(node_map[str(bot_card) + history].get_avg_strategy())
                print("Your opponent chose to " + action_to_pass_bet(action, True))

            history += action_to_pass_bet(action, False)
            current_player = 1 if current_player == 0 else 0
        
        
        if history[-2:] == "bb":
            print("Showdown time...*queue drum roll*")
            print("You drew a " + card_no_as_royal(player_card) + " and your opponent drew a " + card_no_as_royal(bot_card))
            
        if history[-1:] == "p":
            last_player = 1 if current_player == 0 else 0

            if last_player == 0:
                print("You played a terminal pass action.")
            else:
                print("The bot played a terminal pass action.")
                
        payout = get_payout(history, cards[:2])
        
        if payout < 0:
            print("You lost this hand!")
        else:
            print("You won this hand!")
            
        player_tally += payout
        bot_tally += -payout
        
        print(f"Total Scores: You: {player_tally}, Bot: {bot_tally}")
        
        play_again_input = ""
        
        while True:
            try:
                play_again_input = input("Would you like to play again? Y/N: ")
                if play_again_input != "Y" and play_again_input != "N":
                    print("Please enter Yes(Y) or No(N)")
                    continue
                break
            except ValueError:
                print("Please enter Yes(Y) or No(N)")
                
        if play_again_input == "Y":
            continue
        else:
            break
    

            

    