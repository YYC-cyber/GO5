"""
卡牌游戏 Web 服务器
提供 REST API + 静态文件服务
"""
import os

from flask import Flask, jsonify, request, send_from_directory

from src.core.player import Player
from src.core.enemy import Enemy
from src.games.web_battle import WebBattle
from src.games.level_mode import LevelManager
from src import collection

app = Flask(__name__, static_folder=None)

# ── 游戏实例 ─────────────────────────────────────────────
# 支持两种模式: "single" (单场战斗) 和 "level" (关卡模式)
game_mode = None       # "single" | "level"
current_battle = None  # WebBattle 实例
current_level = None   # LevelManager 实例


# ── 静态文件 ─────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('../static', 'index.html')


@app.route('/css/<path:filename>')
def css(filename):
    return send_from_directory('../static/css', filename)


@app.route('/js/<path:filename>')
def js(filename):
    return send_from_directory('../static/js', filename)


@app.route('/images/<path:filename>')
def images(filename):
    return send_from_directory('../static/images', filename)


@app.route('/favicon.ico')
def favicon():
    return '', 204


# ── 角色头像映射 ─────────────────────────────────────────

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


# ── 游戏API: 单场战斗 ──────────────────────────────────

def _make_enemies(mode: str):
    """根据模式创建敌人列表"""
    enemies_map = {
        "normal": [Enemy("哥布林", 42, 8), Enemy("毒沼史莱姆", 48, 7)],
        "elite":  [Enemy("熔岩犬", 62, 12), Enemy("护卫队长", 70, 9)],
        "boss":   [Enemy("诅咒法师", 95, 13), Enemy("镜像怪", 75, 11)],
    }
    result = enemies_map.get(mode, enemies_map["normal"])
    return [Enemy(e.name, e.max_hp, e.base_damage) for e in result]


@app.route('/api/new-game', methods=['POST'])
def new_game():
    """开始单场战斗"""
    global game_mode, current_battle, current_level

    data = request.get_json() or {}
    mode = data.get("mode", "normal")
    character = data.get("character", "warrior")

    from src.core.player import CHARACTER_TEMPLATES
    tmpl = CHARACTER_TEMPLATES.get(character, CHARACTER_TEMPLATES["warrior"])
    player = Player(tmpl["name"], tmpl["hp"], character_id=character)
    enemies = _make_enemies(mode)

    current_level = None
    current_battle = WebBattle(player, enemies)
    current_battle.start()
    game_mode = "single"

    return jsonify({"success": True, "state": _get_state()})


# ── 游戏API: 关卡模式 ──────────────────────────────────

@app.route('/api/start-level', methods=['POST'])
def start_level():
    """开始关卡模式"""
    global game_mode, current_battle, current_level

    data = request.get_json() or {}
    difficulty = data.get("difficulty", "easy")
    character = data.get("character", "warrior")

    current_battle = None
    current_level = LevelManager(difficulty, character_id=character)
    current_level.start()
    game_mode = "level"

    return jsonify({"success": True, "state": _get_state()})


@app.route('/api/claim-reward', methods=['POST'])
def claim_reward():
    """领取关卡奖励并进入下一关"""
    global current_level
    if current_level is None:
        return jsonify({"success": False, "error": "没有进行中的关卡"}), 400

    data = request.get_json() or {}
    reward_id = data.get("reward_id", "heal")
    result = current_level.claim_reward(reward_id)
    return jsonify({
        "success": result["success"],
        "error": result.get("error"),
        "level_complete": result.get("level_complete", False),
        "state": _get_state(),
    })


@app.route('/api/choose-branch', methods=['POST'])
def choose_branch():
    """选择关卡模式的下一条分支路线"""
    global current_level
    if current_level is None:
        return jsonify({"success": False, "error": "没有进行中的关卡"}), 400

    data = request.get_json() or {}
    node_id = data.get("node_id")
    if not node_id:
        return jsonify({"success": False, "error": "缺少 node_id"}), 400

    result = current_level.choose_branch(node_id)
    return jsonify({
        "success": result["success"],
        "error": result.get("error"),
        "state": _get_state(),
    })


@app.route('/api/open-shop', methods=['POST'])
def open_shop():
    """打开商店（关卡模式商店节点）"""
    global current_level
    if current_level is None:
        return jsonify({"success": False, "error": "没有进行中的关卡"}), 400
    result = current_level.open_shop()
    return jsonify({
        "success": result["success"],
        "error": result.get("error"),
        "state": _get_state(),
    })


@app.route('/api/buy-item', methods=['POST'])
def buy_item():
    """购买商店物品"""
    global current_level
    if current_level is None:
        return jsonify({"success": False, "error": "没有进行中的关卡"}), 400
    data = request.get_json() or {}
    item_id = data.get("item_id")
    if not item_id:
        return jsonify({"success": False, "error": "缺少 item_id"}), 400
    result = current_level.buy_item(item_id)
    return jsonify({
        "success": result["success"],
        "error": result.get("error"),
        "state": _get_state(),
    })


@app.route('/api/leave-shop', methods=['POST'])
def leave_shop():
    """离开商店，进入路线选择"""
    global current_level
    if current_level is None:
        return jsonify({"success": False, "error": "没有进行中的关卡"}), 400
    result = current_level.leave_shop()
    return jsonify({
        "success": result["success"],
        "error": result.get("error"),
        "state": _get_state(),
    })


@app.route('/api/restart-stage', methods=['POST'])
def restart_stage():
    """重新开始当前关卡（仅战斗节点）"""
    global current_level
    if current_level is None:
        return jsonify({"success": False, "error": "没有进行中的关卡"}), 400
    result = current_level.restart_stage()
    return jsonify({
        "success": result["success"],
        "error": result.get("error"),
        "state": _get_state(),
    })


# ── 图鉴/统计API ──────────────────────────────────

@app.route('/api/collection', methods=['GET'])
def get_collection():
    """获取图鉴数据"""
    return jsonify({"success": True, "data": collection.get_collection()})


@app.route('/api/unlock-info', methods=['GET'])
def get_unlock_info():
    """获取解锁信息"""
    return jsonify({"success": True, "data": collection.get_unlocked_info()})


# ── 游戏API: 自定义模式 ──────────────────────────────────

@app.route('/api/start-custom', methods=['POST'])
def start_custom():
    """自定义模式: 用户配置敌人参数"""
    global game_mode, current_battle, current_level

    data = request.get_json() or {}
    enemies_config = data.get("enemies", [])
    player_hp = data.get("player_hp", 80)
    character = data.get("character", "warrior")

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

    # 使用角色模板创建玩家
    from src.core.player import CHARACTER_TEMPLATES
    template = CHARACTER_TEMPLATES.get(character, CHARACTER_TEMPLATES["warrior"])
    player_name = template["name"]
    player = Player(player_name, max_hp=max(10, min(999, int(player_hp))),
                    character_id=character)

    current_level = None
    current_battle = WebBattle(player, enemies)
    current_battle.start()
    game_mode = "custom"

    return jsonify({"success": True, "state": _get_state()})


# ── 游戏API: 通用 ──────────────────────────────────────

def _get_state():
    """获取当前游戏状态（自动识别模式）"""
    global game_mode, current_battle, current_level
    if game_mode == "level" and current_level:
        return current_level.get_state()
    if current_battle:
        return current_battle.get_state()
    return None


@app.route('/api/game-state')
def game_state():
    """获取当前游戏状态"""
    state = _get_state()
    if state is None:
        return jsonify({"success": False, "error": "没有进行中的游戏"}), 400
    return jsonify({"success": True, "state": state})


@app.route('/api/play-card', methods=['POST'])
def play_card():
    """打出一张牌"""
    global current_battle, current_level

    data = request.get_json() or {}
    card_index = data.get("card_index")
    target_index = data.get("target_index", 0)

    if card_index is None:
        return jsonify({"success": False, "error": "缺少 card_index"}), 400

    # 关卡模式
    if current_level and current_level.status == "playing":
        result = current_level.play_card(int(card_index), int(target_index))
        return jsonify({
            "success": result["success"],
            "error": result.get("error"),
            "battle_ended": result.get("battle_ended", False),
            "state": _get_state(),
        })

    # 单场战斗
    if current_battle:
        result = current_battle.play_card(int(card_index), int(target_index))
        return jsonify({
            "success": result["success"],
            "error": result.get("error"),
            "battle_ended": result.get("battle_ended", False),
            "state": _get_state(),
        })

    return jsonify({"success": False, "error": "没有进行中的游戏"}), 400


@app.route('/api/end-turn', methods=['POST'])
def end_turn():
    """结束玩家回合"""
    global current_battle, current_level

    # 关卡模式
    if current_level and current_level.status == "playing":
        result = current_level.end_turn()
        return jsonify({
            "success": result["success"],
            "error": result.get("error"),
            "battle_ended": result.get("battle_ended", False),
            "state": _get_state(),
        })

    # 单场战斗
    if current_battle:
        result = current_battle.end_turn()
        return jsonify({
            "success": result["success"],
            "error": result.get("error"),
            "battle_ended": result.get("battle_ended", False),
            "state": _get_state(),
        })

    return jsonify({"success": False, "error": "没有进行中的游戏"}), 400


# ── 游戏API: 技能 ──────────────────────────────────────

@app.route('/api/use-skill', methods=['POST'])
def use_skill():
    """使用角色专属技能"""
    global current_battle, current_level

    if current_level and current_level.status == 'playing':
        result = current_level.battle.use_skill() if current_level.battle else {"success": False, "error": "没有进行中的战斗"}
        return jsonify({
            "success": result["success"],
            "error": result.get("error"),
            "message": result.get("message"),
            "state": _get_state(),
        })

    if current_battle:
        result = current_battle.use_skill()
        return jsonify({
            "success": result["success"],
            "error": result.get("error"),
            "message": result.get("message"),
            "state": _get_state(),
        })

    return jsonify({"success": False, "error": "没有进行中的游戏"}), 400


# ── 启动 ──────────────────────────────────────────────────

def run_server(host='127.0.0.1', port=5000, debug=False, open_browser=True):
    """启动Web服务器"""
    import webbrowser
    url = f"http://{host}:{port}"

    print(f"""
{'='*50}
  🗡️  卡牌对决 - Web版
{'='*50}
  服务器已启动: {url}
  按 Ctrl+C 停止服务器
{'='*50}
""")

    if open_browser:
        webbrowser.open(url)

    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_server()
