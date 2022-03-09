import numpy as np
from p2_mahjong.DEF import *
from p2_mahjong.utils import wind_list, dragon_list, character_list
from p2_mahjong.calculate_util import is_n_sequence, is_trip

funclist = [None] * len(FanNum2TypeDict.keys())


# # 1. Pure Double Chow
def is_pure_double_chow(state, player):
    sequences = state["pile_sequences"] + state["hand_sequences"]
    s_list = []
    for seq in sequences:
        t_seq = sorted(seq)
        if t_seq[0] in s_list:
            return True
        else:
            s_list.append(t_seq[0])
    return False


funclist[FanType2NumDict["PURE_DOUBLE_CHOW"]] = is_pure_double_chow


# 2.SHORT_STRAIGHT
def is_short_straight(state, player):
    sequences = state["pile_sequences"] + state["hand_sequences"]
    if len(sequences) < 2:
        return False
    sl_list = []
    for sequence in sequences:
        sequence = sorted(sequence)
        sl_list.append(sequence[0])

    sl_list = sorted(sl_list)
    for i in range(len(sl_list) - 1):
        if sl_list[i] + 3 in sl_list:
            return True
    return False


funclist[FanType2NumDict["SHORT_STRAIGHT"]] = is_short_straight


# 3.TWO_TERMINAL_CHOWS
def is_two_terminal_chow(state, player):
    sequences = state["pile_sequences"] + state["hand_sequences"]
    if len(sequences) < 2:
        return False
    sl_list = []
    for sequence in sequences:
        sequence = sorted(sequence)
        sl_list.append(sequence[0])
    if 9 in sl_list and 15 in sl_list:
        return True
    else:
        return False


funclist[FanType2NumDict["TWO_TERMINAL_CHOWS"]] = is_two_terminal_chow


# # 4.MELDED_KONG
def is_melded_kong(state, player):
    if len(state["pile_gangs"]) == 0:
        return False
    else:
        return True


funclist[FanType2NumDict["MELDED_KONG"]] = is_melded_kong


# 5.EDGE_WAIT
def is_edge_wait(state, player):
    win_card = state["last_card_id"]
    if win_card not in [11, 15]:
        return False
    sequences = state["hand_sequences"]
    if len(sequences) == 0:
        return False
    seq_head_list = []
    seq_tail_list = []
    seq_mid_list = []
    for seq in sequences:
        seq = sorted(seq)
        seq_head_list.append(seq[0])
        seq_mid_list.append(seq[1])
        seq_tail_list.append(seq[-1])
    if win_card in seq_mid_list:
        return False
    if win_card == 11:
        if win_card in seq_head_list:
            return False
        if win_card in seq_mid_list:
            return False
        if win_card in seq_tail_list:
            return True
    else:
        if win_card in seq_tail_list:
            return False
        if win_card in seq_mid_list:
            return False
        if win_card in seq_head_list:
            return True


funclist[FanType2NumDict["EDGE_WAIT"]] = is_edge_wait


# 6.CLOSED_WAIT
def is_closed_wait(state, player):
    win_card = state["last_card_id"]
    sequences = state["hand_sequences"]
    if len(sequences) == 0:
        return False
    seq_head_list = []
    seq_tail_list = []
    seq_mid_list = []
    for seq in sequences:
        seq = sorted(seq)
        seq_head_list.append(seq[0])
        seq_mid_list.append(seq[1])
        seq_tail_list.append(seq[2])
    seq_head_tail_out = list(set(seq_head_list).union(set(seq_tail_list)))
    if win_card in seq_mid_list and win_card not in seq_head_tail_out:
        return True
    return False


funclist[FanType2NumDict["CLOSED_WAIT"]] = is_closed_wait


# 7.SINGLE_WAIT
def is_single_wait(state, player):
    win_card = state["last_card_id"]
    hand_double = state["hand_double"]
    if len(hand_double) == 7:
        return False
    if win_card not in hand_double[0]:
        return False
    if is_sky_hu(state, player):
        return False

    hand_cards_id_flat = []
    hand_cards = state["hand_sequences"] + state["hand_triplets"]
    for cards in hand_cards:
        hand_cards_id_flat.extend(cards)
    if win_card in hand_cards_id_flat:
        return False
    hand_seq_head_list = []
    hand_seq_tail_list = []
    for seq in state["hand_sequences"]:
        seq = sorted(seq)
        hand_seq_head_list.append(seq[0])
        hand_seq_tail_list.append(seq[-1])
    if win_card + 1 in hand_seq_head_list:
        return False
    if win_card - 1 in hand_seq_tail_list:
        return False
    return True


funclist[FanType2NumDict["SINGLE_WAIT"]] = is_single_wait


# 8.SELF_DRAW
def is_self_drawn(state, player):
    if player != state["winner"]:
        return False
    return state["self_drawn"]


funclist[FanType2NumDict["SELF_DRAW"]] = is_self_drawn


# 9.FLOWER_TILES
def is_flower_tiles(state, player):
    if len(state["players_flower"][player]) > 0:
        return True
    else:
        return False


funclist[FanType2NumDict["FLOWER_TILES"]] = is_flower_tiles


# 10.READY_HAND
def is_ready_hand(state, player):
    return True if state["is_wait"] == 1 else False


funclist[FanType2NumDict["READY_HAND"]] = is_ready_hand


# 11.DRAGON_PUNG
def is_dragon_pung(state, player):
    triplets = state["pile_triplets"] + state["hand_triplets"] \
               + state["pile_gangs"] + state["hidden_pile_gangs"]
    if len(triplets) == 0:
        return False
    triplet_list = [triplet[0] for triplet in triplets if triplet[0] in dragon_list]
    return len(triplet_list) > 0


funclist[FanType2NumDict["DRAGON_PUNG"]] = is_dragon_pung


# 12.CONCEALED_HAND
def is_concealed_hand(state, player):
    pile_length = len(state["pile_sequences"]) + len(state["pile_triplets"]) + len(state["pile_gangs"])
    return pile_length == 0 and state["self_drawn"] == False


funclist[FanType2NumDict["CONCEALED_HAND"]] = is_concealed_hand


# 13.ALL_CHOWS
def is_all_chows(state, player):
    sequences = state["pile_sequences"] + state["hand_sequences"]
    if len(sequences) != 4:
        return False
    double = state["hand_double"]
    if double[0][0] in character_list:
        return True
    else:
        return False


funclist[FanType2NumDict["ALL_CHOWS"]] = is_all_chows


# 14.TILE_HOG
def is_tile_hog(state, player):
    sequences = state["pile_sequences"] + state["hand_sequences"]
    triplets = state["pile_triplets"] + state["hand_triplets"]
    doubles = state["hand_double"]
    all_cards_exclude_gang = sequences + triplets + doubles
    all_cards_exclude_gang_flat = []
    for s in all_cards_exclude_gang:
        all_cards_exclude_gang_flat.extend(s)
    cards_set = set(all_cards_exclude_gang_flat)
    for card in cards_set:
        if all_cards_exclude_gang_flat.count(card) == 4:
            return True
    return False


funclist[FanType2NumDict["TILE_HOG"]] = is_tile_hog


# 15.TWO_CONCEALED_PUNGS
def is_two_concealed_pungs(state, player):
    hand_triplets = state["hand_triplets"] + state["hidden_pile_gangs"]
    num_concealed_triplet = len(hand_triplets)
    if num_concealed_triplet < 2:
        return False
    if not state["self_drawn"]:
        triplet_head = [triplet[0] for triplet in hand_triplets]
        if state["last_card_id"] in triplet_head:
            num_concealed_triplet -= 1
    return num_concealed_triplet >= 2


funclist[FanType2NumDict["TWO_CONCEALED_PUNGS"]] = is_two_concealed_pungs


## 16.CONCEALED_KONG
def is_concealed_kong(state, player):
    if len(state["hidden_pile_gangs"]) == 0:
        return False
    else:
        return True


funclist[FanType2NumDict["CONCEALED_KONG"]] = is_concealed_kong


def is_yao(card_id):
    if card_id not in character_list:
        return False
    if card_id % 9 == 0 or card_id % 9 == 8:
        return True
    else:
        return False

# 17.ALL_SIMPLES


def is_all_simples(state, player):
    sequences = state["pile_sequences"] + state["hand_sequences"]
    triplets = state["pile_triplets"] + state["hand_triplets"]
    doubles = state["hand_double"]
    kongs = state["pile_gangs"] + state["hidden_pile_gangs"]

    for card_list in sequences + triplets + doubles + kongs:
        for card in card_list:
            if card in wind_list + dragon_list or is_yao(card):
                return False
    return True


funclist[FanType2NumDict["ALL_SIMPLES"]] = is_all_simples


# 18.OUTSIDE_HAND
def is_outside_hand(state, player):
    sequences = state["pile_sequences"] + state["hand_sequences"]
    triplets = state["pile_triplets"] + state["hand_triplets"]
    doubles = state["hand_double"]
    kongs = state["pile_gangs"] + state["hidden_pile_gangs"]
    for cards in sequences:
        cards = sorted(cards)
        if is_yao(cards[0]) or is_yao(cards[-1]):
            continue
        else:
            return False

    for cards in triplets + doubles + kongs:
        if is_yao(cards[0]) or cards[0] in wind_list + dragon_list:
            continue
        else:
            return False
    return True


funclist[FanType2NumDict["OUTSIDE_HAND"]] = is_outside_hand


# 19.FULLY_CONCEALED_HAND
def is_fully_concealed_hand(state, player):
    if not state["self_drawn"]:
        return False
    pile_length = len(state["pile_sequences"]) + len(state["pile_triplets"]) + len(state["pile_gangs"])
    return pile_length == 0


funclist[FanType2NumDict["FULLY_CONCEALED_HAND"]] = is_fully_concealed_hand


# 20.TWO_MELDED_KONGS
def is_two_melded_kongs(state, player):
    pile_gangs = state["pile_gangs"]
    return len(pile_gangs) == 2


funclist[FanType2NumDict["TWO_MELDED_KONGS"]] = is_two_melded_kongs


# 21.LAST_TILE
def is_last_tile(state, player):
    win_card = state["last_card_id"]
    table_cards_id = [card for card in state["table"]]
    opp_pile_cards = state["players_pile"][1 - player]
    self_pile_cards = state["players_pile"][player]

    pile_cards_id = []
    for cards in opp_pile_cards + self_pile_cards:
        pile_cards_id.extend([card.get_card_id() for card in cards])

    known_cards_id = pile_cards_id + table_cards_id
    return known_cards_id.count(win_card) == 3


funclist[FanType2NumDict["LAST_TILE"]] = is_last_tile


# 22.LITTLE_THREE_WINDS
def is_little_three_winds(state, player):
    triplets = state["pile_triplets"] + state["hand_triplets"] + \
               state["hidden_pile_gangs"] + state["pile_gangs"]
    triplet_cards = [triplet[0] for triplet in triplets]
    double_cards = [double[0] for double in state["hand_double"]]
    trip_in_winds = [card for card in wind_list if card in triplet_cards]
    num_trip_in_winds = len(trip_in_winds)
    double_in_winds = [card for card in wind_list if card in double_cards]
    num_double_in_winds = len(double_in_winds)
    return num_trip_in_winds >= 2 and num_double_in_winds > 0


funclist[FanType2NumDict["LITTLE_THREE_WINDS"]] = is_little_three_winds


# 23.ALL_PUNGS
def is_all_pungs(state, player):
    triplets = state["pile_triplets"] + state["hand_triplets"] + \
               state["pile_gangs"] + state["hidden_pile_gangs"]
    if len(triplets) < 4:
        return False
    else:
        return True


funclist[FanType2NumDict["ALL_PUNGS"]] = is_all_pungs


# 24.HALF_FLUSH
def is_half_flush(state, player):
    sequences = state["pile_sequences"] + state["hand_sequences"]
    triplets = state["pile_triplets"] + state["hand_triplets"]
    doubles = state["hand_double"]
    kongs = state["pile_gangs"] + state["hidden_pile_gangs"]
    all_cards = []
    for cards in sequences + triplets + doubles + kongs + doubles:
        all_cards.extend(cards)
    honor_length = len([card for card in wind_list + dragon_list if card in all_cards])
    character_length = len([card for card in all_cards if card in character_list])
    return honor_length > 0 and character_length > 0


funclist[FanType2NumDict["HALF_FLUSH"]] = is_half_flush


# 25.TWO_DRAGON_PUNGS
def is_two_dragons_pungs(state, player):
    triplet_gangs = state["pile_triplets"] + state["hand_triplets"] + state["pile_gangs"] + state["hidden_pile_gangs"]
    if len(triplet_gangs) < 2:
        return False
    triplet_gang_cards = [cards[0] for cards in triplet_gangs]
    triplet_gang_cards_in_dragon = [card for card in triplet_gang_cards if card in dragon_list]
    return len(triplet_gang_cards_in_dragon) >= 2


funclist[FanType2NumDict["TWO_DRAGON_PUNGS"]] = is_two_dragons_pungs


## 26.TWO_CONCEALED_KONGS
def is_two_concealed_kongs(state, player):
    if len(state["hidden_pile_gangs"]) == 2:
        return True
    else:
        return False


funclist[FanType2NumDict["TWO_CONCEALED_KONGS"]] = is_two_concealed_kongs


# 27.MELDED_HAND
def is_melded_hand(state, player):
    if state["self_drawn"]:
        return False
    pile_length = len(state["pile_triplets"]) + len(state["pile_sequences"]) + len(state["pile_gangs"])

    return pile_length == 4


funclist[FanType2NumDict["MELDED_HAND"]] = is_melded_hand


# 28.OUT_WITH_REPLACEMENT_TILE
def is_out_with_replacement_tile(state, player):
    return True if state["is_out_with_replacement_tile"] == 1 else False


funclist[FanType2NumDict["OUT_WITH_REPLACEMENT_TILE"]] = is_out_with_replacement_tile


# 29.ROB_KONG

def is_robbing_the_kong(state, player):
    return True if state["is_rob_the_gong"] == 1 else False


funclist[FanType2NumDict["ROB_KONG"]] = is_robbing_the_kong


# 30.LAST_TILE_CLAIM
def is_last_tile_claim(state, player):
    if state["remain_tile_num"] == 0:
        return True
    else:
        return False


funclist[FanType2NumDict["LAST_TILE_CLAIM"]] = is_last_tile_claim


# 31.PURE_STRAIGHT
def is_pure_straight(state, player):
    sequences = state["pile_sequences"] + state["hand_sequences"]

    if len(sequences) < 3:
        return False
    seq_head_list = []
    for seq in sequences:
        seq = sorted(seq)
        seq_head_list.append(seq[0])

    in_seq_head = [index for index in [9, 12, 15] if index in seq_head_list]
    return len(in_seq_head) == 3


funclist[FanType2NumDict["PURE_STRAIGHT"]] = is_pure_straight


# 32.PURE_SHIFTED_CHOWS

def is_three_up(cards, inter=1):
    assert len(cards) == 3
    return cards[0] + inter == cards[1] and cards[1] + inter == cards[2]


def is_shifted_chows(state, player):
    sequences = state["pile_sequences"] + state["hand_sequences"]
    if len(sequences) < 3:
        return False
    seq_head_list = []
    for sequence in sequences:
        sequence = sorted(sequence)
        seq_head_list.append(sequence[0])
    sorted_seq_head_list = sorted(seq_head_list)

    if len(sorted_seq_head_list) == 4:
        check_list = [sorted_seq_head_list[:3], sorted_seq_head_list[1:],
                      [sorted_seq_head_list[index] for index in [0, 1, 3]], \
                      [sorted_seq_head_list[index] for index in [0, 2, 3]]]
        for check_item in check_list:
            if is_three_up(check_item) or is_three_up(check_item, 2):
                return True
        return False
    else:
        return is_three_up(sorted_seq_head_list) or is_three_up(sorted_seq_head_list, 2)


funclist[FanType2NumDict["PURE_SHIFTED_CHOWS"]] = is_shifted_chows


# 33.ALL_FLOWERS
def is_all_flower(state, player):
    if len(set(state["players_flower"][player])) == 8:
        return True
    else:
        return False


funclist[FanType2NumDict["ALL_FLOWERS"]] = is_all_flower


# 34.THREE_CONCEALED_PUNGS
def is_three_concealed_pungs(state, player):
    hand_triplets = state["hand_triplets"] + state["hidden_pile_gangs"]
    num_concealed_triplet = len(hand_triplets)
    if num_concealed_triplet < 3:
        return False
    if not state["self_drawn"]:
        triplet_head = [triplet[0] for triplet in hand_triplets]
        if state["last_card_id"] in triplet_head:
            num_concealed_triplet -= 1
    return num_concealed_triplet >= 3


funclist[FanType2NumDict["THREE_CONCEALED_PUNGS"]] = is_three_concealed_pungs


# 35.FOUR_HONOUR_PUNGS
def is_four_honors_pungs(state, player):
    triplet_gangs = state["pile_triplets"] + state["hand_triplets"] + state["pile_gangs"] + state["hidden_pile_gangs"]
    if len(triplet_gangs) < 4:
        return False
    trip_gang_card_list = [cards[0] for cards in triplet_gangs if cards[0] in wind_list + dragon_list]
    return len(trip_gang_card_list) == 4


funclist[FanType2NumDict["FOUR_HONOUR_PUNGS"]] = is_four_honors_pungs


# 36.BIG_THREE_WINDS
def is_big_three_winds(state, player):
    triplets = state["pile_triplets"] + state["hand_triplets"] + \
               state["pile_gangs"] + state["hidden_pile_gangs"]
    if len(triplets) < 3:
        return False
    trip_inter_wind_cards = [cards[0] for cards in triplets if cards[0] in wind_list]
    return len(trip_inter_wind_cards) >= 3


funclist[FanType2NumDict["BIG_THREE_WINDS"]] = is_big_three_winds


# 37.SEVEN_PAIRS
def is_seven_pairs(state, player):
    doubles = state["hand_double"]
    if len(doubles) == 7:
        return True
    else:
        return False


funclist[FanType2NumDict["SEVEN_PAIRS"]] = is_seven_pairs


# 38.PURE_TRIPLE_CHOW
def is_triple_chow(state, player):
    sequences = state["pile_sequences"] + state["hand_sequences"]
    if len(sequences) < 3:
        return False
    seq_head_list = []
    for sequence in sequences:
        sequence = sorted(sequence)
        seq_head_list.append(sequence[0])
    for head in set(seq_head_list):
        if seq_head_list.count(head) >= 3:
            return True
    return False


funclist[FanType2NumDict["PURE_TRIPLE_CHOW"]] = is_triple_chow


def is_pung(cards):
    assert len(cards) == 3
    return cards[0] == cards[1] and cards[1] == cards[2]


def is_seq(cards):
    assert len(cards) == 3
    return cards[0] + 1 == cards[1] and cards[1] + 1 == cards[2]


# 39.PURE_SHIFTED_PUNGS
def is_shifted_pungs(state, player):
    triplets = state["pile_triplets"] + state["hand_triplets"]
    if len(triplets) < 3:
        return False
    trip_head_list = [triplet[0] for triplet in triplets if triplet[0] in character_list]
    if len(trip_head_list) < 3:
        return False
    sorted_trip_head_list = sorted(trip_head_list)
    if len(sorted_trip_head_list) == 4:
        return is_seq(sorted_trip_head_list[:3]) or is_seq(sorted_trip_head_list[1:])
    else:
        return is_seq(sorted_trip_head_list)


funclist[FanType2NumDict["PURE_SHIFTED_PUNGS"]] = is_shifted_pungs


# 40.FOUR_PURE_SHIFTED_CHOWS
def is_four_up(cards, inter=1):
    return cards[0] + inter == cards[1] and cards[1] + inter == cards[2] and cards[2] + inter == cards[3]


def is_four_shifted_chows(state, player):
    sequences = state["pile_sequences"] + state["hand_sequences"]
    if len(sequences) < 4:
        return False
    seq_head_list = []
    for seq in sequences:
        seq_head_list.append(sorted(seq)[0])
    sorted_seq_head_list = sorted(seq_head_list)
    return is_four_up(sorted_seq_head_list) or is_four_up(sorted_seq_head_list, 2)


funclist[FanType2NumDict["FOUR_PURE_SHIFTED_CHOWS"]] = is_four_shifted_chows


## 41.THREE_KONGS
def is_three_kongs(state, player):
    if len(state["hidden_pile_gangs"]) + len(state["pile_gangs"]) >= 3:
        return True
    else:
        return False


funclist[FanType2NumDict["THREE_KONGS"]] = is_three_kongs


# 42.ALL_TERMINALS_AND_HONOURS
def is_all_terminals_and_honors(state, player):
    triplet_gangs_doubles = state["pile_triplets"] + state["hand_triplets"] + state["pile_gangs"] + state[
        "hidden_pile_gangs"]

    if len(triplet_gangs_doubles) < 4:
        return False
    triplet_gangs_doubles += state["hand_double"]
    all_cards = [cards[0] for cards in triplet_gangs_doubles]
    include_list = wind_list + dragon_list + [9, 17]
    for card in all_cards:
        if card not in include_list:
            return False
    return True


funclist[FanType2NumDict["ALL_TERMINALS_AND_HONOURS"]] = is_all_terminals_and_honors


# 43.HEAVENLY_READY_HAND
def is_sky_ready_hand(state, player):
    return True if state["is_sky_ready_hand"] == 1 else False


funclist[FanType2NumDict["HEAVENLY_READY_HAND"]] = is_sky_ready_hand


# 44.QUADRUPLE_CHOW
def is_quadruple_chow(state, player):
    sequences = state["pile_sequences"] + state["hand_sequences"]
    if len(sequences) < 4:
        return False
    seq_head_list = []
    for seq in sequences:
        seq = sorted(seq)
        seq_head_list.append(seq[0])
    sorted_seq_head_list = sorted(seq_head_list)
    return sorted_seq_head_list[0] == sorted_seq_head_list[3]


funclist[FanType2NumDict["QUADRUPLE_CHOW"]] = is_quadruple_chow


# 45.FOUR_PURE_SHIFTED_PUNGS
def is_four_shifted_pungs(state, player):
    triplets = state["pile_triplets"] + state["hand_triplets"]
    if len(triplets) < 4:
        return False
    triplet_head_list = [triplet[0] for triplet in triplets if triplet[0] in character_list]
    if len(triplet_head_list) < 4:
        return False
    triplet_head_list = sorted(triplet_head_list)
    return is_four_up(triplet_head_list)


funclist[FanType2NumDict["FOUR_PURE_SHIFTED_PUNGS"]] = is_four_shifted_pungs


# 46.FOUR_WINDS_SEVEN_PAIRS
def is_four_winds_seven_pairs(state, player):
    doubles = state["hand_double"]
    if len(doubles) != 7:
        return False

    double_list = [double[0] for double in doubles]
    wind_in_double = [wind for wind in wind_list if wind in double_list]
    return len(wind_in_double) == 4


funclist[FanType2NumDict["FOUR_WINDS_SEVEN_PAIRS"]] = is_four_winds_seven_pairs


# 47.THREE_DRAGONS_SEVEN_PAIRS
def is_three_dragons_seven_pairs(state, player):
    doubles = state["hand_double"]
    if len(doubles) != 7:
        return False

    double_list = [double[0] for double in doubles]
    dragon_in_double = [dragon for dragon in dragon_list if dragon in double_list]
    return len(dragon_in_double) == 3


funclist[FanType2NumDict["THREE_DRAGONS_SEVEN_PAIRS"]] = is_three_dragons_seven_pairs


# 48.LITTLE_FOUR_WINDS
def is_little_four_winds(state, player):
    triplets = state["pile_triplets"] + state["hand_triplets"] + \
               state["pile_gangs"] + state["hidden_pile_gangs"]
    hand_doubles = state["hand_double"]
    if len(triplets) < 3:
        return False
    if hand_doubles[0][0] not in wind_list:
        return False
    triplet_head_list = [triplet[0] for triplet in triplets if triplet[0] in wind_list]
    return len(triplet_head_list) >= 3


funclist[FanType2NumDict["LITTLE_FOUR_WINDS"]] = is_little_four_winds


# 49.LITTLE_THREE_DRAGONS
def is_little_three_dragons(state, player):
    triplets = state["pile_triplets"] + state["hand_triplets"] + \
               state["pile_gangs"] + state["hidden_pile_gangs"]
    hand_doubles = state["hand_double"]
    if len(triplets) < 2:
        return False
    if hand_doubles[0][0] not in dragon_list:
        return False
    triplet_head_list = [triplet[0] for triplet in triplets if triplet[0] in dragon_list]
    return len(triplet_head_list) >= 2


funclist[FanType2NumDict["LITTLE_THREE_DRAGONS"]] = is_little_three_dragons


# 50.ALL_HONOURS
def is_all_honors(state, player):
    if len(state["hand_double"]) == 7:
        return False
    sequences = state["pile_sequences"] + state["hand_sequences"]
    triplets = state["pile_triplets"] + state["hand_triplets"]
    doubles = state["hand_double"]
    kongs = state["pile_gangs"] + state["hidden_pile_gangs"]
    if len(sequences) > 0:
        return False
    for cards in triplets + doubles + kongs:
        if cards[0] not in dragon_list + wind_list:
            return False
    return True


funclist[FanType2NumDict["ALL_HONOURS"]] = is_all_honors


# 51.FOUR_CONCEALED_PUNGS
def is_four_concealed_pungs(state, player):
    hand_triplets_kongs = state["hand_triplets"] + state["hidden_pile_gangs"]
    num_concealed_triplet = len(hand_triplets_kongs)
    if num_concealed_triplet < 4:
        return False
    if not state["self_drawn"]:
        triplet_head = [triplet[0] for triplet in hand_triplets_kongs]
        if state["last_card_id"] in triplet_head:
            num_concealed_triplet -= 1
    return num_concealed_triplet == 4


funclist[FanType2NumDict["FOUR_CONCEALED_PUNGS"]] = is_four_concealed_pungs


# 52.PURE_TERMINAL_CHOWS
def is_terminal_chows(state, player):
    sequences = state["pile_sequences"] + state["hand_sequences"]
    hand_doubles = state["hand_double"]
    if len(sequences) < 4:
        return False
    seq_head_list = []
    for seq in sequences:
        seq = sorted(seq)
        seq_head_list.append(seq[0])

    if seq_head_list.count(9) == 2 and seq_head_list.count(15) == 2:
        if hand_doubles[0][0] == 13:
            return True
    return False


funclist[FanType2NumDict["PURE_TERMINAL_CHOWS"]] = is_terminal_chows


# 53.BIG_FOUR_WINDS
def is_big_four_winds(state, player):
    triplets = state["pile_triplets"] + state["hand_triplets"] + state["pile_gangs"] + state["hidden_pile_gangs"]
    if len(triplets) < 4:
        return False
    for triplet in triplets:
        if triplet[0] not in wind_list:
            return False
    return True


funclist[FanType2NumDict["BIG_FOUR_WINDS"]] = is_big_four_winds


# 54.BIG_THREE_DRAGONS
def is_big_three_dragons(state, player):
    triplets = state["pile_triplets"] + state["hand_triplets"] + state["pile_gangs"] + state["hidden_pile_gangs"]
    if len(triplets) < 3:
        return False
    trip_head_list = [trip[0] for trip in triplets]
    for dragon in dragon_list:
        if dragon not in trip_head_list:
            return False
    return True


funclist[FanType2NumDict["BIG_THREE_DRAGONS"]] = is_big_three_dragons


# 55.NINE_GATES

def is_nine_gates(state, player):
    if len(state["hand_cards_id"]) < 14:
        return False
    sor = sorted(state["hand_cards_id"][:-1])
    is_bamboo = sor[0] == CardIdDef.BAMBOO_1 and sor[-1] == CardIdDef.BAMBOO_9
    is_dot = sor[0] == CardIdDef.DOT_1 and sor[-1] == CardIdDef.DOT_9
    is_character = sor[0] == CardIdDef.CHARACTER_1 and sor[-1] == CardIdDef.CHARACTER_9
    if is_bamboo is False and is_dot is False and is_character is False:
        return False
    if is_trip(sor[0:3]) is False or is_trip(sor[-3:]) is False:
        return False
    return (is_bamboo and is_n_sequence(sor[3:-3], 7, CardIdDef.BAMBOO_2)) \
           or (is_character and is_n_sequence(sor[3:-3], 7, CardIdDef.CHARACTER_2)) \
           or (is_dot and is_n_sequence(sor[3:-3], 7, CardIdDef.DOT_2))


funclist[FanType2NumDict["NINE_GATES"]] = is_nine_gates


## 56.FOUR_KONGS
def is_four_kongs(state, player):
    kong_length = len(state["hidden_pile_gangs"]) + len(state["pile_gangs"])
    return kong_length == 4


funclist[FanType2NumDict["FOUR_KONGS"]] = is_four_kongs


# 57.SEVEN_SHIFTED_PAIRS
def is_seven_shifted_pairs(state, player):
    doubles = state["hand_double"]
    if len(doubles) != 7:
        return False
    doubles_flat = []
    for double in doubles:
        if double[0] not in character_list:
            return False
        doubles_flat.extend(double)
    doubles_flat = sorted(doubles_flat)
    check = np.sum([doubles_flat[i] + 1 == doubles_flat[i + 2] for i in range(0, 12, 2)]) == 6
    if check:
        return True
    else:
        return False


funclist[FanType2NumDict["SEVEN_SHIFTED_PAIRS"]] = is_seven_shifted_pairs


# 58.UPPER_FOUR
def is_upper_four(state, player):
    doubles = state["hand_double"]
    # if len(doubles)==7:
    #    return False
    sequences = state["pile_sequences"] + state["hand_sequences"]
    # triplets = state["pile_triplets"] + state["hand_triplets"]
    triplets = state["pile_triplets"] + state["hand_triplets"] + state["pile_gangs"] + state["hidden_pile_gangs"]
    all_cards = []
    for cards in doubles + sequences + triplets:
        all_cards.extend(cards)
    for card in set(all_cards):
        if card not in range(14, 18):
            return False
    return True


funclist[FanType2NumDict["UPPER_FOUR"]] = is_upper_four


# 59.LOWER_FOUR
def is_lower_four(state, player):
    doubles = state["hand_double"]
    # if len(doubles)==7:
    #    return False
    sequences = state["pile_sequences"] + state["hand_sequences"]
    # triplets = state["pile_triplets"] + state["hand_triplets"]
    triplets = state["pile_triplets"] + state["hand_triplets"] + state["pile_gangs"] + state["hidden_pile_gangs"]
    all_cards = []
    for cards in doubles + sequences + triplets:
        all_cards.extend(cards)
    for card in set(all_cards):
        if card not in range(9, 9 + 4):
            return False
    return True


funclist[FanType2NumDict["LOWER_FOUR"]] = is_lower_four


# 60.BIG_SEVEN_HONOURS
def is_big_seven_honors(state, player):
    doubles = state["hand_double"]
    if len(doubles) != 7:
        return False
    double_list = [double[0] for double in doubles]
    honor_list = wind_list + dragon_list
    honor_in_double = [honor for honor in honor_list if honor in double_list]
    return len(honor_in_double) == 7


funclist[FanType2NumDict["BIG_SEVEN_HONOURS"]] = is_big_seven_honors


# 61.HEAVENLY_HAND
def is_sky_hu(state, player):
    if player != 0:
        return False
    if len(state["hand_cards_id"]) == 14 and state["discard_tile_num"] == 0 and state["self_drawn"] is True:
        return True
    return False


funclist[FanType2NumDict["HEAVENLY_HAND"]] = is_sky_hu


# 62.EARTHLY_HAND
def is_groud_hu(state, player):
    if player == 0:
        return False
    if len(state["hand_cards_id"]) == 14 and state["piles_num"] == 0 and state["self_drawn"] is True and state[
        "discard_tile_num"] == 1:
        return True
    return False


funclist[FanType2NumDict["EARTHLY_HAND"]] = is_groud_hu


# 63.HUMANLY_HAND
def is_human_hu(state, player):
    if player == 0:
        return False
    if len(state["hand_cards_id"]) == 14 and state["piles_num"] == 0 and state["self_drawn"] is False and \
            state["discard_tile_num"] == 0:
        return True
    return False


funclist[FanType2NumDict["HUMANLY_HAND"]] = is_human_hu


# 64.FULL_FLUSH
def is_full_flush(state, player):
    sequences = state["pile_sequences"] + state["hand_sequences"]
    triplets = state["pile_triplets"] + state["hand_triplets"]
    doubles = state["hand_double"]
    kongs = state["pile_gangs"] + state["hidden_pile_gangs"]
    all_cards = []
    for cards in sequences + triplets + doubles + kongs + doubles:
        all_cards.extend(cards)
    for card in all_cards:
        if card not in character_list:
            return False
    return True


funclist[FanType2NumDict["FULL_FLUSH"]] = is_full_flush

if __name__ == "__main__":
    state = {
        "pile_gangs": [],
        "hidden_pile_gangs": [],
        "pile_triplets": [],
        "pile_sequences": [[9, 10, 11], [10, 11, 9], [10, 11, 12]],
        "hand_triplets": [[12, 12, 12]],
        "hand_sequences": [],
        "hand_double": [[9, 9]]
    }
    print(is_lower_four(state, 0))

    state = {
        "pile_gangs": [],
        "hidden_pile_gangs": [],
        "pile_triplets": [],
        "pile_sequences": [[14, 15, 16], [15, 16, 14], [15, 16, 17]],
        "hand_triplets": [[17, 17, 17]],
        "hand_sequences": [],
        "hand_double": [[14, 14]]
    }
    print(is_upper_four(state, 0))

    state = {
        "pile_sequences": [],
        "pile_triplets": [],
        "pile_gangs": [],
        "hidden_pile_gangs": [],
        "hand_sequences": [[9, 10, 11], [14, 15, 16]],
        "hand_triplets": [[27, 27, 27], [30, 30, 30]],
        "hand_double": [[28, 28]],
        "self_drawn": True,
    }
    print(is_fully_concealed_hand(state, 0))
