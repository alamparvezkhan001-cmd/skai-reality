"""Fetch freely licensed portrait photos from Wikimedia Commons.

Reads photos/wanted.json ({slug: Wikipedia article title}), takes each article's lead image,
and keeps it only if it is hosted on Commons under a free licence (public domain, CC0, CC BY,
CC BY-SA). Non-free (fair-use) images are skipped. Writes photos/<slug>.jpg and credits.json.
Runs in GitHub Actions because the authoring environment cannot reach Wikimedia.
"""
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "photos"
UA = {"User-Agent": "SkaiRealityInstagramBot/1.0 (https://github.com/alamparvezkhan001-cmd/skai-reality)"}
FREE = re.compile(r"^(public domain|pd|cc0|cc[- ]by(-sa)?[- ]?\d)", re.I)


def get_json(url, **params):
    req = urllib.request.Request(f"{url}?{urllib.parse.urlencode({**params, 'format': 'json'})}", headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def strip_html(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()


def main():
    wanted = json.loads((ROOT / "wanted.json").read_text(encoding="utf-8"))
    credits_path = ROOT / "credits.json"
    credits = json.loads(credits_path.read_text(encoding="utf-8")) if credits_path.exists() else {}
    for slug, title in wanted.items():
        if slug in credits and (ROOT / credits[slug]["file"]).exists():
            print("have", slug)
            continue
        pages = get_json("https://en.wikipedia.org/w/api.php", action="query", titles=title,
                         prop="pageimages", piprop="name", redirects=1)["query"]["pages"]
        name = next(iter(pages.values())).get("pageimage")
        if not name:
            print("no lead image", slug)
            continue
        info = get_json("https://commons.wikimedia.org/w/api.php", action="query", titles=f"File:{name}",
                        prop="imageinfo", iiprop="url|extmetadata", iiurlwidth=1400)["query"]["pages"]
        page = next(iter(info.values()))
        if "imageinfo" not in page:
            print("not on Commons (likely non-free)", slug, name)
            continue
        ii = page["imageinfo"][0]
        meta = ii.get("extmetadata", {})
        licence = strip_html(meta.get("LicenseShortName", {}).get("value"))
        if not FREE.match(licence):
            print("non-free licence", slug, licence)
            continue
        artist = strip_html(meta.get("Artist", {}).get("value")) or "Unknown author"
        req = urllib.request.Request(ii.get("thumburl") or ii["url"], headers=UA)
        with urllib.request.urlopen(req, timeout=60) as r:
            (ROOT / f"{slug}.jpg").write_bytes(r.read())
        credits[slug] = {
            "file": f"{slug}.jpg",
            "credit": f"{artist[:60]}, {licence}, via Wikimedia Commons",
            "source": ii.get("descriptionurl"),
        }
        print("got", slug, licence, artist)
    credits_path.write_text(json.dumps(credits, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
