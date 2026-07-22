"""
关卡模式 - 30层分支路线系统 (带金币/商店/Boss前营火)

玩家在30个关卡中连续战斗，生命值/状态在关卡之间继承。
每通关一个关卡可选择一项奖励，逐渐应对越来越强的敌人。
新增金币系统，商店节点使用金币交易。
"""

import random
import math
from typing import List, Optional, Dict, Any
from src.core.player import Player
from src.core.enemy import Enemy
from src.games.web_battle import WebBattle


# ── 30关名称池 ──────────────────────────────────────────
STAGE_NAMES = [
    "哥布林哨站", "毒沼浅滩", "前哨突袭", "护卫巡逻", "熔岩犬巢",
    "冰霜峡谷", "熔岩堡垒", "镜像回廊", "暗影之门", "暗影王座",
    "恶魔前哨", "毒沼深渊", "突击部队", "哥布林军团", "烈焰焚路",
    "冰封峡谷", "炼狱熔炉", "镜像风暴", "深渊之门", "暗影降临",
    "混沌裂隙", "腐蚀沼泽", "铁壁堡垒", "虚空回廊", "末日审判",
    "永恒冰窟", "地狱熔炉", "星辰之门", "终焉之径", "黑暗王座",
]

# 敌人池 (按难度递增)
ENEMY_POOL = [
    # 第1-5关 低阶
    [("哥布林", 32, 6), ("史莱姆", 40, 5)],
    [("毒沼史莱姆", 42, 7), ("哥布林", 35, 7)],
    [("哥布林", 36, 8), ("史莱姆", 45, 7)],
    [("护卫队长", 50, 8), ("哥布林", 36, 8)],
    [("熔岩犬", 55, 10), ("史莱姆", 42, 6)],
    # 第6-10关 中阶
    [("寒冰法师", 50, 9), ("哥布林", 38, 8)],
    [("火焰领主", 60, 11), ("史莱姆", 50, 8)],
    [("镜像怪", 65, 10), ("寒冰法师", 48, 9)],
    [("诅咒法师", 65, 11), ("毒沼史莱姆", 55, 9)],
    [("暗影领主", 110, 15), ("诅咒法师", 60, 10)],
    # 第11-15关 中高阶
    [("恶魔猎手", 70, 12), ("熔岩犬", 58, 10)],
    [("毒沼领主", 80, 11), ("史莱姆", 60, 9), ("哥布林", 45, 9)],
    [("突击队长", 75, 13), ("护卫队长", 60, 10), ("哥布林", 48, 9)],
    [("哥布林王", 85, 12), ("哥布林", 50, 10), ("哥布林", 50, 10)],
    [("烈焰守卫", 90, 14), ("熔岩犬", 65, 11)],
    # 第16-20关 高阶
    [("冰霜女巫", 85, 13), ("寒冰法师", 60, 10), ("哥布林", 50, 10)],
    [("炼狱守卫", 95, 15), ("火焰领主", 70, 12)],
    [("幻影魔", 100, 14), ("镜像怪", 70, 11), ("寒冰法师", 55, 10)],
    [("深渊术士", 100, 15), ("诅咒法师", 75, 12), ("毒沼史莱姆", 65, 11)],
    [("暗影大君", 150, 20), ("镜像怪", 80, 13), ("诅咒法师", 70, 12)],
    # 第21-25关 精英
    [("混沌兽", 110, 16), ("恶魔猎手", 80, 13)],
    [("腐蚀领主", 120, 16), ("毒沼领主", 85, 12), ("史莱姆", 70, 10)],
    [("铁壁将军", 130, 18), ("护卫队长", 80, 12), ("突击队长", 75, 13)],
    [("虚空行者", 140, 17), ("幻影魔", 90, 14), ("镜像怪", 75, 12)],
    [("末日军官", 150, 19), ("深渊术士", 90, 15), ("烈焰守卫", 85, 14)],
    # 第26-29关 boss前
    [("永恒守卫", 160, 20), ("冰霜女巫", 80, 14)],
    [("地狱领主", 170, 22), ("炼狱守卫", 95, 16), ("火焰领主", 80, 14)],
    [("星辰使徒", 180, 22), ("虚空行者", 100, 16), ("混沌兽", 95, 15)],
    [("终焉骑士", 200, 24), ("铁壁将军", 100, 16), ("深渊术士", 90, 15)],
    # 第30关 Boss
    [("暗影之神", 280, 30), ("终焉骑士", 120, 18), ("虚空行者", 100, 16)],
]

# 难度修正
DIFFICULTY_MULT = {
    "easy": {"hp": 0.9, "dmg": 0.9, "gold_min": 5, "gold_max": 10},
    "hard": {"hp": 1.1, "dmg": 1.1, "gold_min": 8, "gold_max": 14},
    "hell": {"hp": 1.3, "dmg": 1.25, "gold_min": 12, "gold_max": 18},
}

# ── 章节名称 ──
STAGE_CHAPTERS = [
    "第一章: 边境",
    "第二章: 深入",
    "第三章: 熔炉",
    "第四章: 深渊",
    "第五章: 终焉",
    "第六章: 混沌",
    "第七章: 虚空",
    "第八章: 决战",
]

ROUTE_TYPES = {
    "normal": {
        "route": "普通战", "desc": "标准战斗节点，敌人强度适中",
        "icon": "⚔️", "risk": 2, "reward_hint": "普通升级、基础成长",
    },
    "elite": {
        "route": "精英", "desc": "敌人更强、机制更复杂，适合牌组强势时挑战",
        "icon": "💀", "risk": 3, "reward_hint": "遗物、高概率升级、稀有强化",
    },
    "event": {
        "route": "事件", "desc": "结果不确定，没有战斗，可能获得帮助或付出代价",
        "icon": "❔", "risk": 1, "reward_hint": "随机回血、失血换奖励、诅咒",
    },
    "campfire": {
        "route": "营火", "desc": "休整节点，恢复净化，无战斗",
        "icon": "🔥", "risk": 0, "reward_hint": "恢复、净化、删牌",
    },
    "shop": {
        "route": "商店", "desc": "使用金币购买强化，无战斗",
        "icon": "🛒", "risk": 0, "reward_hint": "金币交易、购牌、回血",
    },
    "boss": {
        "route": "Boss", "desc": "所有路线最终汇合于此",
        "icon": "👑", "risk": 4, "reward_hint": "通关胜利",
    },
}

RELIC_POOL = [
    {"id": "bronze_charm", "name": "铜质护符", "icon": "🧿", "desc": "每场战斗开始获得5点格挡"},
    {"id": "war_drum", "name": "战鼓", "icon": "🥁", "desc": "每场战斗开始获得1点力量"},
    {"id": "toxic_needle", "name": "毒针戒指", "icon": "☠️", "desc": "每场战斗开始对所有敌人施加1层中毒"},
    {"id": "ember_core", "name": "余烬核心", "icon": "🔥", "desc": "每场战斗开始对所有敌人施加1层烧伤"},
    {"id": "bone_totem", "name": "白骨图腾", "icon": "💀", "desc": "每场战斗开始召唤1个骷髅"},
    {"id": "clockwork_cell", "name": "发条电池", "icon": "🔋", "desc": "每场战斗开始额外获得1点能量"},
    {"id": "thorn_badge", "name": "荆棘徽章", "icon": "🌿", "desc": "每场战斗开始获得1点反伤"},
    {"id": "healing_leaf", "name": "治愈叶", "icon": "🍃", "desc": "每场战斗开始回复3点生命"},
    {"id": "mirror_shard", "name": "镜面碎片", "icon": "🪞", "desc": "每场战斗开始获得回响，下一张牌释放两次"},
    {"id": "shield_rune", "name": "护盾符文", "icon": "🛡️", "desc": "每场战斗开始获得2点祝福"},
]

SHOP_ITEMS = [
    {"id": "hp_restore", "name": "生命恢复", "icon": "💚", "desc": "回复 25 点生命", "cost": 15},
    {"id": "hp_full", "name": "完全恢复", "icon": "❤️", "desc": "生命回满", "cost": 30},
    {"id": "strength_pot", "name": "力量药水", "icon": "💪", "desc": "下一轮攻击 +3", "cost": 12},
    {"id": "block_pot", "name": "护盾药水", "icon": "🛡️", "desc": "下一轮防御 +8", "cost": 10},
    {"id": "remove_card", "name": "删牌", "icon": "🗑️", "desc": "删除一张牌", "cost": 20},
    {"id": "upgrade_card", "name": "升级卡牌", "icon": "✨", "desc": "升级一张牌（随机）", "cost": 18},
    {"id": "max_hp", "name": "体魄强化", "icon": "❤️", "desc": "最大生命 +10", "cost": 22},
    {"id": "max_energy", "name": "能量核心", "icon": "🔋", "desc": "最大能量 +1", "cost": 35},
    {"id": "relic", "name": "随机遗物", "icon": "🧿", "desc": "获取一个随机遗物", "cost": 40},
]


def _scale_enemy(enemy, hp_mult: float = 1.0, dmg_mult: float = 1.0, hp_bonus: int = 0, dmg_bonus: int = 0):
    name, hp, dmg = enemy
    scaled_hp = max(1, int(hp * hp_mult) + hp_bonus)
    scaled_dmg = max(1, int(dmg * dmg_mult) + dmg_bonus)
    return (name, scaled_hp, scaled_dmg)


def _get_stage_pool(difficulty: str) -> List[Dict[str, Any]]:
    """根据难度生成30个关卡"""
    mult = DIFFICULTY_MULT.get(difficulty, DIFFICULTY_MULT["easy"])
    stages = []
    for i in range(30):
        name = STAGE_NAMES[i] if i < len(STAGE_NAMES) else f"第{i+1}层"
        base_enemies = ENEMY_POOL[i] if i < len(ENEMY_POOL) else ENEMY_POOL[-1]

        # 难度随层数递增
        layer_factor = 1.0 + i * 0.03
        enemies = [
            _scale_enemy(e, hp_mult=mult["hp"] * layer_factor, dmg_mult=mult["dmg"] * layer_factor)
            for e in base_enemies
        ]
        stages.append({"name": name, "enemies": enemies})
    return stages


def _route_enemies(base_enemies, layer: int, route_type: str):
    """根据路线类型调整敌人"""
    if route_type in ("campfire", "shop", "event"):
        return []  # 非战斗节点无敌人
    if route_type == "elite":
        enemies = [_scale_enemy(e, hp_bonus=8 + layer, dmg_bonus=1 + layer // 5) for e in base_enemies]
        if len(enemies) == 1 and layer >= 3:
            enemies.append(("精英护卫", 60 + layer * 3, 8 + layer // 4))
        return enemies
    return base_enemies


def _build_branch_graph(difficulty: str) -> Dict[str, Any]:
    """构建30层分支图。每层2-3节点。Boss前必为营火，商店随机插入中段。"""
    stages = _get_stage_pool(difficulty)
    total = 30
    nodes: Dict[str, Dict[str, Any]] = {}
    layers: List[List[str]] = []
    node_counter = [0]

    def _node_id(layer: int, idx: int) -> str:
        return f"{layer}{chr(97 + idx)}"

    def _add_node(layer: int, idx: int, route_type: str, base_name: str, enemies, next_ids: List[str]):
        nid = _node_id(layer, idx)
        meta = ROUTE_TYPES.get(route_type, ROUTE_TYPES["normal"])
        suffix = "" if route_type == "normal" else f"·{meta['route']}"
        nodes[nid] = {
            "id": nid,
            "layer": layer,
            "name": f"{base_name}{suffix}",
            "route_type": route_type,
            **meta,
            "enemies": enemies,
            "next": next_ids,
        }
        return nid

    # ── 层0: 起点 ──
    nid = _add_node(0, 0, "normal", stages[0]["name"], stages[0]["enemies"],
                     [_node_id(1, 0), _node_id(1, 1)])
    nodes[nid]["route_type"] = "start"
    nodes[nid]["route"] = "起点"
    nodes[nid]["desc"] = "冒险起点"
    nodes[nid]["icon"] = "🚩"
    nodes[nid]["risk"] = 1
    nodes[nid]["reward_hint"] = "基础奖励"
    layers.append([nid])

    # ── 层1-27: 中段 — 每层2-3个节点 ──
    # 确定商店位置（随机插入层5-20之间，共4-6个商店）
    shop_layers = set(random.sample(range(5, min(22, total - 3)), min(5, 22 - 5)))

    for layer in range(1, total - 2):
        base = stages[layer]
        nids = []
        num_nodes = 3 if layer % 3 == 0 else 2  # 每3层有一个3叉分支

        # 确定本层节点类型
        types = ["normal", "normal"]
        if layer in shop_layers:
            types = ["shop", "normal"]
        elif layer >= 3 and layer % 3 == 0:
            types = ["normal", "elite"]
        elif layer >= 5 and layer % 4 == 0:
            types = ["event", "elite"]
        elif layer >= 2 and layer % 5 == 0:
            types = ["campfire", "normal"]
        else:
            types = ["normal", "event"]

        if num_nodes == 3:
            if layer % 3 == 0:
                types = ["normal", "elite", "event"]

        # 确保每种类型有正确的敌人
        actual_enemies_list = []
        for rt in types:
            actual_enemies_list.append(_route_enemies(base["enemies"], layer, rt))

        # 下一层节点ID
        next_ids = [_node_id(layer + 1, i) for i in range(3 if (layer + 1) % 3 == 0 else 2)]

        for i, rt in enumerate(types):
            al = layer if layer >= 1 else 0
            nid = _add_node(layer, i, rt, base["name"], actual_enemies_list[i],
                             next_ids if i < len(next_ids) else [])
            nids.append(nid)
        layers.append(nids)

    # ── 层28: 营火（Boss前）──
    camp_layer = total - 2
    base_camp = stages[camp_layer]
    boss_next = [_node_id(total - 1, 0)]
    nid = _add_node(camp_layer, 0, "campfire", base_camp["name"], [], boss_next)
    layers.append([nid])

    # ── 层29: Boss ──
    boss_layer = total - 1
    base_boss = stages[boss_layer]
    nid = _add_node(boss_layer, 0, "boss", base_boss["name"], base_boss["enemies"], [])
    nodes[nid]["route_type"] = "boss"
    nodes[nid].update(ROUTE_TYPES["boss"])
    layers.append([nid])

    # 修正next引用：确保每个节点都指向正确的下一层节点
    final_nodes = {}
    for nid, node in nodes.items():
        fn = {**node}
        if fn["next"]:
            valid = [n for n in fn["next"] if n in nodes]
            fn["next"] = valid
        final_nodes[nid] = fn

    return {"nodes": final_nodes, "layers": layers, "start": "0a"}


class LevelManager:
    """关卡模式管理器 (30关分支 + 金币/商店)"""

    def __init__(self, difficulty: str = "easy", character_id: str = "warrior"):
        self.difficulty = difficulty
        self.branch_graph = _build_branch_graph(difficulty)
        self.current_node_id = self.branch_graph["start"]
        self.current_stage = 0
        self.total_stages = 30
        from src.core.player import CHARACTER_TEMPLATES
        tmpl = CHARACTER_TEMPLATES.get(character_id, CHARACTER_TEMPLATES["warrior"])
        self.player = Player(tmpl["name"], tmpl["hp"], character_id=character_id)
        self.character_id = character_id
        self.battle: Optional[WebBattle] = None
        self.status = "idle"
        self.messages: List[str] = []
        self.rewards_taken: List[str] = []
        self.current_rewards: List[Dict[str, str]] = []
        self.relics: List[Dict[str, str]] = []
        self.branch_choices: List[Dict[str, Any]] = []
        self.path_taken: List[str] = []
        self._reward_claimed_for_stage = False
        self._heal_full_used = False
        self._base_strength = 0
        self._next_battle_strength_bonus = 0
        self._next_battle_block_bonus = 0
        self.gold = 0
        self.shop_items: List[Dict[str, Any]] = []
        self._shop_open = False
        self._event_data: Optional[Dict[str, str]] = None

    # ── 公共API ──

    def start(self):
        """开始关卡模式"""
        self.messages.append("🗺️ 关卡模式开始！30层分支远征")
        self.messages.append(f"📋 难度: {self.difficulty}")
        self.current_node_id = self.branch_graph["start"]
        self.current_stage = 0
        self.path_taken = []
        self.branch_choices = []
        self._reward_claimed_for_stage = False
        self._heal_full_used = False
        self._base_strength = 0
        self._next_battle_strength_bonus = 0
        self._next_battle_block_bonus = 0
        self.gold = 0
        self.shop_items = []
        self._shop_open = False
        self._event_data = None
        self._enter_stage()

    def get_state(self) -> Dict[str, Any]:
        """获取完整状态"""
        battle_state = self.battle.get_state() if self.battle else {}
        current_stage_data = self._current_stage_data()

        chapter_idx = min(self.current_stage // 3, len(STAGE_CHAPTERS) - 1)
        chapter_name = STAGE_CHAPTERS[chapter_idx]

        merged_messages = self.messages + battle_state.get("messages", [])

        node_type = current_stage_data.get("route_type", "normal")
        is_non_combat = node_type in ("campfire", "shop", "event")
        is_shop_open = self._shop_open

        result = {
            "mode": "level",
            "difficulty": self.difficulty,
            "current_stage": self.current_stage,
            "total_stages": self.total_stages,
            "stage_name": current_stage_data["name"],
            "current_node": self._node_to_choice(current_stage_data),
            "path_taken": self.path_taken[:],
            "branch_layers": self._branch_layers_state(),
            "branch_choices": self.branch_choices if self.status == "path_select" else [],
            "relics": self.relics,
            "gold": self.gold,
            "chapter": chapter_name,
            "status": self.status,
            "rewards": self.current_rewards if self.status == "stage_clear" else [],
            "messages": merged_messages[-50:],
            "battle": battle_state,
            "is_non_combat": is_non_combat,
            "shop_open": is_shop_open,
            "shop_items": self.shop_items if is_shop_open else [],
            "event_data": self._event_data,
        }

        # ── 平铺 battle 数据 ──
        if battle_state and not is_non_combat:
            result["enemies"] = battle_state.get("enemies", [])
            result["hand"] = battle_state.get("hand", [])
            result["deck_count"] = battle_state.get("deck_count", 0)
            result["discard_count"] = battle_state.get("discard_count", 0)
            result["deck_cards"] = battle_state.get("deck_cards", [])
            result["discard_cards"] = battle_state.get("discard_cards", [])
            bp = battle_state.get("player", {})
            result["player"] = {
                "name": self.player.name,
                "hp": self.player.hp,
                "max_hp": self.player.max_hp,
                "strength": self.player.strength,
                "block": bp.get("block", self.player.block),
                "poison": bp.get("poison", self.player.poison),
                "burn": bp.get("burn", self.player.burn),
                "bleed": bp.get("bleed", self.player.bleed),
                "weak": bp.get("weak", self.player.weak),
                "vulnerable": bp.get("vulnerable", self.player.vulnerable),
                "curse": bp.get("curse", self.player.curse),
                "image": bp.get("image", "勇者.svg"),
                "energy": bp.get("energy", self.player.energy if self.battle else 3),
                "max_energy": bp.get("max_energy", self.player.max_energy),
                "iron_wall": bp.get("iron_wall", self.player.iron_wall),
                "counter": bp.get("counter", self.player.counter),
                "thorns": bp.get("thorns", self.player.thorns),
                "blessing": bp.get("blessing", self.player.blessing),
                "turret_damage": bp.get("turret_damage", getattr(self.player, "turret_damage", 0)),
                "skeletons": bp.get("skeletons", getattr(self.player, "skeletons", 0)),
                "skill_used_this_turn": bp.get("skill_used_this_turn", getattr(self.player, "skill_used_this_turn", False)),
                "double_next_card": bp.get("double_next_card", getattr(self.player, "double_next_card", False)),
                "block_persist": bp.get("block_persist", False),
                "auto_shield": bp.get("auto_shield", False),
                "skill": bp.get("skill"),
                "gold": self.gold,
            }
        else:
            result["enemies"] = []
            result["hand"] = []
            result["deck_cards"] = []
            result["discard_cards"] = []
            result["player"] = {
                "name": self.player.name,
                "hp": self.player.hp,
                "max_hp": self.player.max_hp,
                "strength": self.player.strength,
                "image": "勇者.svg",
                "energy": 3,
                "max_energy": 3,
                "gold": self.gold,
            }

        return result

    def play_card(self, card_index: int, target_index: int) -> Dict[str, Any]:
        if self.status != "playing" or not self.battle:
            return {"success": False, "error": "当前无法出牌"}
        result = self.battle.play_card(card_index, target_index)
        self._check_battle_end()
        return result

    def end_turn(self) -> Dict[str, Any]:
        if self.status != "playing" or not self.battle:
            return {"success": False, "error": "当前无法结束回合"}
        result = self.battle.end_turn()
        self._check_battle_end()
        return result

    def claim_reward(self, reward_id: str) -> Dict[str, Any]:
        """领取奖励并进入路线选择"""
        if self.status != "stage_clear":
            return {"success": False, "error": "当前无法领取奖励"}

        # 应用奖励
        if reward_id == "heal":
            healed = self.player.heal(20)
            self.messages.append(f"💚 休息回复！ +{healed} HP")
        elif reward_id == "max_hp":
            self.player.max_hp += 8
            self.player.hp = min(self.player.max_hp, self.player.hp + 8)
            self.messages.append(f"❤️ 体魄增强！最大生命 +8（当前{self.player.max_hp}）")
        elif reward_id == "rare_power":
            self.player.strength += 1
            self._base_strength += 1
            self.player.max_hp += 5
            self.player.hp = min(self.player.max_hp, self.player.hp + 5)
            self.messages.append(f"🌟 稀有强化！力量 +1，最大生命 +5")
        elif reward_id == "special_training":
            self.player.max_energy += 1
            self.player.energy = self.player.max_energy
            self.messages.append(f"🔧 特殊强化！最大能量 +1（当前{self.player.max_energy}）")
        elif reward_id == "cleanse_supply":
            self.player.poison = self.player.burn = self.player.bleed = 0
            self.player.weak = self.player.vulnerable = self.player.curse = 0
            healed = self.player.heal(18)
            self.messages.append(f"⛺ 补给休整！净化负面状态并回复 {healed} 点生命")
        elif reward_id == "next_attack":
            self._next_battle_strength_bonus += 3
            self.messages.append("⚔️ 获得下一轮攻击 +3 强化")
        elif reward_id == "next_defense":
            self._next_battle_block_bonus += 8
            self.messages.append("🛡️ 获得下一轮防御 +8 强化")
        elif reward_id.startswith("relic:"):
            relic_id = reward_id.split(":", 1)[1]
            relic = next((r for r in RELIC_POOL if r["id"] == relic_id), None)
            if not relic or any(r["id"] == relic_id for r in self.relics):
                return {"success": False, "error": "无效的遗物奖励"}
            self.relics.append(relic)
            self.messages.append(f"{relic['icon']} 获得遗物：{relic['name']}（{relic['desc']}）")
        elif reward_id == "heal_full":
            healed = self.player.max_hp - self.player.hp
            self.player.hp = self.player.max_hp
            self._heal_full_used = True
            self.messages.append(f"❤️ 完全恢复！ +{healed} HP")
        elif reward_id.startswith("upgrade_card:"):
            idx = int(reward_id.split(":", 1)[1])
            cards = self._all_cards()
            if idx < 0 or idx >= len(cards) or cards[idx].upgraded:
                return {"success": False, "error": "无法升级该卡牌"}
            cards[idx].upgrade()
            self.messages.append(f"✨ 升级卡牌：{cards[idx].name}")
        elif reward_id.startswith("remove_card:"):
            idx = int(reward_id.split(":", 1)[1])
            cards = self._all_cards()
            if len(cards) <= 5:
                return {"success": False, "error": "牌组太少，无法删牌"}
            if idx < 0 or idx >= len(cards):
                return {"success": False, "error": "无法删除该卡牌"}
            removed = cards[idx]
            self._remove_card_object(removed)
            self.messages.append(f"🗑️ 删除卡牌：{removed.name}")
        else:
            return {"success": False, "error": "无效的奖励"}

        self.rewards_taken.append(reward_id)
        self.current_rewards = []
        self._reward_claimed_for_stage = True

        self.branch_choices = self._next_branch_choices()
        if not self.branch_choices:
            self.messages.append("🎉 恭喜通关全部路线！")
            self.messages.append("🏆 你成为了真正的卡牌大师！")
            self.status = "victory"
            return {"success": True, "level_complete": True, "state": self.get_state()}

        self.status = "path_select"
        self.messages.append("🧭 选择下一条路线继续前进...")
        return {"success": True, "level_complete": False, "state": self.get_state()}

    def choose_branch(self, node_id: str) -> Dict[str, Any]:
        """选择下一关分支并进入"""
        if self.status != "path_select":
            return {"success": False, "error": "当前无法选择路线"}

        allowed = {choice["id"] for choice in self.branch_choices}
        if node_id not in allowed:
            return {"success": False, "error": "无效的路线选择"}

        self.current_node_id = node_id
        self.current_stage = self.branch_graph["nodes"][node_id]["layer"]
        self.branch_choices = []
        self._reward_claimed_for_stage = False
        self._shop_open = False
        self.shop_items = []
        self._event_data = None
        self._enter_stage()
        return {"success": True, "state": self.get_state()}

    def open_shop(self) -> Dict[str, Any]:
        """打开商店（仅非战斗节点）"""
        node = self._current_stage_data()
        if node.get("route_type") != "shop":
            return {"success": False, "error": "当前不是商店节点"}
        if self._shop_open:
            return {"success": True, "state": self.get_state()}
        self._shop_open = True
        self.shop_items = self._generate_shop_items()
        self.messages.append("🛒 商店已开启，使用金币购买物品！")
        return {"success": True, "state": self.get_state()}

    def buy_item(self, item_id: str) -> Dict[str, Any]:
        """购买商店物品"""
        if not self._shop_open or not self.shop_items:
            return {"success": False, "error": "商店未开启"}
        item = next((it for it in self.shop_items if it["id"] == item_id), None)
        if not item:
            return {"success": False, "error": "无效的商品"}
        if self.gold < item["cost"]:
            return {"success": False, "error": f"金币不足，需要{item['cost']}金币"}
        self.gold -= item["cost"]

        if item_id == "hp_restore":
            healed = self.player.heal(25)
            self.messages.append(f"💚 购买生命恢复！ +{healed} HP")
        elif item_id == "hp_full":
            healed = self.player.max_hp - self.player.hp
            self.player.hp = self.player.max_hp
            self.messages.append(f"❤️ 购买完全恢复！ +{healed} HP")
        elif item_id == "strength_pot":
            self._next_battle_strength_bonus += 3
            self.messages.append("💪 购买力量药水！下一轮攻击 +3")
        elif item_id == "block_pot":
            self._next_battle_block_bonus += 8
            self.messages.append("🛡️ 购买护盾药水！下一轮防御 +8")
        elif item_id == "remove_card":
            cards = self._all_cards()
            if len(cards) <= 5:
                self.gold += item["cost"]
                return {"success": False, "error": "牌组太少，无法删牌"}
            # 随机删一张
            idx = random.randint(0, len(cards) - 1)
            self._remove_card_object(cards[idx])
            self.messages.append(f"🗑️ 删除卡牌：{cards[idx].name}")
        elif item_id == "upgrade_card":
            cards = [c for c in self._all_cards() if not getattr(c, "upgraded", False)]
            if not cards:
                self.gold += item["cost"]
                return {"success": False, "error": "没有可升级的卡牌"}
            card = random.choice(cards)
            card.upgrade()
            self.messages.append(f"✨ 升级卡牌：{card.name}")
        elif item_id == "max_hp":
            self.player.max_hp += 10
            self.player.hp = min(self.player.max_hp, self.player.hp + 10)
            self.messages.append(f"❤️ 体魄强化！最大生命 +10（当前{self.player.max_hp}）")
        elif item_id == "max_energy":
            self.player.max_energy += 1
            self.player.energy = self.player.max_energy
            self.messages.append(f"🔋 能量核心！最大能量 +1（当前{self.player.max_energy}）")
        elif item_id == "relic":
            owned = {r["id"] for r in self.relics}
            candidates = [r for r in RELIC_POOL if r["id"] not in owned]
            if not candidates:
                self.gold += item["cost"]
                return {"success": False, "error": "已拥有所有遗物"}
            relic = random.choice(candidates)
            self.relics.append(relic)
            self.messages.append(f"{relic['icon']} 购买遗物：{relic['name']}（{relic['desc']}）")

        self.shop_items = [it for it in self.shop_items if it["id"] != item_id]
        self.messages.append(f"💰 剩余 {self.gold} 金币")
        return {"success": True, "state": self.get_state()}

    def leave_shop(self) -> Dict[str, Any]:
        """离开商店，进入路线选择"""
        if not self._shop_open:
            return {"success": False, "error": "商店未开启"}
        self._shop_open = False
        self.shop_items = []
        self._after_non_combat()
        return {"success": True, "state": self.get_state()}

    # ── 内部 ──

    def _enter_stage(self):
        """进入当前关卡"""
        stage = self._current_stage_data()
        route_type = stage.get("route_type", "normal")
        if self.current_node_id not in self.path_taken:
            self.path_taken.append(self.current_node_id)

        if route_type in ("campfire", "shop", "event"):
            # 非战斗节点
            self.battle = None
            self.status = "playing"
            self._apply_route_entry_effect(stage)
            if route_type == "shop":
                self._shop_open = True
                self.shop_items = self._generate_shop_items()
            return

        # 战斗节点
        enemies = [Enemy(name, hp, dmg) for name, hp, dmg in stage["enemies"]]
        self.battle = WebBattle(self.player, enemies)
        self.battle.start()
        self._apply_relic_battle_start(enemies)
        self._apply_next_battle_bonus()
        self.status = "playing"

        chapter_idx = min(self.current_stage // 3, len(STAGE_CHAPTERS) - 1)
        chapter = STAGE_CHAPTERS[chapter_idx]
        stage_num = self.current_stage + 1
        total = self.total_stages

        if self.current_stage % 3 == 0:
            self.messages.append(f"\n{'═'*40}")
            self.messages.append(f"  {chapter}")
            self.messages.append(f"{'═'*40}")

        self.messages.append(f"\n{'─'*30}")
        self.messages.append(f"📅 第 {stage_num}/{total} 层: {stage['name']} [{stage.get('route', '路线')}]")
        enemy_list = ", ".join(f"{e[0]}(❤️{e[1]})" for e in stage["enemies"])
        self.messages.append(f"👾 敌人: {enemy_list}")
        self.messages.append(f"{'─'*30}")

    def _apply_relic_battle_start(self, enemies: List[Enemy]):
        if not self.relics:
            return
        for relic in self.relics:
            rid = relic["id"]
            if rid == "bronze_charm":
                self.player.block += 5
            elif rid == "war_drum":
                self.player.strength += 1
            elif rid == "toxic_needle":
                for enemy in enemies:
                    enemy.apply_poison(1)
            elif rid == "ember_core":
                for enemy in enemies:
                    enemy.apply_burn(1)
            elif rid == "bone_totem":
                self.player.skeletons += 1
            elif rid == "clockwork_cell":
                self.player.energy += 1
            elif rid == "thorn_badge":
                self.player.thorns += 1
            elif rid == "healing_leaf":
                self.player.heal(3)
            elif rid == "mirror_shard":
                self.player.double_next_card = True
            elif rid == "shield_rune":
                self.player.blessing += 2
        names = "、".join(f"{r['icon']}{r['name']}" for r in self.relics)
        self.messages.append(f"🏺 遗物生效：{names}")

    def _apply_next_battle_bonus(self):
        if self._next_battle_strength_bonus > 0:
            self.player.strength += self._next_battle_strength_bonus
            self.messages.append(f"⚔️ 上轮奖励生效：攻击 +{self._next_battle_strength_bonus}")
            self._next_battle_strength_bonus = 0
        if self._next_battle_block_bonus > 0:
            self.player.block += self._next_battle_block_bonus
            self.messages.append(f"🛡️ 上轮奖励生效：防御 +{self._next_battle_block_bonus}")
            self._next_battle_block_bonus = 0

    def _apply_route_entry_effect(self, stage: Dict[str, Any]):
        route_type = stage.get("route_type")
        if route_type == "campfire":
            self.player.poison = self.player.burn = self.player.bleed = 0
            self.player.weak = self.player.vulnerable = self.player.curse = 0
            healed = self.player.heal(15)
            self.messages.append(f"🔥 营火休整：净化负面状态并回复 {healed} 点生命")
            self.messages.append("🧭 休息完毕，选择下一条路线继续前进...")
            self._event_data = {"type": "campfire", "title": "营火休整", "message": f"净化了所有负面状态，回复了 {healed} 点生命", "icon": "🔥"}
            # 营火节点自动进入路线选择
            self._after_non_combat()
        elif route_type == "shop":
            self.messages.append("🛒 商店！使用金币购买物品强化自己")
            self.messages.append("💰 选择购买后，点击继续前进选择路线")
            self._shop_open = True
            self.shop_items = self._generate_shop_items()
        elif route_type == "event":
            event = random.choice(["heal", "wound", "curse", "strength"])
            if event == "heal":
                healed = self.player.heal(15)
                self.messages.append(f"❔ 事件：发现补给，回复 {healed} 点生命")
                self._event_data = {"type": "heal", "title": "发现补给", "message": f"回复了 {healed} 点生命", "icon": "💚"}
            elif event == "wound":
                loss = min(10, max(1, self.player.hp - 1))
                self.player.hp -= loss
                self.messages.append(f"❔ 事件：遭遇陷阱，失去 {loss} 点生命")
                self._event_data = {"type": "wound", "title": "遭遇陷阱", "message": f"失去了 {loss} 点生命", "icon": "💀"}
            elif event == "curse":
                from src.core.card import CurseCard
                self.player.discard_pile.append(CurseCard())
                self.messages.append("❔ 事件：获得一张诅咒牌，但获得 5 金币补偿")
                self.gold += 5
                self._event_data = {"type": "curse", "title": "诅咒降临", "message": "获得了一张诅咒牌，作为补偿获得了 5 金币", "icon": "🌑"}
            else:
                self._next_battle_strength_bonus += 1
                self.messages.append("❔ 事件：获得临时启发，下一轮攻击 +1")
                self._event_data = {"type": "strength", "title": "临时启发", "message": "下一轮攻击 +1", "icon": "💪"}
            self._after_non_combat()

    def _after_non_combat(self):
        """非战斗节点结束后进入路线选择"""
        self.status = "stage_clear"
        self.current_rewards = []
        self.branch_choices = self._next_branch_choices()
        if not self.branch_choices:
            if self.current_stage >= self.total_stages - 1:
                self.status = "victory"
                self.messages.append("🏆 恭喜通关！")
            return
        self.status = "path_select"
        self.messages.append("🧭 选择下一条路线继续前进...")

    def _award_gold(self):
        """根据难度和层数奖励金币"""
        mult = DIFFICULTY_MULT.get(self.difficulty, DIFFICULTY_MULT["easy"])
        base = random.randint(mult["gold_min"], mult["gold_max"])
        bonus = self.current_stage // 5
        total = base + bonus
        self.gold += total
        self.messages.append(f"💰 获得 {total} 金币（当前 {self.gold}）")

    def _check_battle_end(self):
        """检查当前战斗是否结束"""
        if not self.battle or not self.battle.game_over:
            return

        if self.battle.winner == "player":
            stage_num = self.current_stage + 1
            total = self.total_stages

            # 奖励金币
            self._award_gold()

            if self.current_stage >= self.total_stages - 1:
                self.messages.append(f"\n{'★'*40}")
                self.messages.append(f"🎉🎉 恭喜通关全部 {total} 关！🎉🎉")
                self.messages.append("🏆 你成为了真正的卡牌大师！")
                self.messages.append(f"{'★'*40}")
                self.status = "victory"
            else:
                self.status = "stage_clear"
                self.messages.append(f"\n✅ 第 {stage_num}/{total} 关通过！")

                if stage_num == 5:
                    self.messages.append("💪 继续前进！")
                elif stage_num == 10:
                    self.messages.append("⚡ 旅程进入中段！")
                elif stage_num == 15:
                    self.messages.append("🔥 前路更加艰险！")
                elif stage_num == 20:
                    self.messages.append("💀 最后的挑战在即！")
                elif stage_num == 25:
                    self.messages.append("👑 距离Boss越来越近！")
                elif stage_num == 29:
                    self.messages.append("⛺ 前方是营火，Boss就在下一层！")

                choices = self._next_branch_choices()
                if choices:
                    preview = " / ".join(f"{c['icon']}{c['name']}" for c in choices)
                    self.messages.append(f"▶ 可选路线: {preview}")
                self.messages.append("🎁 选择一项奖励后，再选择下一条路线...")

                # 清空手牌和 debuff
                self._prepare_next_stage_deck()
                self.player.poison = 0
                self.player.burn = 0
                self.player.bleed = 0
                self.player.weak = 0
                self.player.vulnerable = 0
                self.player.curse = 0
                self.player.block = 0
                self.player.energy = self.player.max_energy
                # 清空遗物与技能提供的临时 buff
                self.player.thorns = 0
                self.player.blessing = 0
                self.player.skeletons = 0
                self.player.double_next_card = False
                self.player.iron_wall = 0
                self.player.counter = 0
                self.player.auto_shield = False
                self.player.block_persist = False
                self.player.turret_damage = 0
                self.player.skill_used_this_turn = False
                self.player.strength = self._base_strength
                self.current_rewards = self._generate_rewards()
        else:
            self.status = "defeat"
            self.messages.append(f"💀 在第 {self.current_stage+1} 关倒下了...")
            self.messages.append("🔄 按 R 重新开始挑战")

    def _current_stage_data(self) -> Dict[str, Any]:
        return self.branch_graph["nodes"][self.current_node_id]

    def _node_to_choice(self, node: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": node["id"],
            "layer": node["layer"],
            "name": node["name"],
            "route": node.get("route", ""),
            "route_type": node.get("route_type", ""),
            "desc": node.get("desc", ""),
            "icon": node.get("icon", "●"),
            "risk": node.get("risk", 1),
            "reward_hint": node.get("reward_hint", ""),
            "enemies": [{"name": e[0], "hp": e[1], "damage": e[2]} for e in node["enemies"]],
        }

    def _next_branch_choices(self) -> List[Dict[str, Any]]:
        current = self._current_stage_data()
        return [self._node_to_choice(self.branch_graph["nodes"][node_id]) for node_id in current.get("next", [])]

    def _branch_layers_state(self) -> List[List[Dict[str, Any]]]:
        layers = []
        for layer in self.branch_graph["layers"]:
            row = []
            for node_id in layer:
                node = self.branch_graph["nodes"][node_id]
                item = self._node_to_choice(node)
                item["visited"] = node_id in self.path_taken
                item["current"] = node_id == self.current_node_id
                item["available"] = any(c["id"] == node_id for c in self.branch_choices)
                row.append(item)
            layers.append(row)
        return layers

    def _prepare_next_stage_deck(self):
        cards = self.player.deck + self.player.discard_pile + self.player.hand
        self.player.hand.clear()
        self.player.discard_pile.clear()
        random.shuffle(cards)
        self.player.deck = cards

    def _all_cards(self) -> List[Any]:
        return self.player.deck + self.player.discard_pile + self.player.hand

    def _make_card(self, card_class_name: str):
        from src.core.player import _get_card_class
        card_cls = _get_card_class(card_class_name)
        return card_cls() if card_cls else None

    def _card_text(self, card) -> str:
        suffix = "✨" if getattr(card, "upgraded", False) else ""
        return f"{card.name}{suffix}：{card.description}"

    def _remove_card_object(self, target):
        for pile in (self.player.deck, self.player.discard_pile, self.player.hand):
            if target in pile:
                pile.remove(target)
                return

    def _generate_shop_items(self) -> List[Dict[str, str]]:
        """生成商店物品列表（随机6-8个）"""
        all_items = [dict(item) for item in SHOP_ITEMS]
        random.shuffle(all_items)
        items = all_items[:random.randint(6, 8)]
        for item in items:
            item["label"] = f"{item['icon']} {item['name']}（{item['cost']}💰）"
            item["desc"] = item.get("desc", "")
        return items

    def _generate_rewards(self) -> List[Dict[str, str]]:
        route_type = self._current_stage_data().get("route_type", "normal")
        rewards: List[Dict[str, str]] = []

        common = {
            "heal": {"id": "heal", "label": "💚 回复 20 点生命", "desc": "恢复20HP"},
            "max_hp": {"id": "max_hp", "label": "❤️ 最大生命 +8", "desc": "同时回复8点生命"},
            "rare_power": {"id": "rare_power", "label": "🌟 稀有强化", "desc": "力量+1，最大生命+5"},
            "special_training": {"id": "special_training", "label": "🔧 特殊强化", "desc": "最大能量+1"},
            "cleanse_supply": {"id": "cleanse_supply", "label": "⛺ 补给休整", "desc": "净化负面状态并回复18点生命"},
            "next_attack": {"id": "next_attack", "label": "⚔️ 下一轮攻击 +3", "desc": "下一场战斗伤害+3"},
            "next_defense": {"id": "next_defense", "label": "🛡️ 下一轮防御 +8", "desc": "下一场战斗开始获得8格挡"},
            "heal_full": {"id": "heal_full", "label": "❤️ 完全恢复", "desc": "HP回满，仅可用一次"},
        }

        route_pools = {
            "normal": ["heal", "max_hp", "next_attack", "next_defense"],
            "elite": ["rare_power", "special_training", "next_attack", "next_defense"],
            "campfire": ["cleanse_supply", "heal", "max_hp", "heal_full"],
            "event": random.sample(["heal", "rare_power", "max_hp", "next_attack", "next_defense"], 3),
        }

        base_ids = route_pools.get(route_type, ["heal", "max_hp", "next_attack", "next_defense"])
        if not self._heal_full_used:
            if route_type in ("normal", "campfire"):
                base_ids.append("heal_full")

        rewards.extend([common[rid] for rid in base_ids[:3]])

        upgrade_candidates = [
            (i, c) for i, c in enumerate(self._all_cards()) if not getattr(c, "upgraded", False)
        ]
        if upgrade_candidates and route_type in ("elite", "normal", "event"):
            idx, card = random.choice(upgrade_candidates)
            rewards.append({
                "id": f"upgrade_card:{idx}",
                "label": f"✨ 升级：{card.name}",
                "desc": card.description,
            })
            if route_type == "elite" and len(upgrade_candidates) > 1:
                idx2, card2 = random.choice([x for x in upgrade_candidates if x[0] != idx])
                rewards.append({
                    "id": f"upgrade_card:{idx2}",
                    "label": f"✨ 精英升级：{card2.name}",
                    "desc": card2.description,
                })

        if len(self._all_cards()) > 8 and route_type in ("normal", "campfire"):
            idx, card = random.choice(list(enumerate(self._all_cards())))
            rewards.append({
                "id": f"remove_card:{idx}",
                "label": f"🗑️ 删除：{card.name}",
                "desc": "从本局牌组中移除这张牌",
            })

        owned = {r["id"] for r in self.relics}
        relic_candidates = [r for r in RELIC_POOL if r["id"] not in owned]
        if relic_candidates and route_type in ("elite", "event", "campfire"):
            relic = random.choice(relic_candidates)
            rewards.append({
                "id": f"relic:{relic['id']}",
                "label": f"{relic['icon']} 遗物：{relic['name']}",
                "desc": relic["desc"],
            })

        random.shuffle(rewards)
        return rewards[:4]