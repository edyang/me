#!/usr/bin/env python3
"""Validate sanitized technical notes and optionally their Jekyll output."""
from pathlib import Path
from datetime import datetime, date
from html import unescape
import argparse, hashlib, json, re, sys
import xml.etree.ElementTree as ET
import yaml

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--site", type=Path)
args = parser.parse_args()
errors = []
def error(path, message):
    errors.append(f"{path}: {message}")
def load_post(path):
    raw = path.read_text(encoding="utf-8")
    parts = raw.split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        raise ValueError("missing YAML front matter")
    return yaml.safe_load(parts[1]), parts[2], raw
def iso_date(value):
    return date.fromisoformat(str(value))
def iso_time(value):
    return datetime.fromisoformat(str(value))

registry = yaml.safe_load((ROOT/"_data/tech_notes.yml").read_text()) or []
ids, paths, urls = set(), set(), set()
for row in registry:
    for field, bag in (("note_id",ids),("path",paths),("permalink",urls)):
        if row[field] in bag: error(row["path"], f"duplicate {field}")
        bag.add(row[field])
    p = ROOT/row["path"]
    if not p.is_file():
        error(row["path"],"missing registered article")
        continue
    if hashlib.sha256(p.read_bytes()).hexdigest() != row["sha256"]:
        error(row["path"],"registry sha256 mismatch")

notes = []
for p in sorted((ROOT/"_posts").glob("*.md")):
    meta, body, raw = load_post(p)
    if not meta.get("tech_note"):
        continue
    notes.append((p,meta,body))
    rel = p.relative_to(ROOT).as_posix()
    required = ("layout","title","excerpt","tags","note_id","source_date","source_dates","date","published_at","updated_at","verification","privacy_reviewed","permalink")
    for key in required:
        if key not in meta: error(rel,f"missing {key}")
    if rel not in paths: error(rel,"article absent from registry")
    if meta.get("layout") != "post": error(rel,"unexpected layout")
    if meta.get("privacy_reviewed") is not True: error(rel,"missing explicit privacy review")
    if meta.get("verification") not in {"observed","partial","proposal","notes"}: error(rel,"invalid verification")
    if not isinstance(meta.get("tags"),list) or not meta["tags"]: error(rel,"missing tags")
    try:
        original = iso_date(meta["source_date"])
        published = iso_time(meta["published_at"])
        updated = iso_time(meta["updated_at"])
        if published.utcoffset() is None or updated.utcoffset() is None: error(rel,"timestamps require timezone")
        if original > published.date(): error(rel,"source date is after publication")
        if updated < published: error(rel,"update precedes publication")
        dates = [iso_date(d) for d in meta["source_dates"]]
        if dates != sorted(set(dates)) or dates[0] != original: error(rel,"source dates must be sorted and begin with source_date")
        if dates[-1] > updated.date(): error(rel,"source date is after update")
        if not p.name.startswith(str(original)+"-"): error(rel,"filename source date mismatch")
        row = next((r for r in registry if r["note_id"] == meta["note_id"]),None)
        if row:
            for key in ("title","source_date","source_dates","published_at","updated_at","permalink","verification","privacy_reviewed"):
                if row.get(key) != meta.get(key): error(rel,f"registry metadata mismatch: {key}")
    except (KeyError,TypeError,ValueError) as exc:
        error(rel,f"invalid dates: {type(exc).__name__}")
    if len(body.strip()) < 350: error(rel,"article has insufficient body")
    if body.count("\x60\x60\x60") % 2: error(rel,"unclosed code fence")
    if "{{" in body or "{%" in body: error(rel,"unexpected Liquid in article body")
    if not re.fullmatch(r"/tech/\d{4}/\d{2}/\d{2}/[a-z0-9-]+/",meta.get("permalink","")): error(rel,"unstable permalink")
    # Conservative checks supplement the mandatory semantic privacy review.
    patterns = {
        "private IPv4": r"(?<![\d.])(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})(?![\d.])",
        "email address": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "mobile number": r"(?<!\d)1[3-9]\d{9}(?!\d)",
        "private key": r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----",
        "credential token": r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,})",
        "personal path": r"(?:/home/[A-Za-z0-9_.-]+/|/Users/[A-Za-z0-9_.-]+/|C:\\Users\\[A-Za-z0-9_.-]+\\)",
        "device MAC": r"(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}",
    }
    for label, pattern in patterns.items():
        if re.search(pattern,body): error(rel,f"possible sensitive content ({label}); review before committing")
    for image in re.findall(r"!\[[^\]]*\]\((/[^)\s]+)\)",body):
        if not (ROOT/image.lstrip("/")).is_file(): error(rel,f"missing image {image}")
    if args.site:
        dest = args.site/meta["permalink"].strip("/")/"index.html"
        if not dest.is_file():
            error(rel,"Jekyll output missing")
        else:
            rendered = dest.read_text()
            if str(meta["source_date"]) not in rendered: error(rel,"source date missing in rendered page")
            if "整理发布" not in rendered: error(rel,"publication label missing")
            if "{{" in rendered or "{%" in rendered: error(rel,"unrendered Liquid")
            if unescape(str(meta["title"])) not in unescape(rendered): error(rel,"title missing in rendered page")
            for image in re.findall(r"!\[[^\]]*\]\((/[^)\s]+)\)",body):
                if not (args.site/image.lstrip("/")).is_file(): error(rel,f"rendered image missing: {image}")

for svg in (ROOT/"img/tech-notes").glob("*.svg"):
    try:
        node = ET.parse(svg).getroot()
        if not node.tag.endswith("svg") or not node.get("viewBox"): error(svg.name,"invalid SVG dimensions")
        for n in node.iter():
            if n.tag.endswith("script") or n.tag.endswith("foreignObject"): error(svg.name,"active SVG content")
    except ET.ParseError:
        error(svg.name,"invalid SVG XML")
if len(notes) != len(registry): error("registry","note count mismatch")
if args.site:
    timeline = args.site/"tech-notes/index.html"
    if not timeline.is_file(): error("timeline","missing rendered timeline")
    else:
        t = timeline.read_text()
        for row in registry:
            if row["permalink"] not in t: error("timeline",f"missing link {row['note_id']}")
    home = args.site/"index.html"
    if not home.is_file() or "/tech-notes/" not in home.read_text(): error("homepage","timeline entry missing")
    try: ET.parse(args.site/"feed.xml")
    except (ET.ParseError,FileNotFoundError) as exc: error("RSS",f"invalid rendered XML: {exc}")

print(json.dumps({"valid":not errors,"articles":len(notes),"diagrams":len(list((ROOT/"img/tech-notes").glob("*.svg"))),"rendered_checked":bool(args.site),"errors":errors},ensure_ascii=False,indent=2))
sys.exit(bool(errors))

