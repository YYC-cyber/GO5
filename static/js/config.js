/**
 * 卡牌对决 — 前端配置常量
 * 所有可调参数集中管理
 */
const GameConfig = {
    // API 超时 (毫秒)
    API_TIMEOUT: 8000,

    // 图片路径
    IMAGE_PATH: '/images/',

    // 游戏模式
    MODES: { SINGLE: 'single', LEVEL: 'level', ENDLESS: 'endless', CUSTOM: 'custom' },

    // 敌人模板
    ENEMY_TEMPLATES: [
        { name: '哥布林', hp: 30, dmg: 6 },
        { name: '史莱姆', hp: 40, dmg: 5 },
        { name: '火焰领主', hp: 55, dmg: 9 },
        { name: '寒冰法师', hp: 45, dmg: 7 },
        { name: '暗影领主', hp: 80, dmg: 12 },
        { name: '毒沼史莱姆', hp: 45, dmg: 7 },
        { name: '熔岩犬', hp: 60, dmg: 10 },
        { name: '镜像怪', hp: 65, dmg: 10 },
        { name: '护卫队长', hp: 70, dmg: 8 },
        { name: '诅咒法师', hp: 70, dmg: 11 },
    ],

    // 意图图标映射
    INTENT_ICONS: {
        '攻击': '⚔️', '防御': '🛡️', '强化': '💪',
        '毒液': '☠️', '灼咬': '🔥', '镜像': '🪞',
        '守护': '🛡️', '诅咒': '🌑', '虚弱': '💫',
    },

    // 状态效果 tooltip 描述
    STATUS_TOOLTIPS: {
        block:        { name: '格挡', desc: '抵消即将受到的伤害，通常在回合结束后清空。' },
        strength:     { name: '力量', desc: '提高攻击造成的伤害。' },
        poison:       { name: '中毒', desc: '回合结束受到层数伤害，然后层数 -1。' },
        burn:         { name: '烧伤', desc: '回合结束受到层数伤害，然后层数 -1。' },
        bleed:        { name: '流血', desc: '回合结束受到层数伤害，然后层数 -1。' },
        weak:         { name: '虚弱', desc: '降低攻击伤害，层数会随回合递减。' },
        vulnerable:   { name: '易伤', desc: '受到的伤害提高，层数会随回合递减。' },
        curse:        { name: '诅咒', desc: '受到伤害时额外受到诅咒层数的伤害。' },
        blessing:     { name: '祝福', desc: '每回合开始获得对应层数的格挡。' },
        thorns:       { name: '反伤', desc: '被敌人攻击时对攻击者造成反击伤害。' },
        turret:       { name: '炮台', desc: '每回合开始自动攻击首个存活敌人。' },
        skeleton:     { name: '骷髅', desc: '每回合开始自动攻击首个存活敌人。' },
        echo:         { name: '回响', desc: '下一张打出的牌释放两次，触发后消失。' },
        iron_wall:    { name: '铁壁', desc: '防御能力强化，格挡会更稳定地保留或产生防御收益。' },
        counter:      { name: '反击', desc: '受到攻击后触发反击效果。' },
        block_persist:{ name: '格挡保留', desc: '回合结束后格挡不会完全清空。' },
        auto_shield:  { name: '自动护盾', desc: '每回合开始自动获得护盾。' },
        relic:        { name: '遗物', desc: '遗物提供持续被动效果。' },
    },

    // 序号标记
    BADGE_GLYPHS: '①②③④⑤⑥⑦⑧⑨',

    // Toast 持续时间 (毫秒)
    TOAST_DURATION: 2500,

    // 动画持续时间 (毫秒)
    FLASH_DURATION: 520,
    TRANSITION_OUT: 300,
};