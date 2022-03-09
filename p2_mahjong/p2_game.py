# coding=utf-8
import numpy as np
from copy import deepcopy
import sys
from p2_mahjong.dealer import MahjongDealer as Dealer
from p2_mahjong.player import MahjongPlayer as Player
from p2_mahjong.round import MahjongRound as Round
from p2_mahjong.DEF import ActionType
log_head = "game.py"


class MahjongGame(object):

    def __init__(self, allow_step_back=False, game_id=""):
        """Initialize the class MajongGame
        """
        self.num_players = 2
        self.allow_step_back = allow_step_back
        self.dealer = None
        self.players = list()
        self.round = None
        self.history = list()
        self.winner = None
        self.beg_card_num = 13  # 起始手牌数   3*4 + 2
        self.game_id = game_id



    def init_game(self, reset_deck=True, initial_deck=None):
        """ Initialize the game of Mahjong

        This version supports two-player Mahjong

        Returns:
            (tuple): Tuple containing:

                (dict): The first state of the game
                (int): Current player's id
        """
        func_head = "init_game()" + self.game_id
        # Initialize a dealer that can deal cards
        self.dealer = Dealer(game_id=self.game_id, reset_deck=reset_deck, initial_deck=initial_deck)
        initial_deck = self.dealer.deck.copy()

        # Initialize four players to play the game
        self.players = [Player(i, game_id=self.game_id) for i in range(self.num_players)]

        self.round = Round(game_id=self.game_id)

        # Deal 13 cards to each player to prepare for the game
        for player in self.players:
            deal_ret = self.dealer.deal_cards(player, self.beg_card_num)
            if deal_ret is False:
                print(log_head, func_head, "fail_in_deal_cards")
                assert False
        for player in self.players:
            deal_ret = self.dealer.replace_flower_tile(player)
            if deal_ret is False:
                print(log_head, func_head, "fail_in_replace_flower_tile")
                assert False
        # Save the history for stepping back to the last state.
        self.history = []

        self.dealer.deal_cards(self.players[self.round.current_player], 1)  # send one card to player0
        state = self.round.get_state(self.players, self.dealer)             # get player0 state
        return state, self.round.current_player, initial_deck

    def step(self, action_key, action_val):
        """ Get the next state

        Args:
            action_key (str): a specific action. (call, raise, fold, or check)
            action_val
        Returns:
            (tuple): Tuple containing:

                (dict): next player's state
                (int): next plater's id
        """
        func_head = "step()"
        if self.allow_step_back:
            hist_dealer = deepcopy(self.dealer)
            hist_round = deepcopy(self.round)
            hist_players = deepcopy(self.players)
            self.history.append((hist_dealer, hist_players, hist_round))
        self.round.proceed_round(self.players, self.dealer, action_key, action_val)

        state = self.round.get_state(self.players, self.dealer)
        return state, self.round.current_player

    def step_back(self):
        """ Return to the previous state of the game

        Returns:
            (bool): True if the game steps back successfully
        """
        if not self.history:
            return False
        self.dealer, self.players, self.round = self.history.pop()
        return True

    @staticmethod
    def get_legal_actions(state, game_id=""):
        """ Return the legal actions for current player

        Returns:
            (list): A list of legal actions
        """
        func_head = "get_legal_actions()" + game_id
        dic_ret = dict()
        for key in state["valid_act"]:

            if key == ActionType.ActionTypeDiscard:
                dic_ret[key] = state['play_cards']
            elif key == ActionType.ActionTypePong:
                dic_ret[key] = state["pong_cards"]
            elif key == ActionType.ActionTypeGong:
                dic_ret[key] = state["gong_cards"]
            elif key == ActionType.ActionTypeConcealedGong:
                dic_ret[key] = state["concealed_gong_cards"]
            elif key == ActionType.ActionTypeAddGong:
                dic_ret[key] = state["add_gong_cards"]
            elif key == ActionType.ActionTypeChow:
                dic_ret[key] = state["chow_cards"]
            elif key == ActionType.ActionTypeHu:
                dic_ret[key] = 1
            elif key == ActionType.ActionTypePass:
                dic_ret[key] = 1
            elif key == ActionType.ActionTypeDraw:
                dic_ret[key] = 1
            elif key == ActionType.ActionTypePassHu:
                dic_ret[key] = 1
            elif key == ActionType.ActionTypeWait:
                dic_ret[key] = 1
            else:
                print(log_head, func_head, "unknown_act_key=", key)
                assert False
        return dic_ret

    @staticmethod
    def get_action_num():
        """ Return the number of applicable actions

        Returns:
            (int): The number of actions. There are 4 actions (call, raise, check and fold)
        """
        return 38

    def get_player_num(self):
        """ return the number of players in Mahjong

        returns:
            (int): the number of players in the game
        """
        return self.num_players

    def get_player_id(self):
        """ return the id of current player in Mahjong

        returns:
            (int): the number of players in the game
        """
        return self.round.current_player

    def is_over(self, state):
        """ Check if the game is over

        Returns:
            (boolean): True if the game is over
        """
        self.winner = state["winner"]
        is_over = state["is_over"]
        return is_over


    def is_self_drawn(self):
        if self.winner is not None:
            return self.players[self.winner].hand[-1].user_id == self.winner
        return False