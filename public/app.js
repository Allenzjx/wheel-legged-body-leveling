const videos=[...document.querySelectorAll('video')];
for(const video of videos){
  video.addEventListener('play',()=>{for(const other of videos)if(other!==video)other.pause();});
  video.addEventListener('error',()=>{const status=video.parentElement.querySelector('.media-status');if(status)status.textContent='Video could not load. Use the direct MP4 link below or try again.';});
}
for(const button of document.querySelectorAll('[data-filter]'))button.addEventListener('click',()=>{
  for(const item of document.querySelectorAll('[data-filter]'))item.setAttribute('aria-pressed',String(item===button));
  for(const card of document.querySelectorAll('[data-category]')){card.hidden=button.dataset.filter!=='All'&&card.dataset.category!==button.dataset.filter;if(card.hidden)card.querySelector('video')?.pause();}
});
for(const button of document.querySelectorAll('[data-height]'))button.addEventListener('click',()=>{
  for(const item of document.querySelectorAll('[data-height]')){const active=item===button;item.setAttribute('aria-selected',String(active));item.tabIndex=active?0:-1;}
  for(const panel of document.querySelectorAll('[data-training]'))panel.hidden=panel.dataset.training!==button.dataset.height;
});
document.querySelector('[role="tablist"]')?.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;e.preventDefault();const tabs=[...document.querySelectorAll('[data-height]')];const next=tabs[e.key==='Home'?0:e.key==='End'?tabs.length-1:(tabs.indexOf(document.activeElement)+1)%tabs.length];next.focus();next.click();});
const links=[...document.querySelectorAll('.nav-links a')];
if('IntersectionObserver' in window){const observer=new IntersectionObserver(entries=>{for(const entry of entries)if(entry.isIntersecting){links.forEach(a=>a.removeAttribute('aria-current'));links.find(a=>a.hash===`#${entry.target.id}`)?.setAttribute('aria-current','location');}},{rootMargin:'-15% 0px -65% 0px'});document.querySelectorAll('main section[id]').forEach(section=>observer.observe(section));}
