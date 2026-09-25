import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {DemoStore,STORAGE_KEY,normalize,matches} from '../site/engine.js';
const seed=JSON.parse(readFileSync(new URL('../site/data/words.json',import.meta.url),'utf8'));
function fixture(){
  const values=new Map();
  const storage={getItem:key=>values.get(key)||null,setItem:(key,value)=>values.set(key,value),removeItem:key=>values.delete(key)};
  return {store:new DemoStore(seed,storage),storage};
}
function finish(store,q,correct=true){q.answers.forEach((a,i)=>store.answer(q.id,i,correct?a.english:'incorrect-answer'));}
function clean(store){store.mutate(data=>{data.quizzes=[];});}

test('opens as student without accounts and labels sample records',()=>{
  const {store}=fixture();assert.equal(store.role,'student');assert.equal(store.words().length,178);
  assert.equal(store.categories().length,19);assert.equal(store.records().length,3);
  assert.ok(store.records().every(r=>r.sample));assert.equal(store.summary().accuracy,60);
});
test('normalization and alternate spellings',()=>{
  assert.equal(normalize('  PENCIL　 Case '),'pencil case');
  assert.ok(matches({english:'pencil case'},'ＰＥＮＣＩＬ　ＣＡＳＥ'));
  assert.ok(matches({english:'colour',aliases:['color']},' COLOR '));
  assert.ok(!matches({english:'colour',aliases:['color']},'colours'));
});
test('role views, word validation, uniqueness, persistence and disable',()=>{
  const {store,storage}=fixture();
  assert.throws(()=>store.saveWord({english:'robot',chinese:'机器人',category:'科技',enabled:true}));
  store.switchRole('teacher');
  const word=store.saveWord({english:'robot',chinese:'机器人',category:'科技',aliases:['a robot'],enabled:true});
  assert.equal(new DemoStore(seed,storage).words({query:'机器人'}).length,1);
  assert.throws(()=>store.saveWord({...word,id:undefined,english:'ＲＯＢＯＴ'}),/已存在/);
  assert.throws(()=>store.saveWord({...word,english:'\n'}));
  store.saveWord({...word,enabled:false});assert.equal(store.words({query:'robot'}).length,0);
  assert.equal(store.words({query:'robot',includeDisabled:true}).length,1);
  assert.throws(()=>store.startQuiz());store.switchRole('student');assert.throws(()=>store.words({includeDisabled:true}));
});
test('quiz sampling, range and one active quiz',()=>{
  const {store}=fixture();
  for(const count of [0,-1,501,1.5,'3',true])assert.throws(()=>store.startQuiz({count}));
  const q=store.startQuiz({count:500,category:'四季时光'});
  assert.equal(q.answers.length,4);assert.equal(new Set(q.answers.map(a=>a.id)).size,4);
  assert.throws(()=>store.startQuiz(),/当前练习/);
});
test('retry, resume, order and completion',()=>{
  const {store,storage}=fixture();clean(store);
  const q=store.startQuiz({count:3});
  assert.throws(()=>store.answer(q.id,1,'wrong'),/当前题目/);
  store.answer(q.id,0,q.answers[0].english.toUpperCase());
  store.answer(q.id,0,q.answers[0].english.toUpperCase());
  assert.throws(()=>store.answer(q.id,0,'changed'),/不能修改/);
  const reopened=new DemoStore(seed,storage);assert.equal(reopened.activeQuiz().answers.filter(a=>a.answer!==null).length,1);
  reopened.answer(q.id,1,'');reopened.answer(q.id,2,q.answers[2].english);
  assert.equal(reopened.activeQuiz(),null);assert.equal(reopened.detail(q.id).accuracy,66.7);
  assert.equal(reopened.records().length,1);
});
test('teacher edits cannot alter a running question or completed grade',()=>{
  const {store}=fixture();clean(store);
  const q=store.startQuiz({count:1});store.switchRole('teacher');
  const w=q.answers[0];store.saveWord({...w,english:'renamed word',chinese:'改过的释义',enabled:false});
  store.switchRole('student');store.answer(q.id,0,w.english);
  assert.equal(store.detail(q.id).correct,1);assert.equal(store.detail(q.id).answers[0].english,w.english);
});
test('review uses latest completed answer and excludes disabled words',()=>{
  const {store}=fixture();clean(store);const q=store.startQuiz({count:4,category:'四季时光'});finish(store,q,false);
  assert.equal(store.mistakes().length,4);const review=store.startQuiz({count:10,mode:'review'});assert.equal(review.answers.length,4);
  finish(store,review,true);assert.equal(store.mistakes().length,0);assert.throws(()=>store.startQuiz({mode:'review'}));
});
test('abandoned exercises excluded from statistics',()=>{
  const {store}=fixture();clean(store);const q=store.startQuiz({count:2});store.answer(q.id,0,'');store.abandon(q.id);
  assert.equal(store.records().length,0);assert.equal(store.mistakes().length,0);assert.throws(()=>store.answer(q.id,1,'x'));
});
test('weighted accuracy differs from arithmetic mean; CSV and JSON export',()=>{
  const {store}=fixture();clean(store);finish(store,store.startQuiz({count:1}),true);finish(store,store.startQuiz({count:3}),false);
  assert.equal(store.summary().accuracy,25);assert.equal(store.summary().average,50);
  assert.equal(JSON.parse(store.exportRecords('json')).records.length,2);assert.ok(store.exportRecords('csv').startsWith('\ufeff'));
  assert.throws(()=>store.exportRecords('xml'));
});
test('CSV neutralizes spreadsheet formula prefixes',()=>{
  const {store}=fixture();clean(store);store.switchRole('teacher');store.saveWord({english:'robot',chinese:'机器人',category:'=1+1',enabled:true});
  store.switchRole('student');finish(store,store.startQuiz({count:1,category:'=1+1'}));
  assert.ok(store.exportRecords('csv').includes("'=1+1"));
});
test('failed storage write does not pretend to save',()=>{
  const {store,storage}=fixture();const previous=storage.getItem(STORAGE_KEY);store.switchRole('teacher');
  storage.setItem=()=>{throw new Error('quota');};
  assert.throws(()=>store.saveWord({english:'robot',chinese:'机器人',category:'科技',enabled:true}),/保存失败/);
  assert.equal(storage.getItem(STORAGE_KEY),previous);assert.equal(store.words({query:'robot'}).length,0);
});
test('reset and invalid storage handling',()=>{
  const {store,storage}=fixture();finish(store,store.startQuiz({count:1}));store.reset();
  assert.equal(store.records().length,3);assert.equal(store.words().length,178);
  storage.setItem(STORAGE_KEY,'invalid');assert.throws(()=>new DemoStore(seed,storage),/无法读取/);
});
test('separate visitors have independent data',()=>{
  const a=fixture().store,b=fixture().store;a.switchRole('teacher');a.saveWord({english:'robot',chinese:'机器人',category:'科技',enabled:true});
  assert.equal(a.words().length,179);assert.equal(b.words().length,178);
});
test('existing store sees updates from another view',()=>{
  const {store,storage}=fixture(),other=new DemoStore(seed,storage);other.switchRole('teacher');other.saveWord({english:'robot',chinese:'机器人',category:'科技',enabled:true});
  assert.equal(store.words().length,179);
});
