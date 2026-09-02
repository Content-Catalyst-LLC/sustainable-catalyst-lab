# Homepage 4D Biodiversity Widget

## Shortcode

```text
[sc_lab_home_preview]
```

Alias:

```text
[sc_lab_home_biodiversity]
```

## Recommended homepage placement

Use the shortcode as the Lab feature section on the Sustainable Catalyst homepage. The shortcode owns its public presentation and loads only the 4D visualization assets it needs; do not wrap it in the older tan/cream Lab feature card.

## Public model dimensions

- X: Habitat quality
- Y: Climate stress
- Z: Relative biodiversity response
- 4th dimension: Time / disturbance progression

The 4D renderer is the same browser-rendered v0.71 visualization system used by the Lab scientific front door. The homepage supplies a biodiversity profile and public-safe presentation rather than introducing a second renderer.

## Scientific boundary

The widget uses deterministic synthetic interface values. It is not a biodiversity dataset, species count, ecological measurement, forecast, conservation-status estimate, or policy conclusion.

## Health endpoint

```text
/wp-json/sc-lab/v1/homepage/v0720/health
```

Expected public state includes:

- `ok: true`
- `version: 0.72.0`
- `profile: biodiversity`
- `dimensionsRepresented: 4`
- `browserRendered: true`
- `computeRequired: false`

## Acceptance check

1. The homepage renders a 4D biodiversity surface rather than descriptive Lab cards alone.
2. Habitat quality, climate stress, biodiversity response, and time are visible as the modeled dimensions.
3. Time slice changes the surface.
4. XW and YW controls alter the projected 4D tesseract.
5. The optional time sweep animates unless reduced motion is preferred.
6. The widget is responsive in Chrome and Safari.
7. The public scientific-boundary statement remains visible.
8. Enter the Lab and Open Graph Studio actions route to the Lab.
