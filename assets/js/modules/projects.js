(function(w){'use strict';
const Lab=w.SCLab=w.SCLab||{},U=Lab.util,KEY='scLabProjectsV010',ACTIVE='scLabActiveProjectV010';
function blank(name='Untitled Lab Project'){const now=U.now();return{id:U.uid('project'),name,createdAt:now,updatedAt:now,description:'',evidence:[],experiments:[],hypotheses:[],decisions:[],notes:[],calculations:[],documents:[],maps:[],activity:[]}}
function read(){try{const data=JSON.parse(localStorage.getItem(KEY)||'[]');return Array.isArray(data)?data:[]}catch(e){return[]}}
function write(items){localStorage.setItem(KEY,JSON.stringify(items))}
class Projects{
 constructor(){this.items=read();if(!this.items.length){this.items=[blank('Lab Project')];write(this.items)}this.activeId=localStorage.getItem(ACTIVE)||this.items[0].id;if(!this.get())this.activeId=this.items[0].id;localStorage.setItem(ACTIVE,this.activeId);this.listeners=[]}
 onChange(fn){this.listeners.push(fn)} emit(){this.listeners.forEach(fn=>fn(this.get(),this.items))}
 get(id=this.activeId){return this.items.find(p=>p.id===id)}
 select(id){if(this.get(id)){this.activeId=id;localStorage.setItem(ACTIVE,id);this.emit()}}
 create(name){const p=blank(name||'Untitled Lab Project');this.items.unshift(p);this.activeId=p.id;this.save();return p}
 update(mutator,activity){const p=this.get();if(!p)return;mutator(p);p.updatedAt=U.now();if(activity)p.activity.unshift({id:U.uid('activity'),at:p.updatedAt,text:activity});p.activity=p.activity.slice(0,200);this.save()}
 save(){write(this.items);localStorage.setItem(ACTIVE,this.activeId);this.emit()}
 add(collection,record,activity){this.update(p=>p[collection].unshift(Object.assign({id:U.uid(collection),createdAt:U.now()},record)),activity);return this.get()[collection][0]}
 export(){U.download(`${this.get().name.replace(/[^a-z0-9]+/gi,'-').toLowerCase()}-lab-project.json`,JSON.stringify(this.get(),null,2),'application/json')}
 import(raw){const p=JSON.parse(raw);if(!p||typeof p!=='object'||!p.name)throw new Error('Invalid project file');const merged=Object.assign(blank(p.name),p,{id:U.uid('project'),updatedAt:U.now()});['evidence','experiments','hypotheses','decisions','notes','calculations','documents','maps','activity'].forEach(k=>{if(!Array.isArray(merged[k]))merged[k]=[]});this.items.unshift(merged);this.activeId=merged.id;this.save();return merged}
}
Lab.Projects=Projects;
})(window);
