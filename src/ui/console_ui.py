from typing import List
from src.core.player import Player
from src.core.enemy import Enemy


class ConsoleUI:
    """命令行用户界面"""

    def show_battle_start(self, player: Player, enemies: List[Enemy]):
        """显示战斗开始"""
        print("\n" + "=" * 60)
        print("⚔️  战斗开始！")
        print("=" * 60)
        print(f"\n📊 战斗双方:")
        print(f"  {player}")
        for enemy in enemies:
            print(f"  {enemy}")
        print("\n💡 提示: 输入数字打出手牌，输入 'e' 结束回合")

    def show_status(self, player: Player, enemies: List[Enemy]):
        """显示状态"""
        print("\n" + "-" * 60)
        print(f"📊 当前状态:")
        print(f"  {player}")
        # 只显示活着的敌人
        alive_enemies = [e for e in enemies if e.is_alive()]
        if alive_enemies:
            for enemy in alive_enemies:
                print(f"  {enemy}")
        else:
            print("  ❌ 所有敌人都被击败了！")
        print("-" * 60)

    def show_energy(self, player: Player):
        """显示能量"""
        energy_bar = "⚡" * player.energy + "·" * (player.max_energy - player.energy)
        print(f"⚡ 能量: {energy_bar} ({player.energy}/{player.max_energy})")
        if player.strength > 0:
            print(f"💪 力量加成: {player.strength}")

    def show_hand(self, player: Player):
        """显示手牌"""
        print(f"\n🎴 手牌 ({len(player.hand)}张):")
        if not player.hand:
            print("  手牌为空")
        else:
            for i, card in enumerate(player.hand, 1):
                # 判断能量是否足够
                can_play = "✅" if player.energy >= card.cost else "❌"
                energy_str = "⚡" * card.cost if card.cost > 0 else "🆓"
                upgraded_str = " ✨" if card.upgraded else ""
                print(f"  {i}. {can_play} [{energy_str}] {card.name} ({card.cost}费){upgraded_str}")
                print(f"     {card.description}")

    def show_help(self):
        """显示帮助"""
        print("\n📖 帮助:")
        print("  输入数字(1-9) - 打出对应编号的卡牌")
        print("  输入 'e' - 结束回合")
        print("  输入 'h' - 查看帮助")
        print("\n💡 提示:")
        print("  - 每回合有3点能量")
        print("  - 使用卡牌会消耗能量")
        print("  - 格挡会在回合结束时消失")
        print("  - 中毒和烧伤会在回合结束时造成伤害")

    def get_player_input(self) -> str:
        """获取玩家输入"""
        return input("\n👉 选择操作: ").strip().lower()

    def select_target(self, enemies: List[Enemy]):
        """选择目标"""
        alive_enemies = [e for e in enemies if e.is_alive()]
        if not alive_enemies:
            print("❌ 没有存活的目标")
            return None

        if len(alive_enemies) == 1:
            print(f"🎯 自动选择目标: {alive_enemies[0].name}")
            return alive_enemies[0]

        print("\n🎯 选择目标:")
        for i, enemy in enumerate(alive_enemies, 1):
            print(f"  {i}. {enemy}")

        while True:
            choice = input("👉 选择目标编号: ").strip()
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(alive_enemies):
                    return alive_enemies[idx]
            print("❌ 无效选择，请重新输入")

    def show_victory(self):
        """显示胜利"""
        print("\n" + "🎉" * 30)
        print("🎉  胜利！所有敌人都被击败了！")
        print("🎉" * 30)

    def show_defeat(self):
        """显示失败"""
        print("\n" + "💀" * 30)
        print("💀  你被击败了...")
        print("💀" * 30)

    def show_battle_result(self, player: Player):
        """显示战斗结果"""
        print("\n" + "=" * 60)
        if player.is_alive():
            print(f"🏆 战斗胜利！")
            print(f"❤️ 剩余HP: {player.hp}/{player.max_hp}")
            print(f"💪 当前力量: {player.strength}")
        else:
            print(f"💀 战斗失败...")
            print(f"❤️ HP: {player.hp}/{player.max_hp}")
        print("=" * 60)