/**
 * 卡牌对决 — 背景与音效系统
 */

// ═══ 章节背景系统 ═══
const ChapterBG = {
    canvas: null,
    ctx: null,
    particles: [],
    currentChapter: null,
    animId: null,

    themes: {
        '第一章: 边境': {
            bg: ['#0a1a2a', '#0d2818'],
            particleColor: 'rgba(100, 200, 120, 0.3)',
            particleCount: 20,
        },
        '第二章: 深入': {
            bg: ['#0d0a1a', '#1a0d2a'],
            particleColor: 'rgba(140, 100, 220, 0.3)',
            particleCount: 18,
        },
        '第三章: 熔炉': {
            bg: ['#1a0a0a', '#2a1500'],
            particleColor: 'rgba(255, 120, 40, 0.35)',
            particleCount: 25,
        },
        '第四章: 深渊': {
            bg: ['#050a15', '#0a1528'],
            particleColor: 'rgba(100, 180, 255, 0.25)',
            particleCount: 15,
        },
        '第五章: 终焉': {
            bg: ['#0a0a14', '#14101e'],
            particleColor: 'rgba(160, 120, 200, 0.2)',
            particleCount: 12,
        },
        '第六章: 混沌': {
            bg: ['#140508', '#0a0505'],
            particleColor: 'rgba(255, 60, 60, 0.3)',
            particleCount: 22,
        },
        '第七章: 虚空': {
            bg: ['#020810', '#0a1020'],
            particleColor: 'rgba(200, 220, 255, 0.25)',
            particleCount: 30,
        },
        '第八章: 决战': {
            bg: ['#0a0800', '#14100a'],
            particleColor: 'rgba(246, 201, 64, 0.35)',
            particleCount: 28,
        },
    },

    init() {
        this.canvas = document.getElementById('bg-canvas');
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        this.resize();
        window.addEventListener('resize', () => this.resize());
    },

    resize() {
        if (!this.canvas) return;
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    },

    setChapter(chapter) {
        if (chapter === this.currentChapter) return;
        this.currentChapter = chapter;
        this.initParticles(chapter);
        if (!this.animId) this.animate();
    },

    setDefault() {
        if (this.currentChapter === null) return;
        this.currentChapter = null;
        if (this.animId) {
            cancelAnimationFrame(this.animId);
            this.animId = null;
        }
        if (this.ctx) {
            this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        }
    },

    initParticles(chapter) {
        const theme = this.themes[chapter] || this.themes['第一章: 边境'];
        this.particles = [];
        for (let i = 0; i < (theme.particleCount || 20); i++) {
            this.particles.push({
                x: Math.random() * (this.canvas?.width || 800),
                y: Math.random() * (this.canvas?.height || 600),
                r: Math.random() * 2 + 1,
                vx: (Math.random() - 0.5) * 0.4,
                vy: (Math.random() - 0.5) * 0.3 - 0.1,
                alpha: Math.random() * 0.5 + 0.2,
            });
        }
    },

    animate() {
        if (!this.canvas || !this.ctx || this.currentChapter === null) {
            this.animId = null;
            return;
        }
        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;
        const theme = this.themes[this.currentChapter] || this.themes['第一章: 边境'];

        // 绘制渐变背景
        const grad = ctx.createLinearGradient(0, 0, 0, h);
        grad.addColorStop(0, theme.bg[0]);
        grad.addColorStop(1, theme.bg[1]);
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, w, h);

        // 绘制粒子
        for (const p of this.particles) {
            p.x += p.vx;
            p.y += p.vy;
            if (p.x < -10) p.x = w + 10;
            if (p.x > w + 10) p.x = -10;
            if (p.y < -10) p.y = h + 10;
            if (p.y > h + 10) p.y = -10;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = theme.particleColor;
            ctx.globalAlpha = p.alpha;
            ctx.fill();
        }
        ctx.globalAlpha = 1;

        this.animId = requestAnimationFrame(() => this.animate());
    },
};

// ═══ 音效系统 ═══
const SFX = {
    ctx: null,
    enabled: true,
    volume: 0.5,

    init() {
        try {
            this.ctx = new (window.AudioContext || window.webkitAudioContext)();
        } catch (e) {
            console.warn('Web Audio API 不可用');
        }
        // 从 localStorage 恢复设置
        const saved = localStorage.getItem('sfx_enabled');
        if (saved !== null) this.enabled = saved === 'true';
        const vol = localStorage.getItem('sfx_volume');
        if (vol !== null) this.volume = Math.min(1, Math.max(0, parseFloat(vol)));
    },

    resume() {
        if (this.ctx && this.ctx.state === 'suspended') {
            this.ctx.resume();
        }
    },

    _play(freq, type, duration, vol) {
        if (!this.enabled || !this.ctx) return;
        this.resume();
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
        gain.gain.setValueAtTime((vol || 1) * this.volume * 0.3, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + duration);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(this.ctx.currentTime);
        osc.stop(this.ctx.currentTime + duration);
    },

    play(name) {
        if (!this.enabled) return;
        switch (name) {
            case 'card_play':    this._play(440, 'triangle', 0.12, 0.8); this._play(660, 'triangle', 0.08, 0.5); break;
            case 'card_hit':     this._play(200, 'sawtooth', 0.15, 0.6); this._play(120, 'square', 0.1, 0.4); break;
            case 'block':        this._play(300, 'sine', 0.1, 0.5); break;
            case 'heal':         this._play(520, 'sine', 0.2, 0.6); setTimeout(() => this._play(660, 'sine', 0.15, 0.4), 80); break;
            case 'enemy_attack': this._play(150, 'sawtooth', 0.18, 0.7); this._play(100, 'square', 0.12, 0.5); break;
            case 'enemy_death':  this._play(400, 'sawtooth', 0.1, 0.5); this._play(600, 'triangle', 0.2, 0.4); this._play(800, 'sine', 0.3, 0.3); break;
            case 'victory':      [520,660,784,1040].forEach((f,i) => setTimeout(() => this._play(f, 'triangle', 0.3, 0.6), i*120)); break;
            case 'defeat':       [400,300,200,150].forEach((f,i) => setTimeout(() => this._play(f, 'sawtooth', 0.25, 0.5), i*150)); break;
            case 'turn_start':   this._play(350, 'sine', 0.15, 0.4); break;
            case 'turn_end':     this._play(250, 'triangle', 0.12, 0.3); break;
            case 'reward':       this._play(600, 'sine', 0.1, 0.5); setTimeout(() => this._play(800, 'sine', 0.15, 0.4), 100); break;
            case 'button':       this._play(500, 'sine', 0.06, 0.3); break;
            case 'error':        this._play(200, 'square', 0.15, 0.5); break;
            case 'gold':         this._play(800, 'sine', 0.08, 0.4); setTimeout(() => this._play(1000, 'sine', 0.08, 0.3), 60); break;
            case 'relic':        [600,800,1000].forEach((f,i) => setTimeout(() => this._play(f, 'triangle', 0.2, 0.5), i*100)); break;
            case 'skill':        this._play(440, 'sine', 0.15, 0.6); this._play(880, 'sine', 0.2, 0.4); break;
            case 'level_up':     [523,659,784].forEach((f,i) => setTimeout(() => this._play(f, 'triangle', 0.2, 0.5), i*80)); break;
        }
    },

    setEnabled(val) {
        this.enabled = val;
        localStorage.setItem('sfx_enabled', val);
    },

    setVolume(val) {
        this.volume = Math.min(1, Math.max(0, val));
        localStorage.setItem('sfx_volume', this.volume);
    },
};
