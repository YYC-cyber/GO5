"""
图鉴/收集路由
"""
from flask import Blueprint, jsonify

from src import collection

handbook_bp = Blueprint('handbook', __name__)


@handbook_bp.route('/api/collection', methods=['GET'])
def get_collection():
    """获取图鉴数据"""
    return jsonify({"success": True, "data": collection.get_collection()})


@handbook_bp.route('/api/unlock-info', methods=['GET'])
def get_unlock_info():
    """获取解锁信息"""
    return jsonify({"success": True, "data": collection.get_unlocked_info()})