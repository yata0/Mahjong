# coding=utf-8
import copy
from p2_mahjong.DEF import ActionType

log_head = "player.py"


class MahjongAction:
    def __init__(self):
        self.action = ActionType.ActionTypeNull
        self.origin_actor_type = 0
        self.player_id = 1
        self.assist_card = []
        self.target_card = None
        self.action_str = None


class MahjongPlayer(object):

    def __init__(self, player_id, game_id=""):
        """ Initialize a player.

        Args:
            player_id (int): The id of the player
        """
        self.player_id = player_id
        self.hand = []
        self.pile = []
        self.hidden_pile = []
        self.history_card = []
        self.history_action = []
        self.PLAYERS_NUM = 2
        self.dic_hand_id2card = dict()
        self.is_wait = False
        self.wait_tile = list()
        self.dic_wait_tile = dict()
        self.wait_del_tile = []
        self.flower_tile = []
        self.pass_hu_cnt = 0
        self.valid_act = dict()
        self.add_gong_card = None
        self.rob_gong_card = None
        self.is_rob_the_gong = False
        self.is_gonging = False
        self.out_with_replacement_tile = False
        self.is_first_action = True
        self.is_sky_ready_hand = False
        self.game_id = game_id
        self.discard_only = False

    def get_state(self):
        dic = dict()
        dic["player_id"] = self.player_id
        dic["hand"] = self.hand.copy()
        dic["pile"] = list()
        for sub_pile in self.pile:
            dic["pile"].append(sub_pile.copy())
        dic["history_card"] = self.history_card.copy()
        dic["history_action"] = list()
        for action in self.history_action:
            cp_action = copy.copy(action)
            dic["history_action"].append(cp_action)
        dic["hand_id2card"] = {card_id: self.dic_hand_id2card[card_id].copy() for card_id in self.dic_hand_id2card}
        return dic

    def load_state(self, dic):
        self.player_id = dic["player_id"]
        self.hand = dic["hand"].copy()
        self.pile = list()
        for sub_pile in dic["pile"]:
            self.pile.append(sub_pile.copy())
        self.history_card = dic["history_card"].copy()
        self.history_action = list()
        for action in dic["history_action"]:
            cp_action = copy.copy(action)
            self.history_action.append(cp_action)
        self.dic_hand_id2card = {card_id: dic["hand_id2card"][card_id].copy() for card_id in dic["hand_id2card"]}
        return

    def get_hand_card_by_id(self, card_id):
        for card in self.hand:
            if card.card_id == card_id:
                assert card.get_user_id() == self.player_id
                return card
        return None

    def get_hand_cards_by_id(self, card_id):
        lis_hand_card = list()
        for card in self.hand:
            if card.get_card_id() == card_id:
                assert card.get_user_id() == self.player_id
                lis_hand_card.append(card)
        return lis_hand_card

    def set_player_id(self, player_id):
        self.player_id = player_id

    def get_player_id(self):
        """ Return the id of the player
        """
        return self.player_id

    def get_hand_str(self):
        return [c.get_str() for c in self.hand]

    def get_pile_str(self):
        return [[c.get_str() for c in s] for s in self.pile]

    def get_concealed_pile_str(self):
        return [[c.get_str() for c in s] for s in self.hidden_pile]

    def play_card(self, dealer, card):
        """ Play one card
        Args:
            dealer (object): Dealer
            card (object): The card to be play.
        """

        action = MahjongAction()
        action.action = ActionType.ActionTypeDiscard
        action.origin_actor_type = 1
        action.player_id = 0
        action.target_card = card
        self.history_action.append(action)
        self.hand.pop(self.hand.index(card))
        self.dic_hand_id2card[card.card_id].remove(card.runtime_id)
        if len(self.dic_hand_id2card[card.card_id]) == 0:
            del self.dic_hand_id2card[card.card_id]
        self.history_card.append(card)
        dealer.push_table_top(card)
        self.is_gonging = False

    def play_card_id(self, dealer, card_id):
        """ Play one card
        Args:
            dealer (object): Dealer
            card_id (int): The id of hand_card to be play.
        """
        func_head = "play_card_id()" + self.game_id
        self.is_first_action = False
        card = self.get_hand_card_by_id(card_id)
        assert card is not None
        self.play_card(dealer, card)
        self.valid_act = dict()
        self.discard_only = False
        if self.is_wait is True and self.wait_del_tile:
            assert card_id in self.wait_del_tile
            self.wait_tile = self.dic_wait_tile[card_id]
            self.wait_del_tile = None

    def chow_card(self, dealer, assist_card_ids):
        """ Perform Chow
        Args:
            dealer (object): Dealer
            assist_card_ids (list): The cards in hand to be Chow.
        """
        func_head = "chow_card()" + self.game_id
        self.is_first_action = False
        last_card = dealer.pop_table_top()
        assert last_card is not None
        card0_id = assist_card_ids[0]
        card1_id = assist_card_ids[1]
        if card0_id > card1_id:
            card0_id, card1_id = card1_id, card0_id
        card0 = self.get_hand_card_by_id(card0_id)
        card1 = self.get_hand_card_by_id(card1_id)
        cards = list()
        cards.append(card0)
        cards.append(card1)
        assert card0 is not None
        assert card1 is not None
        cards.append(last_card)
        self.hand.pop(self.hand.index(card0))
        self.dic_hand_id2card[card0.card_id].remove(card0.runtime_id)
        if len(self.dic_hand_id2card[card0.card_id]) == 0:
            del self.dic_hand_id2card[card0.card_id]
        self.hand.pop(self.hand.index(card1))
        self.dic_hand_id2card[card1.card_id].remove(card1.runtime_id)
        if len(self.dic_hand_id2card[card1.card_id]) == 0:
            del self.dic_hand_id2card[card1.card_id]
        self.pile.append(cards)

        action = MahjongAction()
        action.action = ActionType.ActionTypeChow
        action.origin_actor_type = 1
        action.player_id = 0
        action.target_card = last_card
        action.assist_card.append(card0)
        action.assist_card.append(card1)
        action.action_str = "%d,%d,%d" % (card0_id, card1_id, last_card.card_id)
        self.history_action.append(action)
        self.valid_act = dict()
        self.discard_only = True

    def gong_card(self, dealer, gong_card_id):
        """ Perform Gong
        Args:
            dealer (object): Dealer
            gong_card_id (int): The card to be Gong.
        """
        func_head = "gong_card()" + self.game_id
        self.is_first_action = False
        action = MahjongAction()
        action.action = ActionType.ActionTypeGong
        action.origin_actor_type = 1
        action.player_id = 0

        cards = list()
        for card in self.hand:
            if card.get_card_id() == gong_card_id:
                cards.append(card)
                action.assist_card.append(card)
        is_gong_after_pong = False
        if len(cards) == 1:
            action.action = ActionType.ActionTypeAddGong
            action.target_card = action.assist_card.pop(-1)
            for cur_pile in self.pile:
                cnt = 0
                for pile_card in cur_pile:
                    if pile_card.card_id == gong_card_id:
                        cnt += 1
                if cnt == 3:
                    cur_pile.append(action.target_card)
                    is_gong_after_pong = True
                    break
            assert is_gong_after_pong is True
        elif len(cards) == 3:
            last_card = dealer.pop_table_top()
            assert last_card is not None and last_card.get_card_id() == gong_card_id
            action.target_card = last_card
            cards.append(last_card)
        else:
            print(log_head, func_head, "illegal_card_num=", len(cards))
            assert False
        for card in cards:
            if card in self.hand:
                self.hand.pop(self.hand.index(card))
                self.dic_hand_id2card[card.card_id].remove(card.runtime_id)
                if len(self.dic_hand_id2card[card.card_id]) == 0:
                    del self.dic_hand_id2card[card.card_id]
        if is_gong_after_pong is False:
            self.pile.append(cards)
        self.history_action.append(action)
        self.valid_act = dict()
        self.is_gonging = True

    def concealed_gong_card(self, gong_card_id):
        """ Perform Concealed Gong
        Args:
            gong_card_id (int): The card to be Gong.
        """
        func_head = "concealed_gong_card()" + self.game_id
        self.is_first_action = False
        action = MahjongAction()
        action.action = ActionType.ActionTypeConcealedGong
        action.origin_actor_type = 1
        action.player_id = 0

        cards = list()
        for card in self.hand:
            if card.get_card_id() == gong_card_id:
                cards.append(card)
                action.assist_card.append(card)
        if len(cards) == 4:
            action.target_card = action.assist_card.pop(-1)
        else:
            print(log_head, func_head, "illegal_card_num=", len(cards))
            assert False
        self.hidden_pile.append(cards)
        for card in cards:
            if card in self.hand:
                self.hand.pop(self.hand.index(card))
                self.dic_hand_id2card[card.card_id].remove(card.runtime_id)
                if len(self.dic_hand_id2card[card.card_id]) == 0:
                    del self.dic_hand_id2card[card.card_id]
        self.history_action.append(action)
        self.valid_act = dict()
        self.is_gonging = True
        return

    def pong_card(self, dealer, pong_card_id):
        """ Perform Pong
        Args:
            dealer (object): Dealer
            pong_card_id (int): The cards to be Pong.
        """
        func_head = "pong_card()" + self.game_id
        self.is_first_action = False
        last_card = dealer.pop_table_top()
        assert last_card is not None and last_card.get_card_id() == pong_card_id

        action = MahjongAction()
        action.action = ActionType.ActionTypePong
        action.origin_actor_type = 1
        action.player_id = 0
        action.target_card = last_card
        cards = list()
        for card in self.hand:
            if card.get_card_id() == pong_card_id:
                cards.append(card)
                action.assist_card.append(card)
            if len(cards) == 2:
                break
        for card in cards:
            if card in self.hand:
                self.hand.pop(self.hand.index(card))
                self.dic_hand_id2card[card.card_id].remove(card.runtime_id)
                if len(self.dic_hand_id2card[card.card_id]) == 0:
                    del self.dic_hand_id2card[card.card_id]
        cards.append(last_card)
        assert len(cards) == 3

        self.pile.append(cards)
        self.history_action.append(action)
        self.valid_act = dict()
        self.discard_only = True

    def hu(self, dealer):
        func_head = "hu()" + self.game_id
        if len(self.hand) % 3 == 2:
            if self.is_gonging is True:
                self.out_with_replacement_tile = True
            return
        card = dealer.pop_table_top() if self.rob_gong_card is None else self.rob_gong_card
        assert card is not None
        self.hand.append(card)
        if card.card_id not in self.dic_hand_id2card:
            self.dic_hand_id2card[card.card_id] = list()
        self.dic_hand_id2card[card.card_id].append(card.runtime_id)
        return

    def get_last_player(self):
        last_player_id = (self.player_id + 1) % self.PLAYERS_NUM
        return last_player_id

    def get_next_player(self):
        next_player_id = (self.player_id + 1) % self.PLAYERS_NUM
        return next_player_id

    def wait_cards(self):
        func_head = "wait_cards()"
        assert self.is_wait is False
        action = MahjongAction()
        action.action = ActionType.ActionTypeWait
        action.origin_actor_type = 1
        action.player_id = 0
        self.history_action.append(action)

        self.is_wait = True
        self.valid_act.pop(ActionType.ActionTypeWait)
        if ActionType.ActionTypeHu in self.valid_act:
            self.valid_act.pop(ActionType.ActionTypeHu)
            self.valid_act.pop(ActionType.ActionTypePassHu)
        if self.is_first_action:
            self.is_sky_ready_hand = True
        wait_set = set()
        for dc in self.dic_wait_tile:
            for wc in self.dic_wait_tile[dc]:
                wait_set.add(wc)
        self.wait_tile = list(wait_set)
        return

    def pass_hu(self):
        func_head = "pass_hu()" + self.game_id
        self.pass_hu_cnt += 1

        assert ActionType.ActionTypeHu in self.valid_act
        assert ActionType.ActionTypePassHu in self.valid_act
        self.valid_act.pop(ActionType.ActionTypeHu)
        self.valid_act.pop(ActionType.ActionTypePassHu)
        self.rob_gong_card = None  # 重置抢杠和
        return

    def draw_card(self, dealer):
        """ Perform Draw
        Args:
            dealer (object): Dealer
        """
        func_head = "draw_card()"
        dealer_ret = dealer.deal_cards(self, 1)  # give him one new card
        self.valid_act = dict()
        if dealer_ret:
            if self.is_wait:
                self.wait_del_tile = [self.hand[-1].card_id]
        return dealer_ret

    def remove_kong(self, card):
        func_head = "remove_kong()" + self.game_id
        assert card is not None
        for pile_set in self.pile:
            if card in pile_set:
                pile_set.pop(pile_set.index(card))
                break
        return
