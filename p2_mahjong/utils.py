# coding=utf-8
import sys
import numpy as np
from p2_mahjong.card import MahjongCard as Card
log_head = "utils.py"

CARD_USED_TYPE = ['characters', 'green', 'red', 'white', 'east', 'west', 'north', 'south',
                  'spring', 'summer', 'autumn', 'winter', 'mei', 'lan', 'zhu', 'ju']
card_encoding_dict = {}
card_id = 0
DIC_CHOW = {}
character_list = []
wind_list = []
dragon_list = []
card_used = {}
for _type in ['bamboo', 'characters', 'dots']:
    for _trait in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
        card = _type+"-"+_trait
        card_encoding_dict[card] = card_id
        DIC_CHOW[card_id] = 1
        if _type in ['characters']:
            card_used[card_id] = 1
        character_list.append(card_id)
        card_id += 1

for _trait in ['green', 'red', 'white']:
    card = 'dragons-'+_trait
    card_encoding_dict[card] = card_id
    if _trait in CARD_USED_TYPE:
        card_used[card_id] = 1
    dragon_list.append(card_id)
    card_id += 1

for _trait in ['east', 'west', 'north', 'south']:
    card = 'winds-'+_trait
    card_encoding_dict[card] = card_id
    if _trait in CARD_USED_TYPE:
        card_used[card_id] = 1
    wind_list.append(card_id)
    card_id += 1

for _trait in ['spring', 'summer', 'autumn', 'winter', 'mei', 'lan', 'zhu', 'ju']:
    card = 'flowers-'+_trait
    card_encoding_dict[card] = card_id
    if _trait in CARD_USED_TYPE:
        card_used[card_id] = 1
    card_id += 1

card_decoding_dict = {card_encoding_dict[key]: key for key in card_encoding_dict.keys()}


def init_deck(game_id=""):
    func_head = "init_deck()" + game_id
    deck = []
    idx = 0
    for card_id in card_decoding_dict:
        for _ in range(4):
            if card_id not in card_used:
                continue
            card = Card(runtime_id=idx, card_id=card_id)
            card.type = card_decoding_dict[card_id].split("-")[0]
            card.trait = card_decoding_dict[card_id].split("-")[1]
            deck.append(card)
            idx += 1
            if card.type == "flowers":
                break
    return deck


