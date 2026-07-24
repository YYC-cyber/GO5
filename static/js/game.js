/**
 * 卡牌对决 — 游戏主逻辑（操作、键盘、初始化）
 * 依赖：api.js → core.js → ui.js → menu.js
 */

// ═══ 卡牌操作 ═══
function onCardClick(i){
    if(!isActive()||g.aim||g.busy||isRewardPhase()||isPathSelectPhase())return;
    const c=g.state?.hand?.[i];if(!c||!c.playable)return;
    if(c.self_target){playCard(i,0);return;}
    const al=getActiveEnemies();if(!al.length)return;
    if(al.length===1)playCard(i,g.state.enemies.indexOf(al[0]));
    else{g.sel=i;g.aim=true;renderScreen();}
}
function pickTarget(ti){if(g.sel!==null){playCard(g.sel,ti);g.sel=null;g.aim=false;}}

async function playCard(ci,ti){
    if(g.busy)return;g.busy=true;D.ha.style.pointerEvents='none';
    // 卡牌飞出动画：保存卡牌位置
    const cardEl=D.ha.querySelector(`.card[data-index="${ci}"]`);
    const targetEl=D.ea.querySelector(`.enemy-card[data-index="${ti}"]`);
    if(cardEl)animateCardFlyOut(cardEl,targetEl);
    try{const r=await API.playCard(ci,ti);if(!r.success){console.error(r.error);return;}as(r);if(r.battle_ended&&g.mode!=='level')g.over=true;renderScreen();}catch(e){console.error(e);}finally{g.busy=false;D.ha.style.pointerEvents='';}
}
async function endTurn(){
    if(!isActive()||g.busy)return;if(g.aim||g.sel!==null){cs();return;}
    g.busy=true;D.et.disabled=true;D.et.innerHTML='⏳处理中...';
    try{const r=await API.endTurn();as(r);if(r.battle_ended&&g.mode!=='level')g.over=true;renderScreen();}catch(e){console.error(e);}finally{g.busy=false;D.et.disabled=false;D.et.innerHTML='⏭️结束回合[E]';}
}
async function claimReward(id){
    if(g.busy)return;g.busy=true;
    try{const r=await API.claimReward(id);as(r);if(r.level_complete)g.over=true;renderScreen();}catch(e){console.error(e);}finally{g.busy=false};
}
async function chooseBranch(id){
    if(g.busy)return;g.busy=true;
    try{const r=await API.chooseBranch(id);if(!r.success){console.error(r.error);return;}as(r);D.mapPanel.classList.add('hidden');renderScreen();}catch(e){console.error(e);}finally{g.busy=false};
}

// ═══ 商店 ═══
async function leaveShop(){
    if(g.busy)return;
    g.busy=true;
    try{const r=await API.leaveShop();if(!r.success){console.error(r.error);return;}as(r);renderScreen();}catch(e){console.error(e);}finally{g.busy=false};
}
async function buyShopItem(id){
    if(g.busy)return;g.busy=true;
    try{const r=await API.buyItem(id);if(!r.success){console.error(r.error);}as(r);renderScreen();}catch(e){console.error(e);}finally{g.busy=false};
}

// ═══ 事件/营火 ═══
async function evContinue(){
    if(g.busy)return;
    D.ev.classList.add('hidden');
    if(g.state)g.state.event_data=null;
    renderScreen();
}

// ═══ 失败处理 ═══
function defeatRetry(){
    if(g.busy)return;
    g.busy=true;
    D.df.classList.add('hidden');
    API.restartStage().then(r=>{
        if(!r.success){toast(r.error,'error');D.df.classList.remove('hidden');return;}
        as(r);renderScreen();
    }).catch(e=>console.error(e)).finally(()=>{g.busy=false;});
}
function defeatRestart(){
    if(g.busy)return;
    const diff=g.state?.difficulty||'easy';
    D.df.classList.add('hidden');
    startLevel(diff);
}
function defeatMenu(){
    D.df.classList.add('hidden');
    g.over=false;
    returnToMenu();
}

// ═══ 技能 ═══
async function useSkill(){
    if(!isActive()||g.busy||isRewardPhase()||isPathSelectPhase())return;
    g.busy=true;
    try{const r=await API.useSkill();if(!r.success){console.error(r.error);return;}g.state=r.state;renderScreen();const pc=$('player-area');if(pc)flash(pc,'skill');}catch(e){console.error(e);}finally{g.busy=false};
}

// ═══ 模式启动 ═══
async function startGameMode(m){
    console.log('[GAME] start mode='+m+' char='+g.char);
    closeModal();g.over=false;g.sel=null;g.aim=false;g.busy=false;g.state=null;g.prev=null;
    try{
        const r=await API.newGame(m,g.char);
        console.log('[GAME] response:',r.success?'OK':'FAIL',r.error||'');
        if(!r.success){toast('启动失败: '+r.error,'error');return;}
        g.mode='single';g.prev=null;g.state=r.state;renderScreen();updateShortcutBar();
    }catch(e){console.error(e);toast('网络错误','error');}
}
async function startLevel(d){
    console.log('[LEVEL] start diff='+d+' char='+g.char);
    closeModal();D.mapPanel.classList.add('hidden');g.over=false;g.sel=null;g.aim=false;g.busy=false;g.state=null;g.prev=null;
    try{
        const r=await API.startLevel(d,g.char);
        if(!r.success){toast('启动失败: '+r.error,'error');return;}
        g.mode='level';g.prev=null;g.state=r.state;renderScreen();updateShortcutBar();
        updateChapterBG(r.state);
    }catch(e){console.error(e);toast('网络错误','error');}
}

// ═══ 键盘 ═══
function handleKeyDown(e){
    // 输入框焦点时忽略键盘事件，避免冲突
    const tag=e.target.tagName;
    if(tag==='INPUT'||tag==='TEXTAREA'||tag==='SELECT'||e.target.isContentEditable){
        return;
    }

    const k=e.key,mo=!D.modal.classList.contains('hidden');
    const pp=q('.pile-popup-overlay');
    if(pp&&k==='Escape'){pp.remove();e.preventDefault();return;}
    if(D.mapPanel&&!D.mapPanel.classList.contains('hidden')){
        if(handleMapKeys(e)){e.preventDefault();return;}
    }
    if(mo){
        const onChar=D.stepChar.classList.contains('active');
        if(k==='Escape'){closeModal();updateShortcutBar();e.preventDefault();return;}
        if(k==='ArrowRight'&&onChar){confirmCharacter();e.preventDefault();return;}
        if(k==='ArrowLeft'&&!onChar){showStep('char');e.preventDefault();return;}
        /* 键盘快捷键已移除，请使用鼠标点击选择 */
        return;
    }
    if(g.help){if(k==='Escape'||k==='h'||k==='H'){th();e.preventDefault();}return;}
    if(k==='Escape'){if(g.aim||g.sel!==null)cs();e.preventDefault();return;}
    if(k==='h'||k==='H'){th();e.preventDefault();return;}
    if(k==='r'||k==='R'||k==='n'||k==='N'){returnToMenu();e.preventDefault();return;}
    if(isRewardPhase())return;
    if(k>='1'&&k<='9'){e.preventDefault();if(!isActive()||g.over)return;const idx=+k-1;const c=g.state?.hand?.[idx];if(c&&c.playable)onCardClick(idx);return;}
    if(k==='e'||k==='E'||k==='Enter'||k===' '){e.preventDefault();if(g.over){returnToMenu();return;}if(isRewardPhase())return;endTurn();}
}

// ═══ 事件委托（统一管理动态元素的交互） ═══
function setupEventDelegation(){
    // --- 敌人区域：点击目标选择 ---
    D.ea.addEventListener('click',function(e){
        const card=e.target.closest('.enemy-card.targetable');
        if(card)pickTarget(+card.dataset.index);
    });
    // --- 敌人区域：拖放出牌 ---
    D.ea.addEventListener('dragover',function(e){
        e.preventDefault();
        const card=e.target.closest('.enemy-card:not(.dead)');
        if(card){e.dataTransfer.dropEffect='move';card.classList.add('drag-over');}
    });
    D.ea.addEventListener('dragleave',function(e){
        const card=e.target.closest('.enemy-card');
        if(card)card.classList.remove('drag-over');
    });
    D.ea.addEventListener('drop',function(e){
        e.preventDefault();
        const card=e.target.closest('.enemy-card:not(.dead)');
        if(!card)return;
        card.classList.remove('drag-over');
        const dt=e.dataTransfer.getData('text/plain');
        if(dt.startsWith('card:')){
            const ci=+dt.slice(5);
            if(!isActive()||g.busy||isRewardPhase()||isPathSelectPhase())return;
            const c=g.state?.hand?.[ci];if(!c||!c.playable)return;
            playCard(ci,+card.dataset.index);
        }else if(dt==='skill'){useSkill();}
    });
    // --- 手牌区域：点击出牌 ---
    D.ha.addEventListener('click',function(e){
        const card=e.target.closest('.card.playable');
        if(card)onCardClick(+card.dataset.index);
    });
    // --- 手牌区域：拖放 ---
    D.ha.addEventListener('dragstart',function(e){
        const card=e.target.closest('.card.playable');
        if(card){e.dataTransfer.setData('text/plain','card:'+card.dataset.index);e.dataTransfer.effectAllowed='move';card.classList.add('dragging');hideCardTooltip();}
    });
    D.ha.addEventListener('dragend',function(e){
        const card=e.target.closest('.card');
        if(card)card.classList.remove('dragging');
    });
    // --- 手牌区域：右键取消选择 ---
    D.ha.addEventListener('contextmenu',function(e){
        const card=e.target.closest('.card.selected, .card.playable');
        if(card){e.preventDefault();cs();}
    });
    // --- 手牌区域：Tooltip（mouseover/mouseout 代替 mouseenter/mouseleave 以支持委托） ---
    D.ha.addEventListener('mouseover',function(e){
        const card=e.target.closest('.card');
        if(card)showCardTooltip(card,e);
    });
    D.ha.addEventListener('mouseout',function(e){
        const card=e.target.closest('.card');
        if(card&&!card.contains(e.relatedTarget))hideCardTooltip();
    });
    // --- 路线选择：点击路线卡 ---
    D.routeChoices.addEventListener('click',function(e){
        const card=e.target.closest('.route-card');
        if(card)chooseBranch(card.dataset.node);
    });
    // --- 商店：点击购买按钮 ---
    D.si.addEventListener('click',function(e){
        const btn=e.target.closest('[data-buy]');
        if(btn)buyShopItem(+btn.dataset.buy);
    });
    // --- 牌堆弹窗：点击空白处关闭 ---
    document.addEventListener('click',function(e){
        if(e.target.classList.contains('pile-popup-overlay')||e.target.closest('.pile-popup-close')){
            const ov=e.target.closest('.pile-popup-overlay');
            if(ov)ov.remove();
        }
    });
}

// ═══ 初始化 ═══
async function init(){
    cache();
    setupEventDelegation();

    // 主菜单
    D.menuSingle.addEventListener('click',startSinglePlayer);
    D.menuMulti.addEventListener('click',()=>showComingSoon('多人模式'));
    D.menuCollection.addEventListener('click',showCollection);
    D.menuSettings.addEventListener('click',openSettings);
    D.menuQuit.addEventListener('click',closeGame);
    D.colClose.addEventListener('click',closeCollection);

    D.charOpts.forEach(o=>o.addEventListener('click',function(){selectCharacter(this.dataset.char);}));
    D.charNext.addEventListener('click',confirmCharacter);
    D.modeBack.addEventListener('click',()=>showStep('char'));
    
    D.mN.addEventListener('click',()=>startGameMode('normal'));
    D.mE.addEventListener('click',()=>startGameMode('elite'));
    D.mB.addEventListener('click',()=>startGameMode('boss'));
    D.mL.addEventListener('click',()=>startLevel('easy'));
    D.mLH.addEventListener('click',()=>startLevel('hard'));
    D.mLHe.addEventListener('click',()=>startLevel('hell'));

    D.mEndlessEasy.addEventListener('click',()=>startEndless('easy'));
    D.mEndlessHard.addEventListener('click',()=>startEndless('hard'));
    D.mEndlessHell.addEventListener('click',()=>startEndless('hell'));

    D.cAdd.addEventListener('click',()=>addEnemyRow());
    D.cStart.addEventListener('click',startCustomMode);
    D.presetBtns.forEach(b=>b.addEventListener('click',()=>applyPreset(b.dataset.e)));

    D.et.addEventListener('click',endTurn);
    D.ca.addEventListener('click',cs);
    D.rt.addEventListener('click',returnToMenu);
    D.hb.addEventListener('click',th);

    document.addEventListener('keydown',handleKeyDown);
    document.addEventListener('contextmenu',e=>{if(e.target.closest('.game-container')&&(g.aim||g.sel!==null)){e.preventDefault();cs();}});

    D.pd.addEventListener('click',()=>showPilePopup(`📚 抽牌堆 (${g.state?.deck_count||0}张)`,g.state?.deck_cards||[]));
    D.pi.addEventListener('click',()=>showPilePopup(`📤 弃牌堆 (${g.state?.discard_count||0}张)`,g.state?.discard_cards||[]));
    D.sl.addEventListener('click',leaveShop);
    D.evBtn.addEventListener('click',evContinue);
    D.dfRestart.addEventListener('click',defeatRestart);
    D.dfRetry.addEventListener('click',defeatRetry);
    D.dfMenu.addEventListener('click',defeatMenu);
    // 设置面板
    D.setClose.addEventListener('click',closeSettings);
    D.sfxToggle.addEventListener('click',toggleSFX);
    D.sfxVolume.addEventListener('input',updateVolume);
    D.setLogin.addEventListener('click',handleLogin);
    D.setLogout.addEventListener('click',handleLogout);
    if(D.mapToggle)D.mapToggle.addEventListener('click',toggleMap);
    if(D.mapPanelClose)D.mapPanelClose.addEventListener('click',()=>D.mapPanel.classList.add('hidden'));
    initMapDrag();
    updateShortcutBar();

    try{const r=await API.getState();if(r.success){as(r);hideMainMenu();D.modal.classList.add('hidden');renderScreen();}else showMainMenu();}catch{showMainMenu();}
}

// ═══ 设置面板 ═══
function openSettings(){
    hideMainMenu();
    D.setOverlay.classList.remove('hidden');
    updateSettingsUI();
    SFX.play('button');
}
function closeSettings(){
    D.setOverlay.classList.add('hidden');
    showMainMenu();
    SFX.play('button');
}
function toggleSFX(){
    SFX.setEnabled(!SFX.enabled);
    updateSettingsUI();
    if(SFX.enabled) SFX.play('button');
}
function updateVolume(){
    const v=parseInt(D.sfxVolume.value);
    SFX.setVolume(v/100);
    D.sfxVolumeVal.textContent=v+'%';
}
function updateSettingsUI(){
    D.sfxToggle.textContent=SFX.enabled?'开':'关';
    D.sfxToggle.classList.toggle('off',!SFX.enabled);
    D.sfxVolume.value=Math.round(SFX.volume*100);
    D.sfxVolumeVal.textContent=Math.round(SFX.volume*100)+'%';
}
function handleLogin(){
    SFX.play('button');
    toast('登录功能开发中，敬请期待');
}
function handleLogout(){
    SFX.play('button');
    toast('退出账号功能开发中，敬请期待');
}

// ═══ 章节背景 ═══
function updateChapterBG(state){
    if(!state||!state.chapter)return;
    ChapterBG.setChapter(state.chapter);
}

document.addEventListener('DOMContentLoaded',init);