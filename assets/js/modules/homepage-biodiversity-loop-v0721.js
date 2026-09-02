(function(W,D){
'use strict';
const VERSION='0.72.1', SELECTOR='[data-sc-lab-home-v0720][data-v0721-autoplay-loop="1"]';
const mounted=new WeakSet();
function reducedMotion(){return !!W.matchMedia&&W.matchMedia('(prefers-reduced-motion: reduce)').matches;}
function start(root){
  if(!root||reducedMotion())return;
  const button=root.querySelector('[data-v0710-animate]');
  if(!button||button.getAttribute('aria-pressed')==='true')return;
  button.click();
}
function stop(root){
  const button=root?.querySelector('[data-v0710-animate]');
  if(button&&button.getAttribute('aria-pressed')==='true')button.click();
}
function bind(root){
  if(!root||mounted.has(root))return;
  mounted.add(root);
  const media=W.matchMedia?W.matchMedia('(prefers-reduced-motion: reduce)'):null;
  if(media){
    const onChange=event=>event.matches?stop(root):start(root);
    if(media.addEventListener)media.addEventListener('change',onChange);
    else if(media.addListener)media.addListener(onChange);
  }
  W.requestAnimationFrame(()=>start(root));
}
function boot(){D.querySelectorAll(SELECTOR).forEach(bind);}
if(D.readyState==='loading')D.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
D.addEventListener('sc-lab:app-ready',boot);W.addEventListener('pageshow',boot);
W.SCLab=W.SCLab||{};
W.SCLab.HomepageBiodiversityLoopV0721={version:VERSION,boot,status:()=>({version:VERSION,autoplay:true,loop:true,reducedMotion:true})};
})(window,document);
