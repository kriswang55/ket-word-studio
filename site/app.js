import {i18n, t, cat, meaning, LOCALES, LANGUAGE_NAMES, loadLanguages} from './i18n.js';
import {DemoStore, STORAGE_KEY} from './engine.js';

const app = document.querySelector('#app');
const dialog = document.querySelector('#detail');
const state = {page: 'home', quiz: null, feedback: null, query: '', category: '全部主题', wordRows: []};
let store, seed, toastTimer, searchTimer;
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const date = value => new Date(value).toLocaleString(i18n.locale, {month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hour12:false});
const mode = value => value === 'review' ? t("错题复习") : t("随机练习");
const source = quiz => `<span class="badge ${quiz.sample?'neutral':''}">${quiz.sample?t("示例记录"):t("本次演示")}</span>`;
const empty = text => `<div class="empty">${esc(text)}</div>`;
const stat = (label,value,unit='') => `<div class="stat"><span>${esc(label)}</span><strong>${esc(value)}<small>${esc(unit)}</small></strong></div>`;
const heading = (title,description='',actions='') => `<header class="page-head"><div><h1 tabindex="-1">${esc(title)}</h1>${description?`<p>${esc(description)}</p>`:''}</div>${actions}</header>`;
const exports = () => `<div class="row"><button class="small ghost" data-export="json">${t("导出 JSON")}</button><button class="small ghost" data-export="csv">${t("导出 CSV")}</button></div>`;
const teacher = () => store.role === 'teacher';
const categoryOptions = (selected='全部主题',all=true) => {
  const cats = teacher() ? [...new Set(store.words({includeDisabled:true}).map(w=>w.category))] : store.categories();
  return [...(all?['全部主题']:[]),...cats].map(c=>`<option value="${esc(all?c:cat(c))}"${c===selected?' selected':''}>${esc(cat(c))}</option>`).join('');
};
const canonicalCategory = value => Object.keys(i18n.catalogues[i18n.locale].categories).find(key=>cat(key)===value) ?? value;
const filteredWords = manage => store.words({category:state.category,includeDisabled:manage}).filter(w=>
  !state.query || (w.english+' '+w.chinese+' '+meaning(w.chinese)).normalize('NFKC').toLowerCase().includes(state.query.normalize('NFKC').trim().toLowerCase()));

function toast(message) {
  const box = document.querySelector('#toast'); box.textContent=message; box.classList.add('visible');
  clearTimeout(toastTimer); toastTimer=setTimeout(()=>box.classList.remove('visible'),4500);
}

function shell() {
  document.documentElement.lang=i18n.locale;
  document.title=t('KET Word Studio · 单词测试系统');
  document.querySelector('.dialog-close').setAttribute('aria-label',t('关闭对话框'));

  const nav = teacher() ? [['admin',t("管理概览")],['manage_words',t("词库管理")],['class_records',t("练习记录")]]
    : [['home',t("学习概览")],['quiz',t("单词练习")],['words',t("词汇手册")],['mistakes',t("错题复习")],['records',t("学习记录")]];
  app.innerHTML = `<div class="shell"><aside class="sidebar">
    <a class="brand" href="./"><img src="./icon.svg" alt=""><b>KET Word Studio</b></a>
    <div class="language-switch" role="group" aria-label="${t('语言')}">${LOCALES.map(locale=>`<button type="button" data-language="${locale}" aria-pressed="${locale===i18n.locale}">${LANGUAGE_NAMES[locale]}</button>`).join('')}</div>
    <div class="role-switch" role="group" aria-label="${t("切换演示身份")}"><button data-role="student" aria-pressed="${!teacher()}">${t("学生页面")}</button><button data-role="teacher" aria-pressed="${teacher()}">${t("教师页面")}</button></div>
    <nav class="nav" aria-label="${t("主要导航")}">${nav.map(([key,text])=>`<button data-page="${key}" ${state.page===key?'aria-current="page"':''}>${text}</button>`).join('')}</nav>
    <div class="demo-controls"><p>${t("数据仅保存在此浏览器。")}</p><button class="ghost small" data-action="reset">${t("重置演示数据")}</button></div>
    </aside><main class="main"><div class="context"><span>${t("单词测试系统")}</span><span class="badge">${teacher()?t("教师"):t("学生")}</span></div><div id="content"></div></main></div>`;
}

function chart(records) {
  if (!records.length) return empty(t("暂无已完成的练习。"));
  const rows=[...records].reverse();
  const points=rows.map((r,i)=>[42+i*(350/Math.max(rows.length-1,1)),140-r.accuracy,r]);
  return `<svg class="chart" viewBox="0 0 420 177" role="img" aria-label="${t('最近 {0} 次练习的正确率，按完成顺序排列',rows.length)}">
    ${[0,50,100].map(n=>`<line x1="38" y1="${140-n}" x2="405" y2="${140-n}"/><text x="0" y="${144-n}">${n}%</text>`).join('')}
    <polyline points="${points.map(p=>p.slice(0,2).join(',')).join(' ')}"/>
    ${points.map(([x,y,r],i)=>`<circle cx="${x}" cy="${y}" r="4"><title>${r.sample?t("示例"):t("本次演示")}：${r.accuracy}%</title></circle><text x="${x}" y="166" text-anchor="middle">${i+1}</text>`).join('')}</svg>`;
}

function recordTable(records) {
  if (!records.length) return empty(t("暂无已完成的练习。"));
  return `<div class="table-wrap"><table><thead><tr><th>${t("完成时间")}</th><th>${t("主题 / 方式")}</th><th>${t("正确 / 题数")}</th><th>${t("正确率")}</th><th>${t("来源")}</th><th>${t("操作")}</th></tr></thead><tbody>
    ${records.map(r=>`<tr><td>${date(r.completedAt)}</td><td>${esc(cat(r.category))}<small class="cell-note">${mode(r.mode)}</small></td><td>${r.correct} / ${r.total}</td><td><b>${r.accuracy}%</b></td><td>${source(r)}</td><td><button class="small secondary" data-record="${esc(r.id)}">${t("查看详情")}</button></td></tr>`).join('')}
    </tbody></table></div>`;
}

function home() {
  const d=store.summary(), active=store.activeQuiz();
  return `${heading(t("学习概览"),d.sampleCount?t('当前包含 {0} 条示例记录。新增练习会单独标注。',d.sampleCount):'',`<button data-page="quiz">${active?t("继续练习"):t("开始练习")}</button>`)}
    <section class="stats">${stat(t("已完成练习"),d.attempts,t("次"))}${stat(t("累计正确率"),d.accuracy+'%')}${stat(t("待复习单词"),d.mistakeCount,t("个"))}${stat(t("累计作答"),d.questions,t("题"))}</section>
    <div class="section-grid"><section class="panel"><h2>${t("最近 7 次练习正确率")}</h2>${chart(d.recent)}</section>
      <section class="panel quick-panel"><h2>${t("练习与复习")}</h2><dl><div><dt>${t("启用词汇")}</dt><dd>${d.wordCount}</dd></div><div><dt>${t("词汇主题")}</dt><dd>${store.categories().length}</dd></div><div><dt>${t("待复习单词")}</dt><dd>${d.mistakeCount}</dd></div></dl><div class="row"><button class="secondary" data-action="review">${t("复习错题")}</button><button class="ghost" data-page="words">${t("查看词汇")}</button></div></section></div>
    <div class="section-title"><h2>${t("最近练习")}</h2><button class="small ghost" data-page="records">${t("全部记录")}</button></div>${recordTable(d.recent.slice(0,3))}`;
}

function admin() {
  const d=store.summary();
  return `${heading(t("管理概览"),t("此处展示当前浏览器中学生页面的练习数据。"),`<button data-page="manage_words">${t("管理词汇")}</button>`)}
    <section class="stats">${stat(t("启用词汇"),d.wordCount,t("个"))}${stat(t("词汇主题"),store.categories().length,t("个"))}${stat(t("完成练习"),d.attempts,t("次"))}${stat(t("累计正确率"),d.accuracy+'%')}</section>
    <section class="panel"><h2>${t("最近 7 次练习正确率")}</h2>${chart(d.recent)}</section>
    <div class="section-title"><h2>${t("最近练习")}</h2><button class="small ghost" data-page="class_records">${t("全部记录")}</button></div>${recordTable(d.recent.slice(0,3))}`;
}

function wordTable(words,manage=false) {
  if (!words.length) return empty(t("没有匹配的词汇。"));
  return `<div class="table-wrap"><table><thead><tr><th>${t("英文")}</th><th>${t("中文释义")}</th><th>${t("主题")}</th>${manage?`<th>${t("状态")}</th><th>${t("操作")}</th>`:''}</tr></thead><tbody>
    ${words.map(w=>`<tr><td class="word">${esc(w.english)}</td><td>${esc(meaning(w.chinese))}</td><td><span class="badge neutral">${esc(cat(w.category))}</span></td>${manage?`<td><span class="badge ${w.enabled?'':'neutral'}">${w.enabled?t("启用"):t("停用")}</span></td><td><button class="small secondary" data-word="${esc(w.id)}">${t("编辑")}</button></td>`:''}</tr>`).join('')}</tbody></table></div>`;
}

function wordsPage() {
  const manage=teacher();
  state.wordRows=filteredWords(manage);
  if(manage)state.wordRows.reverse();
  return `${heading(manage?t("词库管理"):t("词汇手册"),manage?t("停用词汇不再用于新练习，已完成的练习内容保持不变。"):t("搜索已启用的词汇。"),manage?`<button data-action="add-word">${t("添加词汇")}</button>`:'')}
    <div class="toolbar"><div class="search"><label for="word-search">${t("搜索词汇")}</label><input id="word-search" placeholder="${t("英文或中文释义")}" value="${esc(state.query)}"></div><div><label for="word-category">${t("词汇主题")}</label><select id="word-category">${categoryOptions(state.category)}</select></div><span id="word-count" class="muted">${t('{0} 个词条',state.wordRows.length)}</span></div>
    <div id="word-results">${wordTable(state.wordRows,manage)}</div>`;
}

function wordEditor(id) {
  const word=id?store.words({includeDisabled:true}).find(w=>w.id===id):null;
  if(id&&!word)throw new Error(t("词条不存在。"));
  const w=word||{english:'',chinese:'',category:'',aliases:[],enabled:true};
  document.querySelector('#detail-content').innerHTML=`<h2 id="dialog-title">${t(word?'编辑词汇':'添加词汇')}</h2>
    <form novalidate id="word-form" data-id="${esc(id||'')}"><div class="form-grid">
      <div><label for="english">${t("英文")}</label><input id="english" name="english" maxlength="100" value="${esc(w.english)}" required></div>
      <div><label for="chinese">${t("中文释义")}</label><input id="chinese" name="chinese" maxlength="200" value="${esc(meaning(w.chinese))}" required></div>
      <div class="wide"><label for="category">${t("主题")}</label><input id="category" name="category" list="category-list" maxlength="40" value="${esc(cat(w.category))}" required><datalist id="category-list">${categoryOptions('',false)}</datalist></div>
      <div class="wide"><label for="aliases">${t("其他可接受答案（用英文分号分隔）")}</label><input id="aliases" name="aliases" maxlength="2020" value="${esc(w.aliases.join('; '))}"></div>
      <label class="check wide"><input name="enabled" type="checkbox" ${w.enabled?'checked':''}>${t("启用词汇")}</label></div>
      <div id="form-error" class="inline-error" role="alert"></div><div class="row"><button type="submit">${t("保存词汇")}</button><button type="button" class="ghost dialog-close-button">${t("取消")}</button></div></form>`;
  dialog.showModal(); document.querySelector('#english').focus();
}

function recordsPage() {
  const d=store.summary();
  return `${heading(teacher()?t("练习记录"):t("学习记录"),t("示例记录与本次演示的记录均已标注来源。"),exports())}
    <section class="stats">${stat(t("最高正确率"),d.best+'%')}${stat(t("最低正确率"),d.worst+'%')}${stat(t("平均正确率"),d.average+'%')}${stat(t("完成练习"),d.attempts,t("次"))}</section>
    ${recordTable(store.records())}<p class="subnote">${t("平均正确率为各次练习的算术平均；累计正确率按总作答题数计算。")}</p>`;
}

function mistakesPage() {
  const rows=store.mistakes();
  return `${heading(t("错题复习"),t("显示最近一次完整练习仍答错的词；再次完成练习并答对后移出。"),rows.length?`<button data-action="review">${t("开始错题练习")}</button>`:'')}
    ${rows.length?`<div class="table-wrap"><table><thead><tr><th>${t("正确拼写")}</th><th>${t("中文释义")}</th><th>${t("上次答案")}</th><th>${t("累计答错")}</th></tr></thead><tbody>${rows.map(r=>`<tr><td class="word">${esc(r.english)}</td><td>${esc(meaning(r.chinese))}</td><td>${esc(r.answer)||t("（跳过）")}</td><td>${t('答错 {0} 次',r.wrongCount)}</td></tr>`).join('')}</tbody></table></div>`:empty(t("暂无待复习错词。"))}`;
}

function quizPage() {
  state.quiz=store.activeQuiz();state.feedback=null;
  if(state.quiz)return quizHtml();
  const count=store.words().length;
  return `${heading(t("单词练习"),t("根据中文释义填写英文。"))}<form novalidate id="quiz-config" class="panel quiz-layout">
    <div class="form-grid"><div><label for="quiz-mode">${t("练习方式")}</label><select id="quiz-mode" name="mode"><option value="random">${t("随机练习")}</option><option value="review">${t("错题复习")}</option></select></div>
    <div><label for="quiz-count">${t("题目数量")}</label><input id="quiz-count" name="count" type="number" min="1" max="500" value="${Math.min(10,count)||1}" required></div>
    <div class="wide"><label for="quiz-category">${t("词汇主题")}</label><select id="quiz-category" name="category">${categoryOptions()}</select></div></div>
    <button type="submit" ${count?'':'disabled'}>${t("开始练习")}</button><p class="subnote">${count?t("同次练习不重复抽词。词数不足时使用实际可用数量；忽略大小写和多余空格。"):t("没有启用的词汇，请先在教师页面添加或启用词汇。")}</p></form>`;
}

function quizHtml() {
  const q=state.quiz,f=state.feedback,index=f?f.index:q.answers.findIndex(a=>a.answer===null);
  const current=q.answers[index],answered=q.answers.filter(a=>a.answer!==null).length,correct=q.answers.filter(a=>a.correct).length;
  return `${heading(t("单词练习"),t("已提交的答案自动保存，离开页面后可以继续。"))}<div class="quiz-layout"><section class="panel quiz-card">
    <div class="quiz-meta"><span class="badge">${esc(cat(current.category))}</span><span>${t('第 {0} / {1} 题',index+1,q.answers.length)}</span></div><progress value="${answered}" max="${q.answers.length}" aria-label="${t("练习进度")}"></progress>
    <p class="muted">${t("请写出对应的英文单词或短语")}</p><h2 class="prompt">${esc(meaning(current.chinese))}</h2>
    <form id="answer-form"><label for="answer-input">${t("你的答案")}</label><input id="answer-input" class="answer-input" name="answer" maxlength="200" autocomplete="off" autocapitalize="none" spellcheck="false" placeholder="${t("输入英文答案")}" ${f?'disabled':''} value="${f?esc(current.answer):''}">
    ${f?`<div class="feedback ${current.correct?'':'wrong'}" role="status">${current.correct?t("回答正确"):t("回答错误，正确答案：")}<b>${esc(current.english)}</b></div><div class="answer-actions"><button type="button" data-action="next">${q.status==='completed'?t("查看本次成绩"):t("下一题")}</button></div>`:`<div class="answer-actions"><button type="submit">${t("提交答案")}</button><button type="button" class="ghost" data-action="skip">${t("跳过此题")}</button></div>`}</form></section>
    <div class="quiz-footer"><span>${t('已答对 {0} 题',correct)} · ${mode(q.mode)}</span>${q.status==='active'?`<button class="small ghost" data-action="abandon">${t("结束本次练习")}</button>`:''}</div></div>`;
}

function detailsTable(rows) {
  return `<div class="table-wrap"><table><thead><tr><th>${t("中文释义")}</th><th>${t("正确答案")}</th><th>${t("你的答案")}</th><th>${t("结果")}</th></tr></thead><tbody>${rows.map(r=>`<tr><td>${esc(meaning(r.chinese))}</td><td class="word">${esc(r.english)}</td><td>${esc(r.answer)||t("（跳过）")}</td><td><span class="badge ${r.correct?'':'wrong'}">${r.correct?t("正确"):t("错误")}</span></td></tr>`).join('')}</tbody></table></div>`;
}

function resultPage(id) {
  state.result=id;
  const r=store.detail(id);
  document.querySelector('#content').innerHTML=`${heading(t("练习完成"),t("成绩已保存至学习记录。"))}<section class="panel result"><strong>${r.accuracy}<span>%</span></strong><p>${t('共 {0} 题 · 答对 {1} 题 · 答错 {2} 题',r.total,r.correct,r.total-r.correct)}</p><div class="answer-actions"><button data-page="quiz">${t("再练一次")}</button><button class="secondary" data-page="mistakes">${t("复习错词")}</button></div></section><div class="section-title"><h2>${t("答题详情")}</h2></div>${detailsTable(r.answers)}`;
}

function showDetail(id) {
  const r=store.detail(id);
  document.querySelector('#detail-content').innerHTML=`<h2 id="dialog-title">${t("练习详情")}</h2><p class="review-note">${date(r.completedAt)} · ${t('{0} / {1} 题正确',r.correct,r.total)} · ${r.sample?t("示例记录"):t("本次演示")}</p>${detailsTable(r.answers)}`;
  dialog.showModal();
}

function navigate(page,focus=true) {
  state.result=null;
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
  state.wordRows=filteredWords(teacher());
  if(teacher())state.wordRows.reverse();
  document.querySelector('#word-results').innerHTML=wordTable(state.wordRows,teacher());
  document.querySelector('#word-count').textContent=t('{0} 个词条',state.wordRows.length);
}

document.addEventListener('submit',event=>{
  event.preventDefault();const form=event.target;
  try {
    if(form.id==='word-form'){
      store.saveWord({id:form.dataset.id||undefined,english:form.elements.english.value,chinese:form.elements.chinese.value,
        category:canonicalCategory(form.elements.category.value),aliases:form.elements.aliases.value.split(';').map(a=>a.trim()).filter(Boolean),enabled:form.elements.enabled.checked});
      dialog.close();state.query='';state.category='全部主题';navigate('manage_words');toast(t("词汇已保存。"));
    }else if(form.id==='quiz-config'){
      state.quiz=store.startQuiz({count:Number(form.elements.count.value),category:form.elements.category.value,mode:form.elements.mode.value});
      state.feedback=null;document.querySelector('#content').innerHTML=quizHtml();document.querySelector('#answer-input').focus();
    }else if(form.id==='answer-form')submitAnswer(form.elements.answer.value);
  }catch(error){if(form.id==='word-form')document.querySelector('#form-error').textContent=t(error.message);else toast(t(error.message));}
});

document.addEventListener('click',event=>{
  const button=event.target.closest('button');if(!button||button.disabled)return;
  try {
    if(button.dataset.language){switchLanguage(button.dataset.language);return;}
    if(button.dataset.page){navigate(button.dataset.page);return;}
    if(button.dataset.role){store.switchRole(button.dataset.role);state.quiz=null;state.feedback=null;state.query='';state.category='全部主题';navigate(teacher()?'admin':'home');return;}
    if(button.dataset.word){wordEditor(button.dataset.word);return;}
    if(button.dataset.record){showDetail(button.dataset.record);return;}
    if(button.dataset.export){
      const format=button.dataset.export;
      const url=URL.createObjectURL(new Blob([store.exportRecords(format,t)],{type:format==='json'?'application/json;charset=utf-8':'text/csv;charset=utf-8'}));
      const link=document.createElement('a');link.href=url;link.download=`ket-records.${format}`;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);return;
    }
    if(button.classList.contains('dialog-close')||button.classList.contains('dialog-close-button')){dialog.close();return;}
    switch(button.dataset.action){
      case 'add-word':wordEditor();break;
      case 'review':navigate('quiz');if(!state.quiz)document.querySelector('#quiz-mode').value='review';else toast(t("请先完成或结束当前练习。"));break;
      case 'skip':submitAnswer('');break;
      case 'next':state.feedback=null;if(state.quiz.status==='completed')resultPage(state.quiz.id);else{document.querySelector('#content').innerHTML=quizHtml();document.querySelector('#answer-input').focus();}break;
      case 'abandon':if(window.confirm(t("结束本次练习？未完成的练习不会计入成绩。"))){store.abandon(state.quiz.id);navigate('quiz');}break;
      case 'reset':case 'recover':if(window.confirm(t("恢复初始词库和示例成绩？此浏览器中新增的词汇和练习记录将被删除。"))){
        if(!store){localStorage.removeItem(STORAGE_KEY);store=new DemoStore(seed,localStorage);}else store.reset();
        state.quiz=null;state.feedback=null;state.query='';state.category='全部主题';navigate(teacher()?'admin':'home');toast(t("演示数据已重置。"));
      }break;
    }
  }catch(error){toast(t(error.message));}
});

document.addEventListener('input',event=>{if(event.target.id==='word-search'){clearTimeout(searchTimer);searchTimer=setTimeout(()=>{try{refreshWords();}catch(e){toast(t(e.message));}},150);}});
function switchLanguage(locale) {
  if(document.querySelector('#word-search')) { state.query=document.querySelector('#word-search').value; state.category=document.querySelector('#word-category').value; }
  const quiz=state.quiz, feedback=state.feedback, result=state.result;
  const draft=document.querySelector('#answer-input')?.value;
  const config=document.querySelector('#quiz-config');
  const values=config?Object.fromEntries(new FormData(config)):null;
  const saved=i18n.select(locale,localStorage);
  navigate(state.page,false);
  if(result) resultPage(result);
  else if(state.page==='quiz'&&quiz){state.quiz=quiz;state.feedback=feedback;document.querySelector('#content').innerHTML=quizHtml();if(draft!==undefined)document.querySelector('#answer-input').value=draft;}
  else if(values) for(const [name,value] of Object.entries(values)) document.querySelector('#quiz-config').elements[name].value=value;
  if(!saved)toast(t('语言偏好无法保存，下次启动将使用英语。'));
}

document.addEventListener('change',event=>{if(event.target.id==='word-category'){try{refreshWords();}catch(e){toast(t(e.message));}}});
window.addEventListener('storage',event=>{
  if(event.key!==STORAGE_KEY||!store)return;
  try{dialog.close();navigate(state.page,false);toast(t("演示数据已在另一个页面更新。"));}catch(e){toast(t(e.message));}
});

async function boot() {
  try{
    await loadLanguages(localStorage);
    const response=await fetch(new URL('./data/words.json',import.meta.url));
    if(!response.ok)throw new Error(t("词库加载失败，请刷新页面重试。"));
    seed=await response.json();store=new DemoStore(seed,localStorage);navigate('home',false);
  }catch(error){app.innerHTML=`<main class="error-page"><h1>${t("无法打开演示")}</h1><p>${esc(t(error.message))}</p>${seed?`<button data-action="recover">${t("重置演示数据")}</button>`:`<p>${t("请通过网站地址访问，或按照 README 启动本地预览。")}</p>`}</main>`;}
}
boot();
