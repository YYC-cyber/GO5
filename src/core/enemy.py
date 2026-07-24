"""
敌人模块 — 数据驱动的 AI 意图系统
"""
import random
from typing import List, Optional
from .character import Character
from src.config import (
    WEAK_DAMAGE_MULTIPLIER,
    INTENT_DEFEND_BLOCK,
    INTENT_STRENGTHEN_AMOUNT,
    INTENT_GUARD_BLOCK,
    INTENT_POISON_AMOUNT,
    INTENT_BURN_AMOUNT,
    INTENT_WEAK_AMOUNT,
    INTENT_CURSE_AMOUNT,
    INTENT_VULNERABLE_AMOUNT,
    INTENT_POISON_DAMAGE_RATIO,
    INTENT_DESCRIPTIONS,
    get_enemy_intent_pool,
)


class Enemy(Character):
    """敌人类 — 数据驱动的 AI 系统"""

    def __init__(self, name: str, max_hp: int, damage: int = 8):
        super().__init__(name, max_hp)
        self.base_damage = damage
        self.intent = "攻击"
        self.intent_value = damage
        self.turn_count = 0

    def choose_intent(self):
        """选择行动意图 — 从配置中获取意图池"""
        self.turn_count += 1
        pool = get_enemy_intent_pool(
            self.name,
            self.hp / self.max_hp,
            self.strength,
        )
        self.intent = random.choice(pool)
        self.intent_value = self.preview_intent_value()
        return self.intent

    def preview_intent_value(self) -> int:
        """预估当前意图的数值，用于玩家回合提前展示"""
        if self.intent == "攻击":
            damage = self.base_damage + self.strength
            if self.weak > 0:
                damage = int(damage * WEAK_DAMAGE_MULTIPLIER)
            return max(1, damage)
        if self.intent in ("毒液", "诅咒", "虚弱"):
            return INTENT_POISON_AMOUNT
        if self.intent == "灼咬":
            return max(1, self.base_damage + self.strength)
        if self.intent == "镜像":
            return max(1, self.base_damage + self.strength)
        if self.intent == "守护":
            return INTENT_GUARD_BLOCK + self.strength
        if self.intent == "防御":
            return INTENT_DEFEND_BLOCK + self.strength
        if self.intent == "强化":
            return INTENT_STRENGTHEN_AMOUNT
        return 0

    def get_intent_text(self) -> str:
        """给前端展示的详细意图文案"""
        value = self.preview_intent_value()
        text_map = {
            "攻击": f"攻击：{value}伤害",
            "防御": f"防御：获得{value}格挡",
            "强化": f"强化：力量+{value}",
            "毒液": f"毒液：{max(1, int(self.base_damage * INTENT_POISON_DAMAGE_RATIO))}伤害 + {INTENT_POISON_AMOUNT}中毒",
            "灼咬": f"灼咬：{value}伤害 + {INTENT_BURN_AMOUNT}烧伤",
            "镜像": f"镜像：{value}伤害 + {INTENT_VULNERABLE_AMOUNT}易伤",
            "守护": f"守护：全体+{value}格挡",
            "诅咒": f"诅咒：塞1张诅咒 + {INTENT_CURSE_AMOUNT}诅咒",
            "虚弱": f"虚弱：施加{INTENT_WEAK_AMOUNT}层虚弱",
        }
        return text_map.get(self.intent, self.intent)

    def get_intent_desc(self) -> str:
        """意图 tooltip 说明"""
        return INTENT_DESCRIPTIONS.get(self.intent, "")

    def take_turn(self, target: Character):
        """执行回合行动"""
        if not self.is_alive():
            return

        print(f"\n🤖 {self.name} 的行动: {self.intent}")

        if self.intent == "攻击":
            damage = self.base_damage + self.strength
            if damage < 1:
                damage = 1
            if self.weak > 0:
                damage = int(damage * WEAK_DAMAGE_MULTIPLIER)
                print(f"💫 {self.name} 因虚弱伤害减少25%")
            actual = target.take_damage(damage)
            print(f"⚔️ {self.name} 对 {target.name} 造成 {actual} 点伤害")
            self._apply_thorns(target)

        elif self.intent == "毒液":
            target.apply_poison(INTENT_POISON_AMOUNT)
            actual = target.take_damage(max(1, int(self.base_damage * INTENT_POISON_DAMAGE_RATIO)))
            print(f"☠️ {self.name} 喷吐毒液，造成 {actual} 点伤害并施加{INTENT_POISON_AMOUNT}层中毒")

        elif self.intent == "灼咬":
            damage = self.base_damage + self.strength
            if self.weak > 0:
                damage = int(damage * WEAK_DAMAGE_MULTIPLIER)
            actual = target.take_damage(max(1, damage))
            target.apply_burn(INTENT_BURN_AMOUNT)
            print(f"🔥 {self.name} 灼咬造成 {actual} 点伤害并施加{INTENT_BURN_AMOUNT}层烧伤")
            self._apply_thorns(target)

        elif self.intent == "镜像":
            copied = getattr(target, "last_played_card_name", None)
            damage = self.base_damage + self.strength
            actual = target.take_damage(max(1, damage))
            if copied:
                target.apply_vulnerable(INTENT_VULNERABLE_AMOUNT)
                print(f"🪞 {self.name} 模仿了「{copied}」，造成 {actual} 点伤害并施加{INTENT_VULNERABLE_AMOUNT}层易伤")
            else:
                print(f"🪞 {self.name} 尚无可模仿卡牌，造成 {actual} 点伤害")
            self._apply_thorns(target)

        elif self.intent == "守护":
            block = INTENT_GUARD_BLOCK + self.strength
            if hasattr(self, "allies"):
                for ally in self.allies:
                    if ally.is_alive():
                        ally.block += block
                print(f"🛡️ {self.name} 为全体敌人提供 {block} 点格挡")
            else:
                self.block += block
                print(f"🛡️ {self.name} 获得 {block} 点格挡")

        elif self.intent == "诅咒":
            from .card import CurseCard
            target.discard_pile.append(CurseCard())
            target.apply_curse(INTENT_CURSE_AMOUNT)
            print(f"🌑 {self.name} 将一张诅咒塞入弃牌堆，并施加{INTENT_CURSE_AMOUNT}层诅咒")

        elif self.intent == "虚弱":
            target.apply_weak(INTENT_WEAK_AMOUNT)
            print(f"💫 {self.name} 施加{INTENT_WEAK_AMOUNT}层虚弱")

        elif self.intent == "防御":
            block = INTENT_DEFEND_BLOCK + self.strength
            self.block += block
            print(f"🛡️ {self.name} 获得 {block} 点格挡")

        elif self.intent == "强化":
            self.strength += INTENT_STRENGTHEN_AMOUNT
            print(f"💪 {self.name} 获得 {INTENT_STRENGTHEN_AMOUNT} 点力量 (当前力量: {self.strength})")

        print(f"📊 {self}")

    def _apply_thorns(self, target: Character):
        if getattr(target, "thorns", 0) > 0 and self.is_alive():
            actual = self.take_damage(target.thorns)
            print(f"🌿 {target.name} 的反伤对 {self.name} 造成 {actual} 点伤害")

    def __str__(self):
        """显示敌人状态，包含格挡"""
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
        if hasattr(self, 'intent'):
            status += f" [意图:{self.intent}]"
        return status