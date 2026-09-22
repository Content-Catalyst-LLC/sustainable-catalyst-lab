# Platform Core v3 Visual Reasoning & Scientific Scene Bridge — Lab v0.109.0

Lab v0.109.0 binds Sustainable Catalyst Lab scientific visualization to Platform Core v3 without merging rendering responsibilities into Core.

## Authority boundary

**Platform Core owns:** canonical visual references, unified research-session visual bindings, renderer-neutral scene semantics, cross-product visual identity, and provenance/reference relationships.

**Research Lab owns:** scientific scene normalization, renderer selection/negotiation, SVG/Canvas/WebGL2/WebGPU rendering, 3D/4D scientific interaction, linked scientific views, uncertainty visualization, and underlying figure/scene artifacts.

Core does not render visuals, perform GPU work, infer uncertainty, infer linked-view relationships, or infer scientific truth from visual form.

## Core contracts

- Unified research runtime: `sc.research.unified-research-scientific-investigation-runtime.v1`
- Visual scene: `sc.visual-runtime.scene.v1`
- Unified visual reasoning: `sc.visual-runtime.unified-reasoning.v1`
- Cross-product visual runtime: `sc.visual-runtime.cross-product-integration.v1`
- Core visual-binding target: `POST /v1/research/unified-runtime/visual-bindings`

## Lab bridge surfaces

The backend exposes 12 v0.109 routes under `/v1/platform-core-v3-visual-scene`: health, manifest, schema, visual normalization/binding, scene normalization/bridging, linked-view bridging, uncertainty bridging, renderer catalog/negotiation, and legacy-scene mapping.

## Scene conversion

Lab v0.77 scientific scenes and v0.88 advanced scientific scene graphs can be converted into a renderer-neutral Core scene envelope. Lab geometry/render state remains authoritative. Core receives semantic nodes, declared parent-child relations, views, source bindings, and a scene hash for research-session lineage.

## Rendering

Renderer discovery exposes the retained Lab renderer registry and WebGPU/advanced-scene capability descriptors. Renderer negotiation is performed by Lab/browser-runtime policy; Core records the resulting reference context but does not choose or execute a renderer automatically.
