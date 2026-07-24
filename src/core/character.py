from typing import List, Optional


class Character:
    """角色基类"""

    def __init__(self, name: str, max_hp: int = 80):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.block = 0
        self.strength = 0

        # 状态
        self.poison = 0
        self.burn = 0
        self.bleed = 0
        self.weak = 0
        self.vulnerable = 0
        self.curse = 0

        # 卡牌相关
        self.deck: List = []
        self.hand: List = []
        self.discard_pile: List = []

        # 能力标记
        self.iron_wall = False
        self.counter = False
        self.thorns = 0

        # 加成
        self.focus_damage = 0
        self.focus_block = 0
        self.blessing = 0

    def take_damage(self, damage: int) -> int:
        """承受伤害，返回实际受到的伤害"""
        if damage <= 0:
            return 0

        # 易伤增加伤害
        if self.vulnerable > 0:
            damage = int(damage * 1.5)
            print(f"💥 {self.name} 易伤增加50%伤害")
        if self.curse > 0:
            damage += self.curse
            print(f"🌑 {self.name} 因诅咒额外受到 {self.curse} 点伤害")

        # 格挡抵消伤害
        actual_damage = damage
        if self.block > 0:
            absorbed = min(self.block, damage)
            self.block -= absorbed
            actual_damage = damage - absorbed
            print(f"🛡️ {self.name} 用格挡抵消了 {absorbed} 点伤害，剩余格挡 {self.block}")

        self.hp -= actual_damage
        if self.hp < 0:
            self.hp = 0

        print(f"💔 {self.name} 受到 {actual_damage} 点伤害")
        return actual_damage

    def heal(self, amount: int) -> int:
        """治疗，返回实际回复量"""
        old_hp = self.hp
        self.hp = min(self.hp + amount, self.max_hp)
        healed = self.hp - old_hp
        if healed > 0:
            print(f"💚 {self.name} 回复了 {healed} 点生命")
        return healed

    def apply_poison(self, amount: int):
        self.poison += amount
        print(f"☠️ {self.name} 中毒 +{amount} (当前: {self.poison})")

    def apply_burn(self, amount: int):
        self.burn += amount
        print(f"🔥 {self.name} 烧伤 +{amount} (当前: {self.burn})")

    def apply_bleed(self, amount: int):
        self.bleed += amount
        print(f"🩸 {self.name} 流血 +{amount} (当前: {self.bleed})")

    def apply_weak(self, amount: int):
        self.weak += amount
        print(f"💫 {self.name} 虚弱 +{amount} (当前: {self.weak})")

    def apply_vulnerable(self, amount: int):
        self.vulnerable += amount
        print(f"💥 {self.name} 易伤 +{amount} (当前: {self.vulnerable})")

    def apply_curse(self, amount: int):
        self.curse += amount
        print(f"🌑 {self.name} 诅咒 +{amount} (当前: {self.curse})")

    def end_turn(self):
        """回合结束时的状态结算"""
        print(f"\n📊 {self.name} 回合结束结算:")

        # 中毒结算
        if self.poison > 0:
            damage = self.poison
            print(f"☠️ {self.name} 中毒发作，受到 {damage} 点伤害")
            self.take_damage(damage)
            self.poison = max(0, self.poison - 1)

        # 烧伤结算
        if self.burn > 0:
            damage = self.burn
            print(f"🔥 {self.name} 烧伤发作，受到 {damage} 点伤害")
            self.take_damage(damage)
            self.burn = max(0, self.burn - 1)

        # 流血结算：每回合按层数受伤，衰减更慢
        if self.bleed > 0:
            damage = self.bleed
            print(f"🩸 {self.name} 流血发作，受到 {damage} 点伤害")
            self.take_damage(damage)
            self.bleed = max(0, self.bleed - 1)

        # 状态递减
        if self.weak > 0:
            old = self.weak
            self.weak -= 1
            print(f"💫 {self.name} 虚弱从 {old} 减至 {self.weak}")
        if self.vulnerable > 0:
            old = self.vulnerable
            self.vulnerable -= 1
            print(f"💥 {self.name} 易伤从 {old} 减至 {self.vulnerable}")
        if self.curse > 0:
            old = self.curse
            self.curse -= 1
            print(f"🌑 {self.name} 诅咒从 {old} 减至 {self.curse}")

        # 清空格挡（圣骑士等拥有保留格挡的角色除外）
        if self.block > 0:
            if getattr(self, "block_persist", False):
                print(f"🛡️ {self.name} 保留了 {self.block} 点格挡")
            else:
                print(f"🛡️ {self.name} 的格挡消失 ({self.block}点)")
                self.block = 0

    def is_alive(self) -> bool:
        return self.hp > 0

    def __str__(self):
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
