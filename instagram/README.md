# Skai Reality — Instagram

Post designs for [@skai_reality_bhiwandi](https://www.instagram.com/skai_reality_bhiwandi/).

- `design/post.html` — 1080×1350 (4:5) slide template. Open with `?s=1`, `?s=2`, `?s=3` to view each slide.
- `posts/<date>-<name>/` — rendered JPEG slides plus `caption.txt` for each post.

## Re-rendering

```bash
for i in 1 2 3; do
  chromium --headless --no-sandbox --hide-scrollbars --virtual-time-budget=8000 \
    --window-size=1080,1600 --screenshot=s$i.png "file://$PWD/design/post.html?s=$i"
done
# then crop each PNG to 1080x1350 and save as JPEG (Instagram needs JPEG, ≤8 MB, 4:5–1.91:1)
```

Publishing goes through the Windsor.ai Instagram connector (`create_carousel_post`), using the
public raw.githubusercontent.com URLs of the slide JPEGs.
