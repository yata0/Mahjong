# coding=utf-8
import copy
import time
import sys, os
sys.path.append("..")
import random
from p2_mahjong.p2_game import MahjongGame
from p2_mahjong.DEF import ActionLabelRange, DIC_CHOW_LABEL2CARD, ActionType, DIC_CHOW_ACTION_STR2LABEL

import numpy as np
from p2_mahjong.calculate_fan import calculate_fan
SAMPLE_CARDS_LIST = 8 * [34*[0]] + 2 * [8*[0]] + [[0]]
SAMPLE_ACTIONS_LIST = 2 * [50*[0]] + 2 * [1*[0]]
CARD_FEATURE_NUM = len(SAMPLE_CARDS_LIST[0])
ACTION_FEATURE_NUM = len(SAMPLE_ACTIONS_LIST[0])
FLOWER_TILE_NUM = 8

log_head = "wrapper.py"
WRAPPER_DEBUG = False


class MJWrapper(object):
    PLAYERS_NUM = 2
    N_ACTIONS = 238

    def __init__(self, game_id=""):
        func_head = "__init__()"
        self.game_id = game_id
        self.game = MahjongGame(game_id=self.game_id)
        self.state, self.button, self.initial_deck = self.game.init_game(True, None)
        self.is_game_over = False
        self.rewards = [0] * MJWrapper.PLAYERS_NUM
        self.winner_id = None

        self.dic_func2cnt = dict()
        self.dic_func2time = dict()
        pass

    @staticmethod
    def get_action_num():
        return MJWrapper.N_ACTIONS

    def get_result(self, state):
        if state is None:
            assert False
        if state['winner'] is not None:
            score, fan_names, fan_scores,hu_cards_dict = calculate_fan(state, state['winner'], self.game_id)
            return score, fan_names, fan_scores,hu_cards_dict
        return None, None, None,None

    def get_game_status(self):
        is_over = self.game.is_over(self.state)
        winner = None
        if is_over:
            winner = self.game.winner
        return is_over, winner

    def get_payoffs(self):
        func_head = "get_payoffs()" + self.game_id
        _done, self.winner_id = self.get_game_status()
        if not _done:
            return [0] * MJWrapper.PLAYERS_NUM, [], []
        else:
            if self.winner_id is None:
                return [0] * MJWrapper.PLAYERS_NUM, [], []
            elif 0 <= self.winner_id < MJWrapper.PLAYERS_NUM:
                score, fan_names, fan_score, hu_cards_dict = calculate_fan(self.state, self.winner_id, self.game_id)
                pay_off = [0] * MJWrapper.PLAYERS_NUM
                pay_off[self.winner_id] = score
                pay_off[1-self.winner_id] = 0 - score
                return pay_off, fan_names, fan_score
            else:
                print(log_head, func_head, "winner_id=", self.winner_id)
                assert False
        pass

    def reset(self, reset_deck=True):
        func_head = "reset()"
        self.game = MahjongGame(reset_deck)
        self.state, self.button, self.initial_deck = self.game.init_game(reset_deck, self.initial_deck)
        self.is_game_over = False
        self.rewards = [0] * MJWrapper.PLAYERS_NUM
        self.winner_id = None

        return self.get_cards(self.state), self.get_actions(self.state), self.get_legal_actions()

    def state_dict(self):
        return self.get_state()


    def get_state(self):
        func_head = "get_state()"
        state = dict()
        state["current_player_id"] = self.get_current_player()
        state["player0"] = self.game.players[0].get_state()
        state["player1"] = self.game.players[1].get_state()
        state["state"] = self.dump_game_state()
        state["round"] = self.game.round.dump_state()
        state["dealer"] = self.game.dealer.get_state()
        return state

    def print_state(self):
        func_head = "print_state()"
        state = dict()
        for k, v in sorted(state.items()):
            print(k + ':' + str(v))

    def load_state_dict(self, state):
        self.load_state(state)

    def load_state(self, state):
        """
        """
        func_head = "load_state()"
        self.game.players[0].load_state(state["player0"])
        self.game.players[1].load_state(state["player1"])
        self.restore_game_state(state["state"])
        self.game.dealer.load_state(state["dealer"])
        self.game.round.load_state(state["round"])
        return

    def trans_action_from_obj2label(self, mahjong_action):
        func_head = "trans_action_from_obj2label()" + self.game_id
        action_label = -1
        if mahjong_action.action == ActionType.ActionTypeChow:
            action_label = DIC_CHOW_ACTION_STR2LABEL[mahjong_action.action_str]
        elif mahjong_action.action == ActionType.ActionTypePong:
            action_label = ActionLabelRange.ACTION_PONG_BEG + mahjong_action.target_card.get_card_id()
        elif mahjong_action.action == ActionType.ActionTypeGong:
            action_label = ActionLabelRange.ACTION_GONG_BEG + mahjong_action.target_card.get_card_id()
        elif mahjong_action.action == ActionType.ActionTypeDiscard:
            action_label = ActionLabelRange.ACTION_DISCARD_BEG + mahjong_action.target_card.get_card_id()
        elif mahjong_action.action == ActionType.ActionTypeConcealedGong:
            action_label = ActionLabelRange.ACTION_CONCEALED_GONG_BEG + mahjong_action.target_card.get_card_id()
        elif mahjong_action.action == ActionType.ActionTypeWait:
            action_label = ActionLabelRange.ACTION_WAIT
        elif mahjong_action.action == ActionType.ActionTypeAddGong:
            action_label = ActionLabelRange.ACTION_ADD_GONG_BEG + mahjong_action.target_card.get_card_id()
        else:
            print("unknown_action=", mahjong_action.action)
            assert False
        return action_label

    def trans_actions_from_obj2label(self, mahjong_actions, num_ele=ACTION_FEATURE_NUM):
        lis_action_id = [-1] * num_ele
        idx = 0
        for action in mahjong_actions:
            lis_action_id[idx] = self.trans_action_from_obj2label(action)
            idx += 1
            if idx >= num_ele:
                break
        return lis_action_id

    def trans_cards_from_obj2label(self, mahjong_cards, num_ele=CARD_FEATURE_NUM):
        lis_card_id = [-1] * num_ele
        idx = 0
        for card in mahjong_cards[::-1]:
            lis_card_id[idx] = card.get_card_id()
            idx += 1
            if idx >= num_ele:
                break
        return lis_card_id

    def parse_action_label(self, action_label):
        func_head = "parse_action_label()" + self.game_id
        action_key = None
        action_val = None

        if ActionLabelRange.ACTION_PONG_BEG <= action_label <= ActionLabelRange.ACTION_PONG_END:
            action_key = ActionType.ActionTypePong
            action_val = action_label - ActionLabelRange.ACTION_PONG_BEG
        elif ActionLabelRange.ACTION_GONG_BEG <= action_label <= ActionLabelRange.ACTION_GONG_END:
            action_key = ActionType.ActionTypeGong
            action_val = action_label - ActionLabelRange.ACTION_GONG_BEG
        elif ActionLabelRange.ACTION_CONCEALED_GONG_BEG <= action_label <= ActionLabelRange.ACTION_CONCEALED_GONG_END:
            action_key = ActionType.ActionTypeConcealedGong
            action_val = action_label - ActionLabelRange.ACTION_CONCEALED_GONG_BEG
        elif ActionLabelRange.ACTION_ADD_GONG_BEG <= action_label <= ActionLabelRange.ACTION_ADD_GONG_END:
            action_key = ActionType.ActionTypeAddGong
            action_val = action_label - ActionLabelRange.ACTION_ADD_GONG_BEG
        elif ActionLabelRange.ACTION_CHOW_BEG <= action_label <= ActionLabelRange.ACTION_CHOW_END:
            action_key = ActionType.ActionTypeChow
            action_val = DIC_CHOW_LABEL2CARD[action_label][0:2]
        elif ActionLabelRange.ACTION_DISCARD_BEG <= action_label <= ActionLabelRange.ACTION_DISCARD_END:
            action_key = ActionType.ActionTypeDiscard
            action_val = action_label - ActionLabelRange.ACTION_DISCARD_BEG
        elif action_label == ActionLabelRange.ACTION_PASS:
            action_key = ActionType.ActionTypePass
        elif action_label == ActionLabelRange.ACTION_GET_CARD:
            action_key = ActionType.ActionTypeDraw
        elif action_label == ActionLabelRange.ACTION_HU:
            action_key = ActionType.ActionTypeHu
        elif action_label == ActionLabelRange.ACTION_PASS_HU:
            action_key = ActionType.ActionTypePassHu
        elif action_label == ActionLabelRange.ACTION_WAIT:
            action_key = ActionType.ActionTypeWait
        else:
            print(log_head, func_head, "unknown_action_label=", action_label)
            assert False
        return action_key, action_val

    def step(self, action_label):
        func_head = "step()" + self.game_id
        action_key, action_val = self.parse_action_label(action_label[0])

        self.state, cur_player = self.game.step(action_key, action_val)
        self.is_game_over = self.game.is_over(self.state)
        self.rewards, _, _ = self.get_payoffs()
        return self.get_cards(self.state), self.get_actions(self.state), self.rewards, self.is_game_over, self.get_legal_actions()

    def get_current_obs(self):
        func_head = "get_current_obs()" + self.game_id
        card = self.get_cards(self.state)
        action = self.get_actions(self.state)
        return card, action

    def get_cards(self, state):
        func_head = "get_cards()" + self.game_id
        cur_player = self.get_current_player()
        next_player = self.get_next_player()

        lis_cards = list()
        # self hand cards
        lis_cards.append(self.trans_cards_from_obj2label(state['current_hand']
                                                         , num_ele=CARD_FEATURE_NUM))
        # self piles
        cur_pile = []
        for t in state['players_pile'][cur_player]:
            cur_pile += t
        lis_cards.append(self.trans_cards_from_obj2label(cur_pile
                                                         , num_ele=CARD_FEATURE_NUM))

        # self concealed kongs
        cur_hidden_pile = []
        for t in state['players_hidden_pile'][cur_player]:
            cur_hidden_pile += t
        lis_cards.append(self.trans_cards_from_obj2label(cur_hidden_pile
                                                         , num_ele=CARD_FEATURE_NUM))
        # self history cards
        lis_cards.append(self.trans_cards_from_obj2label(state['history_cards'][cur_player]
                                                         , num_ele=CARD_FEATURE_NUM))

        # opponent hand cards
        lis_cards.append(self.trans_cards_from_obj2label(state['players_hand'][next_player]
                                                         , num_ele=CARD_FEATURE_NUM))
        # opponent pile cards
        next_pile = []
        for t in state['players_pile'][next_player]:
            next_pile += t
        lis_cards.append(self.trans_cards_from_obj2label(next_pile
                                                         , num_ele=CARD_FEATURE_NUM))
        # opponent concealed kongs
        next_hidden_pile = []
        for t in state['players_hidden_pile'][next_player]:
            next_hidden_pile += t
        lis_cards.append(self.trans_cards_from_obj2label(next_hidden_pile
                                                         , num_ele=CARD_FEATURE_NUM))

        # opponent history cards
        lis_cards.append(self.trans_cards_from_obj2label(state['history_cards'][next_player]
                                                         , num_ele=CARD_FEATURE_NUM))

        # last table card
        if len(state['table']) <= 0:
            lis_cards.append(self.trans_cards_from_obj2label([], num_ele=1))
        else:
            lis_cards.append(self.trans_cards_from_obj2label([state['table'][-1]], num_ele=1))

        # self flower cards
        lis_cards.append(self.trans_cards_from_obj2label(state['players_flower'][cur_player]
                                                         , num_ele=FLOWER_TILE_NUM))
        # opponent flower cards
        lis_cards.append(self.trans_cards_from_obj2label(state['players_flower'][next_player]
                                                         , num_ele=FLOWER_TILE_NUM))
        return lis_cards

    def get_actions(self, state):
        func_head = "get_actions()" + self.game_id
        cur_player = self.get_current_player()
        next_player = self.get_next_player()
        actions = list()
        actions.append(self.trans_actions_from_obj2label(state['history_action'][cur_player][::-1]
                                                         , num_ele=ACTION_FEATURE_NUM))
        actions.append(self.trans_actions_from_obj2label(state['history_action'][next_player][::-1]
                                                         , num_ele=ACTION_FEATURE_NUM))

        actions.append([1 if state["players_wait"][cur_player] is True else 0])
        actions.append([1 if state["players_wait"][next_player] is True else 0])

        return actions

    def get_current_player(self):
        return self.game.get_player_id()


    def get_next_player(self):
        player_idx = self.get_current_player()
        next_player_id = (player_idx + 1) % self.PLAYERS_NUM
        return next_player_id


    def get_legal_actions(self):
        """
        获取action_label
        """
        func_head = "get_legal_actions()" + self.game_id
        t0 = time.time()
        dic_legal_action = self.game.get_legal_actions(self.state, game_id=self.game_id)
        lis_action_label = list()

        for action_type in dic_legal_action:
            card_ids = dic_legal_action[action_type]
            if action_type == ActionType.ActionTypeDiscard:
                for card_id in card_ids:
                    lis_action_label.append(ActionLabelRange.ACTION_DISCARD_BEG + card_id)
            elif action_type == ActionType.ActionTypePass:
                lis_action_label.append(ActionLabelRange.ACTION_PASS)
            elif action_type == ActionType.ActionTypePong:
                for card_id in card_ids:
                    lis_action_label.append(ActionLabelRange.ACTION_PONG_BEG + card_id)
            elif action_type == ActionType.ActionTypeGong:
                for card_id in card_ids:
                    lis_action_label.append(ActionLabelRange.ACTION_GONG_BEG + card_id)
            elif action_type == ActionType.ActionTypeConcealedGong:
                for card_id in card_ids:
                    lis_action_label.append(ActionLabelRange.ACTION_CONCEALED_GONG_BEG + card_id)
            elif action_type == ActionType.ActionTypeAddGong:
                for card_id in card_ids:
                    lis_action_label.append(ActionLabelRange.ACTION_ADD_GONG_BEG + card_id)
            elif action_type == ActionType.ActionTypeChow:
                for chow_action in card_ids:
                    assist_card0_id, assist_card1_id, target_card_id = chow_action
                    action_str = "%d,%d,%d" % (assist_card0_id, assist_card1_id, target_card_id)
                    lis_action_label.append(DIC_CHOW_ACTION_STR2LABEL[action_str])
            elif action_type == ActionType.ActionTypeHu:
                lis_action_label.append(ActionLabelRange.ACTION_HU)
            elif action_type == ActionType.ActionTypeDraw:
                lis_action_label.append(ActionLabelRange.ACTION_GET_CARD)
            elif action_type == ActionType.ActionTypePassHu:
                lis_action_label.append(ActionLabelRange.ACTION_PASS_HU)
            elif action_type == ActionType.ActionTypeWait:
                lis_action_label.append(ActionLabelRange.ACTION_WAIT)
            else:
                print(log_head, func_head, "unknown action_type=", action_type)
                assert False
        return lis_action_label

