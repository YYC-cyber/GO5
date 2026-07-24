/**
 * 卡牌对决 — 菜单、角色选择、模式选择、图鉴、自定义
 */

// ═══ 菜单入口 ═══
function startSinglePlayer(){
    g.menuMode='single';
    hideMainMenu();
    transOut(()=>{
        D.modal.classList.remove('hidden');
        showStep('char');
        updateShortcutBar();
    });
}

async function closeGame(){
    const ok=await confirmAsync('确定要关闭游戏吗？');
    if(ok){
        window.close();
        setTimeout(()=>{toast('请手动关闭浏览器标签页','error');},200);
    }
}

// ═══ 图鉴系统 ═══
async function showCollection(){
    hideMainMenu();
    D.col.classList.remove('hidden');
    try{
        const r=await fetch('/api/collection');
        const j=await r.json();
        g.colData=j.data;
    }catch(e){g.colData=null;}
    renderCollectionTab('cards');
    // 使用事件委托，避免重复绑定导致的内存泄漏
    if(!D.col._hasTabDelegate){
        D.col.addEventListener('click',function(e){
            const tab=e.target.closest('.col-tab');
            if(!tab)return;
            D.colTabs.forEach(t2=>t2.classList.remove('active'));
            tab.classList.add('active');
            renderCollectionTab(tab.dataset.ctab);
        });
        D.col._hasTabDelegate=true;
    }
}

function closeCollection(){
    D.col.classList.add('hidden');
    showMainMenu();
}

function renderCollectionTab(tab){
    if(!D.colContent)return;
    const d=g.colData;
    if(!d){D.colContent.innerHTML='<p style="color:var(--text-dim);padding:20px;">加载失败</p>';return;}
    let html='';
    if(tab==='cards'){
        html=renderCollectionGrid(d.cards,'cards');
    }else if(tab==='enemies'){
        html=renderCollectionGrid(d.enemies,'enemies');
    }else if(tab==='relics'){
        html=renderCollectionGrid(d.relics,'relics');
    }else if(tab==='stats'){
        html=renderStats(d.stats);
    }
    D.colContent.innerHTML=html;
}

function renderCollectionGrid(cat,type){
    const seen=cat.seen||[];
    const all=cat.all||[];
    const seenSet=new Set(seen);
    const progress=seen.length+'/'+cat.total;
    const icons={
        cards:'🃏',enemies:'👾',relics:'🏺',
    };
    let html=`<div class="col-progress">${icons[type]||'📋'} 已收集 ${progress} 项</div>
    <div class="col-grid">`;
    for(const name of all){
        const found=seenSet.has(name);
        const isMystery=type==='enemies'&&!found;
        html+=`<div class="col-item ${found?'':'col-item-hidden'}">
            <span class="col-item-icon">${found?'✅':'❓'}</span>
            <span class="col-item-name ${isMystery?'col-item-mystery':''}">${isMystery?'???':name}</span>
        </div>`;
    }
    html+='</div>';
    return html;
}

function renderStats(stats){
    const cs=stats.char_stats||{};
    let charRows='';
    for(const [cid,info] of Object.entries(cs)){
        charRows+=`<tr>
            <td>${cid}</td>
            <td>${info.wins||0}</td>
            <td>${info.games||0}</td>
            <td>${info.highest_stage||0}</td>
        </tr>`;
    }
    return `<div class="col-stats">
        <div class="col-stat-row">
            <span class="col-stat-label">🏆 总胜场</span>
            <span class="col-stat-val">${stats.total_wins||0}</span>
        </div>
        <div class="col-stat-row">
            <span class="col-stat-label">📋 总场次</span>
            <span class="col-stat-val">${stats.total_games||0}</span>
        </div>
        <div class="col-stat-row">
            <span class="col-stat-label">📈 最高关卡</span>
            <span class="col-stat-val">${stats.highest_stage||0}</span>
        </div>
        <div class="col-stat-row">
            <span class="col-stat-label">📊 胜率</span>
            <span class="col-stat-val">${stats.total_games>0?Math.round(stats.total_wins/stats.total_games*100):0}%</span>
        </div>
        ${charRows?`<h3 style="margin-top:20px;color:var(--gold);">各角色统计</h3>
        <table class="col-table"><thead><tr><th>角色</th><th>胜场</th><th>场次</th><th>最高关卡</th></tr></thead><tbody>${charRows}</tbody></table>`:''}
    </div>`;
}

// ═══ 步骤切换 ═══
function showStep(s){
    const c=s==='char';
    D.stepChar.classList.toggle('active',c);
    D.stepMode.classList.toggle('active',!c);
    D.stepBar.forEach(s=>s.classList.toggle('active',s.dataset.step===(c?'1':'2')));
}

// ═══ 角色选择 ═══
function selectCharacter(id){
    g.char=id;
    D.charOpts.forEach(o=>o.classList.toggle('active',o.dataset.char===id));
    D.cHp.value={warrior:80,elf:65,wizard:55,paladin:90,assassin:60,priest:75,mechanist:70,necromancer:58,alchemist:68}[id]||80;
}
function confirmCharacter(){
    const a=D.charSelect.querySelector('.char-option.active');
    selectCharacter(a?a.dataset.char:'warrior');
    D.modeSubtitle.textContent=`⚔️ ${{warrior:'无畏锋刃',elf:'共鸣之风',wizard:'灼疫使者',paladin:'裁决之盾',assassin:'血色暗影',priest:'棘光圣者',mechanist:'福音齿轮',necromancer:'黑血祭师',alchemist:'蚀毒秘使'}[g.char]} · 选择战斗模式`;
    showStep('mode');
}

// ═══ 无尽模式 ═══
async function startEndless(d){
    console.log('[ENDLESS] start diff='+d+' char='+g.char);
    closeModal();D.mapPanel.classList.add('hidden');g.over=false;g.sel=null;g.aim=false;g.busy=false;g.state=null;g.prev=null;
    try{
        const r=await API.startEndless(d,g.char);
        if(!r.success){toast('启动失败: '+r.error,'error');return;}
        g.mode='endless';g.prev=null;g.state=r.state;renderScreen();updateShortcutBar();
        updateChapterBG(r.state);
    }catch(e){console.error(e);toast('网络错误','error');}
}

// ═══ 自定义战斗 ═══
function addEnemyRow(d){
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
function getCustomConfig(){
    const en=[];
    D.cEnemies.querySelectorAll('.custom-enemy-row').forEach(r=>{
        const n=r.querySelector('.ce-n')?.value||'哥布林';
        const hp=+(r.querySelector('.ce-h')?.value)||30;
        const dmg=+(r.querySelector('.ce-d')?.value)||6;
        en.push({name:n,hp,damage:dmg});
    });
    return {
        enemies:en,
        playerHp:+D.cHp.value||80,
        baseAtk:+D.cAtk.value||0,
        baseDef:+D.cDef.value||0,
        character:g.char||'warrior'
    };
}
async function startCustomMode(){
    if(D.cEnemies.children.length===0)addEnemyRow();
    const c=getCustomConfig();
    console.log('[CUSTOM] sending:',JSON.stringify(c));
    if(!c.enemies.length){showCustomError('❌ 至少需要1个敌人');return;}
    g.state=null;g.prev=null;
    try{
        const r=await API.startCustom(c.enemies,c.playerHp,c.character,c.baseAtk,c.baseDef);
        console.log('[CUSTOM] response:',r.success? 'OK':'FAIL',r.error||'');
        if(!r.success){showCustomError('❌ '+r.error);return;}
        closeModal();g.mode='custom';g.prev=null;g.state=r.state;renderScreen();updateShortcutBar();
    }catch(e){console.error(e);showCustomError('❌ 请求异常: '+e.message);}
}
function showCustomError(m){
    const c=D.cEnemies.closest('.mode-card');if(!c)return;
    const o=c.querySelector('.ce-err');if(o)o.remove();
    const e=document.createElement('div');e.className='ce-err';e.textContent=m;
    c.querySelector('.custom-actions')?.after(e);
}
function applyPreset(j){
    try{const d=JSON.parse(j);D.cEnemies.innerHTML='';d.forEach(e=>addEnemyRow(e));}catch(e){console.error(e);}
}