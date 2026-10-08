# Build Instruction - "Zenith Jeanz" Denim Runway Site

> Adapted from the "vyrn." runway prompt. Everything in `{{DOUBLE_BRACES}}` is a
> placeholder to fill in from the assets you upload (see **Asset checklist** at the end).
> Geometry, animation and interaction specs are kept identical to the original because
> they are brand-agnostic and already tuned.

Build the website described below **exactly** as specified. The whole design is embedded
in this file - do not look for any external design source.

## 0. Deliverable & ground rules

- Produce **one single `index.html`** in the project root. All CSS and JavaScript are
  **inline**. **No frameworks, no build tools, no external requests** (no CDNs, remote
  web-fonts or libraries). Local font files in `/fonts` are allowed (section 3).
- When finished, **serve it on a fresh localhost port** (e.g. `python3 -m http.server <port>`)
  and give the user the URL.
- **Responsive**: fills any window, desktop and mobile, no white letterbox bars, nothing
  important cropped. Re-layout on resize.
- Two states: the **runway** (all models walking) and the **detail** view (one model
  centered with product text). Behaviour in sections 5-9.

## 1. The media (videos in `/media`)

- At build time, look in `/media` for video files (`.mp4`, `.mov`, `.webm`, `.m4v`).
  **Sort by filename. Each video = one model**, in that order. Do not hardcode names.
- If a clip can't play inline (e.g. HEVC `.mov`), transcode to **H.264 `.mp4`**
  (`yuv420p`, `+faststart`, no audio) with ffmpeg, longer side ~900px. Reference the
  browser-playable files from the HTML.
- Every `<video>` is `muted loop autoplay playsinline preload="auto"`.
- Clips are full-body model shots on a **white/near-white background**, composited on a
  white page so frame edges vanish and nearer models occlude farther ones.

### 1a. Fallback fill (REQUIRED)

No videos → still build with **7 models**. Any model whose video is missing or fails to
load renders a solid fill of **`{{FALLBACK_COLOR, default #DCE3EA (pale denim)}}`** in the
same frame, behaving identically to a clip (runway travel, perspective scale, hover
dim/freeze, tap → detail). Implement as a filler element `width/height:100%` of the model box.

## 2. Canvas, scaling & responsiveness

- Author on a fixed **1440 x 900** stage, scaled to **cover** the viewport:
  `scale = max(innerWidth / 1440, innerHeight / 900)`.
- Stage anchored bottom-center: `left:50%; bottom:0; transform-origin:bottom center;
  transform: translateX(-50%) scale(scale)`; `overflow:hidden`. Recompute on `resize`.
- Page/stage background `#ffffff`.

## 3. Fonts & colors

- UI sans stack: `"{{BRAND_SANS}}", "Helvetica Neue", Helvetica, Arial, sans-serif`.
- Price serif stack (lining figures): `"{{BRAND_SERIF}}", "Didot", "Bodoni 72",
  "Times New Roman", Times, serif` + `font-variant-numeric: lining-nums;
  font-feature-settings: "lnum" 1, "onum" 0;`.
- If font files are provided in `/fonts` (`.woff2`), load them with local `@font-face`;
  otherwise rely on the fallbacks.
- Text `#000`; page `#fff`; fallback fill as in 1a.

## 4. Static furniture

### 4a. Logo - top-left, fixed to viewport
`position:fixed; left:12px; top:16px; width:{{LOGO_W}}px; height:{{LOGO_H}}px;
z-index:100000; transform-origin:top left;` scaled by the same cover-scale on resize.
Above the models. Inline the SVG from **`/brand/logo.svg`** verbatim (single colour
black, outlined paths, `preserveAspectRatio="none"`, `viewBox="0 0 {{LOGO_W}} {{LOGO_H}}"`).
Target rendered height ≈ 71px at 1440×900 (scale width proportionally).

### 4b. Bottom navigation - inside the stage, centered
`position:absolute; left:50%; bottom:20px; transform:translateX(-50%); display:flex;
gap:4px; z-index:100001;`. Pills: `background:rgba(0,0,0,0.05); backdrop-filter:blur(20px);
border-radius:200px; height:28px;`.
- Search icon pill (28×28, `padding:0`, 14px icon centred).
- Links pill (`width:600px; padding:6px 24px; justify-content:space-between`), 5 uppercase
  links, 12px, weight 600, `letter-spacing:0.2px`, `#000`:
  **{{NAV_1: New arrivals}} | {{NAV_2: women}} | {{NAV_3: men}} | {{NAV_4: denim}} | {{NAV_5: shows}}**
- Heart, user, cart icon pills.

Icons (feather-style, `stroke:#000; stroke-width:2; 14×14`):

```html
<!-- search -->  <svg viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
<!-- heart  -->  <svg viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
<!-- user   -->  <svg viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
<!-- cart   -->  <svg viewBox="0 0 24 24" fill="none" stroke="#000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/></svg>
```

## 5. The runway - core animation (unchanged)

Models walk toward the viewer along a perspective line: glide left→right, drift down,
grow. Seamless infinite loop; nothing pops on screen.

**Model frame**: absolute box, natural size **1200 × 2980**, `transform-origin:0 0`.

```css
.model video { position:absolute; top:0; left:50%; height:109.29%; width:auto;
  transform: translate(-50%, -4%); transform-origin: top center; }
```

```js
var CX = [-96.5, -1.0, 108.5, 263, 460.5, 694, 1013, 1422.5, 1832];
var BY = [506, 521, 554, 600, 662, 736, 831, 961, 1091];
var SC = [0.034167,0.046667,0.0675,0.098333,0.139167,0.188333,0.251667,0.339167,0.4572];
var NAT_W = 1200, NAT_H = 2980;
function lerp(a,b,t){ return a + (b-a)*t; }
function place(el, q){
  var i = Math.floor(q), f = q - i;
  var s  = lerp(SC[i], SC[i+1], f);
  var cx = lerp(CX[i], CX[i+1], f);
  var by = lerp(BY[i], BY[i+1], f);
  var x = cx - (NAT_W*s)/2, y = by - (NAT_H*s);
  el.style.transform = "translate3d("+x+"px,"+y+"px,0) scale("+s+")";
  el.style.zIndex = String(Math.round(s*10000));
}
var PERIOD = 8, SLOT_MS = 3600, SPACING = PERIOD / N;
var prog = 0, lastTime = null, paused = false;
function frame(now){
  if (lastTime === null) lastTime = now;
  var dt = now - lastTime; lastTime = now;
  if (!paused){
    prog = (prog + dt/SLOT_MS) % PERIOD;
    for (var i=0;i<models.length;i++) place(models[i], (i*SPACING + prog) % PERIOD);
  }
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
```

Stagger each clip's `currentTime` by `(i/N)*duration`. Honor `prefers-reduced-motion`
(place once, don't animate).

## 6. Hover (pointer devices)

Hover a model → `paused = true`, every other model pauses and dims to **70%** opacity,
only the hovered clip keeps playing, **no scale change**. Mouse-out resumes everything.
Dim via a 0.45s opacity transition on an inner wrapper.

## 7. Tap / click → detail view

- Others pause and fade out; tapped model animates (~0.65s transform) to viewport centre
  at ~90% viewport height and keeps playing; runway frozen; side panels fade in (0.5s).

```js
function detailTransform(el){
  var cs = coverScale, vw = innerWidth, vh = innerHeight;
  var s = (vh*0.9) / (NAT_H*cs);
  var maxBoxW = vw - 2*300;
  if (NAT_W*s*cs > maxBoxW) s = maxBoxW/(NAT_W*cs);
  var mcy = 900 - vh/(2*cs);
  var x = 720 - (NAT_W*s)/2, y = mcy - (NAT_H*s)/2;
  el.style.transform = "translate3d("+x+"px,"+y+"px,0) scale("+s+")";
}
```
Recompute on resize while open (no transition). Selected model gets a high `z-index`.

## 8. Detail panels & product data

Both panels fixed to viewport, vertically centred, uppercase, 12px, weight 600, `#000`,
hidden by default.

- **Left** (`left:24px; width:220px;` column, `gap:20px`): name · description
  (`line-height:1.45`) · **more details** (underlined).
- **Right** (`right:24px; width:154px;` column, `gap:12px`, right-aligned):
  **add to wishlist** (underlined) · size row **{{SIZES: 26 28 30 32 34}}**
  (`display:flex; gap:15px`, default **{{DEFAULT_SIZE: 30}}** underlined) · **price**
  (serif, `font-size:40px; letter-spacing:-0.8px; line-height:1`) · **add to cart**
  (black pill `107×32`, `border-radius:23px`, white uppercase 12px).

**Product copy** — distinct per model, assigned in filename order (cycle if more models):
load from **`/brand/products.json`** if present; otherwise use:

| # | Name | Description | Price |
|---|------|-------------|-------|
| 1 | {{NAME_1}} | {{DESC_1}} | {{CURRENCY}}{{PRICE_1}} |
| 2 | {{NAME_2}} | {{DESC_2}} | {{CURRENCY}}{{PRICE_2}} |
| 3 | {{NAME_3}} | {{DESC_3}} | {{CURRENCY}}{{PRICE_3}} |
| 4 | {{NAME_4}} | {{DESC_4}} | {{CURRENCY}}{{PRICE_4}} |
| 5 | {{NAME_5}} | {{DESC_5}} | {{CURRENCY}}{{PRICE_5}} |
| 6 | {{NAME_6}} | {{DESC_6}} | {{CURRENCY}}{{PRICE_6}} |
| 7 | {{NAME_7}} | {{DESC_7}} | {{CURRENCY}}{{PRICE_7}} |
| 8 | {{NAME_8}} | {{DESC_8}} | {{CURRENCY}}{{PRICE_8}} |

## 9. Closing - BACK BUTTON ONLY

Opening pushes `history.pushState`; `popstate` closes (reverse transitions, fade others
in, resume playback, unfreeze runway from where it stopped). No other close mechanism.

## 10. Acceptance checklist

- [ ] One self-contained `index.html`; inline CSS/JS; no external requests.
- [ ] Endless seamless perspective loop; clips staggered.
- [ ] Fills any window, no white bars, re-lays out on resize.
- [ ] Zenith Jeanz logo top-left and nav bottom-centre always above models.
- [ ] Hover freezes runway, dims others to 70%, only hovered clip plays, no scaling.
- [ ] Tap centres model (~90% height), others off, panels fade in with distinct copy.
- [ ] Detail closes only via browser Back.
- [ ] Missing videos fall back to the solid fill and behave identically.
- [ ] Served on a fresh localhost port; URL reported.

---

# Asset checklist (what to upload)

```
/media/      01_*.mp4 … 08_*.mp4   runway clips (required for real content)
/brand/      logo.svg              wordmark (required)
/brand/      products.json         product copy (required, or fill the table above)
/fonts/      *.woff2               brand fonts (optional)
```

### 1. Runway videos — `/media/` (7–8 recommended)
- One model per clip, **full body head-to-toe**, walking **toward camera**, model stays
  roughly **centred in frame** (the site supplies the left→right travel and scaling).
- **Pure white / near-white seamless background**, no floor line, shadow, or props at
  the frame edges (edges must disappear on the white page).
- **Portrait**, aspect ≈ **2:5** (box is 1200×2980); small even margin, feet near the
  bottom edge, head near the top.
- **4–8 s, seamlessly loopable** (last frame matches first), no audio needed.
- Format: H.264 `.mp4` ideal; `.mov`/HEVC is fine (gets transcoded). ≥1080px tall source.
- Name them in runway order: `01_raw-indigo.mp4`, `02_…`. Filename order = runway order
  = product-copy order.

### 2. Logo — `/brand/logo.svg`
- "Zenith Jeanz" wordmark, **black, single colour, text converted to outlines** (no live
  font), tight `viewBox` with no padding. Horizontal lockup.

### 3. Product data — `/brand/products.json`
```json
{
  "currency": "$",
  "sizes": ["26","28","30","32","34"],
  "defaultSize": "30",
  "products": [
    { "name": "…", "description": "1–2 sentences, ~120 chars", "price": 185 }
  ]
}
```
One entry per video, in the same order, all names/prices distinct.

### 4. Brand decisions (just tell me, no file needed)
- 5 nav labels (default: New arrivals | women | men | denim | shows).
- Fallback fill colour (default `#DCE3EA` pale denim; original was `#EDE6E2`).
- Currency and size system (waist 26–34 vs. EU 34–42 vs. S–XL).

### 5. Optional
- Brand font files (`.woff2`) for UI sans and price serif — you need a web licence.
- Favicon (`/brand/favicon.svg` or `.png`).
