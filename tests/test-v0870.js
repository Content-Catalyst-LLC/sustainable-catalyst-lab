const fs=require('fs'),vm=require('vm'),assert=require('assert');
const calls=[];
const pass={setPipeline(){calls.push('setPipeline')},setBindGroup(){},setVertexBuffer(){},draw(n){calls.push(['draw',n])},end(){calls.push('renderPassEnd')}};
const device={
 createShaderModule(x){calls.push(['shader',x.label]);return {label:x.label}},
 createRenderPipeline(x){calls.push(['renderPipeline',x.label]);return {getBindGroupLayout(){return {}}}},
 createComputePipeline(x){calls.push(['computePipeline',x.label]);return {}},
 createBuffer(x){let mapped=new ArrayBuffer(x.size);return {getMappedRange(){return mapped},unmap(){},destroy(){}}},
 createBindGroup(){return {}},
 createTexture(){return {createView(){return {}}}},
 createCommandEncoder(){return {beginRenderPass(){return pass},finish(){return {}}}},
 queue:{writeBuffer(){},submit(){calls.push('submit')}},destroy(){}
};
const adapter={features:new Set(['timestamp-query']),limits:{maxBufferSize:123},async requestDevice(){calls.push('requestDevice');return device}};
const gpu={async requestAdapter(){calls.push('requestAdapter');return adapter},getPreferredCanvasFormat(){return 'bgra8unorm'}};
const contextGPU={configure(x){calls.push(['configure',x.format])},getCurrentTexture(){return {createView(){return {}}}}};
const canvas={width:960,height:540,getContext(type){return type==='webgpu'?contextGPU:null}};
const document={readyState:'complete',querySelector(){return null},addEventListener(){}};
const window={document,navigator:{gpu},GPUBufferUsage:{UNIFORM:1,COPY_DST:2,VERTEX:4},GPUTextureUsage:{RENDER_ATTACHMENT:8},SCLab:{},window:null};window.window=window;
const ctx={window,document,globalThis:window,navigator:window.navigator,console,JSON,Math,Error,String,Array,Object,Number,Set,Float32Array,ArrayBuffer,Promise};vm.createContext(ctx);vm.runInContext(fs.readFileSync('assets/js/modules/webgpu-scientific-renderer-v0870.js','utf8'),ctx);
(async()=>{const R=window.SCLabWebGPUScientificRendererV0870;assert(R);assert.strictEqual(R.version,'0.87.0');assert.strictEqual(R.engineVersion,'2.13.0');assert.strictEqual(R.renderer,'webgpu');assert.strictEqual(R.supported(),true);const d=await R.diagnostics();assert.strictEqual(d.supported,true);const renderer=await R.createRenderer(canvas);const out=await renderer.render({objects:[{type:'point-cloud',positions:[0,0,0,1,0,0,0,1,0],colors:[1,0,0,1,0,1,0,1,0,0,1,1]}]});assert.strictEqual(out.ok,true);assert.strictEqual(out.renderer,'webgpu');assert(calls.some(x=>Array.isArray(x)&&x[0]==='renderPipeline'));assert(calls.some(x=>Array.isArray(x)&&x[0]==='draw'));assert(calls.includes('submit'));const c=await renderer.runCompute({kernel:'histogram-v0870',itemCount:1000});assert.strictEqual(c.pipelineCreated,true);assert.strictEqual(c.createsObservation,false);assert(calls.some(x=>Array.isArray(x)&&x[0]==='computePipeline'));assert.strictEqual(R.boundaries.arbitraryWGSLSource,false);assert.strictEqual(R.boundaries.gpuRequiredForScientificCorrectness,false);console.log('PASS - v0.87.0 browser WebGPU renderer, device pipeline, draw submission and governed compute pipeline');})().catch(e=>{console.error(e);process.exit(1)});
