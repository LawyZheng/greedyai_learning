from MyRobot import Robot


def main():
    robot = Robot()
    print('** 请输入你想说的话，如果你不想聊天了。可以按q键退出程序。 **')
    input('** 请按Enter键，开始聊天。 **')

    replay = ""
    print('我是个机器人: Hello, 你想聊啥呀？')
    while(True):
        replay = input('巨龙为搞你而来: ')
        if replay in ['q', "Q"]:
            print('我是个机器人: 拜拜。下次再聊')
            break

        answer = robot.get_answer(replay)
        print('我是个机器人: %s' % answer)


if __name__ == '__main__':
    main()
