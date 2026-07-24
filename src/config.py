"""
游戏配置中心
所有可调的游戏常量集中管理，避免散落各处
"""
from typing import Dict, Any

# ============================================================
# 游戏基础数值
# ============================================================
DEFAULT_ENERGY = 3
DEFAULT_MAX_ENERGY = 3
DEFAULT_DRAW_PER_TURN = 5
DEFAULT_HP = 80

# 伤害/格挡计算倍率
WEAK_DAMAGE_MULTIPLIER = 0.75
VULNERABLE_DAMAGE_MULTIPLIER = 1.5

# 敌人 AI 通用阈值
AI_LOW_HP_THRESHOLD = 0.3     # HP低于此比例时增加防御倾向
AI_HIGH_STRENGTH_THRESHOLD = 5  # 力量高于此值时增加攻击倾向

# ============================================================
# 关卡模式配置
# ============================================================
LEVEL_TOTAL = 30
LEVEL_DIFFICULTY_MULTIPLIERS = {
    "easy": 0.9,
    "hard": 1.1,
    "hell": 1.3,
}
LEVEL_SCALING_RATE = 0.022       # 每层难度递增率
LEVEL_HELL_CAP = 1.55            # 地狱难度 HP 上限倍率
LEVEL_BOSS_INTERVAL = 10         # Boss 每 N 层出现一次
LEVEL_SHOP_PROBABILITY = 0.15    # 商店节点出现概率
LEVEL_START_GOLD = 99

# 奖励数值
REWARD_HEAL = 20
REWARD_MAX_HP_BONUS = 8
REWARD_STRENGTH_BONUS = 1
REWARD_FOCUS_DAMAGE = 3
REWARD_FOCUS_BLOCK = 8
REWARD_GOLD = 30

# 商店价格
SHOP_CARD_PRICE = 15
SHOP_RELIC_PRICE = 25
SHOP_POTION_PRICE = 20
SHOP_REMOVE_PRICE = 40

# ============================================================
# 角色默认属性
# ============================================================
CHARACTER_DEFAULT_HP = {
    "warrior": 80,
    "elf": 65,
    "wizard": 55,
    "paladin": 90,
    "assassin": 60,
    "priest": 75,
    "mechanist": 70,
    "necromancer": 58,
    "alchemist": 68,
}

# 圣骑士特殊数值
PALADIN_AUTO_SHIELD = 10
IRON_WALL_BLOCK = 5

# ============================================================
# 敌人 AI 意图配置
# ============================================================
# 具名敌人的专属意图池
NAMED_ENEMY_INTENTS: Dict[str, list] = {
    "毒沼史莱姆": ["毒液", "攻击", "防御"],
    "熔岩犬": ["灼咬", "攻击", "强化"],
    "镜像怪": ["镜像", "攻击", "防御"],
    "护卫队长": ["守护", "攻击", "强化"],
    "诅咒法师": ["诅咒", "攻击", "虚弱"],
}

# 通用敌人意图池 (按状态)
GENERIC_INTENT_POOLS = {
    "low_hp": ["攻击", "防御", "防御", "强化"],
    "high_strength": ["攻击", "攻击", "攻击", "防御"],
    "default": ["攻击", "攻击", "防御", "强化"],
}

# 意图执行参数
INTENT_DEFEND_BLOCK = 8
INTENT_STRENGTHEN_AMOUNT = 2
INTENT_GUARD_BLOCK = 10
INTENT_POISON_AMOUNT = 2
INTENT_BURN_AMOUNT = 2
INTENT_WEAK_AMOUNT = 2
INTENT_CURSE_AMOUNT = 2
INTENT_VULNERABLE_AMOUNT = 1
INTENT_POISON_DAMAGE_RATIO = 0.5  # 毒液攻击伤害 = base_damage * 0.5

# 意图描述 (tooltip)
INTENT_DESCRIPTIONS = {
    "攻击": "敌人将直接造成伤害，可用格挡抵消。",
    "防御": "敌人将获得格挡，降低本回合可造成的有效伤害。",
    "强化": "敌人将提升力量，后续攻击更危险。",
    "毒液": "造成少量伤害并让玩家中毒，中毒会在回合结束造成伤害。",
    "灼咬": "造成攻击伤害并附加烧伤，烧伤会在回合结束造成伤害。",
    "镜像": "模仿玩家上一张牌的气势，造成伤害并施加易伤。",
    "守护": "为所有敌人增加格挡，适合优先处理。",
    "诅咒": "向玩家牌堆加入无法打出的诅咒牌，并提高后续受伤。",
    "虚弱": "降低玩家后续攻击伤害。",
}

# ============================================================
# Web 服务配置
# ============================================================
WEB_HOST = "127.0.0.1"
WEB_PORT = 5000
WEB_PORT_SCAN_RANGE = (5000, 5010)

# ============================================================
# 无尽模式配置
# ============================================================
ENDLESS_INITIAL_FLOORS = 10
ENDLESS_EXTEND_THRESHOLD = 5      # 剩余 ≤ N 层时扩展
ENDLESS_EXTEND_AMOUNT = 10        # 每次扩展 N 层
ENDLESS_MINI_BOSS_INTERVAL = 10   # 每 N 层一个小 Boss
ENDLESS_TIER_INTERVAL = 5         # 每 N 层提升难度等级

ENDLESS_BOSS_POOL = [
    "暗影领主", "火焰领主", "镜像怪", "寒冰法师", "诅咒法师",
]


def get_enemy_intent_pool(enemy_name: str, hp_ratio: float, strength: int) -> list:
    """根据敌人状态返回意图池（数据驱动）"""
    if enemy_name in NAMED_ENEMY_INTENTS:
        return NAMED_ENEMY_INTENTS[enemy_name]
    if hp_ratio < AI_LOW_HP_THRESHOLD:
        return GENERIC_INTENT_POOLS["low_hp"]
    if strength > AI_HIGH_STRENGTH_THRESHOLD:
        return GENERIC_INTENT_POOLS["high_strength"]
    return GENERIC_INTENT_POOLS["default"]