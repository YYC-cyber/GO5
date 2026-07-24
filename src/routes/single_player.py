"""
单人模式路由
单场战斗 + 自定义模式
"""
from flask import Blueprint, jsonify, request

import src.state as state
from src.core.player import Player, CHARACTER_TEMPLATES
from src.core.enemy import Enemy
from src.games.web_battle import WebBattle

single_player_bp = Blueprint('single_player', __name__)


def _make_enemies(mode: str):
    """根据模式创建敌人列表"""
    enemies_map = {
        "normal": [Enemy("哥布林", 42, 8), Enemy("毒沼史莱姆", 48, 7)],
        "elite":  [Enemy("熔岩犬", 62, 12), Enemy("护卫队长", 70, 9)],
        "boss":   [Enemy("诅咒法师", 95, 13), Enemy("镜像怪", 75, 11)],
    }
    result = enemies_map.get(mode, enemies_map["normal"])
    return [Enemy(e.name, e.max_hp, e.base_damage) for e in result]


@single_player_bp.route('/api/new-game', methods=['POST'])
def new_game():
    """开始单场战斗"""
    data = request.get_json() or {}
    mode = data.get("mode", "normal")
    character = data.get("character", "warrior")

    tmpl = CHARACTER_TEMPLATES.get(character, CHARACTER_TEMPLATES["warrior"])
    player = Player(tmpl["name"], tmpl["hp"], character_id=character)
    enemies = _make_enemies(mode)

    state.current_level = None
    state.current_battle = WebBattle(player, enemies)
    state.current_battle.start()
    state.game_mode = "single"

    return jsonify({"success": True, "state": state.get_state()})


@single_player_bp.route('/api/start-custom', methods=['POST'])
def start_custom():
    """自定义模式：用户配置敌人参数"""
    data = request.get_json() or {}
    enemies_config = data.get("enemies", [])
    player_hp = data.get("player_hp", 80)
    character = data.get("character", "warrior")
    base_attack = data.get("base_attack", 0)
    base_defense = data.get("base_defense", 0)

    if not enemies_config:
        return jsonify({"success": False, "error": "至少需要1个敌人"}), 400
    if len(enemies_config) > 5:
        return jsonify({"success": False, "error": "最多5个敌人"}), 400

    enemies = []
    for cfg in enemies_config:
        name = cfg.get("name", "哥布林")
        hp = max(1, min(999, int(cfg.get("hp", 30))))
        dmg = max(1, min(99, int(cfg.get("damage", 6))))
        enemies.append(Enemy(name, hp, dmg))

    template = CHARACTER_TEMPLATES.get(character, CHARACTER_TEMPLATES["warrior"])
    player_name = template["name"]
    player = Player(player_name, max_hp=max(10, min(999, int(player_hp))),
                    character_id=character)
    player.strength = max(0, min(50, int(base_attack)))
    player.focus_block = max(0, min(50, int(base_defense)))

    state.current_level = None
    state.current_battle = WebBattle(player, enemies)
    state.current_battle.start()
    state.game_mode = "custom"

    return jsonify({"success": True, "state": state.get_state()})
