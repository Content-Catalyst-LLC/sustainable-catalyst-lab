(function(w){'use strict';const Lab=w.SCLab=w.SCLab||{};
const layers={
'MODIS_Terra_CorrectedReflectance_TrueColor':{label:'True color',group:'Land and atmosphere',unit:'reflectance'},
'MODIS_Terra_Land_Surface_Temp_Day':{label:'Land surface temperature',group:'Temperature',unit:'K'},
'IMERG_Precipitation_Rate':{label:'Precipitation rate',group:'Hydrology',unit:'mm/hr'},
'AIRS_L3_Carbon_Dioxide_500hPa_Volume_Mixing_Ratio_Daily_Day':{label:'Atmospheric CO₂',group:'Atmosphere',unit:'ppmv'},
'MODIS_Terra_Aerosol':{label:'Aerosol optical depth',group:'Atmosphere',unit:'dimensionless'},
'MODIS_Terra_NDSI_Snow_Cover':{label:'Snow cover',group:'Cryosphere',unit:'fraction'},
'VIIRS_SNPP_Chlorophyll_A':{label:'Ocean chlorophyll-a',group:'Ocean',unit:'mg/m³'} };
function gibsUrl(layer,date,bbox,format='image/jpeg'){const p=new URLSearchParams({SERVICE:'WMS',REQUEST:'GetMap',VERSION:'1.1.1',LAYERS:layer,STYLES:'',FORMAT:format,TRANSPARENT:'false',SRS:'EPSG:4326',BBOX:bbox,WIDTH:1400,HEIGHT:700,TIME:date});return 'https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?'+p.toString()}
function render(image,layer,date,bbox,loading){if(loading){loading.hidden=false;loading.textContent='Loading NASA GIBS layer…'}image.onload=()=>{if(loading)loading.hidden=true};image.onerror=()=>{if(loading){loading.hidden=false;loading.textContent='Layer unavailable for this date or region.'}};image.src=gibsUrl(layer,date,bbox);return image.src}
function coordinate(event,image,bbox){const rect=image.getBoundingClientRect(),[minLon,minLat,maxLon,maxLat]=bbox.split(',').map(Number);const x=(event.clientX-rect.left)/rect.width,y=(event.clientY-rect.top)/rect.height;return{longitude:minLon+x*(maxLon-minLon),latitude:maxLat-y*(maxLat-minLat)}}
Lab.ClimateMap={layers,gibsUrl,render,coordinate};})(window);
