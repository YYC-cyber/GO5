import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.player import Player
from src.core.enemy import Enemy
from src.games.web_battle import WebBattle


def test_battle():
    """测试战斗系统"""
    print("🧪 测试战斗系统...")

    player = Player("测试者")
    enemy = Enemy("测试怪物", 20, 5)

    battle = WebBattle(player, [enemy])
    battle.start()
    state = battle.get_state()

    assert state["turn"] == 1
    assert state["player"]["hp"] == 80
    assert len(state["hand"]) > 0
    assert state["enemies"][0]["intent"] in {"攻击", "防御", "强化"}
    assert "intent_value" in state["enemies"][0]

    print("✅ 测试完成")


if __name__ == "__main__":
    test_battle()
