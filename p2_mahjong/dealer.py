# coding=utf-8
import random
from p2_mahjong.utils import init_deck
from p2_mahjong.DEF import MAX_HAND_CARD_NUM
log_head = "dealer.py"


class MahjongDealer(object):
    """ Initialize a mahjong dealer class
    """
    def __init__(self, game_id="", reset_deck=True, initial_deck=None):
        self.game_id = game_id
        if reset_deck:
            self.deck = init_deck(self.game_id)
            self.shuffle()
        else:
            self.deck = initial_deck.copy()
        self.table = []
        self.is_top_avail = False
        self.game_id = game_id

    def load_state(self, state_dict):
        self.deck = state_dict["deck"].copy()
        self.table = state_dict["table"].copy()
        self.is_top_avail = state_dict["is_top_avail"]
        return

    def get_state(self):
        state = dict()
        state["deck"] = self.deck.copy()
        state["table"] = self.table.copy()
        state["is_top_avail"] = self.is_top_avail
        return state

    def get_table(self):
        return self.table

    def get_is_top_avail(self):
        return self.is_top_avail

    def set_table(self, table):
        self.table = table

    def set_is_top_avail(self, is_top_avail):
        self.is_top_avail = is_top_avail

    def set_deck(self, lis):
        new_deck = []
        for cid in lis:
            idx = 0
            for card in self.deck:
                if card.card_id == cid:
                    new_deck.append(card)
                    self.deck.pop(idx)
                    break
                idx += 1
        new_deck += self.deck
        self.deck = new_deck
        self.deck.reverse()
        return

    def shuffle(self):
        """ Shuffle the deck
        """
        random.shuffle(self.deck)

    def replace_flower_tile(self, player):
        func_head = "replace_flower_tile()" + self.game_id
        for idx in range(len(player.hand)):
            while player.hand[idx].type == "flowers":
                player.flower_tile.append(player.hand[idx])
                if len(self.deck) < 1:
                    print(log_head, func_head, "no_card_in_deck_to_replace_flower_tiles")
                    return False
                del player.dic_hand_id2card[player.hand[idx].card_id]
                new_card = self.deck.pop()
                new_card.set_user_id(player.get_player_id())
                player.hand[idx] = new_card
                if new_card.card_id not in player.dic_hand_id2card:
                    player.dic_hand_id2card[new_card.card_id] = []
                player.dic_hand_id2card[new_card.card_id].append(new_card.runtime_id)
        return True

    def deal_cards(self, player, num):
        """ Deal some cards from deck to one player

        Args:
            player (object): The object of MahjongPlayer
            num (int): The number of cards to be dealed
        """
        func_head = "deal_cards()" + self.game_id
        if len(self.deck) < num:
            return False
        is_init = True if num > 1 else False
        for _ in range(num):
            assert len(player.hand) < MAX_HAND_CARD_NUM
            latest_card = self.deck.pop()
            latest_card.set_user_id(player.get_player_id())

            if is_init is False:
                while latest_card.type == "flowers":
                    player.is_gonging = False
                    player.flower_tile.append(latest_card)
                    if len(self.deck) < 1:
                        return False
                    latest_card = self.deck.pop()
                    latest_card.set_user_id(player.get_player_id())
                    pass
            player.hand.append(latest_card)
            if latest_card.card_id not in player.dic_hand_id2card:
                player.dic_hand_id2card[latest_card.card_id] = []
            player.dic_hand_id2card[latest_card.card_id].append(latest_card.runtime_id)
        self.is_top_avail = False
        return True

    def push_table_top(self, card):
        self.table.append(card)
        self.is_top_avail = True
        return

    def pop_table_top(self):
        if self.is_top_avail:
            assert len(self.table) > 0
            self.is_top_avail = False
            return self.table.pop(-1)
        return None

    def get_table_top(self):
        if self.is_top_avail:
            assert len(self.table) > 0
            return self.table[-1]
        return None

