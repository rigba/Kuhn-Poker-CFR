import time

from trainer import CFRTrainer
from game import KuhnGame
from rules import KuhnRules


def pause(seconds: float = 0.3) -> None:
    time.sleep(min(seconds, 0.5))


def ask_iterations() -> int:
    while True:
        try:
            n = int(input("How many iterations would you like to train on?: "))
            if n <= 0:
                print("Please enter a positive integer.")
                continue
            return n
        except ValueError:
            print("Please enter a valid integer.")


def ask_yes_no(prompt: str) -> bool:
    while True:
        response = input(prompt).strip().upper()
        if response in ("Y", "N"):
            return response == "Y"
        print("Please enter Y or N.")


def ask_action() -> int:
    while True:
        response = input("Would you like to pass or bet? P/B: ").strip().upper()
        if response in ("P", "B"):
            return KuhnRules.char_to_action(response.lower())
        print("Please enter Pass(P) or Bet(B).")


def main():
    print("Welcome to a Kuhn Poker CFR Implementation")
    pause(0.2)

    trainer = CFRTrainer()
    avg_value = trainer.train(ask_iterations())
    pause(0.2)
    print(f"Average game value: {avg_value}")
    trainer.print_strategies()

    pause(0.3)
    if not ask_yes_no("Would you like to play against the learnt strategy? Y/N: "):
        print("Very well, thank you for checking out my project!")
        return

    player_tally = 0
    bot_tally = 0
    human_first = True

    while True:
        print()
        pause(0.2)

        game = KuhnGame(trainer, human_first=human_first)
        game.deal()

        if human_first:
            print(f"You are first! You drew a {KuhnRules.card_to_name(game.player_card)}")
        else:
            print(f"You are second! You drew a {KuhnRules.card_to_name(game.player_card)}")

        pause(0.3)

        while not game.is_terminal():
            if game.current_player == 0:
                action = ask_action()
            else:
                print("Your opponent is thinking...")
                pause(0.5)
                action = game.bot_action()
                print(f"Your opponent chose to {KuhnRules.action_to_name(action)}")
                pause(0.3)

            game.apply_action(action)

        if game.history[-2:] == "bb":
            print("Showdown time...")
            pause(0.5)
            print(
                f"You drew a {KuhnRules.card_to_name(game.player_card)} "
                f"and your opponent drew a {KuhnRules.card_to_name(game.bot_card)}"
            )
            pause(0.3)

        payout = game.payout()

        if payout < 0:
            print("You lost this hand!")
        else:
            print("You won this hand!")

        pause(0.3)

        player_tally += payout
        bot_tally -= payout
        print(f"Total Scores: You: {player_tally}, Bot: {bot_tally}")

        pause(0.2)
        if not ask_yes_no("Would you like to play again? Y/N: "):
            break

        human_first = not human_first


if __name__ == "__main__":
    main()