# Seller dashboard mock

A pixel-accurate mobile seller dashboard (home, Data Analysis, date range sheet) with a built-in
day-by-day business simulation. Static HTML, no backend; everything is stored on the device.

## Run it on a phone
1. Phone and computer on the same Wi-Fi.
2. On the computer: `cd app && python3 -m http.server 8765 --bind 0.0.0.0`
3. On the phone, open Safari: `http://<computer-ip>:8765/index.html`
4. Share > Add to Home Screen, then launch from the icon (`app/icon.png`) for the full-screen version.

## Files
- `app/src.html` – editable source (references `app/img/*.png` and `app/fonts/*.woff2`).
- `app/sim.js` – the simulation engine.
- `app/index.html` – built single file (images, fonts and engine inlined). Rebuild after editing: `python3 app/build.py`
- `app/preview.html` – the app inside an iPhone 16 Pro frame for viewing on a desktop browser.
- `tools/render.py` – renders a state in headless Chrome at 402x874 @3x and diffs it against a reference screenshot.
  Example: `python3 tools/render.py "home|ref.png|" "analysis|ref2.png|go=analysis"`
  URL states: `#go=analysis|edit`, `&scroll=N`, `&period=today|last7|last28|day|week|month`, `&sheet=day|week|month`. Add `?test=1` to force the iPhone safe areas.
- `tools/rows.py`, `tools/cols.py` – compare text row / word positions between a reference and a render.
- `tools/measure.py`, `tools/extract.py` – pixel measurement and icon extraction helpers.
- `tools/simtest.js` – prints monthly totals and the event log for several seeds: `node tools/simtest.js app/sim.js`

## Simulation
`app/sim.js` is a seeded day-by-day business simulation (420 days): organic growth, ad spend reinvested from profit,
purchase orders with 16–34 day lead times (sometimes 45–78), production problems (short batches, delays), stockouts
with emergency air freight, demand drops (ad account flags, algorithm changes, checkout bugs) and viral spikes, plus
weekday and seasonal patterns. Items are low ticket (£7.50–£14.50, average order around £10 with 1.6 units) and roughly 3–4% of visitors order. Monthly revenue is tuned to the min/max set on the edit screen (default £50k–£200k).
Today's figures fill in through the day using an intraday curve.

## Data
Stored in localStorage (`tts-clone-v2`). Tap the shop name to edit: simulation settings, shop name, and per-day
income / orders / visitors / buyers / products sold. With the simulation on, edited days are stored as overrides.

## Font
Self-hosted variable sans in `app/fonts/` (SIL Open Font License). Tabular figures (`tnum`) only on the Data Analysis pill,
comparison line and metrics; the home page and the date wheel use proportional digits.
