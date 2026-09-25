/* Sustainable Catalyst Lab v0.135.8.5.1 — Provenance Runtime Authority */
(function(W,D){'use strict';
const A={version:'0.135.8.5.2',ownerVersion:'0.135.8.5.2',owner:'graph-studio-native-provenance-v013585',legacyInteractionEnabled:false,legacyObserverAttached:false,claimedAt:new Date().toISOString()};
W.SCLabProvenanceAuthority=A;
W.SCLab=W.SCLab||{};
W.SCLab.GraphStudioProvenanceAuthorityV0135851={version:A.version,status:()=>({...A}),claim(){A.legacyInteractionEnabled=false;A.legacyObserverAttached=false;return {...A}}};
D.documentElement.dataset.scLabProvenanceAuthority='0.135.8.5.1';
})(window,document);
