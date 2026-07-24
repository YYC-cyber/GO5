from typing import List, Optional
from src.core.player import Player
from src.core.enemy import Enemy
from src.ui.console_ui import ConsoleUI
import time


class Battle:
    """战斗系统"""

    def __init__(self, player: Player, enemies: List[Enemy]):
        self.player = player
        self.enemies = enemies
        self.player.enemies = enemies
        self.ui = ConsoleUI()
        self.turn = 0
        self.game_over = False
        self.player_turn_ended = False  # 标记玩家回合是否结束

    def start(self):
        """开始战斗"""
        self.ui.show_battle_start(self.player, self.enemies)

        # 初始抽牌
        self.player.draw(5)

        # 战斗循环
        while not self.game_over:
            self.turn += 1
            print(f"\n{'=' * 60}")
            print(f"📅 第 {self.turn} 回合")
            print('=' * 60)

            # === 玩家回合 ===
            if self.player.is_alive():
                self.player_turn()
                # 玩家回合结束，标记
                self.player_turn_ended = True

                # 检查战斗是否结束（玩家可能死亡或敌人全灭）
                if self.check_battle_end():
                    break

                # 玩家回合结束后，如果游戏没有结束，进入敌人回合
                # 等待一下让玩家看到结果
                input("\n按 Enter 键让敌人进攻...")

            # === 敌人回合 ===
            if self.player.is_alive() and any(e.is_alive() for e in self.enemies):
                self.enemy_turn()

                # 检查战斗是否结束
                if self.check_battle_end():
                    break

                # 敌人回合结束后，等待一下再开始下一回合
                if not self.game_over:
                    input("\n按 Enter 键开始下一回合...")

        # 显示战斗结果
        self.ui.show_battle_result(self.player)

    def check_battle_end(self) -> bool:
        """检查战斗是否结束"""
        # 检查玩家是否死亡
        if not self.player.is_alive():
            self.game_over = True
            self.ui.show_defeat()
            return True

        # 检查敌人是否全灭
        if not any(e.is_alive() for e in self.enemies):
            self.game_over = True
            self.ui.show_victory()
            return True

        return False

    def player_turn(self):
        """玩家回合"""
        print("\n" + "=" * 40)
        print("🎯 玩家回合")
        print("=" * 40)

        self.player.start_turn()
        for enemy in self.enemies:
            if enemy.is_alive():
                enemy.choose_intent()

        while True:
            # 显示状态
            self.ui.show_status(self.player, self.enemies)
            self.ui.show_energy(self.player)
            self.ui.show_hand(self.player)

            # 获取玩家输入
            choice = self.ui.get_player_input()

            if choice == 'e':
                # 结束回合
                print("\n⏭️ 结束回合")
                self.player.end_turn()
                break

            elif choice == 'h':
                # 查看帮助
                self.ui.show_help()
                continue

            elif choice.isdigit():
                # 打出手牌
                card_index = int(choice) - 1
                if 0 <= card_index < len(self.player.hand):
                    card = self.player.hand[card_index]

                    # 选择目标
                    target = self.ui.select_target(self.enemies)
                    if target:
                        success = self.player.play_card(card, target)
                        if not success:
                            # 如果出牌失败（能量不足等），把牌放回手牌
                            if card not in self.player.hand:
                                self.player.hand.append(card)
                    else:
                        print("❌ 取消出牌")
                else:
                    print("❌ 无效的卡牌编号")
            else:
                print("❌ 无效输入，请输入数字或 'e' 结束回合")

    def enemy_turn(self):
        """敌人回合"""
        print(f"\n{'=' * 40}")
        print("🤖 敌人回合")
        print('=' * 40)

        # 每个敌人依次行动
        for enemy in self.enemies:
            if enemy.is_alive():
                print(f"\n--- {enemy.name} 的行动 ---")
                enemy.take_turn(self.player)

                # 检查玩家是否死亡
                if not self.player.is_alive():
                    print(f"\n💀 {self.player.name} 被击败了！")
                    return

        # 所有敌人都行动完后，显示状态
        print("\n📊 回合结束状态:")
        self.ui.show_status(self.player, self.enemies)

        # 结算每个敌人的回合结束效果
        for enemy in self.enemies:
            if enemy.is_alive():
                enemy.end_turn()
