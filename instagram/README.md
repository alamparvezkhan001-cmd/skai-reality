# Skai Reality — Instagram

Post designs for [@skai_reality_bhiwandi](https://www.instagram.com/skai_reality_bhiwandi/).
Publishing goes through the Windsor.ai Instagram connector, using the public
raw.githubusercontent.com URLs of the JPEGs in this folder.

## Layout

- `brand/` — Skai Reality logo: original upload, transparent full logo, icon, wordmark, and a
  dark icon variant for light backgrounds. Brand colours: navy `#001b39`, yellow `#faac01`, cyan `#0099c5`.
- `design/post.html` — launch carousel template (1080×1350). View slides with `?s=1`, `?s=2`, `?s=3`.
- `posts/2026-10-skai-launch/` — rendered launch carousel + caption.
- `daily/calendar.json` — daily post calendar. Two post types:
  - `motivation` — navy quote card. `text` uses `\n` for line breaks and `*word*` for yellow highlight;
    optional `author` (only for correctly attributed quotes).
  - `gyaan` — light "Real Estate Gyaan" explainer with a `title` and 3–4 `points` of `[heading, text]`.
  - `legend` — "India's / World's Legends": full-bleed photo of a business leader + a verified quote.
    Fields: `person`, `title`, `quote` (`*word*` highlight), optional `source`, `photo` (slug in
    `photos/credits.json`). Only use quotes with a documented source — several viral quotes
    (e.g. the Ratan Tata "right decisions" line) are fake.
- `photos/` — licensed portrait photos + `credits.json` (file name and attribution per slug).
- `daily/out/<date>.jpg|.txt` — rendered post and full caption (CTA + hashtags added automatically).
- `daily/backlog.json`, `daily/backlog-out/` — the earlier text-only motivation/gyaan series, not scheduled.
- `scripts/render_daily.py` — renders the calendar.

## Daily posts

```bash
python3 scripts/render_daily.py               # render everything in the calendar
python3 scripts/render_daily.py 2026-10-20    # render one date
```

A daily routine publishes `daily/out/<today>.jpg` with its caption at ~11 AM IST and appends the
result to `daily/posted.log`. Add new days to `calendar.json`, render, and push.

Instagram API limits: JPEG, ≤ 8 MB, aspect 4:5 to 1.91:1, caption ≤ 2,200 chars, ≤ 30 hashtags.
