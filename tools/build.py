# -*- coding: utf-8 -*-
"""生成《百分之一》作战效能计算器 —— 自包含单文件 HTML。

用法：
    python tools/build.py

输出：
    index.html   （角色与勋章数据全量内嵌，双击即可离线使用）

数据源：
    data/chars.json  角色数据：每名角色的 Lv1-20 四维（攻击/生命/护甲/灵力）+ 初始星级 + 形态
    data/medals.json 勋章数据

更新数据后，请同步修改下面的 DATA_AS_OF。
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")

LV_MAX = 20            # 游戏内等级上限
DATA_AS_OF = "2026-10-09"   # 本仓库角色数据快照截止日期

chars_raw = json.load(open(os.path.join(DATA_DIR, "chars.json"), encoding="utf-8"))
medals_raw = json.load(open(os.path.join(DATA_DIR, "medals.json"), encoding="utf-8"))

# 只保留有等级数据的角色，等级截断到 Lv1-LV_MAX
chars = {}
for name, v in chars_raw["chars"].items():
    lvs = {}
    for k, q in v["lv"].items():
        n = int(k)
        if 1 <= n <= LV_MAX:
            lvs[n] = q
    if lvs:
        chars[name] = {"l": lvs, "r": v["rar"], "e": v["eth"]}

DATA = {
    "chars": chars,
    "medals": medals_raw["attr"],
    "modMax": {"atk": 12, "mg": 12, "hp": 14, "shd": 14},
    "fixed": {"guild": [6, 16, 16, 4], "spc": [2, 2, 2, 2]},
}

html = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<title>作战效能计算器 - 百分之一</title>
<style>
:root{--bg:#f6f7f9;--card:#fff;--bd:#d8dce3;--tx:#1f2328;--tx2:#5a6270;
--ac:#2f6fd0;--ac2:#e8f0fc;--ok:#2e7d4f;--mono:ui-monospace,Consolas,monospace}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,"Segoe UI","Microsoft YaHei",sans-serif;background:var(--bg);
color:var(--tx);line-height:1.6;padding:16px}
.wrap{max-width:1280px;margin:0 auto;display:grid;grid-template-columns:4fr 1fr;gap:16px}
@media(max-width:980px){.wrap{grid-template-columns:1fr}}
h1{font-size:20px;font-weight:600;margin-bottom:4px}
.sub{font-size:13px;color:var(--tx2);margin-bottom:16px}
.meta{font-size:12px;color:var(--tx2);margin:-10px 0 16px}
.meta b{color:var(--tx)}
.card{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:14px;margin-bottom:14px}
.card h2{font-size:14px;font-weight:600;margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid #eceff3}
.row{display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end}
.f{display:flex;flex-direction:column;gap:4px;flex:1;min-width:110px}
label{font-size:12px;color:var(--tx2);font-weight:500}
select,input{font-size:14px;padding:7px 9px;border:1px solid var(--bd);border-radius:6px;
background:#fff;color:var(--tx);font-family:inherit;width:100%}
select:focus,input:focus{outline:2px solid var(--ac2);border-color:var(--ac)}
.chk{display:flex;align-items:center;gap:6px;font-size:14px;color:var(--tx);cursor:pointer;
padding:7px 10px;border:1px solid var(--bd);border-radius:6px;background:#fff;user-select:none}
.chk input{width:auto;margin:0}
.chk.on{border-color:var(--ac);background:var(--ac2);color:var(--ac);font-weight:500}
.hint{font-size:12px;color:var(--tx2);margin-top:6px}
.big{font-size:56px;font-weight:700;color:var(--ac);font-family:var(--mono);line-height:1.1}
.big.na{color:#9aa1ac}
.res{display:flex;align-items:center;gap:16px}
.res h2{margin-bottom:0;padding-bottom:0;border-bottom:none;flex:none}
.seg{display:flex;gap:0;border:1px solid var(--bd);border-radius:6px;overflow:hidden;margin-bottom:14px}
.seg button{flex:1;padding:7px 4px;font-size:13px;border:none;background:#fff;color:var(--tx2);
cursor:pointer;font-family:inherit;border-right:1px solid var(--bd)}
.seg button:last-child{border-right:none}
.seg button.on{background:var(--ac);color:#fff;font-weight:500}
.mini{font-size:11px;color:var(--tx2);font-weight:400}
.ver{float:right;font-size:11px;color:#b6bcc6;font-family:var(--mono)}
.cbx{position:relative}
.cbx-list{position:absolute;top:100%;left:0;right:0;z-index:30;background:#fff;
border:1px solid var(--bd);border-radius:6px;max-height:260px;overflow-y:auto;display:none;
box-shadow:0 6px 16px rgba(15,23,42,.14);margin-top:2px}
.cbx-list.open{display:block}
.cbx-item{padding:6px 10px;font-size:13.5px;cursor:pointer;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.cbx-item:hover,.cbx-item.act{background:var(--ac2);color:var(--ac)}
.cbx-empty{padding:8px 10px;font-size:12px;color:var(--tx2)}
.side{min-width:0}
.side .card{position:sticky;top:16px}
.rk{display:flex;align-items:center;gap:8px;padding:7px 4px;border-bottom:1px solid #eceff3;
font-size:13px;cursor:pointer}
.rk:last-of-type{border-bottom:none}
.rk:hover{background:var(--ac2)}
.rk .no{width:22px;height:22px;border-radius:50%;background:#eef1f5;color:var(--tx2);
display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:600;flex:none}
.rk:nth-child(1) .no{background:#fdeecb;color:#b07d1a}
.rk:nth-child(2) .no{background:#eef0f3;color:#68727f}
.rk:nth-child(3) .no{background:#f7e3d4;color:#a05a2c}
.rk .nm{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.rk .vl{font-family:var(--mono);font-size:12.5px;color:var(--tx2);flex:none}
.note{font-size:11.5px;color:var(--tx2);margin-top:8px;line-height:1.5}
.foot{max-width:1280px;margin:8px auto 0;font-size:11.5px;color:#9aa1ac;line-height:1.6;
text-align:center;padding:12px 4px}
@media(max-width:600px){body{padding:10px}.big{font-size:42px}}
</style>
</head>
<body>
<h1>作战效能计算器 <span class="ver">v8</span></h1>
<div class="sub">《百分之一》 — 战力 = 175 + (等级+生命+护甲)×3 + 攻击×5 + 灵力×10 + 药剂数量×100 + 初始星级×30 + 当前星级×50 + 外部加成折算</div>
<div class="meta">角色数据截止 <b>__DATE__</b>，共 <b>__NCHARS__</b> 名角色，Lv1–20 四维全量内置 · 勋章 5 种 · 基站模块 · 图鉴 · 公会 / 奇点排查</div>

<div class="wrap">
<div class="main">

<div class="card res">
<h2>战力结果</h2>
<div class="big na" id="total">—</div>
</div>

<div class="seg">
  <button class="on" data-v="match">队伍界面</button>
  <button data-v="setup">设置界面</button>
</div>

<div class="card">
<h2>角色</h2>
<div class="row">
<div class="f" style="flex:2.5"><label>角色名（可输入搜索）</label>
<div class="cbx">
<input type="text" id="cname" placeholder="请选择角色 / 输入关键词" autocomplete="off">
<div class="cbx-list" id="cbxlist"></div>
</div></div>
<div class="f"><label>等级</label><select id="clv"></select></div>
<div class="f"><label>当前星级</label><select id="cstar"></select></div>
</div>
<div class="hint" id="chint">请先选择角色</div>
</div>

<div class="card">
<h2>天赋</h2>
<div class="row" id="talwrap"></div>
</div>

<div class="card">
<h2>外部加成 · 勋章 <span class="mini">可带 3 个</span></h2>
<div class="row" id="mdwrap"></div>
</div>

<div class="card">
<h2>外部加成 · 基站模块</h2>
<div class="row" id="modwrap"></div>
</div>

<div class="card">
<h2>外部加成 · 图鉴 <span class="mini">手动填写</span></h2>
<div class="row">
<div class="f"><label>图鉴·攻击（最大值6）</label><input type="number" id="g_atk" min="0" value="0"></div>
<div class="f"><label>图鉴·护甲（最大值10）</label><input type="number" id="g_shd" min="0" value="0"></div>
<div class="f"><label>图鉴·生命（最大值10）</label><input type="number" id="g_hp" min="0" value="0"></div>
<div class="f"><label>图鉴·灵力（最大值4）</label><input type="number" id="g_mg" min="0" value="0"></div>
</div>
</div>

<div class="card">
<h2>固定加成</h2>
<div class="row">
<label class="chk on"><input type="checkbox" id="k_g" checked>公会 +6攻+16血+16盾+4灵</label>
<label class="chk on"><input type="checkbox" id="k_s" checked>奇点排查 +2全属性</label>
</div>
</div>

</div>

<div class="side">
<div class="card">
<h2>战力排行榜</h2>
<div id="rank"></div>
<div class="note">按 Lv20 · 6星 · 天赋全开的本体属性计算，不含所有加成。点击条目可直接载入该角色。</div>
</div>
</div>
</div>

<div class="foot">数据整理自《百分之一》游戏与 BWIKI 社区 · 本工具为非官方粉丝作品，仅供学习交流使用，游戏相关内容版权归原权利方所有</div>

<script>
const D = __DATA__;
const W = {a:5,h:3,s:3,m:10};
const VER = 'v8 (__DATE__)';
console.log('战力计算器 ' + VER);

let scope = 'match';
const $ = id => document.getElementById(id);
const E = (n,v)=>{const e=document.createElement('option');e.value=n;e.textContent=v;return e;};
const num = id => Math.max(0, parseInt($(id).value)||0);
const W4 = v => v[0]*W.a+v[1]*W.h+v[2]*W.s+v[3]*W.m;

// ---------- 角色组合框（点开下拉选 / 输入关键词搜索） ----------
let curName = '';
let hl = -1;
const names = Object.keys(D.chars).sort(new Intl.Collator('zh').compare);
const cInput = $('cname'), cList = $('cbxlist');

function renderList(){
  const q = cInput.value.trim();
  const hits = q ? names.filter(n => n.includes(q)) : names;
  cList.innerHTML = ''; hl = -1;
  if(!hits.length){
    cList.innerHTML = '<div class="cbx-empty">无匹配角色</div>';
  } else {
    hits.slice(0, 80).forEach(n => {
      const d = document.createElement('div');
      d.className = 'cbx-item'; d.textContent = n;
      d.onmousedown = e => { e.preventDefault(); pickName(n); };
      cList.appendChild(d);
    });
    if(hits.length > 80){
      const m = document.createElement('div'); m.className = 'cbx-empty';
      m.textContent = '共 ' + hits.length + ' 个匹配，仅显示前 80，请继续输入';
      cList.appendChild(m);
    }
  }
  cList.classList.add('open');
}
function pickName(n){
  curName = n; cInput.value = n;
  cList.classList.remove('open');
  fillLevels();
}
cInput.addEventListener('focus', renderList);
cInput.addEventListener('input', renderList);
cInput.addEventListener('blur', () => {
  setTimeout(() => { cList.classList.remove('open'); cInput.value = curName; }, 120);
});
cInput.addEventListener('keydown', e => {
  if(e.key === 'Escape'){ cList.classList.remove('open'); cInput.value = curName; return; }
  const items = [...cList.querySelectorAll('.cbx-item')];
  if(!items.length) return;
  if(e.key === 'ArrowDown' || e.key === 'ArrowUp'){
    e.preventDefault();
    hl = e.key === 'ArrowDown' ? Math.min(items.length - 1, hl + 1) : Math.max(0, hl - 1);
    items.forEach((x, i) => x.classList.toggle('act', i === hl));
    items[hl].scrollIntoView({ block: 'nearest' });
  } else if(e.key === 'Enter'){
    e.preventDefault();
    if(hl >= 0 && items[hl]) pickName(items[hl].textContent);
    else if(items.length === 1) pickName(items[0].textContent);
  }
});

function fillLevels(){
  const c = D.chars[curName];
  const lsel = $('clv'), ssel = $('cstar');
  lsel.innerHTML=''; ssel.innerHTML='';
  if(!c){
    $('chint').textContent = '请先选择角色';
    $('talwrap').innerHTML = '';
    calc();
    return;
  }
  const maxLv = Math.min(20, Math.max(...Object.keys(c.l).map(Number)));
  for(let i=1;i<=maxLv;i++) lsel.appendChild(E(i,'Lv'+i));
  lsel.value = Math.min(20, maxLv);
  const s0 = Math.min(6, c.r || 3);
  for(let i=1;i<=6;i++) ssel.appendChild(E(i, i+' 星'));
  ssel.value = s0;
  $('chint').textContent = c.e+' · 初始 '+s0+' 星 · 可升至 Lv'+maxLv;
  fillTal();
  calc();
}

function fillTal(){
  const w = $('talwrap'); w.innerHTML='';
  for(let i=1;i<=3;i++){
    const lab=document.createElement('label');
    lab.className='chk';
    lab.innerHTML='<input type="checkbox" id="t'+i+'">天赋 '+i;
    w.appendChild(lab);
  }
  w.querySelectorAll('input').forEach(cb=>{
    cb.onchange=()=>{ cb.parentElement.classList.toggle('on',cb.checked); calc(); };
  });
}
function talPotions(){
  let p=0;
  for(let i=1;i<=3;i++){ if($('t'+i)&&$('t'+i).checked) p+=i; }
  return p;
}

// ---------- 勋章：固定 3 槽，允许重复装备同类 ----------
function fillMedals(){
  const w=$('mdwrap'); w.innerHTML='';
  for(let i=0;i<3;i++){
    const f=document.createElement('div'); f.className='f';
    const lab=document.createElement('label'); lab.textContent='勋章槽 '+(i+1);
    const s=document.createElement('select'); s.id='md'+i;
    s.appendChild(E('','— 无 —'));
    D.medals.forEach(m=>{
      const og=document.createElement('optgroup'); og.label=m.name;
      Object.keys(m.lv).sort().forEach(l=>{
        const v=m.lv[l];
        const desc=[v[0]?'攻'+v[0]:'',v[1]?'血'+v[1]:'',v[2]?'盾'+v[2]:'',v[3]?'灵'+v[3]:'']
          .filter(Boolean).join(' ');
        og.appendChild(E(m.id+'|'+l, ['I','II','III'][+l-1]+'级 ('+desc+')'));
      });
      s.appendChild(og);
    });
    s.onchange=()=>calc();
    f.appendChild(lab); f.appendChild(s); w.appendChild(f);
  }
}
function medalAdd(){
  const r=[0,0,0,0];
  for(let i=0;i<3;i++){
    const s=$('md'+i); if(!s||!s.value) continue;
    const p=s.value.split('|'); if(p.length!==2) continue;
    const m=D.medals.find(x=>String(x.id)===p[0]); if(!m) continue;
    const v=m.lv[p[1]]; if(v) v.forEach((x,k)=>r[k]+=x);
  }
  return r;
}

// ---------- 基站 ----------
function fillModules(){
  const w=$('modwrap'); w.innerHTML='';
  const defs=[['m_atk','攻击模块',12],['m_shd','护甲模块',14],
              ['m_hp','生命模块',14],['m_mg','灵力模块',12]];
  defs.forEach(d=>{
    const f=document.createElement('div'); f.className='f';
    const lab=document.createElement('label'); lab.textContent=d[1];
    const s=document.createElement('select'); s.id=d[0];
    for(let i=1;i<=d[2];i++) s.appendChild(E(i,'LV'+i+'（+'+i+'）'));
    s.value=1; s.onchange=()=>calc();
    f.appendChild(lab); f.appendChild(s); w.appendChild(f);
  });
}

// ---------- 战力排行榜（本体：Lv20·6星·天赋全开，无外部加成） ----------
function buildRank(){
  const list = names.map(n => {
    const c = D.chars[n];
    const b = c.l[20] || c.l[Math.max(...Object.keys(c.l).map(Number))];
    const ini = Math.min(6, c.r || 3);
    return { n, v: Math.round(175 + (20+b[1]+b[2])*3 + b[0]*5 + b[3]*10 + 600 + ini*30 + 6*50) };
  }).sort((a,b) => b.v - a.v).slice(0, 10);
  const box = $('rank'); box.innerHTML='';
  list.forEach((it, i) => {
    const d = document.createElement('div'); d.className = 'rk';
    d.innerHTML = '<span class="no">'+(i+1)+'</span><span class="nm">'+it.n+'</span><span class="vl">'+it.v+'</span>';
    d.title = it.n;
    d.onclick = () => pickName(it.n);
    box.appendChild(d);
  });
}

// ---------- 计算 ----------
function calc(){
  const c = D.chars[curName];
  const big = $('total');
  if(!c){ big.textContent='—'; big.classList.add('na'); return; }
  const lv=+$('clv').value||1, st=+$('cstar').value||c.r||3;
  const base=(c.l[lv]||c.l[1]).slice();
  const med=medalAdd();
  const addBase=[num('m_atk'),num('m_hp'),num('m_shd'),num('m_mg')];
  const addGal =[num('g_atk'),num('g_hp'),num('g_shd'),num('g_mg')];

  const ini = Math.min(6, c.r || 3);
  st = Math.max(st, ini);   // 星级不可低于初始星
  let total = 175 + (lv+base[1]+base[2])*3 + base[0]*5 + base[3]*10
            + talPotions()*100 + ini*30 + st*50;
  if(W4(addBase)) total += W4(addBase);
  if(W4(addGal)) total += W4(addGal);
  // 队伍界面额外计入：公会 + 奇点排查 + 勋章
  if(scope==='match'){
    if($('k_g').checked) total += W4(D.fixed.guild);
    if($('k_s').checked) total += W4(D.fixed.spc);
    if(W4(med)) total += W4(med);
  }

  big.textContent = Math.round(total);
  big.classList.remove('na');
}

// ---------- 事件绑定 ----------
document.querySelectorAll('.seg button').forEach(b=>{
  b.onclick=()=>{
    document.querySelectorAll('.seg button').forEach(x=>x.classList.remove('on'));
    b.classList.add('on'); scope=b.dataset.v; calc();
  };
});
function bindInputs(){
  ['clv','cstar'].forEach(id=>{ $(id).onchange=calc; });
  ['g_atk','g_shd','g_hp','g_mg'].forEach(id=>{ $(id).oninput=calc; $(id).onchange=calc; });
  ['k_g','k_s'].forEach(id=>{
    const e=$(id);
    e.onchange=()=>{ e.parentElement.classList.toggle('on',e.checked); calc(); };
  });
}

// ---------- 初始化 ----------
fillMedals(); fillModules(); buildRank(); bindInputs(); calc();
</script>
</body>
</html>
'''

out = html.replace('__DATA__', json.dumps(DATA, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'))
out = out.replace('__NCHARS__', str(len(chars))).replace('__DATE__', DATA_AS_OF)

fn = os.path.join(ROOT, 'index.html')
open(fn, 'w', encoding='utf-8').write(out)
print('已生成 index.html (%.0f KB)' % (os.path.getsize(fn) / 1024))
print('  角色 %d 名（Lv1-%d）' % (len(chars), LV_MAX))
print('  勋章 %d 种（3 槽，可重复装备同类）' % len(DATA['medals']))
print('  数据截止 %s' % DATA_AS_OF)
