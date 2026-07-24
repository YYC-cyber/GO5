"""
Web战斗系统 - 捕获print输出并通过API返回状态
"""
import io
import random
from contextlib import redirect_stdout
from typing import List, Optional, Dict, Any

from src.core.player import Player, CHARACTER_TEMPLATES
from src.core.enemy import Enemy
import src.state as _state


class WebBattle:
    """Web兼容的战斗控制器，收集消息而非直接打印"""

    def __init__(self, player: Player, enemies: List[Enemy]):
        self.player = player
        self.enemies = enemies
        self.player.enemies = enemies
        for enemy in self.enemies:
            enemy.allies = self.enemies
        self.turn = 0
        self.game_over = False
        self.winner: Optional[str] = None
        self.messages: List[str] = []
        self._started = False
        self._state_dirty = True
        self._state_cache = None

    # ---- 内部辅助 ----

    def _capture(self, func, *args, **kwargs):
        """执行函数并捕获其所有print输出"""
        f = io.StringIO()
        with redirect_stdout(f):
            result = func(*args, **kwargs)
        output = f.getvalue()
        lines = [line.strip() for line in output.split('\n') if line.strip()]
        self.messages.extend(lines)
        return result

    def _capture_call(self, fn, *args, **kwargs):
        """捕获单个调用的输出"""
        f = io.StringIO()
        with redirect_stdout(f):
            fn(*args, **kwargs)
        output = f.getvalue()
        lines = [line.strip() for line in output.split('\n') if line.strip()]
        self.messages.extend(lines)

    def _check_battle_end(self) -> bool:
        """检查战斗是否结束"""
        if not self.player.is_alive():
            self.game_over = True
            self.winner = "enemy"
            self.messages.append("💀 你被击败了...")
            return True
        if not any(e.is_alive() for e in self.enemies):
            self.game_over = True
            self.winner = "player"
            self.messages.append("🎉 胜利！所有敌人都被击败了！")
            return True
        return False

    # ---- 公共API ----

    def start(self):
        """开始战斗"""
        self.turn = 0
        self.messages.append("⚔️ 战斗开始！")
        self._start_player_turn()
        self._mark_dirty()

    def _mark_dirty(self):
        """标记状态已变更，下次 get_state() 时重新构建"""
        self._state_dirty = True

    def get_state(self) -> Dict[str, Any]:
        """获取完整游戏状态（带缓存，仅脏时重建）"""
        if self._state_dirty or self._state_cache is None:
            self._state_cache = self._build_state()
            self._state_dirty = False
        return self._state_cache

    def _build_state(self) -> Dict[str, Any]:
        """构建完整游戏状态"""
        return {
            "turn": self.turn,
            "game_over": self.game_over,
            "winner": self.winner,
            "mode": getattr(_state, 'game_mode', 'single'),
            "player": self._player_to_dict(),
            "enemies": [self._enemy_to_dict(e) for e in self.enemies],
            "hand": self._hand_to_dict(),
            "messages": self.messages[-50:],  # 只保留最近50条
            "deck_count": len(self.player.deck),
            "discard_count": len(self.player.discard_pile),
            "deck_cards": [self._card_to_dict(card) for card in self.player.deck],
            "discard_cards": [self._card_to_dict(card) for card in self.player.discard_pile],
        }

    def play_card(self, card_index: int, target_index: int) -> Dict[str, Any]:
        """打出一张牌，返回操作结果"""
        if self.game_over:
            return {"success": False, "error": "游戏已结束"}

        # 验证卡牌索引
        if card_index < 0 or card_index >= len(self.player.hand):
            return {"success": False, "error": "无效的卡牌编号"}

        card = self.player.hand[card_index]

        # 自我目标牌：跳过目标有效性检查，自动选一个活着的敌人作为占位
        if card.name in self.SELF_TARGET_NAMES:
            alive = [i for i, e in enumerate(self.enemies) if e.is_alive()]
            target = self.enemies[alive[0]] if alive else self.enemies[0]
        else:
            # 验证目标是否有效
            alive_enemies = [i for i, e in enumerate(self.enemies) if e.is_alive()]
            if target_index not in alive_enemies:
                return {"success": False, "error": "目标已死亡或无效"}
            target = self.enemies[target_index]

        # 捕获play_card输出的所有信息
        f = io.StringIO()
        with redirect_stdout(f):
            success = self.player.play_card(card, target)
        output = f.getvalue()
        lines = [line.strip() for line in output.split('\n') if line.strip()]
        self.messages.extend(lines)

        if not success:
            return {"success": False, "error": "出牌失败（能量不足或条件不满足）"}

        # 检查战斗是否结束
        ended = self._check_battle_end()
        self._mark_dirty()
        return {"success": True, "battle_ended": ended, "error": None}

    def end_turn(self) -> Dict[str, Any]:
        """结束玩家回合，执行敌人回合，然后开始新回合"""
        if self.game_over:
            return {"success": False, "error": "游戏已结束"}

        self.messages.append("⏭️ 回合结束")

        # 玩家回合结束结算
        self._capture_call(self.player.end_turn)

        if self._check_battle_end():
            self._mark_dirty()
            return {"success": True, "battle_ended": True}

        # 敌人回合
        self._run_enemy_turn()

        if self._check_battle_end():
            self._mark_dirty()
            return {"success": True, "battle_ended": True}

        # 开始新回合
        self._start_player_turn()
        self._mark_dirty()
        return {"success": True, "battle_ended": False}

    def use_skill(self) -> Dict[str, Any]:
        """使用角色专属技能"""
        if self.game_over:
            return {"success": False, "error": "游戏已结束"}

        p = self.player
        char_id = getattr(p, 'character_id', None)
        tmpl = CHARACTER_TEMPLATES.get(char_id, {})
        skill = tmpl.get("skill", {})
        cost = skill.get("cost", 99)
        skill_name = skill.get("name", "")

        if not skill_name:
            return {"success": False, "error": "该角色没有技能"}

        if getattr(p, "skill_used_this_turn", False):
            return {"success": False, "error": "本回合已经使用过技能"}

        if p.energy < cost:
            return {"success": False, "error": f"能量不足，需要{cost}点"}

        # 消耗能量
        p.energy -= cost
        p.skill_used_this_turn = True

        if char_id == 'warrior':
            # 净化: 消除全部负面状态
            old = {'毒': p.poison, '烧伤': p.burn, '虚弱': p.weak, '易伤': p.vulnerable}
            p.poison = 0
            p.burn = 0
            p.weak = 0
            p.vulnerable = 0
            details = ' '.join(f'{k}{v}→0' for k, v in old.items() if v > 0)
            self.messages.append(f"✨ 净化！消除全部负面状态 ({details})")

        elif char_id == 'elf':
            # 回响: 下一张牌释放两次
            p.double_next_card = True
            self.messages.append(f"🔄 回响！下一张打出的牌会释放两次")

        elif char_id == 'wizard':
            # 元素爆发: 对所有敌人造成5点伤害+2毒+2烧伤
            for enemy in self.enemies:
                if enemy.is_alive():
                    dmg = 5
                    actual = enemy.take_damage(dmg)
                    enemy.apply_poison(2)
                    enemy.apply_burn(2)
                    self.messages.append(f"💥 元素爆发对 {enemy.name} 造成 {actual} 伤害+2毒+2烧伤")

        elif char_id == 'paladin':
            # 圣盾是被动，无需主动使用
            self.messages.append(f"🛡️ 圣盾已生效，格挡不会被重置")
            return {"success": True, "message": "被动已生效", "state": self.get_state()}

        elif char_id == 'assassin':
            p.energy += 2
            p.strength += 2
            self.messages.append("🗡️ 暗影爆发！本回合获得2点能量和2点力量")

        elif char_id == 'priest':
            healed = p.heal(8)
            for enemy in self.enemies:
                if enemy.is_alive():
                    actual = enemy.take_damage(4)
                    self.messages.append(f"🙏 神圣新星对 {enemy.name} 造成 {actual} 点伤害")
            self.messages.append(f"🙏 神圣新星回复 {healed} 点生命")

        elif char_id == 'mechanist':
            p.turret_damage += 3
            p.energy += 1
            self.messages.append("⚙️ 超频！炮台伤害+3，并获得1点能量")

        elif char_id == 'necromancer':
            p.skeletons += 1
            healed = p.heal(5)
            self.messages.append(f"💀 亡者复苏！召唤1个骷髅并回复 {healed} 点生命")

        elif char_id == 'alchemist':
            import random
            effect = random.choice(["strength", "block", "heal"])
            if effect == "strength":
                p.strength += 2
                self.messages.append("⚗️ 万能药剂：获得2点力量")
            elif effect == "block":
                p.block += 10
                self.messages.append("⚗️ 万能药剂：获得10点格挡")
            else:
                healed = p.heal(10)
                self.messages.append(f"⚗️ 万能药剂：回复 {healed} 点生命")
            for enemy in self.enemies:
                if enemy.is_alive():
                    enemy.apply_poison(2)
            self.messages.append("⚗️ 万能药剂：所有敌人获得2层中毒")

        self.messages.append(f"✨ 使用技能: {skill_name}")
        self._mark_dirty()
        return {"success": True, "message": f"使用 {skill_name}", "state": self.get_state()}


    # ---- 内部流程 ----

    def _start_player_turn(self):
        """开始玩家回合"""
        self.turn += 1
        self.messages.append(f"── 第 {self.turn} 回合 ──")
        self._capture_call(self.player.start_turn)
        self._prepare_enemy_intents()

    def _prepare_enemy_intents(self):
        """在玩家行动前决定敌人的下一步行动，方便玩家做策略选择"""
        for enemy in self.enemies:
            if enemy.is_alive():
                enemy.choose_intent()
        intents = [
            f"{enemy.name}:{enemy.intent}{enemy.intent_value if enemy.intent_value else ''}"
            for enemy in self.enemies if enemy.is_alive()
        ]
        if intents:
            self.messages.append("🔮 敌人意图: " + " / ".join(intents))

    def _run_enemy_turn(self):
        """执行敌人回合"""
        self.messages.append("🤖 敌人回合")
        for enemy in self.enemies:
            if enemy.is_alive():
                self._capture_call(enemy.take_turn, self.player)
                if not self.player.is_alive():
                    break

        # 结算所有敌人的回合结束效果
        for enemy in self.enemies:
            if enemy.is_alive():
                self._capture_call(enemy.end_turn)

    # ---- 角色头像映射 ----

    CHARACTER_IMAGES = {
        "无畏锋刃": "勇者.svg",
        "共鸣之风": "精灵.svg",
        "灼疫使者": "巫师.svg",
        "裁决之盾": "圣骑士.svg",
        "血色暗影": "刺客.svg",
        "棘光圣者": "牧师.svg",
        "福音齿轮": "机械师.svg",
        "黑血祭师": "亡灵法师.svg",
        "蚀毒秘使": "炼金术士.svg",
        "哥布林": "哥布林.svg",
        "史莱姆": "史莱姆.svg",
        "火焰领主": "火焰领主.svg",
        "寒冰法师": "寒冰法师.svg",
        "暗影领主": "暗影领主.svg",
        "毒沼史莱姆": "毒沼史莱姆.svg",
        "熔岩犬": "熔岩犬.svg",
        "镜像怪": "镜像怪.svg",
        "护卫队长": "护卫队长.svg",
        "诅咒法师": "诅咒法师.svg",
    }

    def _get_image(self, name: str) -> str:
        return self.CHARACTER_IMAGES.get(name, "")

    # ---- 序列化 ----

    def _player_to_dict(self) -> Dict:
        p = self.player
        tmpl = CHARACTER_TEMPLATES.get(getattr(p, 'character_id', None), {})
        skill = tmpl.get("skill", {})
        skill_cost = skill.get("cost", 99)
        return {
            "name": p.name,
            "image": self._get_image(p.name),
            "hp": p.hp,
            "max_hp": p.max_hp,
            "block": p.block,
            "energy": p.energy,
            "max_energy": p.max_energy,
            "strength": p.strength,
            "poison": p.poison,
            "burn": p.burn,
            "bleed": p.bleed,
            "weak": p.weak,
            "vulnerable": p.vulnerable,
            "curse": p.curse,
            "iron_wall": p.iron_wall,
            "counter": p.counter,
            "thorns": p.thorns,
            "blessing": p.blessing,
            "focus_damage": getattr(p, "focus_damage", 0),
            "focus_block": getattr(p, "focus_block", 0),
            "turret_damage": getattr(p, "turret_damage", 0),
            "skeletons": getattr(p, "skeletons", 0),
            "skill_used_this_turn": getattr(p, "skill_used_this_turn", False),
            "double_next_card": getattr(p, "double_next_card", False),
            "block_persist": getattr(p, 'block_persist', False),
            "auto_shield": getattr(p, 'auto_shield', False),
            "skill": {
                "name": skill.get("name", ""),
                "desc": skill.get("desc", ""),
                "cost": skill_cost,
                "icon": skill.get("icon", ""),
                "usable": p.energy >= skill_cost and not self.game_over and not getattr(p, "skill_used_this_turn", False),
            } if skill else None,
        }

    def _enemy_to_dict(self, enemy: Enemy) -> Dict:
        return {
            "name": enemy.name,
            "image": self._get_image(enemy.name),
            "hp": enemy.hp,
            "max_hp": enemy.max_hp,
            "block": enemy.block,
            "strength": enemy.strength,
            "poison": enemy.poison,
            "burn": enemy.burn,
            "bleed": enemy.bleed,
            "weak": enemy.weak,
            "vulnerable": enemy.vulnerable,
            "curse": enemy.curse,
            "intent": getattr(enemy, 'intent', '未知'),
            "intent_value": getattr(enemy, 'intent_value', 0),
            "intent_text": enemy.get_intent_text() if hasattr(enemy, "get_intent_text") else getattr(enemy, 'intent', '未知'),
            "intent_desc": enemy.get_intent_desc() if hasattr(enemy, "get_intent_desc") else "",
            "alive": enemy.is_alive(),
        }

    SELF_TARGET_NAMES = {
        "防御", "堡垒", "铁壁", "反击",
        "小治疗", "复苏",
        "战斗怒吼", "狂暴", "肾上腺素",
        "速攻", "影遁", "祝福", "净化祷言", "荆棘光环",
        "部署炮台", "能量电池", "模块升级", "召唤骷髅", "生命汲取",
        "突变药剂",
    }

    def _hand_to_dict(self) -> List[Dict]:
        return [
            self._card_to_dict(card, index=i, playable=self.player.energy >= card.cost)
            for i, card in enumerate(self.player.hand)
        ]

    def _card_to_dict(self, card, index: int = None, playable: bool = False) -> Dict:
        data = {
            "name": card.name,
            "cost": card.cost,
            "type": card.type.value,
            "description": card.description,
            "upgraded": card.upgraded,
            "playable": playable,
            "self_target": card.name in self.SELF_TARGET_NAMES,
        }
        if index is not None:
            data["index"] = index
        return data
