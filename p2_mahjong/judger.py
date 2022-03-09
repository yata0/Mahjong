# coding=utf-8
""" Implement Mahjong Judger class
"""
import sys
from collections import defaultdict
from p2_mahjong.DEF import CardIdDef, ActionType, CARD3_SET_NUM
from p2_mahjong.utils import DIC_CHOW, card_decoding_dict
log_head = "judger.py "


class MahjongJudger(object):
    """ Determine what cards a player can play
    """

    def __init__(self):
        """ Initilize the Judger class for Mahjong
        """
        pass

    @staticmethod
    def judge_gong(player, game_id=""):
        """
        judge if the player can gong or not
        """
        gong_card_id = []
        for card_id in player.dic_hand_id2card:
            if len(player.dic_hand_id2card[card_id]) == 4:
                gong_card_id.append(card_id)
        if len(gong_card_id) > 0:
            return True, gong_card_id
        return False, None

    @staticmethod
    def judge_add_gong(player, game_id=""):
        """
        judge if the player can add_gong or not
        """
        func_head = "judge_add_gong()"
        add_gong_card_id = []
        for to_gong_cid in player.dic_hand_id2card:
            for cur_pile in player.pile:
                cnt = 0
                for card in cur_pile:
                    if card.card_id == to_gong_cid:
                        cnt += 1
                    else:
                        break
                if cnt == 3:
                    if player.is_wait:
                        if to_gong_cid not in player.wait_del_tile:
                            continue
                    add_gong_card_id.append(to_gong_cid)
                    for cur_card in player.hand:
                        if cur_card.card_id == to_gong_cid:
                            player.add_gong_card = cur_card
                elif cnt > 0:
                    break
        if len(add_gong_card_id) > 0:
            return True, add_gong_card_id
        return False, None

    @staticmethod
    def judge_concealed_gong(player, game_id=""):
        """
        judge if the player can concealed_gong or not
        """
        func_head = "judge_concealed_gong()" + game_id
        gong_card_id = []
        for card_id in player.dic_hand_id2card:
            if len(player.dic_hand_id2card[card_id]) == 4:
                if player.is_wait is True:
                    assert len(player.wait_tile) > 0
                    check_list = player.wait_tile
                    set_cnt = len(player.pile) + len(player.hidden_pile) + 1
                    remain_hand = list()
                    dic_id2cnt = dict()
                    for hand_card in player.hand:
                        if hand_card.card_id != card_id:
                            remain_hand.append(hand_card.card_id)
                            if hand_card.card_id not in dic_id2cnt:
                                dic_id2cnt[hand_card.card_id] = []
                            dic_id2cnt[hand_card.card_id].append(hand_card.runtime_id)
                    # is_waited = False
                    for extra_card in check_list:
                        if extra_card == card_id:
                            continue
                        remain_hand_tmp = remain_hand.copy()
                        is_wait_again = MahjongJudger.judge_hu_with_extra_card_v1(remain_hand_tmp, set_cnt, dic_id2cnt, extra_card, game_id)
                        if is_wait_again:
                            gong_card_id.append(card_id)
                            break
                else:
                    gong_card_id.append(card_id)
        if len(gong_card_id) > 0:
            return True, gong_card_id
        return False, gong_card_id

    @staticmethod
    def judge_chow_card(player, table_top_card, game_id=""):
        """
        returns:
            (bool): True if player can chow the card that discard in last round
            (list): if player can chow the card(ie 3), hand card=[1,2,4], then return [[2,1,3], [2,4,3]]
        """
        func_head = "judge_chow_card()" + game_id
        if player.is_wait:
            return False, None
        last_card_user = table_top_card.get_user_id()
        if player.get_last_player() != last_card_user:
            return False, None

        last_card_id = table_top_card.get_card_id()
        left_card_id = last_card_id - 1
        right_card_id = last_card_id + 1
        if left_card_id not in player.dic_hand_id2card and right_card_id not in player.dic_hand_id2card:
            return False, None

        lis_makeup = list()
        if CardIdDef.BAMBOO_1 <= last_card_id <= CardIdDef.BAMBOO_9:
            lis_makeup = MahjongJudger.is_chow(last_card_id, player.dic_hand_id2card
                                               , CardIdDef.BAMBOO_1, CardIdDef.BAMBOO_9, game_id)
        elif CardIdDef.CHARACTER_1 <= last_card_id <= CardIdDef.CHARACTER_9:
            lis_makeup = MahjongJudger.is_chow(last_card_id, player.dic_hand_id2card
                                               , CardIdDef.CHARACTER_1, CardIdDef.CHARACTER_9, game_id)
        elif CardIdDef.DOT_1 <= last_card_id <= CardIdDef.DOT_9:
            lis_makeup = MahjongJudger.is_chow(last_card_id, player.dic_hand_id2card
                                               , CardIdDef.DOT_1, CardIdDef.DOT_9, game_id)
        if len(lis_makeup) > 0:
            return True, lis_makeup
        return False, None

    @staticmethod
    def judge_seven_pairs(player, game_id=""):
        if len(player.hand) != 14:
            return False
        for card_id in player.dic_hand_id2card:
            if len(player.dic_hand_id2card[card_id]) % 2 != 0:
                return False
        return True

    @staticmethod
    def judge_seven_pairs_with_extra_card(hand_card_num, dic_hand_id2card, extra_card_id, game_id=""):
        if hand_card_num != 13:
            return False
        if extra_card_id not in dic_hand_id2card:
            return False
        for card_id in dic_hand_id2card:
            if len(dic_hand_id2card[card_id]) % 2 == 0:
                if card_id == extra_card_id:
                    return False
            else:
                if card_id != extra_card_id:
                    return False
        return True

    @staticmethod
    def judge_hu(player, game_id=""):
        """
        Args:
            player (object): Target player

        Return:
            Result (bool): Win or not
        """
        func_head = "judge_hu()" + game_id
        if MahjongJudger.judge_seven_pairs(player, game_id):
            return True
        latest_id = player.hand[-1].get_card_id()
        left_id = latest_id - 1
        right_id = latest_id + 1
        if left_id not in player.dic_hand_id2card \
                and right_id not in player.dic_hand_id2card \
                and len(player.dic_hand_id2card[latest_id]) < 2:
            return False
        hand_id = [card.get_card_id() for card in player.hand]
        count_dict = {}
        for card_id in hand_id:
            if card_id in count_dict:
                count_dict[card_id] += 1
            else:
                count_dict[card_id] = 1

        set_count = len(player.pile) + len(player.hidden_pile)

        if set_count >= CARD3_SET_NUM and len(set(hand_id)) == 1 and len(hand_id) == 2:
            return True
        for each in count_dict:
            tmp_hand = hand_id.copy()

            if count_dict[each] >= 2:
                for _ in range(2):
                    tmp_hand.pop(tmp_hand.index(each))
                is_3_set, tmp_set_count = MahjongJudger.cal_set(tmp_hand, game_id)
                if is_3_set:
                    if tmp_set_count + set_count >= CARD3_SET_NUM:
                        return True
                    print(log_head, func_head, "tmp_set_count+set_count=", tmp_set_count+set_count)
                    print(log_head, func_head, "CARD3_SET_NUM=", CARD3_SET_NUM)
                    assert False
        return False

    @staticmethod
    def cal_set(cards, game_id=""):
        """ Calculate the set for given cards
        Args:
            cards (list): List of cards.

        Return:
            is_set3 (bool):
            set_count (int): num of 3-element set, valid only if is_set3 == true
        """
        func_head = "cal_set()" + game_id
        # get all of the traits of each type in hand (except dragons and winds)
        _dict_by_type = defaultdict(list)
        set_count = 0

        t_dic_no_chow = {}
        for card_id in cards:
            if card_id not in DIC_CHOW:
                if card_id not in t_dic_no_chow:
                    t_dic_no_chow[card_id] = 0
                t_dic_no_chow[card_id] += 1
        for card_id in t_dic_no_chow:
            if t_dic_no_chow[card_id] == 3:
                set_count += 1
            else:
                return False, set_count

        for card_id in cards:
            if card_id not in DIC_CHOW:
                continue
            else:
                _type = int(card_id / 9)
                _trait = int(card_id % 9)
                _dict_by_type[_type].append(_trait)
        for _type in _dict_by_type.keys():
            values = sorted(_dict_by_type[_type])
            is_3_set, set_num = MahjongJudger.sort_by_3_elements(values, game_id)
            if is_3_set:
                set_count += set_num
            else:
                return False, set_count
        return True, set_count

    @staticmethod
    def sort_by_3_elements(lis, game_id=""):
        next = -1
        if len(lis) % 3 != 0:
            return False, 0
        assert len(lis) % 3 == 0
        for idx_i in range(len(lis)):
            if idx_i <= next:
                continue
            k = idx_i % 3
            if k == 0:
                if lis[idx_i] == lis[idx_i+1] and lis[idx_i] == lis[idx_i+2]:
                    next = idx_i + 2
                    continue
                min_value = min(lis[idx_i:])
                if lis[idx_i] != min_value:
                    min_idx = lis[idx_i:].index(min_value)
                    lis[idx_i], lis[idx_i + min_idx] = lis[idx_i + min_idx], lis[idx_i]
            elif k != 0:
                last_value = lis[idx_i - 1]
                exp_value = last_value + 1
                if exp_value in lis[idx_i:]:
                    exp_idx = lis[idx_i:].index(exp_value) + idx_i
                    lis[idx_i], lis[exp_idx] = lis[exp_idx], lis[idx_i]
                else:
                    return False, len(lis)/3
        return True, len(lis)/3

    @staticmethod
    def chow_1(card_id, dic_hand, game_id=""):
        lis_makeup = list()
        card_id_1 = card_id + 1
        card_id_2 = card_id + 2
        if card_id_1 in dic_hand and card_id_2 in dic_hand:
            lis_makeup.append([card_id_1, card_id_2, card_id])
        return lis_makeup

    @staticmethod
    def chow_2(card_id, dic_hand, game_id=""):
        lis_makeup = list()
        card_id_1 = card_id - 1  # 1
        card_id_2 = card_id + 1  # 3
        card_id_3 = card_id + 2  # 4
        if card_id_2 in dic_hand:
            if card_id_1 in dic_hand:
                lis_makeup.append([card_id_1, card_id_2, card_id])
            if card_id_3 in dic_hand:
                lis_makeup.append([card_id_2, card_id_3, card_id])
        return lis_makeup

    @staticmethod
    def chow_8(card_id, dic_hand, game_id=""):
        lis_makeup = list()
        card_id_1 = card_id - 2  # 6
        card_id_2 = card_id - 1  # 7
        card_id_3 = card_id + 1  # 9
        if card_id_2 in dic_hand:
            if card_id_1 in dic_hand:
                lis_makeup.append([card_id_1, card_id_2, card_id])
            if card_id_3 in dic_hand:
                lis_makeup.append([card_id_2, card_id_3, card_id])
        return lis_makeup

    @staticmethod
    def chow_9(card_id, dic_hand, game_id=""):
        lis_makeup = list()
        card_id_1 = card_id - 2
        card_id_2 = card_id - 1
        if card_id_1 in dic_hand and card_id_2 in dic_hand:
            lis_makeup.append([card_id_1, card_id_2, card_id])
        return lis_makeup

    @staticmethod
    def chow_3_7(card_id, dic_hand, game_id=""):
        lis_makeup = list()
        card_id_1 = card_id - 2
        card_id_2 = card_id - 1
        card_id_3 = card_id + 1
        card_id_4 = card_id + 2
        if card_id_2 in dic_hand:
            if card_id_1 in dic_hand:
                lis_makeup.append([card_id_1, card_id_2, card_id])
            if card_id_3 in dic_hand:
                lis_makeup.append([card_id_2, card_id_3, card_id])
        if card_id_3 in dic_hand and card_id_4 in dic_hand:
            lis_makeup.append([card_id_3, card_id_4, card_id])
        return lis_makeup

    @staticmethod
    def is_chow(card_id, dic_hand, cmp_beg_id, cmp_end_id, game_id=""):
        if card_id == cmp_beg_id:
            lis_makeup = MahjongJudger.chow_1(card_id, dic_hand, game_id)
        elif card_id == (cmp_beg_id + 1):
            lis_makeup = MahjongJudger.chow_2(card_id, dic_hand, game_id)
        elif card_id == (cmp_end_id - 1):
            lis_makeup = MahjongJudger.chow_8(card_id, dic_hand, game_id)
        elif card_id == cmp_end_id:
            lis_makeup = MahjongJudger.chow_9(card_id, dic_hand, game_id)
        else:
            lis_makeup = MahjongJudger.chow_3_7(card_id, dic_hand, game_id)
        return lis_makeup

    @staticmethod
    def is_rob_gong_card(players, current_player, game_id=""):
        """
        judge if oppenent player can rob the gong of current player
        :param players:
        :param current_player:
        :return:
        """
        func_head = "is_rob_gong_card()" + game_id
        next_player = (current_player + 1) % 2
        lis_pid = list()
        play_order = list([next_player])

        for pid in play_order:
            players[pid].valid_act = dict()
        # check who wins
        for pid in play_order:
            is_hu = MahjongJudger.judge_hu_with_extra_card(players[pid], players[current_player].add_gong_card.card_id, game_id)
            if is_hu:
                lis_pid.append(pid)
                players[pid].valid_act[ActionType.ActionTypeHu] = players[current_player].add_gong_card.card_id
                players[pid].valid_act[ActionType.ActionTypePassHu] = 1
                players[pid].rob_gong_card = players[current_player].add_gong_card
            else:
                players[pid].rob_gong_card = None
        if len(lis_pid) > 0:
            lis_pid.append(current_player)
            players[current_player].valid_act[ActionType.ActionTypeDraw] = 1
        return lis_pid

    @staticmethod
    def gong_after_wait(player, gong_card_id, game_id=""):
        func_head = "gong_after_wait()"
        num = len(player.dic_hand_id2card.get(gong_card_id, []))
        if num != 3:
            return False
        new_hand = list()
        for card in player.hand:
            if card.card_id != gong_card_id:
                new_hand.append(card.card_id)
        assert len(new_hand) % 3 == 1
        set_cnt = len(player.pile) + len(player.hidden_pile) + 1 # 刻子数
        dic_id2cnt = {}
        for tid in player.dic_hand_id2card:
            if tid != gong_card_id:
                dic_id2cnt[tid] = player.dic_hand_id2card[tid].copy()
        for extra_card in player.wait_tile:
            cur_tmp_hand = new_hand.copy()
            ret = MahjongJudger.judge_hu_with_extra_card_v1(cur_tmp_hand, set_cnt, dic_id2cnt, extra_card, game_id)
            if ret:
                return True
        return False

    @staticmethod
    def is_target_card(players, current_player, card_to_use, game_id=""):
        func_head = "is_target_card()" + game_id
        next_player = (current_player + 1) % 2
        lis_pid = list()
        play_order = list([next_player])

        for pid in play_order:
            players[pid].valid_act = dict()
        # check who wins
        for pid in play_order:
            is_hu = MahjongJudger.judge_hu_with_extra_card(players[pid], card_to_use.get_card_id(), game_id)
            if is_hu:
                lis_pid.append(pid)
                players[pid].valid_act[ActionType.ActionTypeHu] = card_to_use.get_card_id()
                players[pid].valid_act[ActionType.ActionTypePassHu] = 1

        # check who pg
        for pid in play_order:
            if players[pid].is_wait is True:
                if MahjongJudger.gong_after_wait(players[pid], card_to_use.card_id, game_id):

                    players[pid].valid_act[ActionType.ActionTypeGong] = [card_to_use.card_id]
                    if pid not in lis_pid:
                        lis_pid.append(pid)
                continue
            pg_type, pg_card_id_list = MahjongJudger.judge_pg_with_extra_card(players[pid], card_to_use, game_id)
            if pg_type is not None:
                if pid not in lis_pid:
                    lis_pid.append(pid)
                if pg_type == ActionType.ActionTypePong:
                    players[pid].valid_act[ActionType.ActionTypePong] = pg_card_id_list
                elif pg_type == ActionType.ActionTypeGong:
                    players[pid].valid_act[ActionType.ActionTypePong] = pg_card_id_list
                    players[pid].valid_act[ActionType.ActionTypeGong] = pg_card_id_list
                else:
                    print(log_head, func_head, "illegal_pg_type=", pg_type)
                    assert False
                break

        # check if the next player chow
        is_chow, ch_pattern_list = MahjongJudger.judge_chow_card(players[next_player], card_to_use, game_id)
        if is_chow:
            if next_player not in lis_pid:
                lis_pid.append(next_player)
            players[next_player].valid_act[ActionType.ActionTypeChow] = ch_pattern_list
        if len(lis_pid) > 0:
            if next_player not in lis_pid:
                lis_pid.append(next_player)

        for pid in lis_pid:
            if pid != next_player:
                action_lis = list(players[pid].valid_act.keys())
                if ActionType.ActionTypeChow in action_lis \
                        or ActionType.ActionTypePong in action_lis \
                        or ActionType.ActionTypeGong in action_lis:
                    players[pid].valid_act[ActionType.ActionTypePass] = 1
            else:
                players[pid].valid_act[ActionType.ActionTypeDraw] = 1
        return lis_pid

    @staticmethod
    def judge_hu_with_extra_card(player, extra_card_id, game_id=""):

        func_head = "judge_hu_with_extra_card()" + game_id
        if MahjongJudger.judge_seven_pairs_with_extra_card(len(player.hand), player.dic_hand_id2card, extra_card_id, game_id):
            return True
        left_id = extra_card_id - 1
        right_id = extra_card_id + 1
        if extra_card_id not in player.dic_hand_id2card \
                and left_id not in player.dic_hand_id2card \
                and right_id not in player.dic_hand_id2card:
            return False
        hand = [card.get_card_id() for card in player.hand]
        hand.append(extra_card_id)
        count_dict = {}
        for card in hand:
            if card in count_dict:
                count_dict[card] += 1
            else:
                count_dict[card] = 1

        set_count = len(player.pile) + len(player.hidden_pile)

        if set_count >= CARD3_SET_NUM and len(set(hand)) == 1 and len(hand) == 2:
            return True
        for each in count_dict:
            tmp_hand = hand.copy()
            if count_dict[each] >= 2:
                for _ in range(2):
                    tmp_hand.pop(tmp_hand.index(each))
                is_3_set, tmp_set_count = MahjongJudger.cal_set(tmp_hand, game_id)
                if is_3_set:
                    if tmp_set_count + set_count >= CARD3_SET_NUM:
                        return True
                    print(log_head, func_head, "tmp_set_count+set_count=", tmp_set_count+set_count)
                    print(log_head, func_head, "CARD3_SET_NUM=", CARD3_SET_NUM)
                    print(log_head, func_head, "pid=", player.player_id)
                    print(log_head, func_head, "hand=", player.get_hand_str())
                    print(log_head, func_head, "pile=", player.get_pile_str())
                    print(log_head, func_head, "concealed_pile=", player.get_concealed_pile_str())
                    assert False
        return False

    @staticmethod
    def judge_pg_with_extra_card(player, dealer_top_card, game_id=""):
        pg_type = None
        pg_card_ids = []
        card_id = dealer_top_card.get_card_id()
        cnt = len(player.dic_hand_id2card.get(card_id, []))
        if cnt == 3:
            pg_type = ActionType.ActionTypeGong
            pg_card_ids = [card_id]
        elif cnt == 2:
            pg_type = ActionType.ActionTypePong
            pg_card_ids = [card_id]
        return pg_type, pg_card_ids

    @staticmethod
    def judge_wait(player, game_id=""):
        flag = False
        discard_card_ids = list()
        dic_wait_cards = dict()
        hand = [hand_card.card_id for hand_card in player.hand]

        set_cnt = len(player.pile) + len(player.hidden_pile)
        check_card_lis = list(range(34)) if not player.wait_tile else player.wait_tile
        del_card_lis = list(player.dic_hand_id2card.keys())
        if player.is_wait and player.wait_del_tile:
            del_card_lis = player.wait_del_tile
        for id in del_card_lis:
            if id not in player.dic_hand_id2card:
                continue
            is_wait = False
            wait_card = list()
            tmp_hand = hand.copy()
            tmp_hand.pop(tmp_hand.index(id))
            assert len(tmp_hand) % 3 == 1
            dic_id2cnt = {}
            for tid in player.dic_hand_id2card:
                dic_id2cnt[tid] = player.dic_hand_id2card[tid].copy()
            if len(dic_id2cnt[id]) == 1:
                del dic_id2cnt[id]
            else:
                dic_id2cnt[id].pop(0)
            for extra_card in check_card_lis:
                cur_tmp_hand = tmp_hand.copy()
                ret = MahjongJudger.judge_hu_with_extra_card_v1(cur_tmp_hand, set_cnt, dic_id2cnt, extra_card, game_id)
                if ret:
                    is_wait = True
                    wait_card.append(extra_card)
            if is_wait:
                discard_card_ids.append(id)
                dic_wait_cards[id] = wait_card
        if len(discard_card_ids) > 0:
            flag = True
        return flag, discard_card_ids, dic_wait_cards

    @staticmethod
    def judge_hu_with_extra_card_v1(hand, set_count, dic_hand_id2card, extra_card_id, game_id=""):
        if MahjongJudger.judge_seven_pairs_with_extra_card(len(hand), dic_hand_id2card, extra_card_id, game_id):
            return True
        left_id = extra_card_id - 1
        right_id = extra_card_id + 1
        if extra_card_id not in dic_hand_id2card \
                and left_id not in dic_hand_id2card \
                and right_id not in dic_hand_id2card:

            return False
        hand.append(extra_card_id)
        count_dict = {}
        for card in hand:
            if card in count_dict:
                count_dict[card] += 1
            else:
                count_dict[card] = 1

        if set_count >= CARD3_SET_NUM and len(set(hand)) == 1 and len(hand) == 2:
            return True
        for each in count_dict:
            tmp_hand = hand.copy()
            if count_dict[each] >= 2:
                for _ in range(2):
                    tmp_hand.pop(tmp_hand.index(each))
                is_3_set, tmp_set_count = MahjongJudger.cal_set(tmp_hand, game_id)
                if is_3_set:
                    if tmp_set_count + set_count >= CARD3_SET_NUM:
                        return True
        return False

