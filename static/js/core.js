/**
 * 卡牌对决 — 核心状态、常量与工具函数
 */
let g = {mode:'single',state:null,prev:null,sel:null,aim:false,busy:false,help:false,over:false,char:'warrior'};
let D = {};

// 向后兼容别名 (逐步迁移到 GameConfig)
const ET = GameConfig.ENEMY_TEMPLATES;
const IM = GameConfig.IMAGE_PATH;
const IC = GameConfig.INTENT_ICONS;
const BG = GameConfig.BADGE_GLYPHS;
const ST = GameConfig.STATUS_TOOLTIPS;

function $(s){return document.getElementById(s);}
function q(s){return document.querySelector(s);}
function qa(s){return document.querySelectorAll(s);}

function cache(){
    D={
        menu:$('main-menu'),
        gc:q('.game-container'), vignette:$('low-hp-vignette'),
        menuSingle:$('menu-single'), menuMulti:$('menu-multi'),
        menuCollection:$('menu-collection'), menuSettings:$('menu-settings'),
        menuQuit:$('menu-quit'),
        toast:$('toast-container'), cf:$('confirm-overlay'),
        cfMsg:$('confirm-message'), cfOk:$('confirm-ok'), cfCancel:$('confirm-cancel'),
        tt:$('card-tooltip'), ttName:$('tt-name'), ttCost:$('tt-cost'),
        ttType:$('tt-type'), ttDesc:$('tt-desc'), ttKw:$('tt-keywords'),
        col:$('collection-overlay'), colContent:$('collection-content'),
        colClose:$('collection-close'), colTabs:qa('.col-tab'),
        modal:$('mode-modal'), stepChar:$('step-char'), stepMode:$('step-mode'),
        stepBar:qa('.step'), charSelect:$('char-select'),
        charOpts:qa('#char-select .char-option'), charNext:$('char-next'),
        modeSubtitle:$('mode-subtitle'), modeBack:$('mode-back'),
        mN:$('mode-normal'),mE:$('mode-elite'),mB:$('mode-boss'),
        mL:$('mode-level'),mLH:$('mode-level-hard'),mLHe:$('mode-level-hell'),
        mEndlessEasy:$('mode-endless-easy'),mEndlessHard:$('mode-endless-hard'),mEndlessHell:$('mode-endless-hell'),
        cEnemies:$('custom-enemies'),cAdd:$('custom-add-enemy'),
        cStart:$('custom-start'),cHp:$('custom-player-hp'),
        cAtk:$('custom-player-atk'),cDef:$('custom-player-def'),
        presetBtns:qa('.preset-btn'),
        mapToggle:$('map-toggle'), mapToggleBadge:$('map-toggle-badge'),
        mapPanel:$('map-panel'), mapPanelClose:$('map-panel-close'),
        mapPanelProgress:$('map-panel-progress'),
        mapPanelCanvas:$('map-panel-canvas'),
        mapSvg:$('map-svg'),
        routeMap:$('route-map'), routeChoices:$('route-choices'),
        ea:$('enemy-area'),la:$('log-area'),ha:$('hand-area'),
        pa:q('.player-avatar-img'),
        pn:q('.player-hp-section .player-name'),
        pf:q('.hp-fill'),pt:q('.player-hp-text'),
        ps:$('player-stats'),eo:q('.energy-orbs'),
        pd:$('pile-deck'),pi:$('pile-discard'),
        et:$('end-turn-btn'),ca:$('cancel-btn'),
        rt:$('restart-btn'),hb:$('help-btn'),
        ho:$('help-overlay'),sb:$('shortcut-bar'),
        rp:$('reward-panel'),rb:$('reward-buttons'),rm:$('reward-message'),
        pg:$('player-gold'), sh:$('shop-overlay'),
        si:$('shop-items'), sg:$('shop-gold-val'),
        sl:$('shop-leave-btn'),
        ev:$('event-overlay'), evIcon:$('event-icon'),
        evTitle:$('event-title'), evMsg:$('event-message'),
        evBtn:$('event-continue-btn'),
        df:$('defeat-overlay'), dfMsg:$('defeat-message'),
        dfRestart:$('defeat-restart-btn'), dfRetry:$('defeat-retry-btn'),
        dfMenu:$('defeat-menu-btn'),
        setOverlay:$('settings-overlay'), setClose:$('settings-close'),
        sfxToggle:$('sfx-toggle'), sfxVolume:$('sfx-volume'), sfxVolumeVal:$('sfx-volume-val'),
        setLogin:$('settings-login'), setLogout:$('settings-logout'),
    };
}

function getImageUrl(n){return n?IM+n:'';}
function getIntentIcon(i){return IC[i]||'❓';}
function getIntentText(e){return `${getIntentIcon(e.intent)} ${e.intent_text||`${e.intent}${e.intent_value?` ${e.intent_value}`:''}`}`;}
function getStatusDescription(k,v){
    const s=ST[k]||{name:k,desc:''};
    const n=(v===true||v===undefined||v===null)?'':`：当前 ${v}`;
    return `${s.name}${n}。${s.desc}`;
}
function escapeHtml(s){
    if(s==null||s===undefined)return '';
    return String(s)
        .replace(/&/g,'&amp;')
        .replace(/</g,'&lt;')
        .replace(/>/g,'&gt;')
        .replace(/"/g,'&quot;')
        .replace(/'/g,'&#039;');
}
function formatStatusHtml(cls,txt,title){const t=escapeHtml(title);return `<span class="${cls} has-tip" title="${t}" aria-label="${t}" data-tip="${t}">${txt}</span>`;}
function stat(txt,title,extra='',style=''){const t=escapeHtml(title);return `<div class="stat has-tip ${extra}" style="${style}" title="${t}" aria-label="${t}" data-tip="${t}">${txt}</div>`;}
function renderEnemyBuffs(e){
    let h='';
    if(e.strength>0)h+=formatStatusHtml('buff buff-str',`💪${e.strength}`,getStatusDescription('strength',e.strength));
    if(e.poison>0)h+=formatStatusHtml('buff buff-psn',`☠️${e.poison}`,getStatusDescription('poison',e.poison));
    if(e.burn>0)h+=formatStatusHtml('buff buff-brn',`🔥${e.burn}`,getStatusDescription('burn',e.burn));
    if(e.bleed>0)h+=formatStatusHtml('buff buff-bld',`🩸${e.bleed}`,getStatusDescription('bleed',e.bleed));
    if(e.weak>0)h+=formatStatusHtml('buff buff-wk',`💫${e.weak}`,getStatusDescription('weak',e.weak));
    if(e.vulnerable>0)h+=formatStatusHtml('buff buff-vul',`💥${e.vulnerable}`,getStatusDescription('vulnerable',e.vulnerable));
    if(e.curse>0)h+=formatStatusHtml('buff buff-crs',`🌑${e.curse}`,getStatusDescription('curse',e.curse));
    return h;
}
function isActive(){return g.state&&!g.over;}
function getActiveEnemies(){return g.state?.enemies?.filter(e=>e.alive)||[];}
function isLevelMode(){return g.mode==='level'||g.mode==='endless';}
function getLevelStatus(){return g.state?.status;}
function isRewardPhase(){return isLevelMode()&&getLevelStatus()==='stage_clear';}
function isPathSelectPhase(){return isLevelMode()&&getLevelStatus()==='path_select';}

function updateShortcutBar(){
    if(!D.modal.classList.contains('hidden')){D.sb.textContent='[←]返回 [→]确认 [Esc]关闭';return;}
    if(g.help){D.sb.textContent='[Esc]关闭帮助';return;}
    if(g.over){D.sb.textContent='[R]重新开始 [H]帮助';return;}
    if(g.aim){D.sb.textContent='👆点击敌人或[1-9]选目标 [Esc/右键]取消';return;}
    if(isRewardPhase()){D.sb.textContent='🎁选择奖励后选择路线';return;}
    if(isPathSelectPhase()){D.sb.textContent='🧭选择下一条路线继续前进';return;}
    if(isActive()){D.sb.textContent='[1-9]出牌 [E/Enter]结束 [R]重开 [H]帮助';return;}
    D.sb.textContent='按 [R] 开始';
}
function th(){g.help=!g.help;D.ho.classList.toggle('hidden',!g.help);updateShortcutBar();}
function cs(){if(g.aim||g.sel!==null){g.aim=false;g.sel=null;renderScreen();return true;}return false;}
function closeModal(){D.gc.classList.remove('trans-out');D.modal.classList.add('hidden');}
function returnToMenu(){D.modal.classList.add('hidden');showMainMenu();ChapterBG.setDefault();}
function showMainMenu(){D.gc.classList.remove('trans-out');D.menu.classList.remove('hidden');if(D.modal)D.modal.classList.add('hidden');updateShortcutBar();ChapterBG.setDefault();}
function hideMainMenu(){D.menu.classList.add('hidden');}
function transOut(cb){D.gc.classList.add('trans-out');setTimeout(cb,300);}
function toggleMap(){
    if(!D.mapPanel)return;
    const open=D.mapPanel.classList.toggle('hidden');
    if(!open){
        renderRouteScreen();
        mapDrag._scrolledToCurrent=false;
    }
}

// ═══ Toast 通知 ═══
function toast(msg,type='info'){
    const el=document.createElement('div');
    el.className='toast-item '+(type==='error'?'toast-error':type==='success'?'toast-success':'');
    el.textContent=msg;
    D.toast.appendChild(el);
    setTimeout(()=>{
        el.style.animation='toastOut 0.3s ease-out forwards';
        el.addEventListener('animationend',()=>el.remove());
    },GameConfig.TOAST_DURATION);
}

// ═══ 确认弹窗 ═══
function confirmAsync(msg){
    return new Promise(resolve=>{
        D.cfMsg.textContent=msg;
        D.cf.classList.remove('hidden');
        function ok(){cleanup();resolve(true);}
        function cancel(){cleanup();resolve(false);}
        function cleanup(){
            D.cf.classList.add('hidden');
            D.cfOk.removeEventListener('click',ok);
            D.cfCancel.removeEventListener('click',cancel);
        }
        D.cfOk.addEventListener('click',ok);
        D.cfCancel.addEventListener('click',cancel);
    });
}

function showComingSoon(feature){
    toast(`「${feature}」功能开发中，敬请期待`);
}

function as(r){
    if(!r.state)return;
    g.mode=r.state.mode||'single';
    if(g.mode==='level'){g.state=r.state;g.over=['victory','defeat'].includes(r.state.status);}
    else g.state=r.state;
}

function snapshotState(s){return JSON.parse(JSON.stringify(s||{}));}
function flash(el,cls){el.classList.remove('anim-'+cls);void el.offsetWidth;el.classList.add('anim-'+cls);setTimeout(()=>el.classList.remove('anim-'+cls),GameConfig.FLASH_DURATION);}
function al(t){const d=document.createElement('div');d.className='log-entry sys';d.textContent=t;D.la.appendChild(d);D.la.scrollTop=D.la.scrollHeight;}

// ═══ 浮动伤害数字 ═══
function spawnFloatingNumber(targetEl, value, type){
    if(!targetEl||value<=0)return;
    const el=document.createElement('div');
    el.className='floating-number floating-'+type;
    el.textContent=(type==='heal'?'+':'-')+value;
    const rect=targetEl.getBoundingClientRect();
    el.style.left=(rect.left+rect.width/2)+'px';
    el.style.top=(rect.top+rect.height*0.3)+'px';
    document.body.appendChild(el);
    setTimeout(()=>el.remove(),1200);
}

// ═══ 屏幕震动 ═══
function triggerScreenShake(dmg){
    const gc=D.gc;if(!gc)return;
    const intensity=Math.min(dmg>=30?6:dmg>=20?4:2, 8);
    gc.style.setProperty('--shake-x', intensity+'px');
    gc.style.setProperty('--shake-y', intensity+'px');
    gc.classList.add('screen-shake');
    setTimeout(()=>gc.classList.remove('screen-shake'),400);
}

// ═══ 回合横幅 ═══
function showTurnBanner(text){
    const el=document.createElement('div');
    el.className='turn-banner';
    el.textContent=text;
    document.body.appendChild(el);
    setTimeout(()=>{el.classList.add('turn-banner-fade');},800);
    setTimeout(()=>el.remove(),1400);
}

// ═══ 卡牌飞出动画 ═══
function animateCardFlyOut(cardEl, targetEl){
    if(!cardEl)return;
    const clone=cardEl.cloneNode(true);
    clone.className='card card-fly-clone';
    const cRect=cardEl.getBoundingClientRect();
    clone.style.position='fixed';
    clone.style.left=cRect.left+'px';
    clone.style.top=cRect.top+'px';
    clone.style.width=cRect.width+'px';
    clone.style.height=cRect.height+'px';
    clone.style.zIndex='999';
    clone.style.pointerEvents='none';
    clone.style.transition='all 0.35s ease-in';
    document.body.appendChild(clone);
    if(targetEl){
        const tRect=targetEl.getBoundingClientRect();
        requestAnimationFrame(()=>{
            clone.style.left=(tRect.left+tRect.width/2-cRect.width/2)+'px';
            clone.style.top=(tRect.top+tRect.height*0.3)+'px';
            clone.style.opacity='0';
            clone.style.transform='scale(0.5) rotate(15deg)';
        });
    }else{
        requestAnimationFrame(()=>{
            clone.style.opacity='0';
            clone.style.transform='translateY(-60px) scale(0.5)';
        });
    }
    setTimeout(()=>clone.remove(),400);
}