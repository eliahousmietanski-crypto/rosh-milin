/* Moteur de recherche dans les textes (תנ"ך, זהר, livres de Breslov).
   Tourne dans un Worker pour que l'écran ne fige jamais pendant une recherche ;
   si le navigateur refuse le Worker, la page charge ce fichier et appelle SearchCore directement. */
"use strict";
(function(){
const TV='1';                 // à changer quand les textes changent : ils seront retéléchargés
const CACHE='rosh-milin-texts';
const MK='[֑-ׇֽֿׁׂׅׄ]*';   // voyelles et signes entre deux lettres
const BOOKS=['בראשית','שמות','ויקרא','במדבר','דברים','יהושע','שופטים','שמואל א','שמואל ב','מלכים א','מלכים ב','ישעיהו','ירמיהו','יחזקאל','הושע','יואל','עמוס','עובדיה','יונה','מיכה','נחום','חבקוק','צפניה','חגי','זכריה','מלאכי','תהלים','משלי','איוב','שיר השירים','רות','איכה','קהלת','אסתר','דניאל','עזרא','נחמיה','דברי הימים א','דברי הימים ב'];
const CORPORA={
  zohar:[['זהר',['zohar_1','zohar_2']],['זהר חדש',['zohar_chadash']],['תיקוני זהר',['tikkunei_zohar']]],
  nachman:[['ליקוטי מוהר״ן',['likutei_moharan']],['ספר המידות',['sefer_hamidot']],['סיפורי מעשיות',['sipurei_maasiyot']],['שיחות הר״ן',['sichot_haran']]],
  yetzirah:[['ספר יצירה',['sefer_yetzirah']],['פירוש הגר״א',['gra_sefer_yetzirah']]],
  otiyot:[['אותיות דרבי עקיבא',['otiyot_rabbi_akiva']]],
  shaarei:[['שערי אורה',['shaarei_orah']]],
  hirsch:[['רש״ר הירש',['hirsch']]],
  natan:[['ליקוטי הלכות',['likutei_halakhot_1','likutei_halakhot_2','likutei_halakhot_3','likutei_halakhot_4']],['ליקוטי תפילות',['likutei_tefilot']],['ליקוטי עצות',['likutei_etzot']],['חיי מוהר״ן',['chayei_moharan']],['שבחי הר״ן',['shivchei_haran']]],
};
const consOf=s=>s.replace(/[^א-ת]/g,'');
const vowOf=s=>s.normalize('NFD').replace(/[^א-תְ-ׇֻ]/g,'').replace(/ֺ/g,'ֹ').replace(/ׇ/g,'ָ');
function gem(n){
  let s=''; for(const [v,c] of [[400,'ת'],[300,'ש'],[200,'ר'],[100,'ק']]) while(n>=v){s+=c;n-=v;}
  if(n===15) return s+'טו'; if(n===16) return s+'טז';
  return s+(n>=10?'יכלמנסעפצ'[Math.floor(n/10)-1]:'')+(n%10?'אבגדהוזחט'[n%10-1]:'');
}

/* ---------- fichiers : gardés dans le cache du navigateur après le premier téléchargement ---------- */
const urlOf=f=>f+'?v='+TV;
async function openCache(){ try{ return await caches.open(CACHE); }catch(e){ return null; } }
async function getText(f){
  const c=await openCache(); let r=null;
  if(c) try{ r=await c.match(urlOf(f)); }catch(e){}
  if(!r){
    r=await fetch(urlOf(f)); if(!r.ok) throw new Error('http '+r.status);
    if(c) try{ await c.put(urlOf(f),r.clone()); }catch(e){}
  }
  return r.text();
}
async function cached(fs){
  const c=await openCache(); if(!c) return false;
  for(const f of fs){ try{ if(!await c.match(urlOf(f))) return false; }catch(e){ return false; } }
  return true;
}
const filesOf=src=>CORPORA[src].flatMap(([he,fs])=>fs.map(f=>[he,'corpus/'+f+'.txt']));

/* ---------- תנ"ך : découpé une fois en mots, avec préfixes et voyelles ---------- */
let TK=null, TKP=null;
function loadTanakh(){
  if(!TKP) TKP=getText('tanakh.txt').then(t=>{
    TK=t.split('\n').filter(Boolean).map(l=>{
      const [ref,txt]=l.split('\t'); const [b,c,v]=ref.split(' ').map(Number);
      // chaque mot : lettres sans préfixe, lettres avec préfixe, voyelles ; le כתיב et le קרי comptent tous les deux
      const toks=txt.split(/[ ־]+/).filter(x=>/[א-ת]/.test(x)).map(x=>{
        const y=x.replace(/[()[\]׃]/g,''); const i=y.indexOf('/');
        return {base:consOf(i<0?y:y.slice(i+1)),full:consOf(y),vow:vowOf(y.replace('/','')),pre:i>0};
      });
      return {b,c,v,txt,toks};
    });
  }).catch(e=>{TKP=null;throw e;});
  return TKP;
}
function searchTanakh(words){
  const withV=words.some(t=>t.v), hits=[];
  for(const vs of TK){
    const T=vs.toks;
    for(let i=0;i+words.length<=T.length;i++){
      let ok=true, same=true, pre=false;
      for(let k=0;k<words.length&&ok;k++){
        const x=T[i+k], t=words[k];
        if(x.full===t.c){ if(t.v&&x.vow!==t.v) same=false; }
        else if(k===0&&x.pre&&x.base===t.c){ pre=true; if(t.v&&!x.vow.endsWith(t.v)) same=false; }
        else ok=false;
      }
      if(ok) hits.push({book:BOOKS[vs.b],vs,i,n:words.length,pre,same:withV&&same});
    }
  }
  return {hits,withV};
}
function tanakhPassage(h){
  let k=-1; const pre=[], mark=[], post=[];
  for(const p of h.vs.txt.split(/([ ־]+)/)){
    if(/[א-ת]/.test(p)) k++;
    const t=p.replace('/','');
    (k<h.i?pre:k<h.i+h.n&&(/[א-ת]/.test(p)||k<h.i+h.n-1)?mark:post).push(t);
  }
  return {book:h.book,ref:`${gem(h.vs.c)}, ${gem(h.vs.v)}`,pre:pre.join(''),mark:mark.join(''),post:post.join('')};
}

/* ---------- זהר et Breslov : on ne garde que la position de chaque passage ---------- */
function corpusRe(words){
  const w=words.map(x=>[...x.c].map(l=>l+MK).join(''));
  return new RegExp(`(?<![א-ת֑-ׇ])((?:[ובהלמשכ]${MK}){0,3}?)(${w.join('[\\s־]+')})(?![א-ת֑-ׇׅ])`,'g');
}
let TXT={f:null,t:''};
async function corpusPassage(h){
  if(TXT.f!==h.f) TXT={f:h.f,t:await getText(h.f)};
  const t=TXT.t, a=t.lastIndexOf('\n',h.p)+1, b=t.indexOf('\n',h.p), tab=t.indexOf('\t',a);
  const txt=t.slice(tab+1,b<0?t.length:b), i=h.p-tab-1;
  const s=Math.max(0,i-90), e=Math.min(txt.length,i+h.len+90);
  const pre=s>0?'…'+txt.slice(s,i).replace(/^\S*\s/,''):txt.slice(0,i);
  const post=e<txt.length?txt.slice(i+h.len,e).replace(/\s\S*$/,'')+'…':txt.slice(i+h.len);
  return {book:h.book,ref:t.slice(a,tab),pre,mark:txt.substr(i,h.len),post};
}

/* ---------- interface commune ---------- */
const RES={}, LATEST={};
function summary(src,q,hits,withV){
  const count=f=>{ const books={}; let n=0; for(const h of hits) if(keep(h,f)){ n++; books[h.book]=(books[h.book]||0)+1; } return {n,books}; };
  const s={exact:count('exact'),all:count('all')}; if(withV) s.same=count('same');
  RES[src]={q,hits,withV};
  return s;
}
const keep=(h,f)=>f==='same'?h.same&&!h.pre:f==='exact'?!h.pre:true;
const Core={
  async cached({src}){ return src==='tanakh'?true:cached(filesOf(src).map(x=>x[1])); },
  async search({src,q,words},progress){
    LATEST[src]=q;
    const stale=()=>{ if(LATEST[src]!==q) throw new Error('stale'); };
    if(src==='tanakh'){ await loadTanakh(); stale(); const {hits,withV}=searchTanakh(words); return summary(src,q,hits,withV); }
    const re=corpusRe(words), hits=[], files=filesOf(src);
    for(let k=0;k<files.length;k++){
      const [book,f]=files[k]; progress&&progress({done:k,total:files.length,book});
      const t=await getText(f); stale(); re.lastIndex=0; let m;
      while((m=re.exec(t))) hits.push({book,f,p:m.index,len:m[0].length,pre:m[1].length>0});
      if(k===0) TXT={f,t};   // les premiers passages affichés viennent de ce fichier
    }
    return summary(src,q,hits,false);
  },
  async page({src,q,f,from,n}){
    const R=RES[src]; if(!R||R.q!==q) throw new Error('stale');
    const list=R.hits.filter(h=>keep(h,f)).slice(from,from+n), out=[];
    for(const h of list) out.push(src==='tanakh'?tanakhPassage(h):await corpusPassage(h));
    return out;
  },
};

if(typeof WorkerGlobalScope!=='undefined'&&self instanceof WorkerGlobalScope){
  self.onmessage=async e=>{
    const m=e.data;
    try{ const r=await Core[m.type](m,p=>self.postMessage({id:m.id,progress:p})); self.postMessage({id:m.id,ok:true,r}); }
    catch(err){ self.postMessage({id:m.id,ok:false,e:String(err&&err.message||err)}); }
  };
}else self.SearchCore=Core;
})();
