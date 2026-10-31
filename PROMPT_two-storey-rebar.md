# Build a stunning, highly realistic, fully interactive 3D construction simulation of a two-storey reinforced-concrete frame — every rebar generated from Taiwan structural standard drawings.

Use Three.js and WebGL. Deliver a complete, runnable browser application.

---

## THE OBJECT

A complete two-storey RC frame under construction, centered in a clean, realistic Taiwan construction site: formwork plywood stacked on one side, scaffolding along one elevation, a tower crane footing visible outside the working area.

The frame must contain:

- **Foundation / ground beams (地梁)** with column starter bars projecting upward.
- **2 storeys × 4 bays × 3 bays** column grid, 6.0 m × 5.0 m spans, 3.6 m floor-to-floor (3.0 m clear height `Hn`).
- **Columns 60 × 60 cm**, **beams 40 × 70 cm**, **slabs 15 cm thick**, every member built twice — once as **rebar cage** and once as **formwork + concrete**.
- **8 structural cells** (2 floors × beam/slab frame), each with visible: main bars, closed stirrups, crossties (繫筋), slab mats in two layers, beam-column joint reinforcement, mechanical couplers (續接器), concrete spacers (墊塊).
- Every bar must be individually identifiable: diameter, mark number, drawing reference, and the rule that produced its length.

Required detail per member:

| Member | Must show |
|---|---|
| Column | 12 main bars, closed tie, crossties every tie, 135°/90° alternating hooks, couplers with staggered splices, cover 4 cm |
| Beam | top bars anchored 90° into columns, bottom bars, closed stirrup with one 135° and one 90° hook, alternating per stirrup, web bars when effective depth > 90 cm, cover 4 cm |
| Slab | bottom mat both directions, top mat over supports extending 0.25 L, anchorage `Ld`, corner and opening reinforcement, cover 2 cm |
| Joint | beam bars passing inside/outside the column cage correctly, joint hoops at 10 cm |
| Base | ground-beam cage with column dowels, starter-bar lap lengths |

Realistic metallic materials for rebar (mill-scale grey with rust, helical rib relief, 1.5 cm rib pitch), rubber and steel for couplers, plywood and steel for formwork, cast concrete for the completed members.

---

## REAL CONSTRUCTION ANIMATION

The model must actually be assembled, not merely appear:

- A deterministic `renderAt(t)` construction timeline drives erection: **ground beams → 1F columns → 2F beam/slab frame → 2F columns → roof beam/slab frame**.
- Within each member, bars appear in the real tying order: **main bars → closed stirrups → crossties → spacers**, not all at once.
- Every bar must stay geometrically correct for its entire life: column bars run continuous through the floor line; couplers stay on the intended bar and stagger ≥ 60 cm from their neighbour; beam bars never jump when their parent group animates; stirrups never detach from the main bars.
- Column bars from the lower storey must visually align with the upper storey cage through the beam-column joint — no gaps, no interpenetration, no floating parts.
- Playing speed adjustable from 0 to 1× of real construction pacing; scrubbing the timeline must be fully reversible and frame-exact.
- Provide a slow-motion mode to inspect the tying order at a single joint.

---

## 3D EXPLORATION

- WASD + mouse for first-person walking, with gravity-locked eye height and collision against formwork and stored material.
- Mouse-orbit mode for inspecting any member.
- Smooth zoom and camera interpolation between saved viewpoints (`reset camera` returns to the default cinematic angle).
- Realistic perspective and human scale — an operator standing beside a 3.6 m column cage must read as 1.75 m tall against it.
- Allow walking around and inside the frame, including under the 2F slab.

---

## INTERACTIVE FEATURES

- **START / STOP** — play or pause the construction animation.
- **SPEED** — 0 to 1× playback, smoothly eased, no snapping.
- **CUTAWAY MODE** — make formwork and concrete transparent so the interior cage is visible, with correct depth sorting and no z-fighting.
- **EXPLODED VIEW** — smoothly separate storeys, then members, then individual bar groups along authored axes.
- **ASSEMBLE** — restore every component to its original position with reversible easing.
- **PART INSPECTION** — click any major component to highlight it and display: name, drawing reference (e.g. `RC06`), bar marks (e.g. `12-#7`, `#3@10/15`), quantity, total weight, and the governing rule text.
- **STOREY / MEMBER FILTER** — toggle column, beam, slab, joint, coupler layers independently.
- **RESET CAMERA**.

---

## STANDARDS COMPLIANCE — the core of the task

Every dimension must be traceable to a Taiwan standard drawing. No invented geometry.

**Rebar nominal sizes (CNS 560)** — `#3 Ø9.53`, `#4 Ø12.70`, `#5 Ø15.88`, `#6 Ø19.05`, `#7 Ø22.23`, `#8 Ø25.40`, `#9 Ø28.65`, `#10 Ø32.26`, `#11 Ø35.81`, `#14 Ø43.0` mm.

**Column (RC06)**
- Confinement zone `ℓo = max(Hn/6, max(b,h), 45 cm)`, capped at `H/2`, measured at both column ends.
- First tie at **5 cm** from the floor line; tie spacing `10 cm` inside `ℓo`, `15 cm` in the centre.
- Hook extension `max(6·db, 7.5 cm)`.
- Crossties at **every** tie, hooked to interior main bars, **135° and 90° alternating**, outer-tie hooks offset in the four corners.
- Lateral support required wherever `hx > 20 cm`; tie centre spacing ≤ 35 cm, clear spacing ≤ 15 cm.

**Beam (RC04)**
- At least 2 top bars continuous to the support and anchored 90°.
- First stirrup at **5 cm** from the column face.
- End zone `2h`: `S1 = min(h/4, 8·db, 24·ds, 30 cm)` **and never > 15 cm**.
- Centre zone: `S2 = min(h/2, 30 cm)`.
- Web bars ≥ 2-#4 when effective depth `d = h − cover − db/2 > 90 cm`.
- Stirrup has one 135° and one 90° hook, alternating between adjacent stirrups; on perimeter beams all 135° hooks face outward.

**Slab (RC07 / RC08)**
- Bottom mat both directions at 15 cm.
- Top mat over supports extending **0.25 L**; anchorage `Ld`; minimum bearing 15 cm.
- Corner reinforcement and opening reinforcement per RC07.
- Cover 2 cm.

**Beam penetrations (RC05)**
- `D ≤ h/10` no reinforcement; `≤ 10 cm` → 2-D10; `≤ 20 cm` → 2-D13; `≤ h/3` → 2-D16.
- No penetration within `1·h` of the column face.

**Mechanical couplers (RC10)**
- Sleeve length `3.5·db`, outer diameter `1.8·db`, centre spacing ≥ `3·db`, splice stagger ≥ 60 cm, clear cover ≥ `2·db`.
- Performance grades SA / A / B colour-coded.

**Cover (RC01)** — 4 cm columns and beams, 2 cm slabs, exposed faces per exposure class.
**Spacers (墊塊)** — 5 × 4 × 5 cm concrete blocks every 60–80 cm under bottom bars.

Every generated bar object must carry metadata:
`{ drawing: 'RC06', rule: 'ℓo = max(Hn/6, max(b,h), 45cm)', mark: '12-#7', dia: 22.23, length: 3.05 }`
and the inspection panel must display it.

---

## VISUAL QUALITY

- Physically based materials with an environment map; rebar must never render black.
- Helical rib relief on every bar via normal mapping with UV scaled to the bar's real length (1.5 cm pitch), not a global repeat.
- Soft directional shadows plus hemisphere fill; realistic workshop lighting, no flat ambient.
- Beveled edges on formwork, couplers, base plates and scaffolding.
- Smooth animation, cinematic default framing, deterministic output.
- Minimal, professional, dark control interface — no clutter, no tutorial overlays.

---

## ENGINEERING AND CODE REQUIREMENTS

- All geometry generated **programmatically** from parameters. Do not download a prebuilt building or rebar model.
- One authority for standards data: a single table of rebar sizes, cover values, zone formulas and drawing references — no magic numbers scattered in the renderer.
- Deterministic timeline (`renderAt(t)`) so any frame can be reproduced exactly; no reliance on elapsed wall-clock time for geometry.
- Instanced or merged geometry so a full frame with tens of thousands of bars holds ≥ 50 fps at 1080p on a desktop GPU.
- Robust lifecycle: switching modes, exploding, cutting away and resetting repeatedly must not leak geometries, materials or event listeners.
- No console errors, no dead controls, no placeholder interactions, no fake loading screens.
- Provide all files plus a one-command way to run it locally.

---

## ACCEPTANCE TESTS

The build is only complete when all of the following pass and are demonstrated:

1. Column tie spacing measured in the confinement zone = 100 mm and in the centre = 150 mm, within 1 mm, over 10 random samples.
2. First column tie centre is 50 mm from the floor line; first beam stirrup is 50 mm from the column face.
3. Beam stirrup spacing inside `2h` never exceeds 150 mm for any beam depth.
4. Adjacent couplers are staggered ≥ 600 mm on both faces of every column.
5. Column cages of consecutive storeys are coaxial through the joint — zero lateral offset, zero gap.
6. Every bar's `drawing` + `rule` metadata resolves when clicked, including on exploded and cutaway views.
7. Cutaway, exploded, assemble and reset can be cycled 20 times with no visual artefact, no memory growth and no console error.
8. Frame rate ≥ 50 fps at 1920 × 1080 with the full frame visible and the animation running.
9. Total rebar weight reported by the app matches a hand calculation from bar counts × unit weights to within 1 %.

---

## IMPORTANT

This is a benchmark of your ability to independently design, implement and deliver a sophisticated 3D application.

Do not provide a tutorial or implementation plan instead of the application. Make reasonable decisions autonomously.

Prioritize visual quality, standards correctness, functional interactions and stability equally. Deliver the best working implementation you can.
