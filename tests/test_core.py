"""
核心模块测试套件
覆盖：Player, Enemy, Card, Config, State, Collection, WebBattle, LevelManager
"""
import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.player import Player, CHARACTER_TEMPLATES
from src.core.enemy import Enemy
from src.core.card import Card, CardType, Strike, Defend
from src.config import (
    DEFAULT_ENERGY, DEFAULT_HP, AI_LOW_HP_THRESHOLD,
    WEAK_DAMAGE_MULTIPLIER, VULNERABLE_DAMAGE_MULTIPLIER,
    LEVEL_TOTAL, INTENT_DEFEND_BLOCK, INTENT_STRENGTHEN_AMOUNT,
)
from src import state as game_state
from src.games.web_battle import WebBattle
from src.games.level_mode import LevelManager, EndlessManager


# ═══════════════════════════════════════════════════════════
# 测试工具
# ═══════════════════════════════════════════════════════════

_passed = 0
_failed = 0
_errors = []


def check(condition, msg=""):
    global _passed, _failed, _errors
    if condition:
        _passed += 1
    else:
        _failed += 1
        _errors.append(msg)
        print(f"  ❌ FAIL: {msg}")


def summary():
    print(f"\n{'='*50}")
    print(f"  测试结果: {_passed} 通过, {_failed} 失败")
    if _errors:
        print(f"  失败列表:")
        for e in _errors:
            print(f"    - {e}")
    print(f"{'='*50}")
    return _failed == 0


def reset_state():
    """重置全局状态"""
    game_state.game_mode = None
    game_state.current_battle = None
    game_state.current_level = None


# ═══════════════════════════════════════════════════════════
# Config 测试
# ═══════════════════════════════════════════════════════════

def test_config():
    print("\n📋 Config 配置测试")

    check(DEFAULT_ENERGY == 3, "默认能量应为 3")
    check(DEFAULT_HP == 80, "默认 HP 应为 80")
    check(0 < AI_LOW_HP_THRESHOLD < 1, "AI 低血阈值应在 0-1 之间")
    check(WEAK_DAMAGE_MULTIPLIER == 0.75, "虚弱伤害倍率应为 0.75")
    check(VULNERABLE_DAMAGE_MULTIPLIER == 1.5, "易伤伤害倍率应为 1.5")
    check(LEVEL_TOTAL == 30, "关卡总数应为 30")
    check(INTENT_DEFEND_BLOCK == 8, "意图防御格挡应为 8")
    check(INTENT_STRENGTHEN_AMOUNT == 2, "意图强化量应为 2")

    # 验证角色模板
    from src.config import CHARACTER_DEFAULT_HP
    check(isinstance(CHARACTER_DEFAULT_HP, dict), "角色 HP 配置应为字典")
    check(len(CHARACTER_DEFAULT_HP) >= 9, f"应有至少 9 个角色，实际 {len(CHARACTER_DEFAULT_HP)}")

    # 验证无尽模式配置
    from src.config import ENDLESS_INITIAL_FLOORS, ENDLESS_EXTEND_THRESHOLD
    check(ENDLESS_INITIAL_FLOORS == 10, "无尽模式初始楼层应为 10")
    check(ENDLESS_EXTEND_THRESHOLD == 5, "无尽模式扩展阈值应为 5")


# ═══════════════════════════════════════════════════════════
# Player 测试
# ═══════════════════════════════════════════════════════════

def test_player():
    print("\n👤 Player 测试")

    # 基础创建
    p = Player("测试勇者", 80)
    check(p.name == "测试勇者", "玩家名称")
    check(p.hp == 80, "玩家 HP")
    check(p.max_hp == 80, "玩家最大 HP")
    check(p.energy == DEFAULT_ENERGY, "玩家初始能量")
    check(p.block == 0, "初始格挡为 0")
    check(p.strength == 0, "初始力量为 0")
    check(p.is_alive(), "玩家应存活")

    # 伤害
    p.take_damage(10)
    check(p.hp == 70, "受到 10 点伤害后 HP 应为 70")

    # 格挡
    p.block = 15
    p.take_damage(10)
    check(p.block == 5, "格挡抵消 10 伤害后剩余 5")
    check(p.hp == 70, "格挡后 HP 不变")

    # 治疗
    p.heal(10)
    check(p.hp == 80, "治疗后 HP 恢复到 80")

    # 超量治疗
    p.heal(50)
    check(p.hp == 80, "治疗不应超过最大 HP")

    # 死亡
    p.take_damage(200)
    check(not p.is_alive(), "玩家应死亡")
    check(p.hp <= 0, "死亡后 HP <= 0")

    # 角色模板
    p2 = Player("圣骑士", 90, character_id="paladin")
    check(p2.name == "圣骑士", "圣骑士名称")
    check(p2.max_hp == 90, "圣骑士 HP")

    # 状态效果
    p3 = Player("测试", 80)
    p3.apply_poison(3)
    check(p3.poison == 3, "中毒应为 3")
    p3.apply_burn(2)
    check(p3.burn == 2, "烧伤应为 2")


# ═══════════════════════════════════════════════════════════
# Enemy 测试
# ═══════════════════════════════════════════════════════════

def test_enemy():
    print("\n👾 Enemy 测试")

    # 基础创建
    e = Enemy("哥布林", 30, 6)
    check(e.name == "哥布林", "敌人名称")
    check(e.hp == 30, "敌人 HP")
    check(e.max_hp == 30, "敌人最大 HP")
    check(e.base_damage == 6, "敌人基础伤害")
    check(e.is_alive(), "敌人应存活")

    # 意图选择
    e.choose_intent()
    check(e.intent is not None, "意图应不为空")
    check(e.intent in ("攻击", "防御", "强化"), f"意图应在允许列表中，实际: {e.intent}")

    # 伤害
    actual = e.take_damage(10)
    check(e.hp == 20, "受到 10 伤害后 HP 应为 20")
    check(actual == 10, "实际伤害应为 10")

    # 状态效果
    e.apply_poison(3)
    check(e.poison == 3, "中毒应为 3")
    e.apply_burn(2)
    check(e.burn == 2, "烧伤应为 2")
    e.apply_weak(1)
    check(e.weak == 1, "虚弱应为 1")

    # 死亡
    e.take_damage(100)
    check(not e.is_alive(), "敌人应死亡")


# ═══════════════════════════════════════════════════════════
# Card 测试
# ═══════════════════════════════════════════════════════════

def test_card():
    print("\n🃏 Card 测试")

    c = Strike()
    check(c.name == "猛击", "卡牌名称")
    check(c.type == CardType.ATTACK, "卡牌类型")
    check(c.cost == 1, "卡牌费用")
    check(c.damage == 6, "卡牌伤害")
    check(not c.upgraded, "初始未升级")

    c.upgrade()
    check(c.upgraded, "升级后应标记为已升级")
    check(c.damage == 9, "升级后伤害应为 9")

    c2 = Defend()
    check(c2.block == 5, "防御牌格挡")
    check(c2.type == CardType.SKILL, "技能牌类型")


# ═══════════════════════════════════════════════════════════
# State 测试
# ═══════════════════════════════════════════════════════════

def test_state():
    print("\n📊 State 测试")

    reset_state()
    check(not game_state.has_state(), "初始状态应为空")
    check(game_state.get_state() is None, "get_state 应返回 None")

    # 创建战斗
    p = Player("测试", 80)
    e = Enemy("测试怪物", 20, 5)
    battle = WebBattle(p, [e])
    battle.start()

    game_state.current_battle = battle
    game_state.game_mode = "single"

    check(game_state.has_state(), "has_state 应为 True")
    s = game_state.get_state()
    check(s is not None, "get_state 应返回非空")
    check(s["turn"] == 1, "回合应为 1")
    check(s["player"]["hp"] == 80, "玩家 HP 应为 80")

    # 缓存测试
    s2 = game_state.get_state()
    check(s is s2, "缓存应返回相同对象")

    # 重置
    reset_state()
    check(not game_state.has_state(), "重置后应为空")
    check(game_state.get_state() is None, "重置后 get_state 应返回 None")


# ═══════════════════════════════════════════════════════════
# WebBattle 测试
# ═══════════════════════════════════════════════════════════

def test_web_battle():
    print("\n⚔️ WebBattle 测试")

    reset_state()
    p = Player("测试勇者", 80)
    e = Enemy("哥布林", 30, 6)
    battle = WebBattle(p, [e])
    battle.start()

    state = battle.get_state()
    check(state["turn"] == 1, "回合应为 1")
    check(len(state["hand"]) > 0, "应抽到至少 1 张牌")
    check(len(state["enemies"]) == 1, "应有 1 个敌人")
    check(state["enemies"][0]["alive"], "敌人应存活")
    check(state["enemies"][0]["intent"] is not None, "敌人应有意图")

    # 出牌测试
    hand = state["hand"]
    playable = [i for i, c in enumerate(hand) if c["playable"]]
    if playable:
        result = battle.play_card(playable[0], 0)
        check(result["success"], f"出牌应成功: {result.get('error', '')}")

    # 结束回合
    result = battle.end_turn()
    check(result["success"], "结束回合应成功")

    # 脏标记缓存测试
    state2 = battle.get_state()
    check(state is not state2, "脏标记后应重新构建状态")

    # 技能测试
    result = battle.use_skill()
    check(isinstance(result, dict), "技能结果应为字典")

    # 游戏结束后的状态
    # 强制杀死敌人
    e.hp = 0
    battle._check_battle_end()
    check(battle.game_over, "战斗应结束")
    check(battle.winner == "player", "玩家应获胜")


# ═══════════════════════════════════════════════════════════
# LevelManager 测试
# ═══════════════════════════════════════════════════════════

def test_level_manager():
    print("\n🗺️ LevelManager 测试")

    reset_state()
    lm = LevelManager(difficulty="easy", character_id="warrior")
    check(lm.difficulty == "easy", "难度应为 easy")
    check(lm.current_stage == 0, "初始关卡为 0")
    check(lm.total_stages == 30, "总关卡为 30")
    check(lm.status == "idle", "初始状态为 idle")

    # 开始
    lm.start()
    check(lm.status in ("playing", "path_select"), f"开始后状态应为 playing/path_select，实际: {lm.status}")

    state = lm.get_state()
    check(state["mode"] == "level", "状态模式应为 level")
    check("enemies" in state or "current_node" in state, "状态应包含 enemies 或 current_node")

    # 缓存测试
    state2 = lm.get_state()
    check(state is state2, "缓存应返回相同对象")

    # 有 battle 时的出牌
    if lm.battle and lm.status == "playing":
        hs = lm.battle.get_state()
        playable = [i for i, c in enumerate(hs["hand"]) if c["playable"]]
        if playable:
            result = lm.play_card(playable[0], 0)
            check(isinstance(result, dict), "出牌结果应为字典")

    # 脏标记
    state3 = lm.get_state()
    if lm.battle and lm.status == "playing":
        check(state is not state3 or not lm.battle.game_over, "状态变更后缓存应更新")


# ═══════════════════════════════════════════════════════════
# EndlessManager 测试
# ═══════════════════════════════════════════════════════════

def test_endless_manager():
    print("\n♾️ EndlessManager 测试")

    reset_state()
    em = EndlessManager(difficulty="easy", character_id="warrior")
    check(em.difficulty == "easy", "难度应为 easy")
    check(em.current_floor == 0, "初始楼层为 0")
    check(em.status == "idle", "初始状态为 idle")

    # 开始
    em.start()
    check(em.total_stages >= 10, f"总楼层应 >= 10，实际: {em.total_stages}")
    check(em.status in ("playing", "path_select"), f"开始后状态应为 playing/path_select，实际: {em.status}")

    state = em.get_state()
    check(state["mode"] == "endless", "状态模式应为 endless")

    # 缓存测试
    state2 = em.get_state()
    check(state is state2, "缓存应返回相同对象")


# ═══════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    test_config()
    test_player()
    test_enemy()
    test_card()
    test_state()
    test_web_battle()
    test_level_manager()
    test_endless_manager()

    ok = summary()
    sys.exit(0 if ok else 1)