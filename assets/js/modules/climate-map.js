(function(w){'use strict';
const Lab=w.SCLab=w.SCLab||{};
function gibsUrl(layer,date,bbox){const width=1400,height=700;const params=new URLSearchParams({SERVICE:'WMS',REQUEST:'GetMap',VERSION:'1.1.1',LAYERS:layer,STYLES:'',FORMAT:'image/jpeg',TRANSPARENT:'false',SRS:'EPSG:4326',BBOX:bbox,WIDTH:width,HEIGHT:height,TIME:date});return 'https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?'+params.toString()}
function render(image,layer,date,bbox,loading){if(loading)loading.hidden=false;image.onload=()=>{if(loading)loading.hidden=true};image.onerror=()=>{if(loading){loading.hidden=false;loading.textContent='Layer unavailable for this date or region.'}};image.src=gibsUrl(layer,date,bbox);return image.src}
Lab.ClimateMap={gibsUrl,render};
})(window);
