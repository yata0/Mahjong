import os
import sys
import random
import numpy as np
from p2_mahjong.wrapper import MJWrapper as Wrapper

if __name__ == "__main__":
    wrapper = Wrapper()
    is_game_over = False
    index = 0
    game_count = 1000
    for game_index in range(game_count):
        is_game_over = False
        wrapper.reset()
        legal_actions = wrapper.get_legal_actions()
        while not is_game_over:
            action_label = random.choice(legal_actions)
            cards, actions, reward, is_game_over, legal_actions = wrapper.step([action_label])
            if is_game_over:
                _, winner_id = wrapper.get_game_status()
                if winner_id is not None:
                    print(game_index, wrapper.get_payoffs())
                else:
                    print(game_index, "tie")
            index += 1