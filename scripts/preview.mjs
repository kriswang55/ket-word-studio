/** Dependency-free static preview, also supporting a project-site subpath. */
import http from 'node:http';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';

const root=fileURLToPath(new URL('../site/',import.meta.url));
const port=Number(process.env.PORT||4173);
const prefix='/KETWordStudio';
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.svg':'image/svg+xml'};
const server=http.createServer(async(req,res)=>{
  try{
    let pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
    if(pathname===prefix){res.writeHead(302,{Location:prefix+'/'});res.end();return;}
    if(pathname.startsWith(prefix+'/'))pathname=pathname.slice(prefix.length);
    if(pathname.endsWith('/'))pathname+='index.html';
    const target=path.resolve(root,'.'+pathname);
    if(!target.startsWith(root)||!types[path.extname(target)])throw new Error();
    const body=await readFile(target);
    res.writeHead(200,{'Content-Type':types[path.extname(target)],'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});res.end(body);
  }catch{res.writeHead(404,{'Content-Type':'text/plain; charset=utf-8'});res.end('Not found');}
});
server.listen(port,'127.0.0.1',()=>console.log(`Preview: http://127.0.0.1:${server.address().port}${prefix}/`));
server.on('error',err=>{console.error(err.message);process.exitCode=1;});
