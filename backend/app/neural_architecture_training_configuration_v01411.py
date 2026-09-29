from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime, timezone
from typing import Any

VERSION = "0.141.1"
PREDECESSOR_VERSION = "0.141.0"
RESEARCH_OS_VERSION = "0.140.0"
INTEGRITY_BASELINE = "0.140.0.1"
SCHEMA = "sc-lab-neural-architecture-training-configuration/0.141.1"
ARCHITECTURE_SCHEMA = "sc-lab-neural-architecture-specification/0.141.1"
TRAINING_SCHEMA = "sc-lab-neural-training-configuration/0.141.1"
WORKSPACE_HANDOFF_SCHEMA = "sc-workspace-neural-training-request/1.0"
CORE_HANDOFF_SCHEMA = "sc-core-neural-model-provenance-handoff/1.0"
SNAPSHOT_SCHEMA = "sc-lab-neural-architecture-training-snapshot/0.141.1"

BOUNDARY = (
    "Platform Core defines governed neural-model and provenance semantics; Workspace executes training and inference; "
    "Lab designs, compares, documents, and interprets experiments. Architecture declarations are not executable proof, "
    "training configurations are not successful runs, checkpoints are not endorsed models, and predictions are not evidence."
)

ARCHITECTURE_FAMILIES = (
    "mlp", "cnn", "rnn", "lstm", "gru", "transformer", "encoder-decoder", "autoencoder",
    "variational-autoencoder", "gan", "diffusion", "gnn", "hybrid", "custom"
)
OPTIMIZERS = ("sgd", "adam", "adamw", "rmsprop", "adagrad", "adadelta", "lion", "custom")
LOSSES = (
    "cross-entropy", "binary-cross-entropy", "mse", "mae", "huber", "nll", "kl-divergence",
    "contrastive", "triplet", "cosine-embedding", "ctc", "custom"
)
PRECISION_MODES = ("fp64", "fp32", "tf32", "bf16", "fp16", "mixed", "runtime-default")
COMPUTE_TARGETS = ("cpu", "mps", "cuda", "remote_gpu")
SCHEDULERS = ("none", "step", "multi-step", "cosine", "plateau", "one-cycle", "linear-warmup", "custom")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _txt(value: Any, limit: int = 4096) -> str:
    return str(value or "").strip()[:limit]


def _dict(value: Any) -> dict:
    return copy.deepcopy(value) if isinstance(value, dict) else {}


def _list(value: Any) -> list:
    return copy.deepcopy(value) if isinstance(value, list) else []


def _canon(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def _fp(value: Any) -> str:
    return hashlib.sha256(_canon(value).encode("utf-8")).hexdigest()


def _get(obj: dict, *names: str, default=None):
    if not isinstance(obj, dict):
        return default
    for name in names:
        if name in obj and obj[name] is not None:
            return obj[name]
    return default


def _normalize_layer(item: Any, index: int) -> dict:
    raw = item if isinstance(item, dict) else {"type": item}
    layer_id = _txt(_get(raw, "layerId", "layer_id", "id", "name"), 256) or f"layer-{index+1}"
    layer_type = _txt(_get(raw, "type", "layerType", "layer_type", "kind"), 128) or "custom"
    return {
        "layerId": layer_id,
        "type": layer_type,
        "name": _txt(_get(raw, "name", "label"), 256) or layer_id,
        "inputShape": copy.deepcopy(_get(raw, "inputShape", "input_shape")),
        "outputShape": copy.deepcopy(_get(raw, "outputShape", "output_shape")),
        "parameters": _dict(raw.get("parameters")),
        "trainable": bool(_get(raw, "trainable", default=True)),
        "activation": _txt(raw.get("activation"), 128),
        "normalization": _txt(raw.get("normalization"), 128),
        "dropout": raw.get("dropout"),
        "notes": _list(raw.get("notes")),
    }


def _normalize_edge(item: Any, index: int) -> dict:
    raw = item if isinstance(item, dict) else {}
    return {
        "edgeId": _txt(_get(raw, "edgeId", "edge_id", "id"), 256) or f"edge-{index+1}",
        "source": _txt(_get(raw, "source", "from", "sourceLayer"), 256),
        "target": _txt(_get(raw, "target", "to", "targetLayer"), 256),
        "kind": _txt(_get(raw, "kind", "type"), 128) or "feed-forward",
        "recurrent": bool(raw.get("recurrent", False)),
        "metadata": _dict(raw.get("metadata")),
    }


def normalize_architecture(payload: dict) -> dict:
    root = payload if isinstance(payload, dict) else {}
    raw = root.get("architecture") if isinstance(root.get("architecture"), dict) else _dict(_get(root, "modelSpecification", "model_specification", "model", default=root))
    experiment_id = _txt(_get(root, "experimentId", "experiment_id", "id"), 512)
    architecture_id = _txt(_get(raw, "architectureId", "architecture_id", "id"), 512)
    title = _txt(_get(raw, "title", "name"), 1024)
    family = _txt(_get(raw, "family", "architectureFamily", "architecture_family"), 128) or "custom"
    if family not in ARCHITECTURE_FAMILIES:
        family = "custom"
    if not architecture_id:
        architecture_id = f"arch-{_fp({'experimentId': experiment_id, 'title': title, 'family': family})[:20]}"
    layers = [_normalize_layer(v, i) for i, v in enumerate(_list(raw.get("layers")))]
    edges = [_normalize_edge(v, i) for i, v in enumerate(_list(_get(raw, "edges", "connections", default=[])))]
    record = {
        "schema": ARCHITECTURE_SCHEMA,
        "version": VERSION,
        "recordType": "neural-architecture-specification",
        "architectureId": architecture_id,
        "experimentId": experiment_id,
        "title": title or architecture_id,
        "family": family,
        "framework": _txt(_get(raw, "framework", "frameworkHint", "framework_hint"), 128),
        "inputSignature": copy.deepcopy(_get(raw, "inputSignature", "input_signature")),
        "outputSignature": copy.deepcopy(_get(raw, "outputSignature", "output_signature")),
        "layers": layers,
        "edges": edges,
        "modules": _list(raw.get("modules")),
        "declaredParameterCount": _get(raw, "declaredParameterCount", "declared_parameter_count", "parameterCount"),
        "initialization": _dict(raw.get("initialization")),
        "regularization": _dict(raw.get("regularization")),
        "constraints": _list(raw.get("constraints")),
        "assumptions": _list(raw.get("assumptions")),
        "notes": _list(raw.get("notes")),
        "provenance": _dict(raw.get("provenance")),
        "coreDefinesCanonicalSemantics": True,
        "labExecutesArchitecture": False,
        "automaticArchitectureApproval": False,
        "boundary": BOUNDARY,
    }
    record["fingerprint"] = _fp({k:v for k,v in record.items() if k != "fingerprint"})
    return {"ok": True, "version": VERSION, "architecture": record, "boundary": BOUNDARY}


def validate_architecture(payload: dict) -> dict:
    out = normalize_architecture(payload)
    a = out["architecture"]
    warnings=[]; errors=[]
    ids=[x["layerId"] for x in a["layers"]]
    if len(ids)!=len(set(ids)): errors.append("layer identifiers must be unique")
    known=set(ids)
    for e in a["edges"]:
        if not e["source"] or not e["target"]: errors.append(f"edge {e['edgeId']} requires source and target")
        elif known and (e["source"] not in known or e["target"] not in known): errors.append(f"edge {e['edgeId']} references an unknown layer")
        if e["source"]==e["target"] and not e["recurrent"]: warnings.append(f"edge {e['edgeId']} is self-referential but not declared recurrent")
    if not a["layers"]: warnings.append("no layer graph is declared; architecture remains an abstract specification")
    if a["family"]=="custom" and not a["notes"]: warnings.append("custom architecture has no explanatory notes")
    if not a["inputSignature"]: warnings.append("input signature is not declared")
    if not a["outputSignature"]: warnings.append("output signature is not declared")
    return {"ok": not errors, "version": VERSION, "architecture": a, "errors": errors, "warnings": warnings, "automaticApproval": False, "boundary": BOUNDARY}


def architecture_graph(payload: dict) -> dict:
    a=normalize_architecture(payload)["architecture"]
    nodes=[{"id":x["layerId"],"kind":"layer","label":x["name"],"layerType":x["type"],"trainable":x["trainable"]} for x in a["layers"]]
    edges=[{"id":x["edgeId"],"source":x["source"],"target":x["target"],"kind":x["kind"],"recurrent":x["recurrent"]} for x in a["edges"]]
    return {"ok":True,"version":VERSION,"architectureId":a["architectureId"],"nodes":nodes,"edges":edges,"graphIsDeclaredNotExecuted":True,"boundary":BOUNDARY}


def architecture_summary(payload: dict) -> dict:
    a=normalize_architecture(payload)["architecture"]
    type_counts={}
    for x in a["layers"]: type_counts[x["type"]]=type_counts.get(x["type"],0)+1
    return {"ok":True,"version":VERSION,"architectureId":a["architectureId"],"family":a["family"],"layerCount":len(a["layers"]),"edgeCount":len(a["edges"]),"layerTypes":type_counts,"declaredParameterCount":a["declaredParameterCount"],"parameterCountVerified":False,"boundary":BOUNDARY}


def normalize_training_configuration(payload: dict) -> dict:
    root=payload if isinstance(payload,dict) else {}
    raw=root.get("trainingConfiguration") if isinstance(root.get("trainingConfiguration"),dict) else _dict(_get(root,"training_configuration","training",default=root))
    experiment_id=_txt(_get(root,"experimentId","experiment_id"),512)
    config_id=_txt(_get(raw,"configurationId","configuration_id","configId","id"),512)
    if not config_id:
        config_id=f"traincfg-{_fp({'experimentId':experiment_id,'raw':raw})[:20]}"
    opt=_dict(raw.get("optimizer")); loss=_dict(raw.get("loss")); scheduler=_dict(raw.get("scheduler")); checkpoint=_dict(_get(raw,"checkpointPolicy","checkpoint_policy"))
    opt_name=_txt(_get(opt,"name","type"),128) or _txt(_get(raw,"optimizerName","optimizer_name"),128) or "adamw"
    loss_name=_txt(_get(loss,"name","type"),128) or _txt(_get(raw,"lossName","loss_name"),128) or "cross-entropy"
    sched_name=_txt(_get(scheduler,"name","type"),128) or "none"
    precision=_txt(_get(raw,"precision","precisionMode","precision_mode"),128) or "runtime-default"
    target=_txt(_get(raw,"computeTarget","compute_target"),128) or "cpu"
    record={
        "schema":TRAINING_SCHEMA,"version":VERSION,"recordType":"neural-training-configuration","configurationId":config_id,"experimentId":experiment_id,
        "epochs":_get(raw,"epochs","maxEpochs","max_epochs"),"batchSize":_get(raw,"batchSize","batch_size"),"seed":_get(raw,"seed","randomSeed","random_seed"),
        "optimizer":{"name": opt_name, **{k:v for k,v in opt.items() if k not in {'name','type'}}},
        "loss":{"name": loss_name, **{k:v for k,v in loss.items() if k not in {'name','type'}}},
        "scheduler":{"name":sched_name, **{k:v for k,v in scheduler.items() if k not in {'name','type'}}},
        "precision":precision,"computeTarget":target,"gradientClipping":copy.deepcopy(_get(raw,"gradientClipping","gradient_clipping")),
        "gradientAccumulationSteps":_get(raw,"gradientAccumulationSteps","gradient_accumulation_steps"),"earlyStopping":_dict(_get(raw,"earlyStopping","early_stopping")),
        "checkpointPolicy":checkpoint,"dataSplit":_dict(_get(raw,"dataSplit","data_split")),"augmentation":_list(raw.get("augmentation")),
        "runtime":_dict(raw.get("runtime")),"resourceLimits":_dict(_get(raw,"resourceLimits","resource_limits")),"distributed":_dict(raw.get("distributed")),
        "notes":_list(raw.get("notes")),"provenance":_dict(raw.get("provenance")),"workspaceExecutionAuthority":True,"labExecutesTraining":False,
        "automaticHyperparameterSelection":False,"automaticModelPromotion":False,"boundary":BOUNDARY,
    }
    record["fingerprint"]=_fp({k:v for k,v in record.items() if k!="fingerprint"})
    return {"ok":True,"version":VERSION,"trainingConfiguration":record,"boundary":BOUNDARY}


def validate_training_configuration(payload: dict) -> dict:
    out=normalize_training_configuration(payload); c=out["trainingConfiguration"]; warnings=[]; errors=[]
    if c["optimizer"]["name"] not in OPTIMIZERS: warnings.append("optimizer is custom or outside the built-in catalog")
    if c["loss"]["name"] not in LOSSES: warnings.append("loss is custom or outside the built-in catalog")
    if c["scheduler"]["name"] not in SCHEDULERS: warnings.append("scheduler is custom or outside the built-in catalog")
    if c["precision"] not in PRECISION_MODES: errors.append("unsupported declared precision mode")
    if c["computeTarget"] not in COMPUTE_TARGETS: errors.append("unsupported declared compute target")
    for key in ("epochs","batchSize"):
        v=c.get(key)
        if v is None: warnings.append(f"{key} is not declared")
        elif not isinstance(v,int) or v<=0: errors.append(f"{key} must be a positive integer when declared")
    if c["seed"] is None: warnings.append("deterministic seed is not declared")
    if not c["checkpointPolicy"]: warnings.append("checkpoint policy is not declared")
    return {"ok":not errors,"version":VERSION,"trainingConfiguration":c,"errors":errors,"warnings":warnings,"configurationValidatedNotExecuted":True,"boundary":BOUNDARY}


def optimizer_plan(payload: dict) -> dict:
    c=normalize_training_configuration(payload)["trainingConfiguration"]
    return {"ok":True,"version":VERSION,"configurationId":c["configurationId"],"optimizer":c["optimizer"],"catalogRecognized":c["optimizer"]["name"] in OPTIMIZERS,"selectionWasAutomatic":False,"boundary":BOUNDARY}


def loss_plan(payload: dict) -> dict:
    c=normalize_training_configuration(payload)["trainingConfiguration"]
    return {"ok":True,"version":VERSION,"configurationId":c["configurationId"],"loss":c["loss"],"catalogRecognized":c["loss"]["name"] in LOSSES,"selectionWasAutomatic":False,"boundary":BOUNDARY}


def scheduler_plan(payload: dict) -> dict:
    c=normalize_training_configuration(payload)["trainingConfiguration"]
    return {"ok":True,"version":VERSION,"configurationId":c["configurationId"],"scheduler":c["scheduler"],"selectionWasAutomatic":False,"boundary":BOUNDARY}


def seed_contract(payload: dict) -> dict:
    c=normalize_training_configuration(payload)["trainingConfiguration"]
    return {"ok":True,"version":VERSION,"configurationId":c["configurationId"],"seed":c["seed"],"deterministicSeedDeclared":c["seed"] is not None,"determinismGuaranteed":False,"reason":"A declared seed is necessary but not sufficient for deterministic neural execution.","boundary":BOUNDARY}


def checkpoint_policy(payload: dict) -> dict:
    c=normalize_training_configuration(payload)["trainingConfiguration"]
    return {"ok":True,"version":VERSION,"configurationId":c["configurationId"],"checkpointPolicy":c["checkpointPolicy"],"checkpointIsEndorsedModel":False,"boundary":BOUNDARY}


def precision_plan(payload: dict) -> dict:
    c=normalize_training_configuration(payload)["trainingConfiguration"]
    return {"ok":True,"version":VERSION,"configurationId":c["configurationId"],"precision":c["precision"],"runtimeMustVerifySupport":True,"numericalEquivalenceAssumed":False,"boundary":BOUNDARY}


def resource_plan(payload: dict) -> dict:
    c=normalize_training_configuration(payload)["trainingConfiguration"]
    return {"ok":True,"version":VERSION,"configurationId":c["configurationId"],"computeTarget":c["computeTarget"],"resourceLimits":c["resourceLimits"],"distributed":c["distributed"],"executionAuthority":"workspace","automaticScheduling":False,"boundary":BOUNDARY}


def dataset_binding(payload: dict) -> dict:
    root=payload if isinstance(payload,dict) else {}; datasets=_list(_get(root,"datasets","datasetBindings",default=[])); transformations=_list(root.get("transformations"))
    rows=[]
    for i,d in enumerate(datasets):
        x=d if isinstance(d,dict) else {"ref":d}
        rows.append({"index":i,"datasetRef":_txt(_get(x,"datasetRef","id","ref"),1024),"version":_txt(_get(x,"version","datasetVersion"),256),"role":_txt(_get(x,"role","split"),128) or "declared-input","sourceHash":_txt(_get(x,"sourceHash","hash","sha256"),256)})
    return {"ok":True,"version":VERSION,"datasets":rows,"transformations":transformations,"silentMutationAllowed":False,"boundary":BOUNDARY}


def experiment_binding(payload: dict) -> dict:
    root=payload if isinstance(payload,dict) else {}; experiment=_dict(root.get("experiment")); arch=normalize_architecture(root).get("architecture"); cfg=normalize_training_configuration(root).get("trainingConfiguration")
    experiment_id=_txt(_get(root,"experimentId","experiment_id"),512) or _txt(_get(experiment,"experimentId","id"),512) or arch["experimentId"] or cfg["experimentId"]
    return {"ok":True,"version":VERSION,"experimentId":experiment_id,"machineLearningExperimentWorkspaceVersion":PREDECESSOR_VERSION,"architectureId":arch["architectureId"],"configurationId":cfg["configurationId"],"bindingFingerprint":_fp({"experimentId":experiment_id,"architecture":arch["fingerprint"],"trainingConfiguration":cfg["fingerprint"]}),"automaticExecution":False,"boundary":BOUNDARY}


def workspace_handoff(payload: dict) -> dict:
    root=payload if isinstance(payload,dict) else {}; arch=normalize_architecture(root)["architecture"]; cfg=normalize_training_configuration(root)["trainingConfiguration"]
    exp=experiment_binding(root)
    request={"schema":WORKSPACE_HANDOFF_SCHEMA,"requestedBy":"sustainable-catalyst-lab","labRelease":VERSION,"experimentId":exp["experimentId"],"architecture":arch,"trainingConfiguration":cfg,"datasets":_list(root.get("datasets")),"transformations":_list(root.get("transformations")),"evaluationPlan":_dict(_get(root,"evaluationPlan","evaluation_plan")),"automaticExecution":False,"executionAuthority":"workspace","sourceFingerprint":exp["bindingFingerprint"]}
    request["requestFingerprint"]=_fp(request)
    return {"ok":True,"version":VERSION,"handoff":request,"labExecutesTraining":False,"boundary":BOUNDARY}


def core_handoff(payload: dict) -> dict:
    root=payload if isinstance(payload,dict) else {}; arch=normalize_architecture(root)["architecture"]; cfg=normalize_training_configuration(root)["trainingConfiguration"]
    packet={"schema":CORE_HANDOFF_SCHEMA,"labRelease":VERSION,"architectureSpecification":arch,"trainingConfiguration":cfg,"canonicalAuthority":"platform-core","labMayDefineScientificContext":True,"labMayOverrideCoreObjectSemantics":False}
    packet["fingerprint"]=_fp(packet)
    return {"ok":True,"version":VERSION,"handoff":packet,"boundary":BOUNDARY}


def configuration_fingerprint(payload: dict) -> dict:
    root=payload if isinstance(payload,dict) else {}; arch=normalize_architecture(root)["architecture"]; cfg=normalize_training_configuration(root)["trainingConfiguration"]
    fp=_fp({"architecture":arch["fingerprint"],"trainingConfiguration":cfg["fingerprint"],"datasets":_list(root.get("datasets")),"transformations":_list(root.get("transformations")),"evaluationPlan":_dict(_get(root,"evaluationPlan","evaluation_plan"))})
    return {"ok":True,"version":VERSION,"fingerprint":fp,"deterministicFromDeclaredConfiguration":True,"executionResultFingerprint":False,"boundary":BOUNDARY}


def compare_architectures(payload: dict) -> dict:
    root=payload if isinstance(payload,dict) else {}; items=_list(_get(root,"architectures","items",default=[])); rows=[]
    for i,item in enumerate(items):
        a=normalize_architecture({"architecture":item})["architecture"]
        rows.append({"index":i,"architectureId":a["architectureId"],"family":a["family"],"layerCount":len(a["layers"]),"edgeCount":len(a["edges"]),"declaredParameterCount":a["declaredParameterCount"],"fingerprint":a["fingerprint"]})
    return {"ok":True,"version":VERSION,"architectures":rows,"winnerSelected":False,"rankingProduced":False,"boundary":BOUNDARY}


def compare_training_configurations(payload: dict) -> dict:
    root=payload if isinstance(payload,dict) else {}; items=_list(_get(root,"configurations","trainingConfigurations","items",default=[])); rows=[]
    for i,item in enumerate(items):
        c=normalize_training_configuration({"trainingConfiguration":item})["trainingConfiguration"]
        rows.append({"index":i,"configurationId":c["configurationId"],"optimizer":c["optimizer"]["name"],"loss":c["loss"]["name"],"scheduler":c["scheduler"]["name"],"epochs":c["epochs"],"batchSize":c["batchSize"],"seed":c["seed"],"precision":c["precision"],"computeTarget":c["computeTarget"],"fingerprint":c["fingerprint"]})
    return {"ok":True,"version":VERSION,"configurations":rows,"winnerSelected":False,"automaticTuning":False,"boundary":BOUNDARY}


def snapshot(payload: dict) -> dict:
    root=payload if isinstance(payload,dict) else {}; arch=normalize_architecture(root)["architecture"]; cfg=normalize_training_configuration(root)["trainingConfiguration"]
    content={"schema":SNAPSHOT_SCHEMA,"version":VERSION,"architecture":arch,"trainingConfiguration":cfg,"datasets":_list(root.get("datasets")),"transformations":_list(root.get("transformations")),"evaluationPlan":_dict(_get(root,"evaluationPlan","evaluation_plan")),"experimentId":_txt(_get(root,"experimentId","experiment_id"),512)}
    fp=_fp(content)
    return {"ok":True,"version":VERSION,"snapshot":{**content,"snapshotId":f"natc-{fp[:24]}","fingerprint":fp},"generatedAt":_now(),"fingerprintExcludesGeneratedAt":True,"boundary":BOUNDARY}


def compare_snapshots(payload: dict) -> dict:
    root=payload if isinstance(payload,dict) else {}; left=_dict(root.get("left")); right=_dict(root.get("right"));
    def body(x):
        x=copy.deepcopy(x.get("snapshot") if isinstance(x.get("snapshot"),dict) else x)
        for k in ("snapshotId","fingerprint","generatedAt"): x.pop(k,None)
        return x
    l=body(left); r=body(right); keys=sorted(set(l)|set(r)); changes=[{"field":k,"left":l.get(k),"right":r.get(k)} for k in keys if l.get(k)!=r.get(k)]
    return {"ok":True,"version":VERSION,"equal":not changes,"changes":changes,"scientificSignificanceInferred":False,"boundary":BOUNDARY}


def reproducibility_packet(payload: dict) -> dict:
    snap=snapshot(payload)["snapshot"]
    packet={"schema":"sc-lab-neural-architecture-training-reproducibility-package/0.141.1","version":VERSION,"snapshot":snap,"workspaceHandoff":workspace_handoff(payload)["handoff"],"coreHandoff":core_handoff(payload)["handoff"],"requirements":["dataset versions/hashes","transformation lineage","architecture fingerprint","training configuration fingerprint","runtime/environment identity","returned run/checkpoint lineage"]}
    packet["fingerprint"]=_fp(packet)
    return {"ok":True,"version":VERSION,"package":packet,"reproducibilityCertified":False,"boundary":BOUNDARY}


def health() -> dict:
    return {"ok":True,"version":VERSION,"neural_architecture_training_configuration":True,"machineLearningExperimentWorkspaceVersion":PREDECESSOR_VERSION,"scientificResearchOperatingSystemVersion":RESEARCH_OS_VERSION,"manifestIntegrityBaseline":INTEGRITY_BASELINE,"api_route_count":33,"workspaceExecutionRequired":True,"labExecutesTraining":False,"predictionIsEvidence":False,"boundary":BOUNDARY}


def contract() -> dict:
    return {"ok":True,"version":VERSION,"schema":SCHEMA,"architectureSchema":ARCHITECTURE_SCHEMA,"trainingSchema":TRAINING_SCHEMA,"workspaceHandoffSchema":WORKSPACE_HANDOFF_SCHEMA,"coreHandoffSchema":CORE_HANDOFF_SCHEMA,"boundary":BOUNDARY}


def policy() -> dict:
    return {"ok":True,"version":VERSION,"coreDefinesCanonicalNeuralObjects":True,"workspaceExecutes":True,"labExperiments":True,"automaticArchitectureApproval":False,"automaticHyperparameterSelection":False,"automaticBestModelSelection":False,"checkpointIsEndorsedModel":False,"predictionIsEvidence":False,"boundary":BOUNDARY}


def release_gates() -> dict:
    return {"ok":True,"version":VERSION,"gates":["v0.140.0.1 installed-runtime integrity baseline retained","v0.141.0 ML Experiment Workspace retained","Platform Core neural object contracts available before governed handoff","Workspace neural runtime available before execution","architecture and training configuration fingerprints preserved with returned run lineage"],"automaticGateWaiver":False,"boundary":BOUNDARY}


def interpretation_boundary(_: dict|None=None) -> dict:
    return {"ok":True,"version":VERSION,"statements":["architecture specification is not executed model behavior","training configuration is not training success","declared parameter count is not independently verified","seed declaration does not guarantee determinism","checkpoint is not an endorsed model","prediction is not evidence"],"boundary":BOUNDARY}


def acceptance_report() -> dict:
    return {"ok":True,"version":VERSION,"architectureSpecification":True,"architectureValidation":True,"architectureGraph":True,"trainingConfiguration":True,"optimizerLossSchedulerPlans":True,"seedCheckpointPrecisionResourceContracts":True,"experimentBindingV01410":True,"workspaceExecutionHandoff":True,"platformCoreHandoff":True,"deterministicConfigurationFingerprint":True,"architectureConfigurationComparison":True,"reproducibilityPacket":True,"deterministicSnapshots":True,"manifestIntegrityBaselineV014001":True,"automaticBestModelSelection":False,"automaticScientificValidity":False,"predictionIsEvidence":False,"boundary":BOUNDARY}
