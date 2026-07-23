"""
图鉴 + 多局成长系统

使用 JSON 文件持久化，跟踪：
- 已遇到的卡牌、敌人、遗物
- 各角色胜场、最高关卡、通关次数
- 解锁状态（初始3角色可用，胜场解锁更多）
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

DATA_DIR = Path(__file__).resolve().parent.parent
COLLECTION_FILE = DATA_DIR / "collection_data.json"

# 初始解锁角色（3个基础角色）
BASE_UNLOCKED = {"warrior", "elf", "wizard"}

# 解锁条件：角色ID -> 所需总胜场数
UNLOCK_REQUIREMENTS = {
    "warrior": 0,      # 初始解锁
    "elf": 0,           # 初始解锁
    "wizard": 0,        # 初始解锁
    "paladin": 3,       # 累计3胜
    "assassin": 5,      # 累计5胜
    "priest": 8,        # 累计8胜
    "mechanist": 12,    # 累计12胜
    "necromancer": 16,  # 累计16胜
    "alchemist": 20,    # 累计20胜
}

# 所有可收集的卡牌名称
ALL_CARD_NAMES = [
    "斩击", "重击", "防御", "双连斩", "旋风斩", "狂暴打击", "连击", "铁壁", "战吼",
    "背刺", "圣光打击", "神圣惩击", "盾击", "流血", "诅咒箭", "牺牲",
    "元素融合", "吸血斩", "弱化打击", "毒击", "燃火击",
    "堡垒", "反击", "小治疗", "愈合", "削弱", "毒云", "火球术",
    "肾上腺素", "快速抽牌", "暗影弃牌", "净化", "毒瓶", "突变", "转化", "能量电池",
    "狂怒", "祝福", "荆棘光环", "布置炮台", "模块升级", "召唤骷髅", "生命汲取",
    "诅咒", "万能药剂",
]

# 所有敌人名称
ALL_ENEMY_NAMES = [
    "哥布林", "史莱姆", "火焰领主", "寒冰法师", "暗影领主",
    "毒沼史莱姆", "熔岩犬", "镜像怪", "护卫队长", "诅咒法师",
    "暗影之神", "暗影大君", "终焉骑士", "恶魔猎手", "毒沼领主",
    "突击队长", "哥布林王", "烈焰守卫", "冰霜女巫", "炼狱守卫",
    "幻影魔", "深渊术士", "混沌兽", "腐蚀领主", "铁壁将军",
    "虚空行者", "末日军官", "永恒守卫", "地狱领主", "星辰使徒",
]

# 所有遗物名称
ALL_RELIC_NAMES = [
    "铜质护符", "战鼓", "毒针戒指", "余烬核心", "白骨图腾",
    "发条电池", "荆棘徽章", "治愈叶", "镜面碎片", "护盾符文",
]


def _default_data() -> Dict[str, Any]:
    return {
        "seen_cards": [],
        "seen_enemies": [],
        "seen_relics": [],
        "total_wins": 0,
        "total_games": 0,
        "highest_stage": 0,
        "char_stats": {},
        "unlocked_chars": list(BASE_UNLOCKED),
    }


def _load() -> Dict[str, Any]:
    if not COLLECTION_FILE.exists():
        return _default_data()
    try:
        with open(COLLECTION_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 确保所有字段存在
        defaults = _default_data()
        for k, v in defaults.items():
            if k not in data:
                data[k] = v
        return data
    except (json.JSONDecodeError, IOError):
        return _default_data()


def _save(data: Dict[str, Any]):
    COLLECTION_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(COLLECTION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_collection() -> Dict[str, Any]:
    """获取完整图鉴数据"""
    data = _load()
    return {
        "cards": {
            "seen": data["seen_cards"],
            "total": len(ALL_CARD_NAMES),
            "all": ALL_CARD_NAMES,
        },
        "enemies": {
            "seen": data["seen_enemies"],
            "total": len(ALL_ENEMY_NAMES),
            "all": ALL_ENEMY_NAMES,
        },
        "relics": {
            "seen": data["seen_relics"],
            "total": len(ALL_RELIC_NAMES),
            "all": ALL_RELIC_NAMES,
        },
        "stats": {
            "total_wins": data["total_wins"],
            "total_games": data["total_games"],
            "highest_stage": data["highest_stage"],
            "char_stats": data["char_stats"],
        },
        "unlocked_chars": data.get("unlocked_chars", list(BASE_UNLOCKED)),
        "unlock_requirements": UNLOCK_REQUIREMENTS,
    }


def record_card_seen(card_name: str):
    """记录遇到的卡牌"""
    data = _load()
    if card_name not in data["seen_cards"]:
        data["seen_cards"].append(card_name)
    _save(data)


def record_enemy_seen(enemy_name: str):
    """记录遇到的敌人"""
    data = _load()
    if enemy_name not in data["seen_enemies"]:
        data["seen_enemies"].append(enemy_name)
    _save(data)


def record_relic_seen(relic_name: str):
    """记录遇到的遗物"""
    data = _load()
    if relic_name not in data["seen_relics"]:
        data["seen_relics"].append(relic_name)
    _save(data)


def record_game_result(won: bool, character_id: str, highest_stage: int):
    """记录游戏结果，更新统计和解锁"""
    data = _load()
    data["total_games"] += 1

    if character_id not in data["char_stats"]:
        data["char_stats"][character_id] = {"wins": 0, "games": 0, "highest_stage": 0}

    data["char_stats"][character_id]["games"] += 1
    data["highest_stage"] = max(data["highest_stage"], highest_stage)
    data["char_stats"][character_id]["highest_stage"] = max(
        data["char_stats"][character_id]["highest_stage"], highest_stage
    )

    if won:
        data["total_wins"] += 1
        data["char_stats"][character_id]["wins"] += 1

    # 检查解锁
    total_wins = data["total_wins"]
    unlocked = set(data.get("unlocked_chars", list(BASE_UNLOCKED)))
    for char_id, req in UNLOCK_REQUIREMENTS.items():
        if total_wins >= req and char_id not in unlocked:
            unlocked.add(char_id)
    data["unlocked_chars"] = list(unlocked)

    _save(data)


def is_char_unlocked(character_id: str) -> bool:
    """检查角色是否已解锁"""
    data = _load()
    unlocked = set(data.get("unlocked_chars", list(BASE_UNLOCKED)))
    return character_id in unlocked


def get_unlocked_info() -> Dict[str, Any]:
    """获取解锁信息"""
    data = _load()
    total_wins = data["total_wins"]
    unlocked = set(data.get("unlocked_chars", list(BASE_UNLOCKED)))
    chars_info = {}
    for char_id, req in UNLOCK_REQUIREMENTS.items():
        chars_info[char_id] = {
            "unlocked": char_id in unlocked,
            "requirement": req,
            "progress": min(total_wins, req),
        }
    return {
        "total_wins": total_wins,
        "chars": chars_info,
    }