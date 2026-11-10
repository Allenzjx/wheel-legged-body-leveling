import fs from 'node:fs';
import path from 'node:path';
const root=path.resolve('dist');const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const errors=[];let checked=0;
const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);
if(new Set(ids).size!==ids.length)errors.push('Duplicate HTML IDs');
for(const [,url]of html.matchAll(/(?:src|href|poster)="([^"]+)"/g)){
  if(/^(https?:|mailto:|data:)/.test(url))continue;
  if(url.startsWith('#')){if(!ids.includes(url.slice(1)))errors.push(`Missing anchor ${url}`);continue;}
  if(url.startsWith('/'))errors.push(`Root-relative URL breaks repository subpath: ${url}`);
  const target=path.resolve(root,url.split('#')[0]);
  if(!target.startsWith(root+path.sep)||!fs.existsSync(target))errors.push(`Missing/unsafe local asset ${url}`);checked++;
}
for(const [,attrs]of html.matchAll(/<video\b([^>]*)>/g)){for(const required of ['controls','playsinline','preload="none"','poster='])if(!attrs.includes(required))errors.push(`Video missing ${required}`);if(/autoplay/.test(attrs))errors.push('Autoplay is not allowed');}
for(const [,attrs]of html.matchAll(/<img\b([^>]*)>/g))if(!/alt="[^"]+"/.test(attrs))errors.push('Image missing descriptive alt');
if(/TODO|placeholder|lorem ipsum|[A-Za-z]:\\|file:\/\//i.test(html))errors.push('Placeholder or local machine path in published HTML');
const resultFigures=JSON.parse(fs.readFileSync('content/results.json','utf8')).figures;
if(resultFigures.length!==5||resultFigures.some(f=>!html.includes(f.src)))errors.push('The five supplied results figures must be present');
if(html.indexOf('id="comparison"')>html.indexOf('id="recording"'))errors.push('Core comparison must precede the detailed sections');
if(/based on poster|latest.{0,20}policy|head_04|237,361|16\.7%|14\.5%/i.test(html))errors.push('Superseded framing or unscoped experimental claim in the report');
const githubLinks=[...html.matchAll(/href="(https?:\/\/(?:[^/]*\.)?github\.com\/[^\"]+)"/gi)].map(m=>m[1]);
if(githubLinks.length!==1||githubLinks[0]!=='https://github.com/Allenzjx/wheel-legged-body-leveling/tree/main/research/50mm')errors.push('Only the organized full-traversal 50 mm training link is permitted');
if(html.indexOf('50 mm Training Code')>html.indexOf('id="comparison"'))errors.push('The training-code link must appear in the opening title section');
if(/terminal training|terminal policy|late.updated|[\u3400-\u9fff]/i.test(html))errors.push('Public report must use English full-traversal framing');
const config=JSON.parse(fs.readFileSync('content/site.json','utf8'));
for(const v of config.videos){const file=path.join(root,v.src),buf=fs.readFileSync(file);if(buf.subarray(0,200).toString().includes('git-lfs'))errors.push(`LFS pointer: ${v.src}`);const moov=buf.indexOf(Buffer.from('moov')),mdat=buf.indexOf(Buffer.from('mdat'));if(moov<0||moov>mdat)errors.push(`No faststart: ${v.src}`);if(fs.statSync(file).size>25*1024*1024)errors.push(`Video exceeds static hosting per-file budget: ${v.src}`);}
if(errors.length){console.error(errors.join('\n'));process.exit(1);}console.log(`PASS: ${checked} local references, ${ids.length} unique anchors; media faststart, captions, accessibility basics, relative deployment paths and content hygiene.`);
