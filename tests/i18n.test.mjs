import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {Translator, LOCALES, LANGUAGE_KEY} from '../site/i18n.js';
import {DemoStore, STORAGE_KEY} from '../site/engine.js';
const catalogues=Object.fromEntries(LOCALES.map(locale=>[locale,JSON.parse(fs.readFileSync(new URL(`../site/locales/${locale}.json`,import.meta.url),'utf8'))]));
const seed=JSON.parse(fs.readFileSync(new URL('../site/data/words.json',import.meta.url),'utf8'));
const storage=()=>{const values=new Map();return {getItem:k=>values.get(k)||null,setItem:(k,v)=>values.set(k,v)};};

test('all three catalogues have identical keys and formatting placeholders',()=>{
  for(const locale of LOCALES) for(const group of ['messages','categories','prompts']){
    assert.deepEqual(Object.keys(catalogues[locale][group]).sort(),Object.keys(catalogues.en[group]).sort());
    for(const [key,value] of Object.entries(catalogues[locale][group])){
      assert.ok(value.length>0,key);
      assert.deepEqual(value.match(/\{\d+\}/gu)?.sort()||[],catalogues.en[group][key].match(/\{\d+\}/gu)?.sort()||[]);
    }
  }
});
test('English default, Hong Kong Traditional Chinese, and unsupported locale handling',()=>{
  const i=new Translator(catalogues);
  assert.equal(i.locale,'en');assert.equal(i.t('学习概览'),'Learning overview');
  i.select('zh-HK');assert.equal(i.t('学习概览'),'學習概覽');
  assert.equal(i.t('第 {0} / {1} 题',1,5),'第 1 / 5 題');
  assert.equal(i.meaning('儿子'),'兒子');
  assert.equal(i.category('数码科技'),'數碼科技');
  assert.throws(()=>i.select('invalid'));
  assert.equal(new Translator(catalogues,'invalid').locale,'en');
});
test('language changes and preference failures cannot modify a running practice',()=>{
  const s=storage(),store=new DemoStore(seed,s),i=new Translator(catalogues);
  const q=store.startQuiz({count:2});store.answer(q.id,0,q.answers[0].english);
  const before=s.getItem(STORAGE_KEY);
  for(const locale of LOCALES){assert.equal(i.select(locale,s),true);assert.equal(s.getItem(STORAGE_KEY),before);}
  assert.equal(s.getItem(LANGUAGE_KEY),'zh-HK');
  assert.equal(i.select('en',{setItem(){throw Error('quota');}}),false);
  assert.equal(s.getItem(STORAGE_KEY),before);
  assert.equal(store.activeQuiz().answers.filter(a=>a.answer!==null).length,1);
});
test('domain validation messages and CSV headings translate; JSON remains machine-readable',()=>{
  const i=new Translator(catalogues);
  assert.equal(i.t('英文需要 1–100 个字符，不能包含控制字符。'),'English must contain 1–100 characters and no control characters.');
  const store=new DemoStore(seed,storage());
  const before=store.exportRecords('json');
  const csv=store.exportRecords('csv',i.t.bind(i));
  assert.match(csv,/Completed/);assert.match(csv,/All topics/);
  i.select('zh-HK');assert.match(store.exportRecords('csv',i.t.bind(i)),/完成時間/);
  assert.deepEqual(JSON.parse(before).records,JSON.parse(store.exportRecords('json')).records);
});
