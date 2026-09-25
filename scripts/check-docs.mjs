/** Validate all equivalent documents, relative links and GitHub heading anchors. */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
const manifest=JSON.parse(fs.readFileSync(path.join(root,'doc/languages.json'),'utf8'));
const errors=[];
const content=file=>fs.readFileSync(path.join(root,file),'utf8');
const prose=text=>text.replace(/^```[^\n]*\n[\s\S]*?^```\s*$/gm,'');
const anchors=file=>{
  const counts=new Map(),ids=new Set();
  for(const match of prose(content(file)).matchAll(/^#{1,6}\s+(.+)$/gm)){
    const base=match[1].replace(/[*`]/gu,'').toLowerCase().replace(/[^\p{L}\p{N}_\-\s]/gu,'').replace(/\s/gu,'-');
    const n=counts.get(base)||0;ids.add(base+(n?`-${n}`:''));counts.set(base,n+1);
  }
  return ids;
};
for(const group of manifest.documents){
  if(group.length!==3) errors.push('Missing language equivalent: '+group.join(', '));
  for(const file of group){
    if(!fs.existsSync(path.join(root,file))){errors.push('Missing document: '+file);continue;}
    const text=content(file),top=text.split('\n').slice(0,6).join('\n');
    for(const peer of group.filter(peer=>peer!==file)){
      const relative=path.relative(path.dirname(file),peer).split(path.sep).join('/');
      if(!top.includes(`](${relative})`))errors.push(`${file}: missing language link to ${peer}`);
    }
    for(const [,raw] of prose(text).matchAll(/\]\(([^)]+)\)/gu)){
      if(/^(https?:|mailto:)/u.test(raw))continue;
      const [name,fragment]=decodeURIComponent(raw).split('#');
      const target=name?path.normalize(path.join(path.dirname(file),name)):file;
      const absolute=path.resolve(root,target);
      if(!absolute.startsWith(root)||!fs.existsSync(absolute)){errors.push(`${file}: broken link ${raw}`);continue;}
      if(fragment&&target.endsWith('.md')&&!anchors(target).has(fragment))errors.push(`${file}: missing anchor ${raw}`);
    }
    if(/^README(?:\.[^.]+)?\.md$/u.test(file)&&text.includes('kriswang55'))errors.push(`${file}: personal username in README`);
  }
}
if(errors.length){console.error(errors.join('\n'));process.exitCode=1;}
else console.log(`Verified ${manifest.documents.flat().length} documents: language links, relative files and heading anchors.`);
