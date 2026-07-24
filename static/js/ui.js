/**
 * 卡牌对决 — 渲染模块
 * 战斗界面、地图、日志、商店、事件等所有渲染函数
 */

// ═══ 卡牌 Tooltip ═══
const KEYWORDS={
    '回响':'下一张打出的牌释放两次',
    '连击':'本回合每打出过一张牌，伤害+2',
    '消耗':'使用后从牌组中永久移除',
    '流血':'每回合造成层数点伤害，持续衰减',
    '中毒':'每回合造成层数点伤害，持续衰减',
    '烧伤':'每回合造成层数点伤害，持续衰减',
    '虚弱':'攻击伤害降低25%',
    '易伤':'受到的伤害增加50%',
    '诅咒':'无法打出，回合结束时自动弃掉',
    '力量':'增加攻击牌造成的伤害',
    '格挡':'抵消伤害，部分格挡会保留',
    '荆棘':'受到攻击时反弹伤害',
    '炮台':'每回合对随机敌人造成伤害',
    '骷髅':'每回合攻击随机敌人',
    '祝福':'每回合回复生命',
    '铁壁':'获得格挡时额外+3',
    '反击':'受到攻击时反击',
    '护盾保留':'回合结束时不消除全部格挡',
    '自动护盾':'每回合自动获得10格挡',
    '双倍':'下一张牌效果翻倍',
};
function showCardTooltip(card,ev){
    if(!D.tt)return;
    const type=card.dataset.type||'';
    const typeNames={attack:'攻击',skill:'技能',power:'能力',curse:'诅咒'};
    const typeName=typeNames[type]||'';
    D.ttName.textContent=card.dataset.name||'';
    D.ttCost.textContent=card.dataset.cost||'0';
    D.ttCost.style.display=(type==='curse'&&!card.dataset.cost)?'none':'';
    D.ttType.textContent=typeName;
    D.ttType.className='tt-type type-'+(type==='attack'?'攻击':type==='skill'?'技能':type==='power'?'能力':'诅咒');
    D.ttDesc.textContent=card.dataset.desc||'';
    const desc=card.dataset.desc||'';
    let kwHtml='';
    for(const [kw,exp] of Object.entries(KEYWORDS)){
        if(desc.includes(kw)){
            kwHtml+=`<span>${kw}</span>: ${exp}<br>`;
        }
    }
    D.ttKw.innerHTML=kwHtml||'';
    D.tt.classList.remove('hidden');
    const rect=card.getBoundingClientRect();
    let x=rect.left+rect.width/2;
    let y=rect.top-10;
    D.tt.style.left=x+'px';
    D.tt.style.top=y+'px';
    D.tt.style.transform='translate(-50%,-100%)';
    const tRect=D.tt.getBoundingClientRect();
    if(tRect.top<0){D.tt.style.top=(rect.bottom+10)+'px';D.tt.style.transform='translate(-50%,0)';}
    if(tRect.left<0)D.tt.style.left='10px';
    if(tRect.right>window.innerWidth)D.tt.style.left=(window.innerWidth-tRect.width-10)+'px';
}
function hideCardTooltip(){
    if(D.tt)D.tt.classList.add('hidden');
}

// ═══ 敌人渲染 ═══
function renderEnemies(){
    D.ea.innerHTML='';
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
        const img=getImageUrl(e.image);
        const body=d?`<div class="dead-label">💀已击败</div>`:
            `<div class="hp-row"><span class="hp-heart">❤️</span><span class="hp-num">${e.hp}</span><span class="hp-max">/${e.max_hp}</span></div>
             <div class="hp-bar"><div class="hp-fill${hp<30?' low':''}" style="width:${hp}%"></div></div>
             <div class="buffs">${e.block>0?formatStatusHtml('block-badge',`🛡️${e.block}`,getStatusDescription('block',e.block)):''}${renderEnemyBuffs(e)}</div>
             ${e.intent?`<div class="intent intent-${e.intent}" title="${e.intent_desc||''}">${getIntentText(e)}</div>`:''}`;
        const p=!d&&g.aim?'<div class="target-prompt">👆点击选择目标</div>':'';
        D.ea.innerHTML+=`<div class="enemy-card ${t}${d?' dead':''}" data-index="${i}">${p}${img?`<div class="portrait"><img src="${img}" onerror="this.style.display='none'"></div>`:''}<div class="enemy-name">${d?'💀 ':''}${e.name}</div>${body}</div>`;
    });
}

// ═══ 手牌渲染 ═══
function renderHand(){
    hideCardTooltip();
    D.ha.innerHTML='';
    const h=g.state?.hand;
    if(!h||h.length===0){D.ha.innerHTML='<div class="hand-empty">🃏手牌为空</div>';return;}
    const prevHand=g.prev?.hand||[];
    const isNew=h.length>prevHand.length;
    h.forEach((c,i)=>{
        const cp=c.playable&&!g.aim&&isActive()&&!isRewardPhase();
        const sel=g.sel===i;
        const newCard=isNew&&i>=prevHand.length;
        const cls=['card',`card-${c.type}`,cp?'playable':'',sel?'selected':'',!cp&&!sel&&isActive()?'disabled':'',newCard?'card-new':''].filter(Boolean).join(' ');
        D.ha.innerHTML+=`<div class="${cls}" data-index="${i}" data-name="${c.name}" data-cost="${c.cost}" data-type="${c.type}" data-desc="${c.description}" data-upgraded="${c.upgraded||''}"${cp?' draggable="true"':''}>${i<9?`<div class="card-badge">${BG[i]}</div>`:''}<div class="card-cost">${c.cost}</div><div class="card-name">${c.name}</div>${c.self_target&&cp?'<div class="self-tag">🔄自身</div>':''}<div class="card-type">${c.type}</div><div class="card-desc">${c.description}</div>${c.upgraded?'<div class="upgraded">✨升级</div>':''}</div>`;
    });
}

// ═══ 玩家状态渲染 ═══
function renderPlayer(){
    const p=g.state?.player;if(!p)return;
    const hp=Math.max(0,(p.hp/p.max_hp)*100),l=hp<30;
    if(D.pa){if(p.image){D.pa.src=getImageUrl(p.image);D.pa.style.display='block';D.pa.onerror=function(){this.style.display='none'};}else D.pa.style.display='none';}
    if(D.pn)D.pn.textContent=p.name;
    if(D.pf){D.pf.style.width=hp+'%';D.pf.className='hp-fill'+(l?' low':'');}
    if(D.pt)D.pt.innerHTML=`<span class="hp-val">${p.hp}</span><span class="hp-sep">/</span><span class="hp-max-val">${p.max_hp}</span>`;
    if(D.vignette){
        if(hp<15){D.vignette.className='low-hp-vignette danger';}
        else if(hp<30){D.vignette.className='low-hp-vignette warning';}
        else{D.vignette.className='low-hp-vignette hidden';}
    }
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
        ${p.block>0?stat(`🛡️${p.block}`,getStatusDescription('block',p.block),'stat-blk'):''}
        ${p.strength>0?stat(`💪${p.strength}`,getStatusDescription('strength',p.strength)):''}
        ${p.poison>0?stat(`☠️${p.poison}`,getStatusDescription('poison',p.poison)):''}
        ${p.burn>0?stat(`🔥${p.burn}`,getStatusDescription('burn',p.burn)):''}
        ${p.bleed>0?stat(`🩸${p.bleed}`,getStatusDescription('bleed',p.bleed)):''}
        ${p.weak>0?stat(`💫${p.weak}`,getStatusDescription('weak',p.weak)):''}
        ${p.vulnerable>0?stat(`💥${p.vulnerable}`,getStatusDescription('vulnerable',p.vulnerable)):''}
        ${p.curse>0?stat(`🌑${p.curse}`,getStatusDescription('curse',p.curse)):''}
        ${p.blessing>0?stat(`✨${p.blessing}`,getStatusDescription('blessing',p.blessing)):''}
        ${p.thorns>0?stat(`🌿${p.thorns}`,getStatusDescription('thorns',p.thorns)):''}
        ${p.turret_damage>0?stat(`🤖${p.turret_damage}`,getStatusDescription('turret',p.turret_damage)):''}
        ${p.skeletons>0?stat(`💀${p.skeletons}`,getStatusDescription('skeleton',p.skeletons)):''}
        ${p.double_next_card?stat('🔄回响',getStatusDescription('echo',true),'','color:#c084fc;'):''}
        ${p.iron_wall?stat('🏰铁壁',getStatusDescription('iron_wall',true),'','color:#3b82f6;'):''}
        ${p.counter?stat('🔄反击',getStatusDescription('counter',true),'','color:#f59e0b;'):''}
        ${p.block_persist?stat('🧱保留',getStatusDescription('block_persist',true),'','color:#60a5fa;'):''}
        ${p.auto_shield?stat('🛡️自动',getStatusDescription('auto_shield',true),'','color:#38bdf8;'):''}
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
        sb.setAttribute('draggable','true');
        sb.addEventListener('dragstart',e=>{e.dataTransfer.setData('text/plain','skill');e.dataTransfer.effectAllowed='move';sb.classList.add('dragging');});
        sb.addEventListener('dragend',()=>sb.classList.remove('dragging'));
    }else{
        const sb=D.ha.querySelector('.skill-btn');
        if(sb)sb.style.display='none';
    }

    if(g.state){D.pd.textContent=`📚${g.state.deck_count??0}`;D.pi.textContent=`📤${g.state.discard_count??0}`;}

    const gold=p.gold??g.state?.gold??0;
    if(D.pg){
        D.pg.style.display=gold>0||g.mode==='level'?'block':'none';
        D.pg.textContent=`💰 ${gold}`;
    }
}

// ═══ 地图图标 ═══
function renderStageInfo(){
    if(!isLevelMode()){D.mapToggle.classList.add('hidden');return;}
    const s=g.state;if(!s)return;
    const c=s.current_stage+1,t=s.total_stages;
    D.mapToggle.classList.remove('hidden');
    if(D.mapToggleBadge)D.mapToggleBadge.textContent=`${c}/${t}`;
}

// ═══ 奖励/路线 ═══
function renderReward(){
    if(isPathSelectPhase()&&g.state?.branch_choices?.length){
        if(D.mapPanel){
            D.mapPanel.classList.remove('hidden');
            mapDrag._scrolledToCurrent=false;
        }
    }
    renderRouteScreen();
    if(isRewardPhase()&&g.state?.rewards?.length){
        D.rp.classList.remove('hidden');const s=g.state;let nh='<div class="next-stage-preview">领奖后会进入路线选择界面</div>';
        D.rm.innerHTML=`🎉第${s.current_stage+1}/${s.total_stages}层通过！${nh}`;D.rb.innerHTML='';
        s.rewards.forEach(r=>{const b=document.createElement('button');b.className='btn btn-primary';b.innerHTML=r.label;b.title=r.desc||'';b.addEventListener('click',()=>claimReward(r.id));D.rb.appendChild(b);});
    }else D.rp.classList.add('hidden');
}

// ═══ 地图系统 ═══
let mapDrag={on:false,sx:0,sy:0,scrollX:0,scrollY:0};

function renderRouteScreen(){
    if(!D.mapPanel)return;
    if(!isLevelMode()){D.mapPanel.classList.add('hidden');return;}
    const s=g.state;if(!s)return;
    const c=s.current_stage+1,t=s.total_stages;
    if(D.mapPanelProgress)D.mapPanelProgress.textContent=`${c}/${t}`;

    const layers=s.branch_layers||[];
    if(!layers.length){D.routeMap.innerHTML='';D.mapSvg.innerHTML='';return;}

    const canvas=D.mapPanelCanvas;
    const nodeGap=90, layerGap=100, padX=80, padY=60;
    const totalLayers=layers.length;
    const maxNodes=Math.max(...layers.map(l=>l.length),1);
    const canvasW=Math.max(maxNodes*nodeGap+padX*2, canvas.clientWidth);
    const canvasH=totalLayers*layerGap+padY*2;

    D.mapSvg.style.width=canvasW+'px';
    D.mapSvg.style.height=canvasH+'px';
    D.mapSvg.setAttribute('viewBox',`0 0 ${canvasW} ${canvasH}`);
    D.routeMap.style.width=canvasW+'px';
    D.routeMap.style.height=canvasH+'px';

    const nodeMap={};
    layers.forEach((layer,li)=>{
        const nCount=layer.length;
        const startX=canvasW/2-(nCount-1)*nodeGap/2;
        layer.forEach((n,ni)=>{
            const x=startX+ni*nodeGap;
            const y=padY+li*layerGap;
            nodeMap[n.id]={x,y,node:n};
        });
    });

    let svgHtml='';
    Object.values(nodeMap).forEach(({x,y,node:n})=>{
        if(!n.next||!n.next.length)return;
        n.next.forEach(nid=>{
            const to=nodeMap[nid];
            if(!to)return;
            const visited=n.visited&&to.node.visited;
            const active=n.current;
            const stroke=visited?'rgba(246,201,64,.5)':active?'rgba(246,201,64,.35)':'rgba(255,255,255,.12)';
            const width=visited?2:active?1.5:1;
            svgHtml+=`<line x1="${x}" y1="${y}" x2="${to.x}" y2="${to.y}" stroke="${stroke}" stroke-width="${width}" stroke-linecap="round"/>`;
        });
    });
    D.mapSvg.innerHTML=svgHtml;

    let nodesHtml='';
    Object.values(nodeMap).forEach(({x,y,node:n})=>{
        const rt=n.route_type||'';
        const tc=rt==='normal'?'combat':rt==='elite'?'elite':rt==='event'?'event':rt==='campfire'?'campfire':rt==='shop'?'shop':rt==='boss'?'boss':'';
        const cls=['route-map-node',`type-${tc}`,n.visited?'visited':'',n.current?'current':'',n.available?'available':''].filter(Boolean).join(' ');
        nodesHtml+=`<div class="${cls}" data-tip="${n.name}" style="left:${x}px;top:${y}px;" title="${n.name}">${n.icon||'●'}<span class="node-layer">${n.layer+1}</span></div>`;
    });
    D.routeMap.innerHTML=nodesHtml;

    if(isPathSelectPhase()&&s.branch_choices?.length){
        D.routeChoices.innerHTML='<div class="route-choices-header">选择下一条路线</div>'+s.branch_choices.map(b=>{
            const rt=b.route||'';const tc=rt==='战斗'?'combat':rt==='精英'?'elite':rt==='事件'?'event':rt==='营火'?'campfire':rt==='商店'?'shop':rt==='Boss'?'boss':'';
            const enemies=b.enemies.map(e=>`<span>${e.name}<small>❤️${e.hp}</small></span>`).join('');
            const risk='★'.repeat(b.risk||1)+'☆'.repeat(Math.max(0,4-(b.risk||1)));
            return `<button class="route-card type-${tc}" data-node="${b.id}">
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
    }else{
        D.routeChoices.innerHTML='';
    }

    if(!mapDrag._scrolledToCurrent){
        const curNode=nodeMap[s.current_node_id];
        if(curNode){
            const sx=curNode.x-canvas.clientWidth/2;
            const sy=curNode.y-canvas.clientHeight/2+layerGap/2;
            canvas.scrollTo({left:Math.max(0,sx),top:Math.max(0,sy),behavior:'instant'});
        }
        mapDrag._scrolledToCurrent=true;
    }
}

function initMapDrag(){
    const canvas=D.mapPanelCanvas;
    if(!canvas)return;
    canvas.addEventListener('mousedown',e=>{
        if(e.target.closest('.route-map-node')||e.target.closest('.route-card'))return;
        mapDrag.on=true;
        mapDrag.sx=e.clientX;
        mapDrag.sy=e.clientY;
        mapDrag.scrollX=canvas.scrollLeft;
        mapDrag.scrollY=canvas.scrollTop;
        canvas.classList.add('grabbing');
        e.preventDefault();
    });
    window.addEventListener('mousemove',e=>{
        if(!mapDrag.on)return;
        const dx=e.clientX-mapDrag.sx;
        const dy=e.clientY-mapDrag.sy;
        canvas.scrollLeft=mapDrag.scrollX-dx;
        canvas.scrollTop=mapDrag.scrollY-dy;
    });
    window.addEventListener('mouseup',()=>{
        if(mapDrag.on){mapDrag.on=false;canvas.classList.remove('grabbing');}
    });
}

function handleMapKeys(e){
    const canvas=D.mapPanelCanvas;
    if(!canvas)return false;
    const k=e.key;
    const step=120;
    switch(k){
        case 'ArrowUp': canvas.scrollBy({top:-step,behavior:'instant'}); return true;
        case 'ArrowDown': canvas.scrollBy({top:step,behavior:'instant'}); return true;
        case 'ArrowLeft': canvas.scrollBy({left:-step,behavior:'instant'}); return true;
        case 'ArrowRight': canvas.scrollBy({left:step,behavior:'instant'}); return true;
        case 'Escape': D.mapPanel.classList.add('hidden'); return true;
    }
    return false;
}

// ═══ 日志渲染 ═══
function renderLog(){
    D.la.innerHTML='';const ms=g.state?.messages;
    if(!ms||ms.length===0){D.la.innerHTML='<div class="log-entry sys">游戏开始...</div>';return;}
    ms.forEach(m=>{let c='log-entry';if(/回合/.test(m)&&/[──第]/.test(m))c+=' turn';else if(/伤害|打击|受到/.test(m))c+=' dmg';else if(/回复|治疗|恢复/.test(m))c+=' heal';else if(/格挡|铁壁/.test(m))c+=' block';else if(/中毒|烧伤|虚弱|易伤/.test(m))c+=' buff';else if(/胜利|恭喜|通关/.test(m))c+=' victory';else if(/击败|倒下/.test(m))c+=' defeat';else if(/──|战斗开始|取消|休息|力量提升|奖励/.test(m)||m.includes('🎁')||m.includes('✅'))c+=' sys';D.la.innerHTML+=`<div class="${c}">${m}</div>`;});
    D.la.scrollTop=D.la.scrollHeight;
}

// ═══ 按钮状态 ═══
function renderButtons(){
    if(g.over){D.et.style.display='none';D.ca.style.display='none';D.rt.style.display='flex';D.rt.innerHTML='🔄再来一局[R]';return;}
    if(g.aim){D.et.style.display='none';D.ca.style.display='flex';D.rt.style.display='flex';D.rt.innerHTML='🔄重新开始[R]';return;}
    if(isRewardPhase()||isPathSelectPhase()){D.et.style.display='none';D.ca.style.display='none';D.rt.style.display='none';return;}
    if(isActive()){D.et.style.display='flex';D.ca.style.display='none';D.rt.style.display='flex';D.rt.innerHTML='🔄重新开始[R]';}
    else{D.et.style.display='none';D.ca.style.display='none';D.rt.style.display='none';}
}

// ═══ 动画 ═══
function renderAnimations(){
    const p=g.prev,n=g.state;if(!p||!n)return;
    const pp=p.player||{},np=n.player||{};
    const pc=$('player-area');
    if(pc){
        if((np.hp??0)<(pp.hp??0)){
            flash(pc,'hit');
            const dmg=pp.hp-np.hp;
            spawnFloatingNumber(pc,dmg,'damage');
            SFX.play('card_hit');
            if(dmg>=20)triggerScreenShake(dmg);
        }
        else if((np.block??0)>(pp.block??0)){
            flash(pc,'guard');
            const blk=np.block-pp.block;
            spawnFloatingNumber(pc,blk,'block');
            SFX.play('block');
        }
        if((np.hp??0)>(pp.hp??0)){
            const heal=np.hp-pp.hp;
            spawnFloatingNumber(pc,heal,'heal');
            SFX.play('heal');
        }
        if((np.poison??0)<(pp.poison??0)||(np.burn??0)<(pp.burn??0)||(np.bleed??0)<(pp.bleed??0))flash(pc,'status-damage');
    }
    // 回合横幅
    const prevTurn=p.turn||0, curTurn=n.turn||0;
    if(curTurn>prevTurn){
        showTurnBanner('⚔️ 你的回合');
        SFX.play('turn_start');
    } else if(curTurn===prevTurn && prevTurn>0 && (p._enemy_turn!==n._enemy_turn)){
        showTurnBanner('💀 敌人回合');
        SFX.play('enemy_attack');
    }
    // 敌人动画
    (n.enemies||[]).forEach((e,i)=>{
        const old=(p.enemies||[])[i]||{};
        const el=D.ea.querySelector(`.enemy-card[data-index="${i}"]`);
        if(!el)return;
        if(old.alive&&!e.alive){
            el.classList.add('death-dissolve');
            SFX.play('enemy_death');
            setTimeout(()=>el.classList.remove('death-dissolve'),800);
        }
        if((e.hp??0)<(old.hp??0)){
            flash(el,'hit');
            const dmg=old.hp-e.hp;
            spawnFloatingNumber(el,dmg,'damage');
            SFX.play('card_hit');
            if(dmg>=20)triggerScreenShake(dmg);
        }
        else if((e.block??0)>(old.block??0)){
            flash(el,'guard');
            const blk=e.block-old.block;
            spawnFloatingNumber(el,blk,'block');
            SFX.play('block');
        }
        if((e.poison??0)<(old.poison??0)||(e.burn??0)<(old.burn??0)||(e.bleed??0)<(old.bleed??0))flash(el,'status-damage');
    });
}

function renderScreen(){if(!g.state)return;renderStageInfo();renderEnemies();renderHand();renderPlayer();renderLog();renderReward();renderButtons();updateShortcutBar();renderShop();renderEventOverlay();renderDefeatOverlay();renderAnimations();g.prev=snapshotState(g.state);}

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
}

// ═══ 事件/营火 ═══
function renderEventOverlay(){
    if(!D.ev)return;
    const ed=g.state?.event_data;
    const isNonCombat=g.state?.is_non_combat;
    const nodeType=g.state?.current_node?.route_type;
    const show=(isNonCombat&&(nodeType==='event'||nodeType==='campfire')&&ed);
    D.ev.classList.toggle('hidden',!show);
    if(!show)return;
    D.evIcon.textContent=ed.icon||'❔';
    D.evTitle.textContent=ed.title||'事件';
    D.evMsg.textContent=ed.message||'';
}

// ═══ 失败弹窗 ═══
function renderDefeatOverlay(){
    if(!D.df)return;
    const show=g.over&&g.state?.status==='defeat';
    D.df.classList.toggle('hidden',!show);
    if(!show)return;
    const s=g.state;
    D.dfMsg.textContent=`在第 ${s.current_stage+1}/${s.total_stages} 层倒下了...`;
    const rt=s.current_node?.route_type;
    const canRetry=rt&&!['campfire','shop','event'].includes(rt);
    if(D.dfRetry){
        D.dfRetry.style.display=canRetry?'':'none';
        if(!canRetry)D.dfRetry.title='非战斗节点无法重试';
    }
}

// ═══ 牌堆查看 ═══
function fmtCard(c){
    return `<div class="pile-card card-${c.type}">
        <span class="pile-card-cost">${c.cost}</span>
        <span class="pile-card-name">${c.name}${c.upgraded?' ✨':''}</span>
        <span class="pile-card-type">${c.type}</span>
        <span class="pile-card-desc">${c.description}</span>
    </div>`;
}
function showPilePopup(title,cards){
    const old=q('.pile-popup-overlay');if(old)old.remove();
    const ov=document.createElement('div');ov.className='pile-popup-overlay';
    ov.innerHTML=`<div class="pile-popup">
        <div class="pile-popup-head"><strong>${title}</strong><button class="btn btn-ghost pile-popup-close">✕</button></div>
        <div class="pile-popup-body">${cards&&cards.length?cards.map(fmtCard).join(''):'<div class="hand-empty">暂无卡牌</div>'}</div>
        <div class="pile-popup-hint">点击空白处或按 Esc 关闭</div>
    </div>`;
    document.body.appendChild(ov);
}