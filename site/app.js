import {DemoStore, STORAGE_KEY} from './engine.js';

const app = document.querySelector('#app');
const dialog = document.querySelector('#detail');
const state = {page: 'home', quiz: null, feedback: null, query: '', category: '全部主题', wordRows: []};
let store, seed, toastTimer, searchTimer;
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const date = value => new Date(value).toLocaleString('zh-CN', {month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hour12:false});
const mode = value => value === 'review' ? '错题复习' : '随机练习';
const source = quiz => `<span class="badge ${quiz.sample?'neutral':''}">${quiz.sample?'示例记录':'本次演示'}</span>`;
const empty = text => `<div class="empty">${esc(text)}</div>`;
const stat = (label,value,unit='') => `<div class="stat"><span>${esc(label)}</span><strong>${esc(value)}<small>${esc(unit)}</small></strong></div>`;
const heading = (title,description='',actions='') => `<header class="page-head"><div><h1 tabindex="-1">${esc(title)}</h1>${description?`<p>${esc(description)}</p>`:''}</div>${actions}</header>`;
const exports = () => '<div class="row"><button class="small ghost" data-export="json">导出 JSON</button><button class="small ghost" data-export="csv">导出 CSV</button></div>';
const teacher = () => store.role === 'teacher';
const categoryOptions = (selected='全部主题',all=true) => {
  const cats = teacher() ? [...new Set(store.words({includeDisabled:true}).map(w=>w.category))] : store.categories();
  return [...(all?['全部主题']:[]),...cats].map(c=>`<option${c===selected?' selected':''}>${esc(c)}</option>`).join('');
};

function toast(message) {
  const box = document.querySelector('#toast'); box.textContent=message; box.classList.add('visible');
  clearTimeout(toastTimer); toastTimer=setTimeout(()=>box.classList.remove('visible'),4500);
}

function shell() {
  const nav = teacher() ? [['admin','管理概览'],['manage_words','词库管理'],['class_records','练习记录']]
    : [['home','学习概览'],['quiz','单词练习'],['words','词汇手册'],['mistakes','错题复习'],['records','学习记录']];
  app.innerHTML = `<div class="shell"><aside class="sidebar">
    <a class="brand" href="./"><img src="./icon.svg" alt=""><b>KET Word Studio</b></a>
    <div class="role-switch" role="group" aria-label="切换演示身份"><button data-role="student" aria-pressed="${!teacher()}">学生页面</button><button data-role="teacher" aria-pressed="${teacher()}">教师页面</button></div>
    <nav class="nav" aria-label="主要导航">${nav.map(([key,text])=>`<button data-page="${key}" ${state.page===key?'aria-current="page"':''}>${text}</button>`).join('')}</nav>
    <div class="demo-controls"><p>数据仅保存在此浏览器。</p><button class="ghost small" data-action="reset">重置演示数据</button></div>
    </aside><main class="main"><div class="context"><span>单词测试系统</span><span class="badge">${teacher()?'教师':'学生'}</span></div><div id="content"></div></main></div>`;
}

function chart(records) {
  if (!records.length) return empty('暂无已完成的练习。');
  const rows=[...records].reverse();
  const points=rows.map((r,i)=>[42+i*(350/Math.max(rows.length-1,1)),140-r.accuracy,r]);
  return `<svg class="chart" viewBox="0 0 420 177" role="img" aria-label="最近 ${rows.length} 次练习的正确率，按完成顺序排列">
    ${[0,50,100].map(n=>`<line x1="38" y1="${140-n}" x2="405" y2="${140-n}"/><text x="0" y="${144-n}">${n}%</text>`).join('')}
    <polyline points="${points.map(p=>p.slice(0,2).join(',')).join(' ')}"/>
    ${points.map(([x,y,r],i)=>`<circle cx="${x}" cy="${y}" r="4"><title>${r.sample?'示例':'本次演示'}：${r.accuracy}%</title></circle><text x="${x}" y="166" text-anchor="middle">${i+1}</text>`).join('')}</svg>`;
}

function recordTable(records) {
  if (!records.length) return empty('暂无已完成的练习。');
  return `<div class="table-wrap"><table><thead><tr><th>完成时间</th><th>主题 / 方式</th><th>正确 / 题数</th><th>正确率</th><th>来源</th><th>操作</th></tr></thead><tbody>
    ${records.map(r=>`<tr><td>${date(r.completedAt)}</td><td>${esc(r.category)}<small class="cell-note">${mode(r.mode)}</small></td><td>${r.correct} / ${r.total}</td><td><b>${r.accuracy}%</b></td><td>${source(r)}</td><td><button class="small secondary" data-record="${esc(r.id)}">查看详情</button></td></tr>`).join('')}
    </tbody></table></div>`;
}

function home() {
  const d=store.summary(), active=store.activeQuiz();
  return `${heading('学习概览',d.sampleCount?`当前包含 ${d.sampleCount} 条示例记录。新增练习会单独标注。`:'',`<button data-page="quiz">${active?'继续练习':'开始练习'}</button>`)}
    <section class="stats">${stat('已完成练习',d.attempts,'次')}${stat('累计正确率',d.accuracy+'%')}${stat('待复习单词',d.mistakeCount,'个')}${stat('累计作答',d.questions,'题')}</section>
    <div class="section-grid"><section class="panel"><h2>最近 7 次练习正确率</h2>${chart(d.recent)}</section>
      <section class="panel quick-panel"><h2>练习与复习</h2><dl><div><dt>启用词汇</dt><dd>${d.wordCount}</dd></div><div><dt>词汇主题</dt><dd>${store.categories().length}</dd></div><div><dt>待复习单词</dt><dd>${d.mistakeCount}</dd></div></dl><div class="row"><button class="secondary" data-action="review">复习错题</button><button class="ghost" data-page="words">查看词汇</button></div></section></div>
    <div class="section-title"><h2>最近练习</h2><button class="small ghost" data-page="records">全部记录</button></div>${recordTable(d.recent.slice(0,3))}`;
}

function admin() {
  const d=store.summary();
  return `${heading('管理概览','此处展示当前浏览器中学生页面的练习数据。',`<button data-page="manage_words">管理词汇</button>`)}
    <section class="stats">${stat('启用词汇',d.wordCount,'个')}${stat('词汇主题',store.categories().length,'个')}${stat('完成练习',d.attempts,'次')}${stat('累计正确率',d.accuracy+'%')}</section>
    <section class="panel"><h2>最近 7 次练习正确率</h2>${chart(d.recent)}</section>
    <div class="section-title"><h2>最近练习</h2><button class="small ghost" data-page="class_records">全部记录</button></div>${recordTable(d.recent.slice(0,3))}`;
}

function wordTable(words,manage=false) {
  if (!words.length) return empty('没有匹配的词汇。');
  return `<div class="table-wrap"><table><thead><tr><th>英文</th><th>中文释义</th><th>主题</th>${manage?'<th>状态</th><th>操作</th>':''}</tr></thead><tbody>
    ${words.map(w=>`<tr><td class="word">${esc(w.english)}</td><td>${esc(w.chinese)}</td><td><span class="badge neutral">${esc(w.category)}</span></td>${manage?`<td><span class="badge ${w.enabled?'':'neutral'}">${w.enabled?'启用':'停用'}</span></td><td><button class="small secondary" data-word="${esc(w.id)}">编辑</button></td>`:''}</tr>`).join('')}</tbody></table></div>`;
}

function wordsPage() {
  const manage=teacher();
  state.wordRows=store.words({query:state.query,category:state.category,includeDisabled:manage});
  if(manage)state.wordRows.reverse();
  return `${heading(manage?'词库管理':'词汇手册',manage?'停用词汇不再用于新练习，已完成的练习内容保持不变。':'搜索已启用的词汇。',manage?'<button data-action="add-word">添加词汇</button>':'')}
    <div class="toolbar"><div class="search"><label for="word-search">搜索词汇</label><input id="word-search" placeholder="英文或中文释义" value="${esc(state.query)}"></div><div><label for="word-category">词汇主题</label><select id="word-category">${categoryOptions(state.category)}</select></div><span id="word-count" class="muted">${state.wordRows.length} 个词条</span></div>
    <div id="word-results">${wordTable(state.wordRows,manage)}</div>`;
}

function wordEditor(id) {
  const word=id?store.words({includeDisabled:true}).find(w=>w.id===id):null;
  if(id&&!word)throw new Error('词条不存在。');
  const w=word||{english:'',chinese:'',category:'',aliases:[],enabled:true};
  document.querySelector('#detail-content').innerHTML=`<h2 id="dialog-title">${word?'编辑':'添加'}词汇</h2>
    <form id="word-form" data-id="${esc(id||'')}"><div class="form-grid">
      <div><label for="english">英文</label><input id="english" name="english" maxlength="100" value="${esc(w.english)}" required></div>
      <div><label for="chinese">中文释义</label><input id="chinese" name="chinese" maxlength="200" value="${esc(w.chinese)}" required></div>
      <div class="wide"><label for="category">主题</label><input id="category" name="category" list="category-list" maxlength="40" value="${esc(w.category)}" required><datalist id="category-list">${categoryOptions('',false)}</datalist></div>
      <div class="wide"><label for="aliases">其他可接受答案（用英文分号分隔）</label><input id="aliases" name="aliases" maxlength="2020" value="${esc(w.aliases.join('; '))}"></div>
      <label class="check wide"><input name="enabled" type="checkbox" ${w.enabled?'checked':''}>启用词汇</label></div>
      <div id="form-error" class="inline-error" role="alert"></div><div class="row"><button type="submit">保存词汇</button><button type="button" class="ghost dialog-close-button">取消</button></div></form>`;
  dialog.showModal(); document.querySelector('#english').focus();
}

function recordsPage() {
  const d=store.summary();
  return `${heading(teacher()?'练习记录':'学习记录','示例记录与本次演示的记录均已标注来源。',exports())}
    <section class="stats">${stat('最高正确率',d.best+'%')}${stat('最低正确率',d.worst+'%')}${stat('平均正确率',d.average+'%')}${stat('完成练习',d.attempts,'次')}</section>
    ${recordTable(store.records())}<p class="subnote">平均正确率为各次练习的算术平均；累计正确率按总作答题数计算。</p>`;
}

function mistakesPage() {
  const rows=store.mistakes();
  return `${heading('错题复习','显示最近一次完整练习仍答错的词；再次完成练习并答对后移出。',rows.length?'<button data-action="review">开始错题练习</button>':'')}
    ${rows.length?`<div class="table-wrap"><table><thead><tr><th>正确拼写</th><th>中文释义</th><th>上次答案</th><th>累计答错</th></tr></thead><tbody>${rows.map(r=>`<tr><td class="word">${esc(r.english)}</td><td>${esc(r.chinese)}</td><td>${esc(r.answer)||'（跳过）'}</td><td>${r.wrongCount} 次</td></tr>`).join('')}</tbody></table></div>`:empty('暂无待复习错词。')}`;
}

function quizPage() {
  state.quiz=store.activeQuiz();state.feedback=null;
  if(state.quiz)return quizHtml();
  const count=store.words().length;
  return `${heading('单词练习','根据中文释义填写英文。')}<form id="quiz-config" class="panel quiz-layout">
    <div class="form-grid"><div><label for="quiz-mode">练习方式</label><select id="quiz-mode" name="mode"><option value="random">随机练习</option><option value="review">错题复习</option></select></div>
    <div><label for="quiz-count">题目数量</label><input id="quiz-count" name="count" type="number" min="1" max="500" value="${Math.min(10,count)||1}" required></div>
    <div class="wide"><label for="quiz-category">词汇主题</label><select id="quiz-category" name="category">${categoryOptions()}</select></div></div>
    <button type="submit" ${count?'':'disabled'}>开始练习</button><p class="subnote">${count?'同次练习不重复抽词。词数不足时使用实际可用数量；忽略大小写和多余空格。':'没有启用的词汇，请先在教师页面添加或启用词汇。'}</p></form>`;
}

function quizHtml() {
  const q=state.quiz,f=state.feedback,index=f?f.index:q.answers.findIndex(a=>a.answer===null);
  const current=q.answers[index],answered=q.answers.filter(a=>a.answer!==null).length,correct=q.answers.filter(a=>a.correct).length;
  return `${heading('单词练习','已提交的答案自动保存，离开页面后可以继续。')}<div class="quiz-layout"><section class="panel quiz-card">
    <div class="quiz-meta"><span class="badge">${esc(current.category)}</span><span>第 ${index+1} / ${q.answers.length} 题</span></div><progress value="${answered}" max="${q.answers.length}" aria-label="练习进度"></progress>
    <p class="muted">请写出对应的英文单词或短语</p><h2 class="prompt">${esc(current.chinese)}</h2>
    <form id="answer-form"><label for="answer-input">你的答案</label><input id="answer-input" class="answer-input" name="answer" maxlength="200" autocomplete="off" autocapitalize="none" spellcheck="false" placeholder="输入英文答案" ${f?'disabled':''} value="${f?esc(current.answer):''}">
    ${f?`<div class="feedback ${current.correct?'':'wrong'}" role="status">${current.correct?'回答正确':'回答错误，正确答案：'}<b>${esc(current.english)}</b></div><div class="answer-actions"><button type="button" data-action="next">${q.status==='completed'?'查看本次成绩':'下一题'}</button></div>`:'<div class="answer-actions"><button type="submit">提交答案</button><button type="button" class="ghost" data-action="skip">跳过此题</button></div>'}</form></section>
    <div class="quiz-footer"><span>已答对 ${correct} 题 · ${mode(q.mode)}</span>${q.status==='active'?'<button class="small ghost" data-action="abandon">结束本次练习</button>':''}</div></div>`;
}

function detailsTable(rows) {
  return `<div class="table-wrap"><table><thead><tr><th>中文释义</th><th>正确答案</th><th>你的答案</th><th>结果</th></tr></thead><tbody>${rows.map(r=>`<tr><td>${esc(r.chinese)}</td><td class="word">${esc(r.english)}</td><td>${esc(r.answer)||'（跳过）'}</td><td><span class="badge ${r.correct?'':'wrong'}">${r.correct?'正确':'错误'}</span></td></tr>`).join('')}</tbody></table></div>`;
}

function resultPage(id) {
  const r=store.detail(id);
  document.querySelector('#content').innerHTML=`${heading('练习完成','成绩已保存至学习记录。')}<section class="panel result"><strong>${r.accuracy}<span>%</span></strong><p>共 ${r.total} 题 · 答对 ${r.correct} 题 · 答错 ${r.total-r.correct} 题</p><div class="answer-actions"><button data-page="quiz">再练一次</button><button class="secondary" data-page="mistakes">复习错词</button></div></section><div class="section-title"><h2>答题详情</h2></div>${detailsTable(r.answers)}`;
}

function showDetail(id) {
  const r=store.detail(id);
  document.querySelector('#detail-content').innerHTML=`<h2 id="dialog-title">练习详情</h2><p class="review-note">${date(r.completedAt)} · ${r.correct} / ${r.total} 题正确 · ${r.sample?'示例记录':'本次演示'}</p>${detailsTable(r.answers)}`;
  dialog.showModal();
}

function navigate(page,focus=true) {
  clearTimeout(searchTimer);
  const allowed=teacher()?['admin','manage_words','class_records']:['home','quiz','words','mistakes','records'];
  state.page=allowed.includes(page)?page:allowed[0];
  if(!['words','manage_words'].includes(state.page)){state.query='';state.category='全部主题';}
  shell();
  const pages={home,admin,words:wordsPage,manage_words:wordsPage,quiz:quizPage,mistakes:mistakesPage,records:recordsPage,class_records:recordsPage};
  document.querySelector('#content').innerHTML=pages[state.page]();
  if(focus)document.querySelector('h1')?.focus({preventScroll:true});
  if(state.page==='quiz'&&state.quiz)document.querySelector('#answer-input')?.focus();
  window.scrollTo(0,0);
}

function submitAnswer(answer) {
  if(state.feedback||!state.quiz)return;
  const index=state.quiz.answers.findIndex(a=>a.answer===null);
  const result=store.answer(state.quiz.id,index,answer);state.quiz=result.quiz;state.feedback={index};
  document.querySelector('#content').innerHTML=quizHtml();document.querySelector('[data-action="next"]').focus();
}

function refreshWords() {
  if(!['words','manage_words'].includes(state.page))return;
  state.query=document.querySelector('#word-search').value;state.category=document.querySelector('#word-category').value;
  state.wordRows=store.words({query:state.query,category:state.category,includeDisabled:teacher()});
  if(teacher())state.wordRows.reverse();
  document.querySelector('#word-results').innerHTML=wordTable(state.wordRows,teacher());
  document.querySelector('#word-count').textContent=state.wordRows.length+' 个词条';
}

document.addEventListener('submit',event=>{
  event.preventDefault();const form=event.target;
  try {
    if(form.id==='word-form'){
      store.saveWord({id:form.dataset.id||undefined,english:form.elements.english.value,chinese:form.elements.chinese.value,
        category:form.elements.category.value,aliases:form.elements.aliases.value.split(';').map(a=>a.trim()).filter(Boolean),enabled:form.elements.enabled.checked});
      dialog.close();state.query='';state.category='全部主题';navigate('manage_words');toast('词汇已保存。');
    }else if(form.id==='quiz-config'){
      state.quiz=store.startQuiz({count:Number(form.elements.count.value),category:form.elements.category.value,mode:form.elements.mode.value});
      state.feedback=null;document.querySelector('#content').innerHTML=quizHtml();document.querySelector('#answer-input').focus();
    }else if(form.id==='answer-form')submitAnswer(form.elements.answer.value);
  }catch(error){if(form.id==='word-form')document.querySelector('#form-error').textContent=error.message;else toast(error.message);}
});

document.addEventListener('click',event=>{
  const button=event.target.closest('button');if(!button||button.disabled)return;
  try {
    if(button.dataset.page){navigate(button.dataset.page);return;}
    if(button.dataset.role){store.switchRole(button.dataset.role);state.quiz=null;state.feedback=null;state.query='';state.category='全部主题';navigate(teacher()?'admin':'home');return;}
    if(button.dataset.word){wordEditor(button.dataset.word);return;}
    if(button.dataset.record){showDetail(button.dataset.record);return;}
    if(button.dataset.export){
      const format=button.dataset.export;
      const url=URL.createObjectURL(new Blob([store.exportRecords(format)],{type:format==='json'?'application/json;charset=utf-8':'text/csv;charset=utf-8'}));
      const link=document.createElement('a');link.href=url;link.download=`ket-records.${format}`;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);return;
    }
    if(button.classList.contains('dialog-close')||button.classList.contains('dialog-close-button')){dialog.close();return;}
    switch(button.dataset.action){
      case 'add-word':wordEditor();break;
      case 'review':navigate('quiz');if(!state.quiz)document.querySelector('#quiz-mode').value='review';else toast('请先完成或结束当前练习。');break;
      case 'skip':submitAnswer('');break;
      case 'next':state.feedback=null;if(state.quiz.status==='completed')resultPage(state.quiz.id);else{document.querySelector('#content').innerHTML=quizHtml();document.querySelector('#answer-input').focus();}break;
      case 'abandon':if(window.confirm('结束本次练习？未完成的练习不会计入成绩。')){store.abandon(state.quiz.id);navigate('quiz');}break;
      case 'reset':case 'recover':if(window.confirm('恢复初始词库和示例成绩？此浏览器中新增的词汇和练习记录将被删除。')){
        if(!store){localStorage.removeItem(STORAGE_KEY);store=new DemoStore(seed,localStorage);}else store.reset();
        state.quiz=null;state.feedback=null;state.query='';state.category='全部主题';navigate(teacher()?'admin':'home');toast('演示数据已重置。');
      }break;
    }
  }catch(error){toast(error.message);}
});

document.addEventListener('input',event=>{if(event.target.id==='word-search'){clearTimeout(searchTimer);searchTimer=setTimeout(()=>{try{refreshWords();}catch(e){toast(e.message);}},150);}});
document.addEventListener('change',event=>{if(event.target.id==='word-category'){try{refreshWords();}catch(e){toast(e.message);}}});
window.addEventListener('storage',event=>{
  if(event.key!==STORAGE_KEY||!store)return;
  try{dialog.close();navigate(state.page,false);toast('演示数据已在另一个页面更新。');}catch(e){toast(e.message);}
});

async function boot() {
  try{
    const response=await fetch(new URL('./data/words.json',import.meta.url));
    if(!response.ok)throw new Error('词库加载失败，请刷新页面重试。');
    seed=await response.json();store=new DemoStore(seed,localStorage);navigate('home',false);
  }catch(error){app.innerHTML=`<main class="error-page"><h1>无法打开演示</h1><p>${esc(error.message)}</p>${seed?'<button data-action="recover">重置演示数据</button>':'<p>请通过网站地址访问，或按照 README 启动本地预览。</p>'}</main>`;}
}
boot();
