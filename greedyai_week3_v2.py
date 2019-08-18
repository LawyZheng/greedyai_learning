import random


def get_one_card(poker_pool):
    return poker_pool.pop(random.randint(0, len(poker_pool)-1))


def score_count(hand_card):
    # J Q K 都为10点。
    # A先作为11点，如果总点数大于21点的话，则作为1点。

    score = 0
    have_A = False

    # 查看每张牌的末尾字符是什么。
    # 如果是0，则应该抽到的是10点。如果是其他数字，则应该是对应点数。
    # 如果是J Q K，则为10点。
    for each_card in hand_card:

        if each_card[-1] in ['J', 'Q', 'K', '0']:
            score += 10
        elif each_card[-1] == 'A':
            score += 1
            have_A = True
        else:
            score += int(each_card[-1])

    # 如果有A，则进行额外的点数添加。
    # 由于两张A如果都最为11点计算的话，结果必然大于21点，因此最多只有1张A最为11点计算。
    if have_A and score < 12:
        score += 10

    return score


def if_get_next():
    if_get_next_card = input("是否继续叫牌？ (Y/N) >>>>>>")
    if if_get_next_card.upper() == 'Y':
        return True
    elif if_get_next_card.upper() == 'N':
        return False
    else:
        print("无效的输入，请重新输入。")
        return if_get_next()


def win_or_equal_posibility(pc_score, player_score, poker_pool):
    delta = player_score - pc_score
    win_count = 0
    cards_number = len(poker_pool)

    # 查看牌库里的每一张牌
    for each_card in poker_pool:
        # 卡池里点数为10的牌
        if each_card[-1] in ['0', 'J', 'Q', 'K']:
            if pc_score + 10 < 22 and delta <= 10:
                win_count += 1

        # 卡池里的A
        elif each_card[-1] == 'A':
            # 如果庄家点数 < 11 的话，抽到A应该作为11点计算
            if pc_score < 11 and delta <= 11:
                win_count += 1
            # 如果庄家点数 >= 11 的话，抽到的A应该作为1点计算
            if pc_score + 1 < 22 and delta <= 1:
                win_count += 1

        # 卡池里的其他牌，即2-9
        else:
            if pc_score + int(each_card[-1]) < 22 and delta <= int(each_card[-1]):
                win_count += 1

    return win_count/cards_number


def pc_get_card(pc_hand_card, player_score, poker_pool):
    # 电脑叫牌。
    # 直到手牌点数大于玩家手牌点数。
    # 或者手牌数量等于5张。
    # 或者庄家手牌点数大于等于21，才停止叫牌。

    # new update
    # 庄家叫牌前先计算拿到牌的胜率，大于50%才会继续叫牌

    # 计算目前庄家手牌的点数
    pc_score = score_count(pc_hand_card)
    while(pc_score < player_score):
        # 如果手牌数等于5张，则不能再继续叫牌
        if len(pc_hand_card) == 5:
            break

        # 如果相差>=11，那么则无需进行获胜概率的计算，直接进行叫牌
        # 如果继续叫牌的获胜和平局概率小于30%，则停止叫牌
        if player_score - pc_score < 11 and win_or_equal_posibility(pc_score, player_score, poker_pool) < 0.3:
            break

        # 抽取一张牌
        pc_hand_card.append(get_one_card(poker_pool))
        # 重新计算手牌的点数
        pc_score = score_count(pc_hand_card)

        # # 如果电脑的点数已经达到21点，或者大于21点，则不用继续叫牌，退出循环
        # if score_count(pc_hand_card) >= 21:
        #     break


def random_card():
    poker_pool = list()

    # 初始化一组牌
    card_types = ['黑桃', '红桃', '梅花', '方块']
    for card_type in card_types:
        for i in range(13):
            if i == 0:
                poker_pool.append(card_type + 'A')
            elif i < 10:
                poker_pool.append(card_type + str(i+1))
            elif i == 10:
                poker_pool.append(card_type + 'J')
            elif i == 11:
                poker_pool.append(card_type + 'Q')
            elif i == 12:
                poker_pool.append(card_type + 'K')

    # 洗牌
    random.shuffle(poker_pool)

    return poker_pool


def every_round(poker_pool):
    # 返回 电脑胜-1 or 平局0 or 玩家胜1
    # 叫牌规则：
    # 玩家在手牌小于5张，且点数小于21点的时候可以叫牌。
    # 电脑在手牌小于5张，且点数大于等于玩家点数的时候可以叫牌。

    pc_hand_card = list()
    player_hand_card = list()

    # 初始化发牌，电脑和玩家各发两张
    for i in range(2):
        pc_hand_card.append(get_one_card(poker_pool))
    for i in range(2):
        player_hand_card.append(get_one_card(poker_pool))

    # 查看双方的手牌
    print("庄家的手牌为: [**, %s]" % pc_hand_card[1])
    print("目前你的手牌为: {}".format(player_hand_card))

    # 计算双方目前的点数
    pc_score = score_count(pc_hand_card)
    player_score = score_count(player_hand_card)

    # # 平局
    # if pc_score == player_score == 21:
    #     print("双方点数都达到21点。")
    #     print("庄家的手牌为: {}".format(pc_hand_card))
    #     return 0
    # # 电脑胜
    # elif pc_score == 21:
    #     print("庄家点数达到21点。")
    #     print("庄家的手牌为: {}".format(pc_hand_card))
    #     return -1
    # # 玩家胜
    # elif player_score == 21:
    #     print("玩家点数达到21点。")
    #     print("庄家的手牌为: {}".format(pc_hand_card))
    #     return 1

    # 玩家是否继续叫牌
    if_get_next_card = if_get_next()
    while if_get_next_card:
        # 是否持有5张手牌
        if len(player_hand_card) == 5:
            print("已经有5张手牌，无法继续叫牌。")
            break

        # 玩家叫取一张牌
        player_hand_card.append(get_one_card(poker_pool))
        print("目前你的手牌为: {}".format(player_hand_card))

        # 计算玩家点数，是否大于21。
        player_score = score_count(player_hand_card)
        if player_score > 21:
            print("玩家点数大于21点，本回合游戏结束。")
            print("庄家的手牌为: {}".format(pc_hand_card))
            return -1

        # 是否继续叫牌
        if_get_next_card = if_get_next()

    # 庄家叫牌
    print("玩家停止叫牌。")
    print("庄家正在进行叫牌...")

    pc_get_card(pc_hand_card, player_score, poker_pool)
    pc_score = score_count(pc_hand_card)
    print("庄家叫牌结束。")
    print("庄家的手牌为: {}".format(pc_hand_card))

    # 结果判断
    if pc_score > 21:
        print("庄家点数大于21点，本回合游戏结束。")
        return 1
    elif pc_score == player_score:
        return 0
    else:
        return -1 if pc_score > player_score else 1


def continue_game():
    if_continue = input("是否继续进行游戏？ (Y/N) >>>>>>>>>")
    if if_continue.upper() == 'Y':
        return True
    elif if_continue.upper() == 'N':
        return False
    else:
        print("无效的输入，请重新输入。")
        return continue_game()


def main():
    input("按Enter键开始游戏。")
    # 洗牌
    print("正在进行洗牌...")
    poker_pool = random_card()
    print("洗牌结束，游戏正式开始。")

    game_round = 1
    # 前面表示电脑得分，后面表示玩家得分
    total_scores = [0, 0]

    while(True):
        print("-"*20)
        print("第%d回合开始。" % game_round)

        # 如果卡池里的牌少于15张，就重新洗牌
        if len(poker_pool) < 15:
            print("由于卡池里的牌少于15张，正在进行重新洗牌。")
            poker_pool = random_card()
            print("重新洗牌结束，游戏继续。")

        # -1:电脑获胜  0:平局  1:玩家获胜
        result = every_round(poker_pool)

        if result == -1:
            print("庄家获胜。")
            total_scores[0] += 1
        elif result == 1:
            print("玩家获胜。")
            total_scores[1] += 1
        else:
            print("平局。")

        print("当前比分为 >>>>>>  庄家 %d - %d 玩家。" %
              (total_scores[0], total_scores[1]))

        if_continue_game = continue_game()
        if if_continue_game:
            game_round += 1
        else:
            print("游戏结束。")
            break


if __name__ == '__main__':
    main()
