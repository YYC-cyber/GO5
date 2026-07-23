from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, List


class CardType(Enum):
    ATTACK = "攻击"
    SKILL = "技能"
    POWER = "能力"


class Card(ABC):
    """卡牌基类"""

    def __init__(self, name: str, card_type: CardType, cost: int, description: str):
        self.name = name
        self.type = card_type
        self.cost = cost
        self.description = description
        self.is_exhausted = False
        self.upgraded = False

    @abstractmethod
    def play(self, player, target):
        """执行卡牌效果"""
        pass

    def upgrade(self):
        """升级卡牌"""
        self.upgraded = True

    def __str__(self):
        return f"{self.name}({self.cost}费): {self.description}"


# ============ 攻击牌 ============
class Strike(Card):
    def __init__(self):
        super().__init__("猛击", CardType.ATTACK, 1, "造成6点伤害")
        self.damage = 6

    def play(self, player, target):
        damage = self.damage + player.strength + player.focus_damage
        actual = target.take_damage(damage)
        print(f"⚔️ {player.name} 对 {target.name} 造成 {actual} 点伤害")

    def upgrade(self):
        self.upgraded = True
        self.description = "造成9点伤害"
        self.damage = 9


class HeavyStrike(Card):
    def __init__(self):
        super().__init__("重击", CardType.ATTACK, 2, "造成12点伤害")
        self.damage = 12

    def play(self, player, target):
        damage = self.damage + player.strength + player.focus_damage
        actual = target.take_damage(damage)
        print(f"⚔️ {player.name} 对 {target.name} 造成 {actual} 点伤害")

    def upgrade(self):
        self.upgraded = True
        self.description = "造成16点伤害"
        self.damage = 16


class DoubleStrike(Card):
    def __init__(self):
        super().__init__("双重打击", CardType.ATTACK, 1, "造成2次4点伤害")
        self.damage = 4

    def play(self, player, target):
        damage = self.damage + player.strength + player.focus_damage
        total = 0
        for i in range(2):
            actual = target.take_damage(damage)
            total += actual
            print(f"⚔️ 第{i + 1}次打击造成 {actual} 点伤害")
        print(f"⚔️ 总共造成 {total} 点伤害")

    def upgrade(self):
        self.upgraded = True
        self.description = "造成2次6点伤害"
        self.damage = 6


class Whirlwind(Card):
    def __init__(self):
        super().__init__("旋风斩", CardType.ATTACK, 2, "对所有敌人造成5点伤害")
        self.damage = 5

    def play(self, player, target):
        damage = self.damage + player.strength + player.focus_damage
        if hasattr(player, 'enemies') and player.enemies:
            for enemy in player.enemies:
                if enemy.is_alive():
                    actual = enemy.take_damage(damage)
                    print(f"⚔️ {player.name} 对 {enemy.name} 造成 {actual} 点伤害")
        else:
            actual = target.take_damage(damage)
            print(f"⚔️ {player.name} 对 {target.name} 造成 {actual} 点伤害")

    def upgrade(self):
        self.upgraded = True
        self.description = "对所有敌人造成8点伤害"
        self.damage = 8


class Rampage(Card):
    def __init__(self):
        super().__init__("狂怒", CardType.ATTACK, 1, "造成4点伤害，本场战斗每使用一次+3伤害")
        self.times_played = 0
        self.base_damage = 4
        self.growth = 3

    def play(self, player, target):
        self.times_played += 1
        damage = self.base_damage + (self.times_played - 1) * self.growth + player.strength + player.focus_damage
        actual = target.take_damage(damage)
        print(f"⚔️ {player.name} 对 {target.name} 造成 {actual} 点伤害 (已使用{self.times_played}次)")

    def upgrade(self):
        self.upgraded = True
        self.description = "造成5点伤害，每使用一次+4伤害"
        self.base_damage = 5
        self.growth = 4


# ============ 防御牌 ============
class Defend(Card):
    def __init__(self):
        super().__init__("防御", CardType.SKILL, 1, "获得5点格挡")
        self.block = 5

    def play(self, player, target):
        block = self.block + player.focus_block
        player.block += block
        print(f"🛡️ {player.name} 获得 {block} 点格挡 (当前格挡: {player.block})")

    def upgrade(self):
        self.upgraded = True
        self.description = "获得8点格挡"
        self.block = 8


class Fortress(Card):
    def __init__(self):
        super().__init__("堡垒", CardType.SKILL, 2, "获得12点格挡")
        self.block = 12

    def play(self, player, target):
        block = self.block + player.focus_block
        player.block += block
        print(f"🛡️ {player.name} 获得 {block} 点格挡")

    def upgrade(self):
        self.upgraded = True
        self.description = "获得15点格挡"
        self.block = 15


class IronWall(Card):
    def __init__(self):
        super().__init__("铁壁", CardType.POWER, 2, "每回合获得5点格挡")
        self.block = 5

    def play(self, player, target):
        player.iron_wall = True
        player.iron_wall_block = self.block
        print(f"🛡️ {player.name} 获得铁壁效果，每回合获得{self.block}点格挡")

    def upgrade(self):
        self.upgraded = True
        self.description = "每回合获得8点格挡"
        self.block = 8


class CounterStrike(Card):
    def __init__(self):
        super().__init__("反击", CardType.SKILL, 1, "获得4点格挡，反弹本回合受到的伤害")
        self.block = 4

    def play(self, player, target):
        block = self.block + player.focus_block
        player.block += block
        player.counter = True
        print(f"🛡️ {player.name} 获得 {block} 点格挡，进入反击状态")

    def upgrade(self):
        self.upgraded = True
        self.description = "获得6点格挡"
        self.block = 6


# ============ 回复牌 ============
class MinorHeal(Card):
    def __init__(self):
        super().__init__("小治疗", CardType.SKILL, 1, "回复4点生命")
        self.heal_amount = 4

    def play(self, player, target):
        healed = player.heal(self.heal_amount)
        print(f"💚 {player.name} 回复了 {healed} 点生命")

    def upgrade(self):
        self.upgraded = True
        self.description = "回复7点生命"
        self.heal_amount = 7


class Rejuvenate(Card):
    def __init__(self):
        super().__init__("复苏", CardType.SKILL, 2, "回复12点生命")
        self.heal_amount = 12

    def play(self, player, target):
        healed = player.heal(self.heal_amount)
        print(f"💚 {player.name} 回复了 {healed} 点生命")

    def upgrade(self):
        self.upgraded = True
        self.description = "回复16点生命"
        self.heal_amount = 16


class VampireStrike(Card):
    def __init__(self):
        super().__init__("吸血鬼打击", CardType.ATTACK, 1, "造成6点伤害，回复伤害值的一半生命")
        self.damage = 6

    def play(self, player, target):
        damage = self.damage + player.strength + player.focus_damage
        actual = target.take_damage(damage)
        heal_amount = actual // 2
        if heal_amount > 0:
            player.heal(heal_amount)
        print(f"⚔️ {player.name} 造成 {actual} 点伤害，回复 {heal_amount} 点生命")

    def upgrade(self):
        self.upgraded = True
        self.description = "造成9点伤害，回复伤害值的一半生命"
        self.damage = 9


# ============ 削弱牌 ============
class WeakenStrike(Card):
    def __init__(self):
        super().__init__("虚弱打击", CardType.ATTACK, 1, "造成4点伤害，施加2层虚弱")
        self.damage = 4
        self.weak = 2

    def play(self, player, target):
        damage = self.damage + player.strength + player.focus_damage
        actual = target.take_damage(damage)
        target.apply_weak(self.weak)
        print(f"⚔️ {player.name} 造成 {actual} 点伤害，{target.name} 获得 {self.weak} 层虚弱")

    def upgrade(self):
        self.upgraded = True
        self.description = "造成7点伤害，施加3层虚弱"
        self.damage = 7
        self.weak = 3


class Enfeeble(Card):
    def __init__(self):
        super().__init__("虚弱术", CardType.SKILL, 1, "施加3层虚弱")
        self.weak = 3

    def play(self, player, target):
        target.apply_weak(self.weak)
        print(f"💫 {target.name} 获得 {self.weak} 层虚弱")

    def upgrade(self):
        self.upgraded = True
        self.description = "施加4层虚弱"
        self.weak = 4


# ============ 中毒牌 ============
class PoisonStrike(Card):
    def __init__(self):
        super().__init__("毒刃", CardType.ATTACK, 1, "造成3点伤害，施加3层中毒")
        self.damage = 3
        self.poison = 3

    def play(self, player, target):
        damage = self.damage + player.strength + player.focus_damage
        actual = target.take_damage(damage)
        target.apply_poison(self.poison)
        print(f"⚔️ {player.name} 造成 {actual} 点伤害，{target.name} 中毒 {self.poison} 层")

    def upgrade(self):
        self.upgraded = True
        self.description = "造成5点伤害，施加5层中毒"
        self.damage = 5
        self.poison = 5


class PoisonCloud(Card):
    def __init__(self):
        super().__init__("毒云", CardType.SKILL, 2, "施加5层中毒")
        self.poison = 5

    def play(self, player, target):
        target.apply_poison(self.poison)
        print(f"☠️ {target.name} 获得 {self.poison} 层中毒")

    def upgrade(self):
        self.upgraded = True
        self.description = "施加7层中毒"
        self.poison = 7


class Catalyst(Card):
    def __init__(self):
        super().__init__("催化剂", CardType.SKILL, 1, "立即结算目标的所有中毒伤害")
        self.multiplier = 1.0

    def play(self, player, target):
        if target.poison > 0:
            damage = int(target.poison * self.multiplier)
            target.take_damage(damage)
            print(f"💥 引爆中毒！{target.name} 受到 {damage} 点伤害")
            target.poison = 0
        else:
            print("目标没有中毒效果")

    def upgrade(self):
        self.upgraded = True
        self.description = "立即结算目标的所有中毒伤害，并额外造成50%伤害"
        self.multiplier = 1.5


# ============ 烧伤牌 ============
class BurnStrike(Card):
    def __init__(self):
        super().__init__("烈焰打击", CardType.ATTACK, 1, "造成5点伤害，施加2层烧伤")
        self.damage = 5
        self.burn = 2

    def play(self, player, target):
        damage = self.damage + player.strength + player.focus_damage
        actual = target.take_damage(damage)
        target.apply_burn(self.burn)
        print(f"⚔️ {player.name} 造成 {actual} 点伤害，{target.name} 烧伤 {self.burn} 层")

    def upgrade(self):
        self.upgraded = True
        self.description = "造成8点伤害，施加3层烧伤"
        self.damage = 8
        self.burn = 3


class Fireball(Card):
    def __init__(self):
        super().__init__("火球术", CardType.SKILL, 2, "施加4层烧伤")
        self.burn = 4

    def play(self, player, target):
        target.apply_burn(self.burn)
        print(f"🔥 {target.name} 获得 {self.burn} 层烧伤")

    def upgrade(self):
        self.upgraded = True
        self.description = "施加6层烧伤"
        self.burn = 6


# ============ 加伤牌 ============
class BattleCry(Card):
    def __init__(self):
        super().__init__("战斗怒吼", CardType.POWER, 1, "获得2层易伤和2点力量")
        self.vulnerable = 2
        self.strength = 2

    def play(self, player, target):
        player.apply_vulnerable(self.vulnerable)
        player.strength += self.strength
        print(f"💪 {player.name} 获得 {self.vulnerable} 层易伤和 {self.strength} 点力量")

    def upgrade(self):
        self.upgraded = True
        self.description = "获得3层易伤和3点力量"
        self.vulnerable = 3
        self.strength = 3


class Rage(Card):
    def __init__(self):
        super().__init__("狂暴", CardType.POWER, 1, "获得3点力量")
        self.strength = 3

    def play(self, player, target):
        player.strength += self.strength
        print(f"💪 {player.name} 获得 {self.strength} 点力量")

    def upgrade(self):
        self.upgraded = True
        self.description = "获得4点力量"
        self.strength = 4


class Adrenaline(Card):
    def __init__(self):
        super().__init__("肾上腺素", CardType.SKILL, 0, "获得1点能量，抽2张牌")
        self.energy_gain = 1
        self.draw_count = 2

    def play(self, player, target):
        player.energy += self.energy_gain
        player.draw(self.draw_count)
        print(f"⚡ {player.name} 获得 {self.energy_gain} 点能量，抽 {self.draw_count} 张牌")

    def upgrade(self):
        self.upgraded = True
        self.description = "获得2点能量，抽2张牌"
        self.energy_gain = 2


# ============ 抽牌牌 ============
class QuickDraw(Card):
    def __init__(self):
        super().__init__("速攻", CardType.SKILL, 0, "抽2张牌")
        self.draw_count = 2

    def play(self, player, target):
        player.draw(self.draw_count)
        print(f"📤 {player.name} 抽了 {self.draw_count} 张牌")

    def upgrade(self):
        self.upgraded = True
        self.description = "抽3张牌"
        self.draw_count = 3


# ============ 特殊牌 ============
class ComboStrike(Card):
    def __init__(self):
        super().__init__("连击", CardType.ATTACK, 1, "造成4点伤害，本回合每打出过1张牌额外+3伤害")
        self.damage = 4
        self.bonus = 3

    def play(self, player, target):
        base = self.damage + player.strength + player.focus_damage
        bonus = player.cards_played_this_turn * self.bonus
        total = base + bonus
        actual = target.take_damage(total)
        print(f"⚔️ {player.name} 造成 {actual} 点伤害 (本回合已出{player.cards_played_this_turn}张牌)")

    def upgrade(self):
        self.upgraded = True
        self.description = "造成6点伤害，每打出过1张牌额外+4伤害"
        self.damage = 6
        self.bonus = 4


class Sacrifice(Card):
    def __init__(self):
        super().__init__("牺牲", CardType.ATTACK, 0, "失去5点生命，造成20点伤害，消耗")
        self.is_exhausted = True
        self.hp_loss = 5
        self.damage = 20

    def play(self, player, target):
        player.take_damage(self.hp_loss)
        damage = self.damage + player.strength + player.focus_damage
        actual = target.take_damage(damage)
        print(f"💀 {player.name} 失去{self.hp_loss}点生命，造成 {actual} 点伤害")

    def upgrade(self):
        self.upgraded = True
        self.description = "失去3点生命，造成25点伤害，消耗"
        self.hp_loss = 3
        self.damage = 25


class ElementalFusion(Card):
    def __init__(self):
        super().__init__("元素融合", CardType.ATTACK, 2, "造成4点伤害，施加2层中毒，2层烧伤")
        self.damage = 4
        self.poison = 2
        self.burn = 2

    def play(self, player, target):
        damage = self.damage + player.strength + player.focus_damage
        actual = target.take_damage(damage)
        target.apply_poison(self.poison)
        target.apply_burn(self.burn)
        print(f"⚔️ {player.name} 造成 {actual} 点伤害，施加{self.poison}层中毒和{self.burn}层烧伤")

    def upgrade(self):
        self.upgraded = True
        self.description = "造成6点伤害，施加3层中毒，3层烧伤"
        self.damage = 6
        self.poison = 3
        self.burn = 3


# ============ 圣骑士专属牌 ============
class ShieldStrike(Card):
    def __init__(self):
        super().__init__("圣盾打击", CardType.ATTACK, 2, "造成格挡值×1.5的伤害")
        self.block_multiplier = 1.5

    def play(self, player, target):
        base = max(5, int(player.block * self.block_multiplier))
        damage = base + player.strength
        actual = target.take_damage(damage)
        print(f"🛡️ {player.name} 用圣盾打击造成 {actual} 点伤害 (基于格挡{player.block})")

    def upgrade(self):
        self.upgraded = True
        self.description = "造成格挡值×2的伤害"
        self.block_multiplier = 2


# ============ 刺客牌 ============
class BleedCut(Card):
    def __init__(self):
        super().__init__("割裂", CardType.ATTACK, 1, "造成5点伤害，施加3层流血")
        self.damage = 5
        self.bleed = 3

    def play(self, player, target):
        actual = target.take_damage(self.damage + player.strength + player.focus_damage)
        target.apply_bleed(self.bleed)
        print(f"🩸 {player.name} 造成 {actual} 点伤害，施加 {self.bleed} 层流血")

    def upgrade(self):
        self.upgraded = True
        self.description = "造成7点伤害，施加4层流血"
        self.damage = 7
        self.bleed = 4


class Backstab(Card):
    def __init__(self):
        super().__init__("背刺", CardType.ATTACK, 0, "造成6点伤害，本回合每出过1张牌+2伤害")
        self.damage = 6
        self.bonus = 2

    def play(self, player, target):
        total = self.damage + player.cards_played_this_turn * self.bonus + player.strength + player.focus_damage
        actual = target.take_damage(total)
        print(f"🗡️ 背刺造成 {actual} 点伤害")

    def upgrade(self):
        self.upgraded = True
        self.description = "造成8点伤害，本回合每出过1张牌+3伤害"
        self.damage = 8
        self.bonus = 3


class ShadowDiscard(Card):
    def __init__(self):
        super().__init__("影遁", CardType.SKILL, 0, "弃掉1张手牌，获得1点能量和4点格挡")
        self.block = 4
        self.energy_gain = 1

    def play(self, player, target):
        discarded = None
        for card in list(player.hand):
            if card is not self:
                discarded = card
                player.hand.remove(card)
                player.discard_pile.append(card)
                break
        player.energy += self.energy_gain
        player.block += self.block + player.focus_block
        msg = f"，弃掉 {discarded.name}" if discarded else ""
        print(f"🌘 影遁获得 {self.energy_gain} 点能量和 {self.block} 点格挡{msg}")

    def upgrade(self):
        self.upgraded = True
        self.description = "弃掉1张手牌，获得2点能量和6点格挡"
        self.block = 6
        self.energy_gain = 2


# ============ 牧师牌 ============
class HolySmite(Card):
    def __init__(self):
        super().__init__("圣光惩击", CardType.ATTACK, 1, "造成6点伤害，回复2点生命")
        self.damage = 6
        self.heal_amount = 2

    def play(self, player, target):
        actual = target.take_damage(self.damage + player.strength + player.focus_damage)
        healed = player.heal(self.heal_amount)
        print(f"✨ 圣光惩击造成 {actual} 点伤害，回复 {healed} 点生命")

    def upgrade(self):
        self.upgraded = True
        self.description = "造成9点伤害，回复3点生命"
        self.damage = 9
        self.heal_amount = 3


class Blessing(Card):
    def __init__(self):
        super().__init__("祝福", CardType.POWER, 1, "每回合开始获得3点格挡")
        self.blessing = 3

    def play(self, player, target):
        player.blessing += self.blessing
        print(f"✨ {player.name} 获得祝福，每回合 +{self.blessing} 格挡")

    def upgrade(self):
        self.upgraded = True
        self.description = "每回合开始获得5点格挡"
        self.blessing = 5


class Purify(Card):
    def __init__(self):
        super().__init__("净化祷言", CardType.SKILL, 1, "清除负面状态，回复5点生命")
        self.heal_amount = 5

    def play(self, player, target):
        player.poison = player.burn = player.bleed = player.weak = player.vulnerable = player.curse = 0
        healed = player.heal(self.heal_amount)
        print(f"🙏 净化全部负面状态，回复 {healed} 点生命")

    def upgrade(self):
        self.upgraded = True
        self.description = "清除负面状态，回复8点生命"
        self.heal_amount = 8


class ThornAura(Card):
    def __init__(self):
        super().__init__("荆棘光环", CardType.POWER, 1, "获得3点反伤")
        self.thorns = 3

    def play(self, player, target):
        player.thorns += self.thorns
        print(f"🌿 {player.name} 获得 {self.thorns} 点反伤")

    def upgrade(self):
        self.upgraded = True
        self.description = "获得5点反伤"
        self.thorns = 5


# ============ 机械师牌 ============
class DeployTurret(Card):
    def __init__(self):
        super().__init__("部署炮台", CardType.POWER, 2, "每回合开始对首个敌人造成4点伤害")
        self.turret = 4

    def play(self, player, target):
        player.turret_damage += self.turret
        print(f"🤖 部署炮台，每回合自动造成 {self.turret} 点伤害")

    def upgrade(self):
        self.upgraded = True
        self.description = "每回合开始对首个敌人造成6点伤害"
        self.turret = 6


class EnergyBattery(Card):
    def __init__(self):
        super().__init__("能量电池", CardType.SKILL, 0, "获得2点能量")
        self.energy_gain = 2

    def play(self, player, target):
        player.energy += self.energy_gain
        print(f"🔋 获得 {self.energy_gain} 点能量")

    def upgrade(self):
        self.upgraded = True
        self.description = "获得3点能量"
        self.energy_gain = 3


class ModuleUpgrade(Card):
    def __init__(self):
        super().__init__("模块升级", CardType.POWER, 1, "获得1点力量和1点格挡加成")
        self.amount = 1

    def play(self, player, target):
        player.strength += self.amount
        player.focus_block += self.amount
        print(f"⚙️ 模块升级：力量 +{self.amount}，格挡加成 +{self.amount}")

    def upgrade(self):
        self.upgraded = True
        self.description = "获得2点力量和2点格挡加成"
        self.amount = 2


# ============ 亡灵法师牌 ============
class RaiseSkeleton(Card):
    def __init__(self):
        super().__init__("召唤骷髅", CardType.POWER, 1, "召唤1个骷髅，每回合自动造成3点伤害")
        self.count = 1

    def play(self, player, target):
        player.skeletons += self.count
        print(f"💀 召唤 {self.count} 个骷髅仆从（当前{player.skeletons}）")

    def upgrade(self):
        self.upgraded = True
        self.description = "召唤2个骷髅，每个每回合自动造成3点伤害"
        self.count = 2


class LifeTap(Card):
    def __init__(self):
        super().__init__("生命汲取", CardType.SKILL, 0, "失去4点生命，获得2点能量，抽1张牌")
        self.hp_loss = 4
        self.energy_gain = 2

    def play(self, player, target):
        player.take_damage(self.hp_loss)
        player.energy += self.energy_gain
        draw_count = 2 if self.upgraded else 1
        player.draw(draw_count)

    def upgrade(self):
        self.upgraded = True
        self.description = "失去3点生命，获得2点能量，抽2张牌"
        self.hp_loss = 3


class CurseBolt(Card):
    def __init__(self):
        super().__init__("诅咒箭", CardType.ATTACK, 1, "造成5点伤害，施加2层诅咒和1层虚弱")
        self.damage = 5
        self.curse = 2

    def play(self, player, target):
        actual = target.take_damage(self.damage + player.strength + player.focus_damage)
        target.apply_curse(self.curse)
        target.apply_weak(1)
        print(f"🌑 诅咒箭造成 {actual} 点伤害，施加 {self.curse} 层诅咒")

    def upgrade(self):
        self.upgraded = True
        self.description = "造成8点伤害，施加3层诅咒和1层虚弱"
        self.damage = 8
        self.curse = 3


# ============ 炼金术士牌 ============
class VenomFlask(Card):
    def __init__(self):
        super().__init__("毒液瓶", CardType.SKILL, 1, "施加4层中毒和1层虚弱")
        self.poison = 4

    def play(self, player, target):
        target.apply_poison(self.poison)
        target.apply_weak(1)
        print(f"⚗️ 毒液瓶施加 {self.poison} 层中毒和1层虚弱")

    def upgrade(self):
        self.upgraded = True
        self.description = "施加6层中毒和2层虚弱"
        self.poison = 6


class Mutagen(Card):
    def __init__(self):
        super().__init__("突变药剂", CardType.SKILL, 1, "随机获得力量、格挡或治疗")
        self.amount = 6

    def play(self, player, target):
        import random
        effect = random.choice(["strength", "block", "heal"])
        if effect == "strength":
            player.strength += 2
            print("🧪 突变药剂：获得2点力量")
        elif effect == "block":
            player.block += self.amount
            print(f"🧪 突变药剂：获得{self.amount}点格挡")
        else:
            healed = player.heal(self.amount)
            print(f"🧪 突变药剂：回复{healed}点生命")

    def upgrade(self):
        self.upgraded = True
        self.description = "随机获得更强的力量、格挡或治疗"
        self.amount = 9


class Transmute(Card):
    def __init__(self):
        super().__init__("状态转换", CardType.SKILL, 1, "将目标烧伤转化为等量中毒，若无烧伤则施加3毒")

    def play(self, player, target):
        if target.burn > 0:
            amount = target.burn * (2 if self.upgraded else 1)
            target.burn = 0
            target.apply_poison(amount)
        else:
            amount = 5 if self.upgraded else 3
            target.apply_poison(amount)

    def upgrade(self):
        self.upgraded = True
        self.description = "将目标烧伤转化为双倍中毒，若无烧伤则施加5毒"


class CurseCard(Card):
    def __init__(self):
        super().__init__("诅咒", CardType.SKILL, 99, "无法打出，占据手牌")

    def play(self, player, target):
        print("🌑 诅咒无法被打出")
