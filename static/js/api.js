/**
 * 卡牌对决 — API 层
 * 封装所有后端API调用
 */
const API = {
    async request(method, url, body){
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), GameConfig.API_TIMEOUT);
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' },
            signal: controller.signal
        };
        if (body) options.body = JSON.stringify(body);
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (e) {
            console.error('API Error:', e);
            return {
                success: false,
                error: e.name === 'AbortError'
                    ? '请求超时，请检查网络后重试'
                    : `请求失败: ${e.message}`
            };
        } finally {
            clearTimeout(timeoutId);
        }
    },
    newGame(mode, character) { return this.request('POST', '/api/new-game', { mode, character }); },
    startLevel(difficulty, character) { return this.request('POST', '/api/start-level', { difficulty, character }); },
    startEndless(difficulty, character) { return this.request('POST', '/api/start-endless', { difficulty, character }); },
    startCustom(enemies, playerHp, character, baseAttack, baseDefense) {
        return this.request('POST', '/api/start-custom', {
            enemies, player_hp: playerHp, character,
            base_attack: baseAttack || 0, base_defense: baseDefense || 0
        });
    },
    getState() { return this.request('GET', '/api/game-state'); },
    playCard(cardIndex, targetIndex) { return this.request('POST', '/api/play-card', { card_index: cardIndex, target_index: targetIndex }); },
    endTurn() { return this.request('POST', '/api/end-turn'); },
    claimReward(id) { return this.request('POST', '/api/claim-reward', { reward_id: id }); },
    chooseBranch(id) { return this.request('POST', '/api/choose-branch', { node_id: id }); },
    useSkill() { return this.request('POST', '/api/use-skill', {}); },
    openShop() { return this.request('POST', '/api/open-shop', {}); },
    buyItem(id) { return this.request('POST', '/api/buy-item', { item_id: id }); },
    leaveShop() { return this.request('POST', '/api/leave-shop', {}); },
    restartStage() { return this.request('POST', '/api/restart-stage', {}); },
};