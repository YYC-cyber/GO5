"""
卡牌游戏 Web 服务器
提供 REST API + 静态文件服务
使用模块化蓝图路由
"""
import os
from flask import Flask, send_from_directory, jsonify

from src.routes.single_player import single_player_bp
from src.routes.level_mode import level_mode_bp
from src.routes.multiplayer_mode import multiplayer_mode_bp
from src.routes.handbook import handbook_bp
from src.routes.setting import setting_bp
from src.routes.battle import battle_bp
from src.config import WEB_HOST, WEB_PORT

app = Flask(__name__, static_folder=None)
app.secret_key = os.environ.get('CARDGAME_SECRET_KEY', 'dev_key_change_in_production')

# ── 全局异常处理 ──────────────────────────────────────────
@app.errorhandler(Exception)
def handle_exception(e):
    """捕获未处理异常，防止泄露堆栈信息"""
    import traceback
    traceback.print_exc()
    return jsonify({"success": False, "error": "服务器内部错误"}), 500

# ── 注册蓝图 ─────────────────────────────────────────────
app.register_blueprint(single_player_bp)
app.register_blueprint(level_mode_bp)
app.register_blueprint(multiplayer_mode_bp)
app.register_blueprint(handbook_bp)
app.register_blueprint(setting_bp)
app.register_blueprint(battle_bp)


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


# ── 启动 ──────────────────────────────────────────────────

def run_server(host=None, port=None, debug=False, open_browser=True):
    """启动Web服务器"""
    import webbrowser
    host = host or WEB_HOST
    port = port or WEB_PORT
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