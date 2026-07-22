/**
 * 卡牌对决 v5 — 角色→模式 完整流程
 */
const API = {
    async request(m,u,b){
        const o={method:m,headers:{'Content-Type':'application/json'}};
        if(b)o.body=JSON.stringify(b);
        return(await fetch(u,o)).json();
    },
    newGame(m,c){return this.request('POST','/api/new-game',{mode:m,character:c});},
    startLevel(d,c){return this.request('POST','/api/start-level',{difficulty:d,character:c});},
    startCustom(e,h,c){return this.request('POST','/api/start-custom',{enemies:e,player_hp:h,character:c});},
    getState(){return this.request('GET','/api/game-state');},
    playCard(ci,ti){return this.request('POST','/api/play-card',{card_index:ci,target_index:ti});},
    endTurn(){return this.request('POST','/api/end-turn');},
    claimReward(id){return this.request('POST','/api/claim-reward',{reward_id:id});},
    chooseBranch(id){return this.request('POST','/api/choose-branch',{node_id:id});},
    useSkill(){return this.request('POST','/api/use-skill',{});},
    openShop(){return this.request('POST','/api/open-shop',{});},
    buyItem(id){return this.request('POST','/api/buy-item',{item_id:id});},
    leaveShop(){return this.request('POST','/api/leave-shop',{});},
};

let g = {mode:'single',state:null,prev:null,sel:null,aim:false,busy:false,help:false,over:false,char:'warrior'};
let D = {};

const ET = [
    {name:'哥布林',hp:30,dmg:6},{name:'史莱姆',hp:40,dmg:5},
    {name:'火焰领主',hp:55,dmg:9},{name:'寒冰法师',hp:45,dmg:7},{name:'暗影领主',hp:80,dmg:12},
    {name:'毒沼史莱姆',hp:45,dmg:7},{name:'熔岩犬',hp:60,dmg:10},{name:'镜像怪',hp:65,dmg:10},
    {name:'护卫队长',hp:70,dmg:8},{name:'诅咒法师',hp:70,dmg:11},
];

function $(s){return document.getElementById(s);}
function q(s){return document.querySelector(s);}
function qa(s){return document.querySelectorAll(s);}

function cache(){
    D={
        modal:$('mode-modal'), stepChar:$('step-char'), stepMode:$('step-mode'),
        stepBar:qa('.step'), charSelect:$('char-select'),
        charOpts:qa('#char-select .char-option'), charNext:$('char-next'),
        modeSubtitle:$('mode-subtitle'), modeBack:$('mode-back'), customBack:$('custom-back'),
        tabBtns:qa('.tab-btn'), tabPanels:qa('.tab-panel'),
        mN:$('mode-normal'),mE:$('mode-elite'),mB:$('mode-boss'),
        mL:$('mode-level'),mLH:$('mode-level-hard'),mLHe:$('mode-level-hell'),
        cEnemies:$('custom-enemies'),cAdd:$('custom-add-enemy'),
        cStart:$('custom-start'),cHp:$('custom-player-hp'),
        presetBtns:qa('.preset-btn'),
        stage:$('stage-info'),
        routeOverlay:$('route-overlay'), routeMap:$('route-map'),
        routeChoices:$('route-choices'), routeCurrent:$('route-current'),
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
    };
}

const IM='/images/', IC={攻击:'⚔️',防御:'🛡️',强化:'💪',毒液:'☠️',灼咬:'🔥',镜像:'🪞',守护:'🛡️',诅咒:'🌑',虚弱:'💫'}, BG='①②③④⑤⑥⑦⑧⑨';
const ST={
    block:{name:'格挡',desc:'抵消即将受到的伤害，通常在回合结束后清空。'},
    strength:{name:'力量',desc:'提高攻击造成的伤害。'},
    poison:{name:'中毒',desc:'回合结束受到层数伤害，然后层数 -1。'},
    burn:{name:'烧伤',desc:'回合结束受到层数伤害，然后层数 -1。'},
    bleed:{name:'流血',desc:'回合结束受到层数伤害，然后层数 -1。'},
    weak:{name:'虚弱',desc:'降低攻击伤害，层数会随回合递减。'},
    vulnerable:{name:'易伤',desc:'受到的伤害提高，层数会随回合递减。'},
    curse:{name:'诅咒',desc:'受到伤害时额外受到诅咒层数的伤害。'},
    blessing:{name:'祝福',desc:'每回合开始获得对应层数的格挡。'},
    thorns:{name:'反伤',desc:'被敌人攻击时对攻击者造成反击伤害。'},
    turret:{name:'炮台',desc:'每回合开始自动攻击首个存活敌人。'},
    skeleton:{name:'骷髅',desc:'每回合开始自动攻击首个存活敌人。'},
    echo:{name:'回响',desc:'下一张打出的牌释放两次，触发后消失。'},
    iron_wall:{name:'铁壁',desc:'防御能力强化，格挡会更稳定地保留或产生防御收益。'},
    counter:{name:'反击',desc:'受到攻击后触发反击效果。'},
    block_persist:{name:'格挡保留',desc:'回合结束后格挡不会完全清空。'},
    auto_shield:{name:'自动护盾',desc:'每回合开始自动获得护盾。'},
    relic:{name:'遗物',desc:'遗物提供持续被动效果。'}
};
function iu(n){return n?IM+n:'';}
function ii(i){return IC[i]||'❓';}
function it(e){return `${ii(e.intent)} ${e.intent_text||`${e.intent}${e.intent_value?` ${e.intent_value}`:''}`}`;}
function sd(k,v){
    const s=ST[k]||{name:k,desc:''};
    const n=(v===true||v===undefined||v===null)?'':`：当前 ${v}`;
    return `${s.name}${n}。${s.desc}`;
}
function esc(s){return String(s||'').replace(/"/g,'&quot;');}
function sf(cls,txt,title){const t=esc(title);return `<span class="${cls} has-tip" title="${t}" aria-label="${t}" data-tip="${t}">${txt}</span>`;}
function stat(txt,title,extra='',style=''){const t=esc(title);return `<div class="stat has-tip ${extra}" style="${style}" title="${t}" aria-label="${t}" data-tip="${t}">${txt}</div>`;}
function bh(e){
    let h='';
    if(e.strength>0)h+=sf('buff buff-str',`💪${e.strength}`,sd('strength',e.strength));
    if(e.poison>0)h+=sf('buff buff-psn',`☠️${e.poison}`,sd('poison',e.poison));
    if(e.burn>0)h+=sf('buff buff-brn',`🔥${e.burn}`,sd('burn',e.burn));
    if(e.bleed>0)h+=sf('buff buff-bld',`🩸${e.bleed}`,sd('bleed',e.bleed));
    if(e.weak>0)h+=sf('buff buff-wk',`💫${e.weak}`,sd('weak',e.weak));
    if(e.vulnerable>0)h+=sf('buff buff-vul',`💥${e.vulnerable}`,sd('vulnerable',e.vulnerable));
    if(e.curse>0)h+=sf('buff buff-crs',`🌑${e.curse}`,sd('curse',e.curse));
    return h;
}
function act(){return g.state&&!g.over;}
function aen(){return g.state?.enemies?.filter(e=>e.alive)||[];}
function isL(){return g.mode==='level';}
function lvS(){return g.state?.status;}
function isR(){return isL()&&lvS()==='stage_clear';}
function isP(){return isL()&&lvS()==='path_select';}

function scb(){
    if(!D.modal.classList.contains('hidden')){D.sb.textContent='[←]返回 [→]确认 [Esc]关闭';return;}
    if(g.help){D.sb.textContent='[Esc]关闭帮助';return;}
    if(g.over){D.sb.textContent='[R]重新开始 [H]帮助';return;}
    if(g.aim){D.sb.textContent='👆点击敌人或[1-9]选目标 [Esc/右键]取消';return;}
    if(isR()){D.sb.textContent='🎁选择奖励后选择路线';return;}
    if(isP()){D.sb.textContent='🧭选择下一条路线继续前进';return;}
    if(act()){D.sb.textContent='[1-9]出牌 [E/Enter]结束 [R]重开 [H]帮助';return;}
    D.sb.textContent='按 [R] 开始';
}
function th(){g.help=!g.help;D.ho.classList.toggle('hidden',!g.help);scb();}
function cs(){if(g.aim||g.sel!==null){g.aim=false;g.sel=null;ra();return true;}return false;}
function cm(){D.modal.classList.add('hidden');}
function om(){D.modal.classList.remove('hidden');ss('char');scb();}

function ss(s){
    const c=s==='char';
    D.stepChar.classList.toggle('active',c);
    D.stepMode.classList.toggle('active',!c);
    D.stepBar.forEach(s=>s.classList.toggle('active',s.dataset.step===(c?'1':'2')));
}
function st(t){
    D.tabBtns.forEach(b=>b.classList.toggle('active',b.dataset.tab===t));
    D.tabPanels.forEach(p=>p.classList.toggle('active',p.id==='tab-'+t));
    if(t==='custom'&&D.cEnemies.children.length===0)aer();
}

// ═══ 角色 ═══
function sc(id){
    g.char=id;
    D.charOpts.forEach(o=>o.classList.toggle('active',o.dataset.char===id));
    D.cHp.value={warrior:80,elf:65,wizard:55,paladin:90,assassin:60,priest:75,mechanist:70,necromancer:58,alchemist:68}[id]||80;
}
function cc(){
    const a=D.charSelect.querySelector('.char-option.active');
    sc(a?a.dataset.char:'warrior');
    D.modeSubtitle.textContent=`⚔️ ${{warrior:'勇者',elf:'精灵',wizard:'巫师',paladin:'圣骑士',assassin:'刺客',priest:'牧师',mechanist:'机械师',necromancer:'亡灵法师',alchemist:'炼金术士'}[g.char]} · 选择战斗模式`;
    ss('mode');
}

// ═══ 自定义 ═══
function aer(d){
    const r=document.createElement('div');r.className='custom-enemy-row';
    const dt=d||{}; const names=ET.map(e=>e.name);
    const idx=Math.max(0,names.indexOf(dt.n||'哥布林'));
    r.innerHTML=`
        <select class="ce-n">${names.map((n,i)=>`<option value="${n}"${i===idx?' selected':''}>${n}</option>`).join('')}</select>
        <label>HP<input type="number" class="ce-h" value="${dt.hp||ET[idx].hp}"></label>
        <label>攻击<input type="number" class="ce-d" value="${dt.d||ET[idx].dmg}"></label>
        <button class="btn-ghost-sm ce-x">✕</button>`;
    r.querySelector('.ce-n').addEventListener('change',function(){
        const f=ET.find(e=>e.name===this.value);
        if(f){r.querySelector('.ce-h').value=f.hp;r.querySelector('.ce-d').value=f.dmg;}
    });
    r.querySelector('.ce-x').addEventListener('click',()=>{r.remove();D.cAdd.style.display=D.cEnemies.children.length>=5?'none':'';});
    D.cAdd.style.display=D.cEnemies.children.length>=4?'none':'';
    D.cEnemies.appendChild(r);
}
function gc(){
    const en=[];
    D.cEnemies.querySelectorAll('.custom-enemy-row').forEach(r=>{
        const n=r.querySelector('.ce-n')?.value||'哥布林';
        const hp=+(r.querySelector('.ce-h')?.value)||30;
        const dmg=+(r.querySelector('.ce-d')?.value)||6;
        en.push({name:n,hp,damage:dmg});
    });
    return {enemies:en,playerHp:+D.cHp.value||80,character:g.char||'warrior'};
}
async function scm(){
    if(D.cEnemies.children.length===0)aer();
    const c=gc();
    console.log('[CUSTOM] sending:',JSON.stringify(c));
    if(!c.enemies.length){ser('❌ 至少需要1个敌人');return;}
    g.state=null;g.prev=null;
    try{
        const r=await API.startCustom(c.enemies,c.playerHp,c.character);
        console.log('[CUSTOM] response:',r.success? 'OK':'FAIL',r.error||'');
        if(!r.success){ser('❌ '+r.error);return;}
        cm();g.mode='custom';g.prev=null;g.state=r.state;ra();scb();
    }catch(e){console.error(e);ser('❌ 请求异常: '+e.message);}
}
function ser(m){
    const c=D.cEnemies.closest('.tab-panel');if(!c)return;
    const o=c.querySelector('.ce-err');if(o)o.remove();
    const e=document.createElement('div');e.className='ce-err';e.textContent=m;
    c.querySelector('.custom-actions')?.after(e);
}
function ap(j){
    try{const d=JSON.parse(j);D.cEnemies.innerHTML='';d.forEach(e=>aer(e));}catch(e){console.error(e);}
}

// ═══ 渲染 ═══
function re(){
    D.ea.innerHTML='';
    // 非战斗节点（营火、商店、事件）显示提示
    if(g.state?.is_non_combat){
        const node=g.state?.current_node||{};
        let msg='';
        if(node.route_type==='campfire')msg='🔥 营火休整中...';
        else if(node.route_type==='shop')msg='🛒 商店营业中...';
        else if(node.route_type==='event')msg='❔ 事件已触发...';
        else msg='📋 非战斗节点';
        D.ea.innerHTML=`<div style="color:var(--text-muted);text-align:center;padding:40px;font-size:18px;">${msg}</div>`;
        return;
    }
    if(!g.state?.enemies){D.ea.innerHTML='<div style="color:var(--text-muted);text-align:center;padding:30px;">🃏 等待游戏开始</div>';return;}
    g.state.enemies.forEach((e,i)=>{
        const d=!e.alive,hp=Math.max(0,(e.hp/e.max_hp)*100);
        const t=!d&&g.aim?'targetable':'';
        const img=iu(e.image);
        const body=d?`<div class="dead-label">💀已击败</div>`:
            `<div class="hp-row"><span class="hp-heart">❤️</span><span class="hp-num">${e.hp}</span><span class="hp-max">/${e.max_hp}</span></div>
             <div class="hp-bar"><div class="hp-fill${hp<30?' low':''}" style="width:${hp}%"></div></div>
             <div class="buffs">${e.block>0?sf('block-badge',`🛡️${e.block}`,sd('block',e.block)):''}${bh(e)}</div>
             ${e.intent?`<div class="intent intent-${e.intent}" title="${e.intent_desc||''}">${it(e)}</div>`:''}`;
        const p=!d&&g.aim?'<div class="target-prompt">👆点击选择目标</div>':'';
        D.ea.innerHTML+=`<div class="enemy-card ${t}${d?' dead':''}" data-index="${i}">${p}${img?`<div class="portrait"><img src="${img}" onerror="this.style.display='none'"></div>`:''}<div class="enemy-name">${d?'💀 ':''}${e.name}</div>${body}</div>`;
    });
    if(g.aim)D.ea.querySelectorAll('.enemy-card.targetable').forEach(el=>{el.addEventListener('click',()=>pt(+el.dataset.index));});
}
function rh(){
    D.ha.innerHTML='';
    const h=g.state?.hand;
    if(!h||h.length===0){D.ha.innerHTML='<div class="hand-empty">🃏手牌为空</div>';return;}
    h.forEach((c,i)=>{
        const cp=c.playable&&!g.aim&&act()&&!isR();
        const sel=g.sel===i;
        const cls=['card',`card-${c.type}`,cp?'playable':'',sel?'selected':'',!cp&&!sel&&act()?'disabled':''].filter(Boolean).join(' ');
        D.ha.innerHTML+=`<div class="${cls}" data-index="${i}"><div class="card-cost">${c.cost}</div>${i<9?`<div class="card-badge">${BG[i]}</div>`:''}<div class="card-name">${c.name}</div>${c.self_target&&cp?'<div class="self-tag">🔄自身</div>':''}<div class="card-type">${c.type}</div><div class="card-desc">${c.description}</div>${c.upgraded?'<div class="upgraded">✨升级</div>':''}</div>`;
    });
    D.ha.querySelectorAll('.card.playable').forEach(el=>{el.addEventListener('click',()=>oc(+el.dataset.index));});
    D.ha.querySelectorAll('.card.selected, .card.playable').forEach(el=>{el.addEventListener('contextmenu',e=>{e.preventDefault();cs();});});
}
function rp(){
    const p=g.state?.player;if(!p)return;
    const hp=Math.max(0,(p.hp/p.max_hp)*100),l=hp<30;
    if(D.pa){if(p.image){D.pa.src=iu(p.image);D.pa.style.display='block';D.pa.onerror=function(){this.style.display='none'};}else D.pa.style.display='none';}
    if(D.pn)D.pn.textContent=p.name;
    if(D.pf){D.pf.style.width=hp+'%';D.pf.className='hp-fill'+(l?' low':'');}
    if(D.pt)D.pt.innerHTML=`<span class="hp-val">${p.hp}</span><span class="hp-sep">/</span><span class="hp-max-val">${p.max_hp}</span>`;
    const e=D.eo;
    if(e){
        const cur=p.energy??0;
        const max=p.max_energy||3;
        e.className='energy-orbs'+(cur>max?' overflow':'');
        e.innerHTML=`<span class="energy-icon">⚡</span><span class="energy-current">${cur}</span><span class="energy-sep">/</span><span class="energy-max">${max}</span>`;
        e.title=`当前能量 ${cur} / 最大能量 ${max}${cur>max?'（已溢出）':''}`;
    }
    const relics=(g.state?.relics||[]).map(r=>stat(r.icon,`遗物：${r.name}。${r.desc}`,'relic-stat')).join('');
    D.ps.innerHTML=`
        ${p.block>0?stat(`🛡️${p.block}`,sd('block',p.block),'stat-blk'):''}
        ${p.strength>0?stat(`💪${p.strength}`,sd('strength',p.strength)):''}
        ${p.poison>0?stat(`☠️${p.poison}`,sd('poison',p.poison)):''}
        ${p.burn>0?stat(`🔥${p.burn}`,sd('burn',p.burn)):''}
        ${p.bleed>0?stat(`🩸${p.bleed}`,sd('bleed',p.bleed)):''}
        ${p.weak>0?stat(`💫${p.weak}`,sd('weak',p.weak)):''}
        ${p.vulnerable>0?stat(`💥${p.vulnerable}`,sd('vulnerable',p.vulnerable)):''}
        ${p.curse>0?stat(`🌑${p.curse}`,sd('curse',p.curse)):''}
        ${p.blessing>0?stat(`✨${p.blessing}`,sd('blessing',p.blessing)):''}
        ${p.thorns>0?stat(`🌿${p.thorns}`,sd('thorns',p.thorns)):''}
        ${p.turret_damage>0?stat(`🤖${p.turret_damage}`,sd('turret',p.turret_damage)):''}
        ${p.skeletons>0?stat(`💀${p.skeletons}`,sd('skeleton',p.skeletons)):''}
        ${p.double_next_card?stat('🔄回响',sd('echo',true),'','color:#c084fc;'):''}
        ${p.iron_wall?stat('🏰铁壁',sd('iron_wall',true),'','color:#3b82f6;'):''}
        ${p.counter?stat('🔄反击',sd('counter',true),'','color:#f59e0b;'):''}
        ${p.block_persist?stat('🧱保留',sd('block_persist',true),'','color:#60a5fa;'):''}
        ${p.auto_shield?stat('🛡️自动',sd('auto_shield',true),'','color:#38bdf8;'):''}
        ${relics}
    `.trim();

    const sk=g.state?.player?.skill;
    if(sk&&sk.name&&sk.cost>0){
        let sb=D.ha.querySelector('.skill-btn');
        if(!sb){
            sb=document.createElement('button');sb.className='skill-btn';
            D.ha.appendChild(sb);
        }
        sb.innerHTML=`${sk.icon||'⚡'} ${sk.name} (${sk.cost}费)${p.skill_used_this_turn?' · 已使用':''}`;
        sb.title=p.skill_used_this_turn?'本回合已经使用过技能':sk.desc;
        sb.disabled=!sk.usable;
        sb.style.display='';
        sb.onclick=useSkill;
    }else{
        const sb=D.ha.querySelector('.skill-btn');
        if(sb)sb.style.display='none';
    }

    if(g.state){D.pd.textContent=`📚${g.state.deck_count??0}`;D.pi.textContent=`📤${g.state.discard_count??0}`;}

    // 金币显示
    const gold=p.gold??g.state?.gold??0;
    if(D.pg){
        D.pg.style.display=gold>0||g.mode==='level'?'block':'none';
        D.pg.textContent=`💰 ${gold}`;
    }
}
function rsi(){
    if(!isL()){D.stage.style.display='none';return;}
    D.stage.style.display='flex';const s=g.state;if(!s)return;
    const c=s.current_stage+1,t=s.total_stages;
    const rows=(s.branch_layers||[]).map(layer=>`<div class="map-layer">${layer.map(n=>`<div class="map-node ${n.visited?'visited':''} ${n.current?'current':''} ${n.available?'available':''}" title="${n.name}">${n.icon||'●'}<span>${n.layer+1}</span></div>`).join('')}</div>`).join('');
    D.stage.innerHTML=`<div class="stage-map">${rows}</div><div class="stage-label">${c}/${t}</div><div class="stage-chapter">${s.chapter||''}</div><div class="stage-name">${s.stage_name||''}</div>`;
}
function rrw(){
    renderRouteScreen();
    if(isR()&&g.state?.rewards?.length){
        D.rp.classList.remove('hidden');const s=g.state;let nh='<div class="next-stage-preview">领奖后会进入路线选择界面</div>';
        D.rm.innerHTML=`🎉第${s.current_stage+1}/${s.total_stages}层通过！${nh}`;D.rb.innerHTML='';
        s.rewards.forEach(r=>{const b=document.createElement('button');b.className='btn btn-primary';b.innerHTML=r.label;b.title=r.desc||'';b.addEventListener('click',()=>cr(r.id));D.rb.appendChild(b);});
    }else D.rp.classList.add('hidden');
}
function renderRouteScreen(){
    if(!D.routeOverlay)return;
    const open=isP()&&g.state?.branch_choices?.length;
    D.routeOverlay.classList.toggle('hidden',!open);
    if(!open)return;
    const s=g.state, cur=s.current_node||{};
    D.routeCurrent.innerHTML=`当前：${cur.icon||'●'} ${cur.name||''}`;
    D.routeMap.innerHTML=(s.branch_layers||[]).map(layer=>`<div class="route-layer">${layer.map(n=>`<div class="route-node ${n.visited?'visited':''} ${n.current?'current':''} ${n.available?'available':''}" title="${n.name}"><span>${n.icon||'●'}</span><em>${n.layer+1}</em></div>`).join('')}</div>`).join('');
    D.routeChoices.innerHTML=s.branch_choices.map(b=>{
        const enemies=b.enemies.map(e=>`<span>${e.name}<small>❤️${e.hp}</small></span>`).join('');
        const risk='★'.repeat(b.risk||1)+'☆'.repeat(Math.max(0,4-(b.risk||1)));
        return `<button class="route-card" data-node="${b.id}">
            <div class="route-card-icon">${b.icon||'●'}</div>
            <div class="route-card-body">
                <strong>${b.name}</strong>
                <label>${b.route||''}</label>
                <p>${b.desc||''}</p>
                <div class="route-meta"><span>风险 ${risk}</span><span>奖励：${b.reward_hint||'普通奖励'}</span></div>
                <div class="route-enemies">${enemies}</div>
            </div>
        </button>`;
    }).join('');
    D.routeChoices.querySelectorAll('.route-card').forEach(b=>b.addEventListener('click',()=>cb(b.dataset.node)));
}
function rl(){
    D.la.innerHTML='';const ms=g.state?.messages;
    if(!ms||ms.length===0){D.la.innerHTML='<div class="log-entry sys">游戏开始...</div>';return;}
    ms.forEach(m=>{let c='log-entry';if(/回合/.test(m)&&/[──第]/.test(m))c+=' turn';else if(/伤害|打击|受到/.test(m))c+=' dmg';else if(/回复|治疗|恢复/.test(m))c+=' heal';else if(/格挡|铁壁/.test(m))c+=' block';else if(/中毒|烧伤|虚弱|易伤/.test(m))c+=' buff';else if(/胜利|恭喜|通关/.test(m))c+=' victory';else if(/击败|倒下/.test(m))c+=' defeat';else if(/──|战斗开始|取消|休息|力量提升|奖励/.test(m)||m.includes('🎁')||m.includes('✅'))c+=' sys';D.la.innerHTML+=`<div class="${c}">${m}</div>`;});
    D.la.scrollTop=D.la.scrollHeight;
}
function rb(){
    if(g.over){D.et.style.display='none';D.ca.style.display='none';D.rt.style.display='flex';D.rt.innerHTML='🔄再来一局[R]';return;}
    if(g.aim){D.et.style.display='none';D.ca.style.display='flex';D.rt.style.display='flex';D.rt.innerHTML='🔄重新开始[R]';return;}
    if(isR()||isP()){D.et.style.display='none';D.ca.style.display='none';D.rt.style.display='none';return;}
    if(act()){D.et.style.display='flex';D.ca.style.display='none';D.rt.style.display='flex';D.rt.innerHTML='🔄重新开始[R]';}
    else{D.et.style.display='none';D.ca.style.display='none';D.rt.style.display='none';}
}
function snap(s){return JSON.parse(JSON.stringify(s||{}));}
function anim(){
    const p=g.prev,n=g.state;if(!p||!n)return;
    const pp=p.player||{},np=n.player||{};
    const pc=$('player-area');
    if(pc){
        if((np.hp??0)<(pp.hp??0))flash(pc,'hit');
        else if((np.block??0)>(pp.block??0))flash(pc,'guard');
        if((np.poison??0)<(pp.poison??0)||(np.burn??0)<(pp.burn??0)||(np.bleed??0)<(pp.bleed??0))flash(pc,'status-damage');
    }
    (n.enemies||[]).forEach((e,i)=>{
        const old=(p.enemies||[])[i]||{};
        const el=D.ea.querySelector(`.enemy-card[data-index="${i}"]`);
        if(!el)return;
        if((e.hp??0)<(old.hp??0))flash(el,'hit');
        else if((e.block??0)>(old.block??0))flash(el,'guard');
        if((e.poison??0)<(old.poison??0)||(e.burn??0)<(old.burn??0)||(e.bleed??0)<(old.bleed??0))flash(el,'status-damage');
    });
}
function flash(el,cls){el.classList.remove('anim-'+cls);void el.offsetWidth;el.classList.add('anim-'+cls);setTimeout(()=>el.classList.remove('anim-'+cls),520);}
function ra(){if(!g.state)return;rsi();re();rh();rp();rl();rrw();rb();scb();renderShop();renderEventOverlay();anim();g.prev=snap(g.state);}

// ═══ 操作 ═══
function oc(i){
    if(!act()||g.aim||g.busy||isR()||isP())return;
    const c=g.state?.hand?.[i];if(!c||!c.playable)return;
    if(c.self_target){pc(i,0);return;}
    const al=aen();if(!al.length)return;
    if(al.length===1)pc(i,g.state.enemies.indexOf(al[0]));
    else{g.sel=i;g.aim=true;ra();}
}
function pt(ti){if(g.sel!==null){pc(g.sel,ti);g.sel=null;g.aim=false;}}

async function pc(ci,ti){
    if(g.busy)return;g.busy=true;D.ha.style.pointerEvents='none';
    try{const r=await API.playCard(ci,ti);if(!r.success){console.error(r.error);return;}as(r);if(r.battle_ended&&g.mode!=='level')g.over=true;ra();}catch(e){console.error(e);}finally{g.busy=false;D.ha.style.pointerEvents='';}
}
async function et(){
    if(!act()||g.busy)return;if(g.aim||g.sel!==null){cs();return;}
    g.busy=true;D.et.disabled=true;D.et.innerHTML='⏳处理中...';
    try{const r=await API.endTurn();as(r);if(r.battle_ended&&g.mode!=='level')g.over=true;ra();}catch(e){console.error(e);}finally{g.busy=false;D.et.disabled=false;D.et.innerHTML='⏭️结束回合[E]';}
}
async function cr(id){
    if(g.busy)return;g.busy=true;
    try{const r=await API.claimReward(id);as(r);if(r.level_complete)g.over=true;ra();}catch(e){console.error(e);}finally{g.busy=false};
}
async function cb(id){
    if(g.busy)return;g.busy=true;
    try{const r=await API.chooseBranch(id);if(!r.success){console.error(r.error);return;}as(r);ra();}catch(e){console.error(e);}finally{g.busy=false};
}

// ═══ 商店 ═══
function renderShop(){
    if(!D.sh)return;
    const open=g.state?.shop_open&&g.state?.is_non_combat&&g.state?.current_node?.route_type==='shop';
    D.sh.classList.toggle('hidden',!open);
    if(!open)return;
    const s=g.state;
    D.sg.textContent=s.gold||0;
    D.si.innerHTML=(s.shop_items||[]).map(item=>{
        const canBuy=(s.gold||0)>=item.cost;
        return `<div class="shop-item ${canBuy?'':'shop-item-disabled'}">
            <div class="shop-item-icon">${item.icon||'🛒'}</div>
            <div class="shop-item-body">
                <strong>${item.name}</strong>
                <p>${item.desc||''}</p>
                <span class="shop-item-cost">${item.cost}💰</span>
            </div>
            <button class="btn btn-primary btn-sm" data-buy="${item.id}" ${canBuy?'':'disabled'}>
                ${canBuy?'购买':'💰不足'}
            </button>
        </div>`;
    }).join('');
    D.si.querySelectorAll('[data-buy]').forEach(b=>b.addEventListener('click',async function(){
        if(g.busy)return;g.busy=true;
        try{const r=await API.buyItem(this.dataset.buy);if(!r.success){console.error(r.error);}as(r);ra();}catch(e){console.error(e);}finally{g.busy=false};
    }));
}
async function slv(){
    /* 离开商店，进入路线选择 */
    if(g.busy)return;
    g.busy=true;
    try{
        const r=await API.leaveShop();
        if(!r.success){console.error(r.error);return;}
        as(r);ra();
    }catch(e){console.error(e);}finally{g.busy=false};
}
function renderEventOverlay(){
    if(!D.ev)return;
    const ed=g.state?.event_data;
    const isNonCombat=g.state?.is_non_combat;
    const nodeType=g.state?.current_node?.route_type;
    // 营地/事件节点显示弹窗
    const show=(isNonCombat&&(nodeType==='event'||nodeType==='campfire')&&ed);
    D.ev.classList.toggle('hidden',!show);
    if(!show)return;
    D.evIcon.textContent=ed.icon||'❔';
    D.evTitle.textContent=ed.title||'事件';
    D.evMsg.textContent=ed.message||'';
}
async function evContinue(){
    /* 事件弹窗继续：进入路线选择 */
    if(g.busy)return;
    D.ev.classList.add('hidden');
    ra();
}
async function useSkill(){
    if(!act()||g.busy||isR()||isP())return;
    g.busy=true;
    try{const r=await API.useSkill();if(!r.success){console.error(r.error);return;}g.state=r.state;ra();const pc=$('player-area');if(pc)flash(pc,'skill');}catch(e){console.error(e);}finally{g.busy=false};
}

function fmtCard(c){
    return `<div class="pile-card card-${c.type}">
        <span class="pile-card-cost">${c.cost}</span>
        <span class="pile-card-name">${c.name}${c.upgraded?' ✨':''}</span>
        <span class="pile-card-type">${c.type}</span>
        <span class="pile-card-desc">${c.description}</span>
    </div>`;
}
function sp(title,cards){
    const old=q('.pile-popup-overlay');if(old)old.remove();
    const ov=document.createElement('div');ov.className='pile-popup-overlay';
    ov.innerHTML=`<div class="pile-popup">
        <div class="pile-popup-head"><strong>${title}</strong><button class="btn btn-ghost pile-popup-close">✕</button></div>
        <div class="pile-popup-body">${cards&&cards.length?cards.map(fmtCard).join(''):'<div class="hand-empty">暂无卡牌</div>'}</div>
        <div class="pile-popup-hint">点击空白处或按 Esc 关闭</div>
    </div>`;
    document.body.appendChild(ov);
    ov.addEventListener('click',e=>{if(e.target===ov||e.target.closest('.pile-popup-close'))ov.remove();});
}

function as(r){
    if(!r.state)return;
    g.mode=r.state.mode||'single';
    if(g.mode==='level'){g.state=r.state;g.over=['victory','defeat'].includes(r.state.status);}
    else g.state=r.state;
}

async function sgm(m){
    console.log('[GAME] start mode='+m+' char='+g.char);
    cm();g.over=false;g.sel=null;g.aim=false;g.busy=false;g.state=null;g.prev=null;
    try{
        const r=await API.newGame(m,g.char);
        console.log('[GAME] response:',r.success?'OK':'FAIL',r.error||'');
        if(!r.success){alert('启动失败: '+r.error);return;}
        g.mode='single';g.prev=null;g.state=r.state;ra();scb();
    }catch(e){console.error(e);alert('网络错误');}
}
async function sl(d){
    console.log('[LEVEL] start diff='+d+' char='+g.char);
    cm();g.over=false;g.sel=null;g.aim=false;g.busy=false;g.state=null;g.prev=null;
    try{
        const r=await API.startLevel(d,g.char);
        if(!r.success){alert('启动失败: '+r.error);return;}
        g.mode='level';g.prev=null;g.state=r.state;ra();scb();
    }catch(e){console.error(e);alert('网络错误');}
}

// ═══ 键盘 ═══
function hkd(e){
    const k=e.key,mo=!D.modal.classList.contains('hidden');
    const pp=q('.pile-popup-overlay');
    if(pp&&k==='Escape'){pp.remove();e.preventDefault();return;}
    if(mo){
        const onChar=D.stepChar.classList.contains('active');
        if(k==='Escape'){cm();scb();e.preventDefault();return;}
        if(k==='ArrowRight'&&onChar){cc();e.preventDefault();return;}
        if(k==='ArrowLeft'&&!onChar){ss('char');e.preventDefault();return;}
        if(!onChar){if(k==='1'){st('classic');e.preventDefault();}else if(k==='2'){st('level');e.preventDefault();}else if(k==='3'){st('custom');e.preventDefault();}}
        return;
    }
    if(g.help){if(k==='Escape'||k==='h'||k==='H'){th();e.preventDefault();}return;}
    if(k==='Escape'){if(g.aim||g.sel!==null)cs();e.preventDefault();return;}
    if(k==='h'||k==='H'){th();e.preventDefault();return;}
    if(k==='r'||k==='R'||k==='n'||k==='N'){om();e.preventDefault();return;}
    if(isR())return;
    if(k>='1'&&k<='9'){e.preventDefault();if(!act()||g.over)return;const idx=+k-1;const c=g.state?.hand?.[idx];if(c&&c.playable)oc(idx);return;}
    if(k==='e'||k==='E'||k==='Enter'||k===' '){e.preventDefault();if(g.over){om();return;}if(isR())return;et();}
}

// ═══ 初始化 ═══
async function init(){
    cache();

    D.charOpts.forEach(o=>o.addEventListener('click',function(){sc(this.dataset.char);}));
    D.charNext.addEventListener('click',cc);
    D.modeBack.addEventListener('click',()=>ss('char'));
    D.customBack.addEventListener('click',()=>ss('char'));
    D.tabBtns.forEach(b=>b.addEventListener('click',()=>st(b.dataset.tab)));

    D.mN.addEventListener('click',()=>sgm('normal'));
    D.mE.addEventListener('click',()=>sgm('elite'));
    D.mB.addEventListener('click',()=>sgm('boss'));
    D.mL.addEventListener('click',()=>sl('easy'));
    D.mLH.addEventListener('click',()=>sl('hard'));
    D.mLHe.addEventListener('click',()=>sl('hell'));

    D.cAdd.addEventListener('click',()=>aer());
    D.cStart.addEventListener('click',scm);
    D.presetBtns.forEach(b=>b.addEventListener('click',()=>ap(b.dataset.e)));

    D.et.addEventListener('click',et);
    D.ca.addEventListener('click',cs);
    D.rt.addEventListener('click',om);
    D.hb.addEventListener('click',th);

    document.addEventListener('keydown',hkd);
    document.addEventListener('contextmenu',e=>{if(e.target.closest('.game-container')&&(g.aim||g.sel!==null)){e.preventDefault();cs();}});

    D.pd.addEventListener('click',()=>sp(`📚 抽牌堆 (${g.state?.deck_count||0}张)`,g.state?.deck_cards||[]));
    D.pi.addEventListener('click',()=>sp(`📤 弃牌堆 (${g.state?.discard_count||0}张)`,g.state?.discard_cards||[]));
    D.sl.addEventListener('click',slv);
    D.evBtn.addEventListener('click',evContinue);
    scb();

    try{const r=await API.getState();if(r.success){as(r);D.modal.classList.add('hidden');ra();}else D.modal.classList.remove('hidden');}catch{D.modal.classList.remove('hidden');}
}

function al(t){const d=document.createElement('div');d.className='log-entry sys';d.textContent=t;D.la.appendChild(d);D.la.scrollTop=D.la.scrollHeight;}
document.addEventListener('DOMContentLoaded',init);
