from .character import Character
import random
from typing import List, Optional


# ── 角色模板 ──────────────────────────────────────────────
# id: (显示名, HP, 卡牌列表(每张牌一个类, 数量表示重复))
CHARACTER_TEMPLATES = {
    "warrior": {
        "name": "勇者", "hp": 80,
        "image": "勇者.svg",
        "desc": "专注力量的战士",
        "cards": [
            ("Strike", 4), ("Defend", 2), ("HeavyStrike", 2),
            ("Rampage", 1), ("BattleCry", 1), ("Rage", 1),
            ("WeakenStrike", 1), ("MinorHeal", 1),
        ],
        "skill": {"name": "净化", "desc": "消除全部负面状态", "cost": 2, "icon": "✨"},
    },
    "elf": {
        "name": "精灵", "hp": 65,
        "image": "精灵.svg",
        "desc": "敏捷灵巧的连击大师",
        "cards": [
            ("Strike", 2), ("Defend", 2),
            ("DoubleStrike", 2), ("ComboStrike", 2),
            ("QuickDraw", 1), ("Adrenaline", 1),
            ("PoisonStrike", 1), ("MinorHeal", 1),
            ("Rampage", 1), ("Whirlwind", 1),
        ],
        "skill": {"name": "回响", "desc": "下一张打出的牌释放两次", "cost": 2, "icon": "🔄"},
    },
    "wizard": {
        "name": "巫师", "hp": 55,
        "image": "巫师.svg",
        "desc": "元素魔法的掌控者",
        "cards": [
            ("Strike", 2), ("Defend", 2),
            ("PoisonStrike", 1), ("BurnStrike", 1),
            ("PoisonCloud", 1), ("Fireball", 1), ("Catalyst", 1),
            ("Adrenaline", 1), ("QuickDraw", 1), ("MinorHeal", 1),
            ("ElementalFusion", 2), ("Enfeeble", 1),
        ],
        "skill": {"name": "元素爆发", "desc": "对所有敌人造成5点伤害+2层毒+2层烧伤", "cost": 2, "icon": "💥"},
    },
    "paladin": {
        "name": "圣骑士", "hp": 90,
        "image": "圣骑士.svg",
        "desc": "坚不可摧的守护者",
        "cards": [
            ("Strike", 2), ("Defend", 4),
            ("Fortress", 1), ("IronWall", 1), ("CounterStrike", 1),
            ("Rejuvenate", 1), ("ShieldStrike", 2), ("MinorHeal", 1),
        ],
        "skill": {"name": "圣盾", "desc": "被动：每轮自动获得10点护盾，护盾不重置", "cost": 0, "icon": "🛡️"},
    },
    "assassin": {
        "name": "刺客", "hp": 60,
        "image": "刺客.svg",
        "desc": "连击、流血、弃牌与低费爆发",
        "cards": [
            ("Backstab", 3), ("BleedCut", 3), ("ShadowDiscard", 2),
            ("QuickDraw", 2), ("ComboStrike", 2), ("Defend", 2),
        ],
        "skill": {"name": "暗影爆发", "desc": "本回合获得2点能量和2点力量", "cost": 1, "icon": "🗡️"},
    },
    "priest": {
        "name": "牧师", "hp": 75,
        "image": "牧师.svg",
        "desc": "治疗、净化、祝福与反伤",
        "cards": [
            ("HolySmite", 3), ("MinorHeal", 2), ("Purify", 2),
            ("Blessing", 2), ("ThornAura", 1), ("Defend", 3),
        ],
        "skill": {"name": "神圣新星", "desc": "回复8点生命并对所有敌人造成4点伤害", "cost": 2, "icon": "🙏"},
    },
    "mechanist": {
        "name": "机械师", "hp": 70,
        "image": "机械师.svg",
        "desc": "炮台、能量电池与装备模块",
        "cards": [
            ("Strike", 2), ("DeployTurret", 2), ("EnergyBattery", 2),
            ("ModuleUpgrade", 2), ("Defend", 3), ("HeavyStrike", 1),
        ],
        "skill": {"name": "超频", "desc": "炮台伤害+3，获得1点能量", "cost": 1, "icon": "⚙️"},
    },
    "necromancer": {
        "name": "亡灵法师", "hp": 58,
        "image": "亡灵法师.svg",
        "desc": "牺牲生命、召唤骷髅、诅咒敌人",
        "cards": [
            ("CurseBolt", 3), ("RaiseSkeleton", 2), ("LifeTap", 2),
            ("Sacrifice", 1), ("VampireStrike", 2), ("Defend", 2),
        ],
        "skill": {"name": "亡者复苏", "desc": "召唤1个骷髅并回复5点生命", "cost": 2, "icon": "💀"},
    },
    "alchemist": {
        "name": "炼金术士", "hp": 68,
        "image": "炼金术士.svg",
        "desc": "药水、中毒、随机强化与状态转换",
        "cards": [
            ("VenomFlask", 3), ("Mutagen", 2), ("Transmute", 2),
            ("PoisonStrike", 2), ("BurnStrike", 1), ("Defend", 2),
        ],
        "skill": {"name": "万能药剂", "desc": "随机强化并对所有敌人施加2毒", "cost": 2, "icon": "⚗️"},
    },
}




def _get_card_class(name):
    """根据卡牌类名获取卡牌类 (如 'Strike' -> src.core.card.Strike)"""
    from . import card as card_module
    cls = getattr(card_module, name, None)
    if cls and isinstance(cls, type):
        return cls
    # 兼容: 按中文名查找
    for attr in dir(card_module):
        cls = getattr(card_module, attr)
        if isinstance(cls, type) and hasattr(cls, '__bases__'):
            for base in cls.__bases__:
                if base.__name__ == 'Card':
                    try:
                        if cls().name == name:
                            return cls
                    except Exception:
                        pass
    return None


class Player(Character):
    """玩家类"""

    def __init__(self, name: str = "勇者", max_hp: int = 80,
                 character_id: Optional[str] = None):
        super().__init__(name, max_hp)
        self.character_id = character_id
        self.energy = 3
        self.max_energy = 3
        self.cards_played_this_turn = 0
        self.skill_used_this_turn = False

        # 额外能力
        self.prayer = False
        self.echo_form = False
        self.extra_turn = False
        self.double_next_card = False
        self.turret_damage = 0
        self.skeletons = 0
        self.last_played_card_name = None

        # 敌人列表（用于AOE）
        self.enemies: List[Character] = []

        # 被动标记
        self.block_persist = (character_id == 'paladin')
        self.auto_shield = (character_id == 'paladin')  # 每轮自动+10盾
        self.iron_wall_block = 5

        # 初始卡组
        self.deck = self._make_deck(character_id)

    @staticmethod
    def _make_deck(character_id: Optional[str] = None) -> list:
        """根据角色ID生成初始牌组"""
        from .card import Strike, Defend, WeakenStrike, BurnStrike, BattleCry, QuickDraw, MinorHeal

        template = CHARACTER_TEMPLATES.get(character_id) if character_id else None

        if template:
            deck = []
            for card_name, count in template["cards"]:
                card_cls = _get_card_class(card_name)
                if card_cls:
                    deck.extend([card_cls() for _ in range(count)])
            if deck:
                random.shuffle(deck)
                return deck

        # 默认勇者牌组
        deck = [
            Strike(), Strike(), Strike(), Strike(),
            Defend(), Defend(), Defend(), Defend(),
            WeakenStrike(), BurnStrike(), BattleCry(),
            QuickDraw(), MinorHeal(),
        ]
        random.shuffle(deck)
        return deck

    def start_turn(self):
        """回合开始"""
        # 重置能量
        self.energy = self.max_energy
        self.cards_played_this_turn = 0
        self.skill_used_this_turn = False

        # 能力效果
        if self.iron_wall:
            block = self.iron_wall_block + self.focus_block
            self.block += block
            print(f"🛡️ 铁壁提供 {block} 点格挡")
        if self.auto_shield:
            self.block += 10
            print(f"🛡️ 圣盾提供 10 点格挡 (当前{self.block})")

        if self.prayer:
            healed = self.heal(3)
            if healed > 0:
                print(f"💚 祈祷回复 {healed} 点生命")

        if self.blessing > 0:
            self.block += self.blessing
            print(f"✨ 祝福提供 {self.blessing} 点格挡")

        if self.turret_damage > 0 and self.enemies:
            for enemy in self.enemies:
                if enemy.is_alive():
                    actual = enemy.take_damage(self.turret_damage)
                    print(f"🤖 炮台对 {enemy.name} 造成 {actual} 点伤害")
                    break

        if self.skeletons > 0 and self.enemies:
            damage = self.skeletons * 3
            for enemy in self.enemies:
                if enemy.is_alive():
                    actual = enemy.take_damage(damage)
                    print(f"💀 骷髅仆从对 {enemy.name} 造成 {actual} 点伤害")
                    break

        # 抽牌
        drawn = self.draw(5)
        print(f"\n📋 {self.name} 的回合开始")
        print(f"⚡ 能量: {self.energy}/{self.max_energy}")
        print(f"📤 抽了 {drawn} 张牌")

    def draw(self, count: int):
        """抽牌"""
        drawn = 0
        for _ in range(count):
            if not self.deck and not self.discard_pile:
                break

            if not self.deck:
                # 洗牌
                self.deck = self.discard_pile[:]
                self.discard_pile.clear()
                random.shuffle(self.deck)
                print("📤 抽牌堆已洗牌")

            if self.deck:
                card = self.deck.pop()
                self.hand.append(card)
                drawn += 1

        return drawn

    def play_card(self, card, target) -> bool:
        """打出卡牌"""
        # 检查能量
        if self.energy < card.cost:
            print(f"❌ 能量不足！需要 {card.cost} 点能量，当前只有 {self.energy} 点")
            return False

        if not target.is_alive():
            print("❌ 目标已死亡！")
            return False

        # 消耗能量
        self.energy -= card.cost
        self.cards_played_this_turn += 1

        print(f"\n🎴 打出 {card.name} (消耗 {card.cost} 能量，剩余 {self.energy})")
        self.last_played_card_name = card.name

        # 从手牌中移除
        if card in self.hand:
            self.hand.remove(card)

        # 执行卡牌效果
        card.play(self, target)

        # 回响 - 下一张牌释放两次
        if self.double_next_card:
            self.double_next_card = False
            if target.is_alive() or card.name in {"旋风斩"}:
                print(f"🔄 回响触发！{card.name} 再次释放")
                card.play(self, target)
            else:
                print(f"🔄 回响触发，但目标已被击败")

        # 将牌放入弃牌堆（除非消耗）
        if not card.is_exhausted:
            self.discard_pile.append(card)
            print(f"📤 {card.name} 进入弃牌堆")
        else:
            print(f"💨 {card.name} 已消耗")

        return True

    def end_turn(self):
        """结束回合"""
        print(f"\n📋 {self.name} 的回合结束")
        print(f"⚡ 剩余能量: {self.energy}")

        # 先调用父类的end_turn（会清空格挡、结算状态等）
        super().end_turn()

        # 弃掉所有手牌
        discarded = len(self.hand)
        while self.hand:
            self.discard_pile.append(self.hand.pop())
        if discarded > 0:
            print(f"📤 弃掉了 {discarded} 张手牌")

        print(f"💪 当前力量: {self.strength}")

    def __str__(self):
        """显示玩家状态，包含格挡"""
        status = f"{self.name} HP: {self.hp}/{self.max_hp}"
        if self.block > 0:
            status += f" 🛡️格挡:{self.block}"
        if self.strength > 0:
            status += f" 💪力量:{self.strength}"
        if self.poison > 0:
            status += f" ☠️毒:{self.poison}"
        if self.burn > 0:
            status += f" 🔥烧伤:{self.burn}"
        if self.bleed > 0:
            status += f" 🩸流血:{self.bleed}"
        if self.weak > 0:
            status += f" 💫虚弱:{self.weak}"
        if self.vulnerable > 0:
            status += f" 💥易伤:{self.vulnerable}"
        if self.curse > 0:
            status += f" 🌑诅咒:{self.curse}"
        return status
