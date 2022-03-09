import numpy as np
from p2_mahjong.calculate_fan_func import funclist
from p2_mahjong.DEF import ConflictDict, ConflictList
from p2_mahjong.DEF import FanType2NumDict, FanNumList, FanNum2TypeDict
from p2_mahjong.calculate_util import split_hands, struct_cards

log_head = "calculate_fan.py"

def calculate_fan_item(hu_cards_dict, player, game_id=""):
    func_head = "calculate_fan_item()" + game_id
    flower_cards = hu_cards_dict["players_flower"][player]
    num_fans = len(FanNum2TypeDict.keys())
    fan_valid_array = np.array([0] * num_fans)
    flower_num = len(flower_cards)
    fan_func_valid_array = np.array([1] * num_fans, dtype=np.int32)

    valid_index = []
    for i in range(num_fans)[::-1]:
        func = funclist[i]
        if fan_func_valid_array[i] == 1 and func(hu_cards_dict, player):
            fan_valid_array[i] = 1.
            valid_index.append(i)
            if i in ConflictDict:
                fan_func_valid_array[ConflictDict[i]] = 0

    valid_index = [index for index in valid_index if index in ConflictList]

    for index in valid_index:
        fan_valid_array[ConflictDict[index]] = 0
    fan_array = np.array(FanNumList)
    fan_array[8] = flower_num
    points = np.sum(fan_array * fan_valid_array)
    indexs = np.where(fan_valid_array > 0)
    fan_names = []
    fan_scores= []
    if len(indexs[0]) > 0:
        fan_names = [FanNum2TypeDict[index] for index in indexs[0]]
        fan_scores = [fan_array[index] for index in indexs[0]]
    return points, fan_names, fan_scores

def calculate_fan(state, player, game_id=""):
    func_head = "calculate_fan()" + game_id
    hu_cards_list = split_hu(state, player, game_id)
    points_list = []
    fan_name_list = []
    fan_score_list = []
    piles_num = 0
    for pid in state["players_pile"]:
        piles_num += len(state["players_pile"][pid])
    discard_tile_num = len(state["table"])
    remain_tile_num = len(state["deck"])
    is_wait = 1 if state["is_wait"] is True else 0
    is_rob_the_gong = 1 if state["is_rob_the_gong"] is True else 0
    is_out_with_replacement_tile = 1 if state["out_with_replacement_tile"] is True else 0
    is_sky_ready_hand = 1 if state["is_sky_ready_hand"] is True else 0

    for hu_cards_dict in hu_cards_list:
        hu_cards_dict["winner"] = state["winner"]

        hu_cards_dict["players_flower"] = state["players_flower"]
        hu_cards_dict["table"] = state["table"]
        hu_cards_dict["discard_tile_num"] = discard_tile_num
        hu_cards_dict["remain_tile_num"] = remain_tile_num
        hu_cards_dict["piles_num"] = piles_num
        hu_cards_dict["is_wait"] = is_wait
        hu_cards_dict["is_rob_the_gong"] = is_rob_the_gong
        hu_cards_dict["is_out_with_replacement_tile"] = is_out_with_replacement_tile
        hu_cards_dict["is_sky_ready_hand"] = is_sky_ready_hand
        hu_cards_dict["players_pile"] = state["players_pile"]

        point, fan_names, fan_scores = calculate_fan_item(hu_cards_dict, player, game_id)
        points_list.append(point)
        fan_name_list.append(fan_names)
        fan_score_list.append(fan_scores)
    index = np.argmax(points_list)
    point = points_list[index]
    fan_names = fan_name_list[index]
    fan_scores = fan_score_list[index]
    hu_cards_dict = hu_cards_list[index]
    return point, fan_names, fan_scores, hu_cards_dict


def split_hu(state, player, game_id=""):
    func_head = "split_hu()" + game_id
    pile_cards = state["players_pile"][player]
    hand_cards = state["current_hand"]
    results_list = []

    hidden_pile_cards = state["players_hidden_pile"][player]
    last_card = hand_cards[-1]
    self_drawn = last_card.user_id == player
    last_card_id = last_card.card_id

    hidden_pile_cards_id = []
    for hidden_pile in hidden_pile_cards:
        hidden_pile_cards_id.append([card.get_card_id() for card in hidden_pile])
    pile_cards_id = []
    for pile in pile_cards:
        pile_cards_id.append([card.get_card_id() for card in pile])
    pile_sequences = []
    pile_triplets = []
    pile_gangs = []
    for pile_id in pile_cards_id:
        if len(pile_id) == 4:
            pile_gangs.append(pile_id)
        elif pile_id[0] == pile_id[1]:
            pile_triplets.append(pile_id)
        else:
            pile_sequences.append(pile_id)

    hand_cards_id = [card.get_card_id() for card in hand_cards]
    if len(hand_cards_id) == 14:
        sorted_hand_cards = sorted(hand_cards_id)
        double_check = [sorted_hand_cards[i] == sorted_hand_cards[i + 1] for i in range(0, 14, 2)]
        if np.sum(double_check) == 7:
            results_list.append(
                {
                    "pile_sequences": pile_sequences,
                    "pile_triplets": pile_triplets,
                    "pile_gangs": pile_gangs,
                    "hidden_pile_gangs": hidden_pile_cards_id,
                    "hand_sequences": [],
                    "hand_triplets": [],
                    "hand_double": [sorted_hand_cards[i:i + 2] for i in range(0, 14, 2)],
                    "self_drawn": self_drawn,
                    "last_card_id": last_card_id,
                    "hand_cards_id": hand_cards_id
                })

    split_hand_list = []
    flag = split_hands(hand_cards_id, pile_cards_id + hidden_pile_cards_id, split_hand_list)
    if flag:
        result_list = struct_cards(hand_cards_id, pile_cards_id, hidden_pile_cards_id, self_drawn, last_card_id
                                   , split_hand_list)
        results_list.extend(result_list)

    return results_list
