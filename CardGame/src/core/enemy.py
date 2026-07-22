from .character import Character
import random
from typing import List, Optional


class Enemy(Character):
    """敌人类"""

    def __init__(self, name: str, max_hp: int, damage: int = 8):
        super().__init__(name, max_hp)
        self.base_damage = damage
        self.intent = "攻击"
        self.intent_value = damage
        self.turn_count = 0

    def choose_intent(self):
        """选择行动意图"""
        self.turn_count += 1

        if self.name == "毒沼史莱姆":
            intents = ["毒液", "攻击", "防御"]
        elif self.name == "熔岩犬":
            intents = ["灼咬", "攻击", "强化"]
        elif self.name == "镜像怪":
            intents = ["镜像", "攻击", "防御"]
        elif self.name == "护卫队长":
            intents = ["守护", "攻击", "强化"]
        elif self.name == "诅咒法师":
            intents = ["诅咒", "攻击", "虚弱"]
        # 更丰富的AI逻辑
        elif self.hp < self.max_hp * 0.3:  # 低血量时更容易防御
            intents = ["攻击", "防御", "防御", "强化"]
        elif self.strength > 5:  # 力量高时更倾向攻击
            intents = ["攻击", "攻击", "攻击", "防御"]
        else:
            intents = ["攻击", "攻击", "防御", "强化"]

        self.intent = random.choice(intents)
        self.intent_value = self.preview_intent_value()
        return self.intent

    def preview_intent_value(self) -> int:
        """预估当前意图的数值，用于玩家回合提前展示"""
        if self.intent == "攻击":
            damage = self.base_damage + self.strength
            if self.weak > 0:
                damage = int(damage * 0.75)
            return max(1, damage)
        if self.intent in ("毒液", "诅咒", "虚弱"):
            return 2
        if self.intent == "灼咬":
            return max(1, self.base_damage + self.strength)
        if self.intent == "镜像":
            return max(1, self.base_damage + self.strength)
        if self.intent == "守护":
            return 10 + self.strength
        if self.intent == "防御":
            return 8 + self.strength
        if self.intent == "强化":
            return 2
        return 0

    def get_intent_text(self) -> str:
        """给前端展示的详细意图文案"""
        value = self.preview_intent_value()
        if self.intent == "攻击":
            return f"攻击：{value}伤害"
        if self.intent == "防御":
            return f"防御：获得{value}格挡"
        if self.intent == "强化":
            return f"强化：力量+{value}"
        if self.intent == "毒液":
            return f"毒液：{max(1, self.base_damage // 2)}伤害 + 2中毒"
        if self.intent == "灼咬":
            return f"灼咬：{value}伤害 + 2烧伤"
        if self.intent == "镜像":
            return f"镜像：{value}伤害 + 1易伤"
        if self.intent == "守护":
            return f"守护：全体+{value}格挡"
        if self.intent == "诅咒":
            return "诅咒：塞1张诅咒 + 2诅咒"
        if self.intent == "虚弱":
            return "虚弱：施加2层虚弱"
        return self.intent

    def get_intent_desc(self) -> str:
        """意图 tooltip 说明"""
        descriptions = {
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
        return descriptions.get(self.intent, "")

    def take_turn(self, target: Character):
        """执行回合行动"""
        if not self.is_alive():
            return

        print(f"\n🤖 {self.name} 的行动: {self.intent}")

        # 虚弱减少攻击伤害
        damage_multiplier = 0.75 if self.weak > 0 else 1.0

        if self.intent == "攻击":
            # 基础伤害 + 力量加成。伤害不再随机，确保提前显示的意图可信。
            damage = self.base_damage + self.strength
            if damage < 1:
                damage = 1

            # 应用虚弱效果
            if self.weak > 0:
                damage = int(damage * 0.75)
                print(f"💫 {self.name} 因虚弱伤害减少25%")

            actual = target.take_damage(damage)
            print(f"⚔️ {self.name} 对 {target.name} 造成 {actual} 点伤害")
            self._apply_thorns(target)

        elif self.intent == "毒液":
            target.apply_poison(2)
            actual = target.take_damage(max(1, self.base_damage // 2))
            print(f"☠️ {self.name} 喷吐毒液，造成 {actual} 点伤害并施加2层中毒")

        elif self.intent == "灼咬":
            damage = self.base_damage + self.strength
            if self.weak > 0:
                damage = int(damage * 0.75)
            actual = target.take_damage(max(1, damage))
            target.apply_burn(2)
            print(f"🔥 {self.name} 灼咬造成 {actual} 点伤害并施加2层烧伤")
            self._apply_thorns(target)

        elif self.intent == "镜像":
            copied = getattr(target, "last_played_card_name", None)
            damage = self.base_damage + self.strength
            actual = target.take_damage(max(1, damage))
            if copied:
                target.apply_vulnerable(1)
                print(f"🪞 {self.name} 模仿了「{copied}」，造成 {actual} 点伤害并施加1层易伤")
            else:
                print(f"🪞 {self.name} 尚无可模仿卡牌，造成 {actual} 点伤害")
            self._apply_thorns(target)

        elif self.intent == "守护":
            block = 10 + self.strength
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
            target.apply_curse(2)
            print(f"🌑 {self.name} 将一张诅咒塞入弃牌堆，并施加2层诅咒")

        elif self.intent == "虚弱":
            target.apply_weak(2)
            print(f"💫 {self.name} 施加2层虚弱")

        elif self.intent == "防御":
            block = 8 + self.strength
            self.block += block
            print(f"🛡️ {self.name} 获得 {block} 点格挡")

        elif self.intent == "强化":
            self.strength += 2
            print(f"💪 {self.name} 获得 2 点力量 (当前力量: {self.strength})")

        # 打印状态
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
