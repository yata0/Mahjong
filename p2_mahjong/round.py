# coding=utf-8
import sys
from p2_mahjong.judger import MahjongJudger as Judger
from p2_mahjong.DEF import ActionType
log_head = "round.py "


class MahjongRound(object):

    def __init__(self, game_id=""):
        """ Initialize the round class
        """
        self.current_player = 0
        self.is_over = False
        self.winner = None
        self.lis_pid_order = []
        self.game_id = game_id

    def dump_state(self):
        dic_state = dict()
        dic_state["current_player"] = self.current_player
        dic_state["is_over"] = self.is_over
        dic_state["winner"] = self.winner
        dic_state["pid_order"] = self.lis_pid_order.copy()
        dic_state["pid2action"] = {}
        for pid in self.dic_pid2action:
            dic_state["pid2action"][pid] = dict()
            for action in self.dic_pid2action[pid]:
                if isinstance(self.dic_pid2action[pid][action], int):
                    dic_state["pid2action"][pid][action] = self.dic_pid2action[pid][action]
                else:
                    dic_state["pid2action"][pid][action] = self.dic_pid2action[pid][action].copy()
        return dic_state

    def load_state(self, state_dic):
        self.current_player = state_dic["current_player"]
        self.is_over = state_dic["is_over"]
        self.winner = state_dic["winner"]
        self.lis_pid_order = state_dic["pid_order"].copy()

        self.dic_pid2action = {}
        for pid in state_dic["pid2action"]:
            self.dic_pid2action[pid] = dict()
            for action in state_dic["pid2action"][pid]:
                if isinstance(state_dic["pid2action"][pid][action], int):
                    self.dic_pid2action[pid][action] = state_dic["pid2action"][pid][action]
                else:
                    self.dic_pid2action[pid][action] = state_dic["pid2action"][pid][action].copy()
        return

    def init_pid_order(self, lis_pid_order):
        assert isinstance(lis_pid_order, list)
        self.lis_pid_order = lis_pid_order
        return

    def proceed_round(self, players, dealer, action_key, action_val):
        """ Call other Classes's functions to keep one round running

        Args:
            players (object): object of MJPlayer
            dealer (object): object of Dealer
            action_key (str): string of legal action
            action_val (str):
        Return:
            (bool): indicates whether this round is done or not.
                    False only if the dealer has no card in deck when according to the rules
        """
        func_head = "proceed_round()" + self.game_id
        dealer_ret = True
        if action_key == ActionType.ActionTypePass:
            cur_index = self.lis_pid_order.index(self.current_player)
            next_user = self.lis_pid_order[cur_index + 1]
            self.current_player = next_user

        elif action_key == ActionType.ActionTypePassHu:

            players[self.current_player].pass_hu()
            if len(players[self.current_player].valid_act) == 0:
                cur_index = self.lis_pid_order.index(self.current_player)
                next_user = self.lis_pid_order[cur_index + 1]
                self.current_player = next_user
            elif len(players[self.current_player].valid_act) == 1 and ActionType.ActionTypeDraw in players[self.current_player].valid_act:
                dealer_ret = players[self.current_player].draw_card(dealer)
        elif action_key == ActionType.ActionTypeWait:
            players[self.current_player].wait_cards()

        elif action_key == ActionType.ActionTypeGong:
            players[self.current_player].gong_card(dealer, action_val)  # gong_card_id
            dealer_ret = players[self.current_player].draw_card(dealer)

        elif action_key == ActionType.ActionTypeConcealedGong:
            players[self.current_player].concealed_gong_card(action_val)  # gong_card_id
            dealer_ret = players[self.current_player].draw_card(dealer)

        elif action_key == ActionType.ActionTypeAddGong:
            players[self.current_player].gong_card(dealer, action_val)
            self.lis_pid_order = Judger.is_rob_gong_card(players, self.current_player, self.game_id)
            if len(self.lis_pid_order) > 0:
                self.current_player = self.lis_pid_order[0]
            else:
                dealer_ret = players[self.current_player].draw_card(dealer)  # get_one_new_card_from_dealer

        elif action_key == ActionType.ActionTypePong:
            players[self.current_player].pong_card(dealer, action_val)  # pong_card_id

        elif action_key == ActionType.ActionTypeChow:
            players[self.current_player].chow_card(dealer, action_val)  # assist_card_ids

        elif action_key == ActionType.ActionTypeDiscard:
            players[self.current_player].play_card_id(dealer, action_val)
            assert(len(players[self.current_player].hand) % 3 == 1)
            card_to_use = dealer.get_table_top()
            self.lis_pid_order = Judger.is_target_card(players, self.current_player, card_to_use, self.game_id)

            if len(self.lis_pid_order) > 0:
                self.current_player = self.lis_pid_order[0]
            else:
                next_player = players[self.current_player].get_next_player()
                self.current_player = next_player
                dealer_ret = players[self.current_player].draw_card(dealer)

        elif action_key == ActionType.ActionTypeDraw:
            dealer_ret = players[self.current_player].draw_card(dealer)  # get_one_new_card_from_dealer

        elif action_key == ActionType.ActionTypeHu:
            if players[self.current_player].rob_gong_card is not None:
                players[players[self.current_player].rob_gong_card.user_id].\
                    remove_kong(players[self.current_player].rob_gong_card)
                players[self.current_player].is_rob_the_gong = True
            players[self.current_player].hu(dealer)
            self.is_over = True
            self.winner = self.current_player

        else:
            assert False

        if dealer_ret is False:
            self.is_over = True
            return False
        return True

    def get_state(self, players, dealer):
        """ Get player's state

        Args:
            dealer (object):
            players (list): The list of MahjongPlayer
        Return:
            state (dict): The information of the state
        """
        func_head = "get_state()" + self.game_id
        player_id = self.current_player
        state = {}
        valid_act = []

        gong_card_ids = None
        concealed_gong_card_ids = None
        add_gong_card_ids = None
        pong_card_ids = None
        chow_card_ids = None
        if self.is_over is True:
            pass
        else:
            if len(players[player_id].hand) % 3 == 2:
                # he can choose hu/gong/discard
                if len(players[player_id].valid_act) == 0:
                    is_hu = False
                    is_add_gong = False
                    is_concealed_gong = False
                    if players[player_id].discard_only is False:
                        is_hu = Judger.judge_hu(players[player_id], self.game_id)  # check current player is win or not
                        is_add_gong, add_gong_card_ids = Judger.judge_add_gong(players[player_id], self.game_id)
                        is_concealed_gong, concealed_gong_card_ids = Judger.judge_concealed_gong(players[player_id], self.game_id)
                    is_wait, del_card_ids, dic_wait_cards = Judger.judge_wait(players[player_id], self.game_id) # check current player is waiting
                    dic_valid_act = dict()
                    if is_hu:
                        dic_valid_act[ActionType.ActionTypeHu] = players[player_id].hand[-1].get_card_id()
                        dic_valid_act[ActionType.ActionTypePassHu] = 1

                    if is_concealed_gong:
                        dic_valid_act[ActionType.ActionTypeConcealedGong] = concealed_gong_card_ids
                    if is_add_gong:
                        dic_valid_act[ActionType.ActionTypeAddGong] = add_gong_card_ids
                    if players[player_id].is_wait is False and is_wait:
                        dic_valid_act[ActionType.ActionTypeWait] = 1
                    if is_wait:
                        players[player_id].wait_del_tile = del_card_ids
                        players[player_id].dic_wait_tile = dic_wait_cards
                    dic_valid_act[ActionType.ActionTypeDiscard] = 1
                    players[player_id].valid_act = dic_valid_act
                    valid_act = list(dic_valid_act.keys())

                else:
                    if ActionType.ActionTypeConcealedGong in players[player_id].valid_act:
                        is_concealed_gong, concealed_gong_card_ids = Judger.judge_concealed_gong(players[player_id], self.game_id)
                        if is_concealed_gong is False:
                            players[player_id].valid_act.pop(ActionType.ActionTypeConcealedGong)
                        else:
                            players[player_id].valid_act[ActionType.ActionTypeConcealedGong] = concealed_gong_card_ids
                    if ActionType.ActionTypeAddGong in players[player_id].valid_act:
                        remain_gid = list()
                        for gid in players[player_id].valid_act[ActionType.ActionTypeAddGong]:
                            if gid in players[player_id].wait_del_tile:
                                remain_gid.append(gid)
                        if len(remain_gid) == 0:
                            players[player_id].valid_act.pop(ActionType.ActionTypeAddGong)
                        else:
                            players[player_id].valid_act[ActionType.ActionTypeAddGong] = remain_gid

                    valid_act = list(players[player_id].valid_act.keys())

                    if ActionType.ActionTypeGong in valid_act:
                        gong_card_ids = players[player_id].valid_act[ActionType.ActionTypeGong]
                    if ActionType.ActionTypeConcealedGong in valid_act:
                        concealed_gong_card_ids = players[player_id].valid_act[ActionType.ActionTypeConcealedGong]
                    if ActionType.ActionTypeAddGong in valid_act:
                        add_gong_card_ids = players[player_id].valid_act[ActionType.ActionTypeAddGong]
                    if ActionType.ActionTypeWait in valid_act:
                        is_wait, del_card_ids, dic_wait_cards = Judger.judge_wait(players[player_id], self.game_id)
                        assert is_wait is True
                        players[player_id].wait_del_tile = del_card_ids
                        players[player_id].dic_wait_tile = dic_wait_cards
            else:
                valid_act = list(players[player_id].valid_act.keys())
                if ActionType.ActionTypePong in players[player_id].valid_act:
                    pong_card_ids = players[player_id].valid_act[ActionType.ActionTypePong]
                if ActionType.ActionTypeGong in players[player_id].valid_act:
                    gong_card_ids = players[player_id].valid_act[ActionType.ActionTypeGong]
                if ActionType.ActionTypeChow in players[player_id].valid_act:
                    chow_card_ids = players[player_id].valid_act[ActionType.ActionTypeChow]

        state['valid_act'] = valid_act

        if ActionType.ActionTypeDiscard in valid_act:
            if players[player_id].is_wait is False:
                state['play_cards'] = list(players[player_id].dic_hand_id2card.keys())  # eg: [1,2,3]
            else:
                if players[player_id].wait_del_tile:
                    new_id = []
                    for nid in players[player_id].wait_del_tile:
                        if players[player_id].get_hand_card_by_id(nid):
                            new_id.append(nid)
                    state['play_cards'] = new_id

                else:
                    state['play_cards'] = [players[player_id].hand[-1].card_id]
        if ActionType.ActionTypeChow in valid_act:
            state['chow_cards'] = chow_card_ids                                     # eg: [[1,2,3],[2,4,3]]
        if ActionType.ActionTypePong in valid_act:
            state['pong_cards'] = pong_card_ids                                     # eg: [1,2,3]
        if ActionType.ActionTypeGong in valid_act:
            state['gong_cards'] = gong_card_ids                                     # eg: [1,2,3]
        if ActionType.ActionTypeConcealedGong in valid_act:
            state['concealed_gong_cards'] = concealed_gong_card_ids                 # eg: [1,2,3]
        if ActionType.ActionTypeAddGong in valid_act:
            state['add_gong_cards'] = add_gong_card_ids

        state['table'] = dealer.table                                               # eg: [MahjongCard, MahjongCard]
        state['deck'] = dealer.deck
        state['player'] = player_id                                                 # eg: 0
        state['current_hand'] = players[player_id].hand                             # eg: [MahjongCard, MahjongCard]
        state['players_hand'] = {p.player_id: p.hand for p in players}
        state['players_pile'] = {p.player_id: p.pile for p in players}              # eg: {1: [[MahjongCard, MahjongCard]. [MahjongCard, MahjongCard]]}
        state['players_hidden_pile'] = {p.player_id: p.hidden_pile for p in players}
        state['players_flower'] = {p.player_id: p.flower_tile for p in players}
        state['history_cards'] = {p.player_id: p.history_card for p in players}     # eg: {1: [MahjongCard, MahjongCard]}
        state['history_action'] = {p.player_id: p.history_action for p in players}  # eg: {1: [MahjongAction, MahjongAction]}
        state['is_over'] = self.is_over                                             # eg: True
        state['winner'] = self.winner  # if no one wins, winner_id=None             # eg: 1/None
        state['is_wait'] = players[player_id].is_wait
        state['is_rob_the_gong'] = players[player_id].is_rob_the_gong
        state['out_with_replacement_tile'] = players[player_id].out_with_replacement_tile
        state['is_sky_ready_hand'] = players[player_id].is_sky_ready_hand
        state['players_wait'] = {p.player_id: p.is_wait for p in players}           # eg {0: True, 1: False}
        return state
