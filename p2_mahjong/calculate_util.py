import numpy as np
from collections import defaultdict
from p2_mahjong.utils import character_list

num_list = character_list


def split_hands(hand_id, pile_id, result_list):
    hand_id_count_dict = defaultdict(int)
    for card_id in hand_id:
        hand_id_count_dict[card_id] += 1
    fixed_cnt = len(pile_id)
    tmp = []
    return divide_recursively(hand_id_count_dict, fixed_cnt, 0, tmp, result_list)


def divide_tail_add_division(fixed_cnt, work_division, result_list):
    sorted_work_division = sorted(work_division)
    if sorted_work_division not in result_list:
        result_list.append(sorted_work_division)


def divide_tail(hand_table, fixed_cnt, work_division, result_list):
    hand_id_in_table = list(hand_table.keys())
    for i in hand_id_in_table:
        if hand_table[i] < 2:
            continue
        hand_table[i] -= 2
        if np.sum([hand_table[c] for c in hand_table]) == 0:
            hand_table[i] += 2
            work_division.append([i] * 2)
            divide_tail_add_division(fixed_cnt, work_division, result_list)
            return True
        hand_table[i] += 2

    return False


def is_division_branch_exists(fixed_cnt, step, work_division, result_list):
    if (len(result_list) <= 0) or (step < 3):
        return False

    return sorted(work_division) in result_list


def divide_recursively(hand_table, fixed_cnt, step, work_division, result_list):
    idx = fixed_cnt + step
    if idx == 4:
        return divide_tail(hand_table, fixed_cnt, work_division, result_list)
    result = False
    hand_id_in_table = list(hand_table.keys())
    for i in hand_id_in_table:
        if hand_table[i] < 1:
            continue
        if hand_table[i] > 2:
            work_division_cp = work_division.copy()
            work_division_cp.append([i] * 3)

            if not is_division_branch_exists(fixed_cnt, step + 1, work_division_cp, result_list):
                hand_table[i] -= 3
                if divide_recursively(hand_table, fixed_cnt, step + 1, work_division_cp, result_list):
                    result = True
                hand_table[i] += 3

        if i in num_list:
            if (i % 9) < 8 and hand_table[i + 1] and hand_table[i + 2]:
                work_division_cp = work_division.copy()
                work_division_cp.append([i, i + 1, i + 2])
                if not is_division_branch_exists(fixed_cnt, step + 1, work_division_cp, result_list):
                    hand_table[i] -= 1
                    hand_table[i + 1] -= 1
                    hand_table[i + 2] -= 1
                    if divide_recursively(hand_table, fixed_cnt, step + 1, work_division_cp, result_list):
                        result = True
                    hand_table[i] += 1
                    hand_table[i + 1] += 1
                    hand_table[i + 2] += 1
    return result


def is_sequence(lis):
    lis = sorted(lis)
    if len(lis) != 3:
        return False
    return lis[0] + 1 == lis[1] and lis[0] + 2 == lis[2]


def is_trip(lis):
    if len(lis) != 3:
        return False
    return lis[0] == lis[1] and lis[1] == lis[2]


def is_n_sequence(lis, count, beg_num):
    new_lis = sorted(lis)
    if len(new_lis) != count:
        return False
    if new_lis[0] != beg_num:
        return False
    for idx in range(1, count):
        if (new_lis[idx] - new_lis[idx - 1]) != 1:
            return False
    return True


def struct_cards(hand_cards_id, pile_cards, hidden_pile_cards, self_drawn, last_card_id, result_list):
    final_result_list = []
    pile_gangs = []
    pile_sequence = []
    pile_triplet = []
    hidden_gangs = hidden_pile_cards
    for piles in pile_cards:
        if len(piles) == 4:
            pile_gangs.append(piles)
        else:
            if is_sequence(piles):
                pile_sequence.append(piles)
            else:
                pile_triplet.append(piles)
    for result in result_list:
        hand_sequence = []
        hand_triplet = []
        hand_double = []

        for l in result:
            if is_trip(l):
                hand_triplet.append(l)
            elif is_sequence(l):
                hand_sequence.append(l)
            else:
                hand_double.append(l)
        final_result_list.append(
            {
                "pile_sequences": pile_sequence,
                "pile_triplets": pile_triplet,
                "pile_gangs": pile_gangs,
                "hidden_pile_gangs": hidden_gangs,
                "hand_sequences": hand_sequence,
                "hand_triplets": hand_triplet,
                "hand_double": hand_double,
                "self_drawn": self_drawn,
                "last_card_id": last_card_id,
                "hand_cards_id": hand_cards_id
            }
        )
    return final_result_list
