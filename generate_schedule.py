#!/usr/bin/env python3
"""Generate a responsive Hugo schedule fragment from a local or remote CSV."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


REQUIRED_COLUMNS = {"date", "start", "end", "type", "course", "speaker", "label", "color", "link"}
DAY_NAMES = {
    "en": ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"),
    "it": ("lun", "mar", "mer", "gio", "ven", "sab", "dom"),
}
MONTH_NAMES = {
    "en": ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"),
    "it": ("gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"),
}
FALLBACK_COLORS = ("#3a6ea5", "#3f8f64", "#c0892c", "#8657a5", "#a64f53", "#3f8580")
SAFE_LABEL_TAGS = {"br", "small", "strong", "em"}
FEATURED_TYPES = {"social", "dinner", "reception"}
START_MARKER = "<!-- TIMETABLE:START -->"
END_MARKER = "<!-- TIMETABLE:END -->"


@dataclass(frozen=True)
class Course:
    key: str
    speaker: str
    label: str
    color: str
    link: str
    row_number: int


@dataclass(frozen=True)
class Event:
    start: datetime
    end: datetime | None
    type: str
    course: str
    speaker: str
    label: str
    color: str
    link: str
    row_number: int

    @property
    def is_break(self) -> bool:
        return self.type == "break"

    @property
    def is_featured(self) -> bool:
        return self.type in FEATURED_TYPES

    @property
    def layout_end(self) -> datetime:
        return self.end or self.start + timedelta(hours=1)


class _LabelSanitizer(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in SAFE_LABEL_TAGS:
            self.parts.append(f"<{tag}>")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in SAFE_LABEL_TAGS:
            self.parts.append(f"<{tag}>")

    def handle_endtag(self, tag: str) -> None:
        if tag in SAFE_LABEL_TAGS and tag != "br":
            self.parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        self.parts.append(html.escape(data))

    def handle_entityref(self, name: str) -> None:
        self.parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self.parts.append(f"&#{name};")


def safe_label(value: str) -> str:
    parser = _LabelSanitizer()
    parser.feed(value)
    parser.close()
    return "".join(parser.parts)


def esc(value: str) -> str:
    return html.escape(value, quote=True)


def read_csv_text(source: str) -> str:
    parsed = urlparse(source)
    if parsed.scheme in {"http", "https"}:
        request = Request(source, headers={"User-Agent": "Hugo schedule pre-build/2.0"})
        try:
            with urlopen(request, timeout=30) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                return response.read().decode(charset).lstrip("\ufeff")
        except (HTTPError, URLError, TimeoutError) as exc:
            raise ValueError(f"could not download CSV from {source}: {exc}") from exc
    if parsed.scheme:
        raise ValueError("CSV source must be a local path or an http(s) URL")
    return Path(source).read_text(encoding="utf-8-sig")


def google_csv_url(sheet: str, gid: str) -> str:
    sheet = sheet.strip()
    gid = gid.strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", sheet):
        raise ValueError("--sheet must be the Google spreadsheet ID, not its full URL")
    if not re.fullmatch(r"[0-9]+", gid):
        raise ValueError("--gid must be the numeric Google Sheets tab gid")
    return f"https://docs.google.com/spreadsheets/d/{sheet}/export?format=csv&gid={gid}"


def parse_date(value: str, row_number: int) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"row {row_number}: date must use YYYY-MM-DD") from exc


def parse_time(value: str, row_number: int, field: str, *, optional: bool = False) -> time | None:
    value = value.strip()
    if not value and optional:
        return None
    if not value:
        raise ValueError(f"row {row_number}: '{field}' is empty")
    for fmt in ("%H:%M", "%H.%M"):
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue
    raise ValueError(f"row {row_number}: {field} must use HH:MM")


def clean_type(value: str, row_number: int) -> str:
    value = value.strip().casefold()
    if not re.fullmatch(r"[a-z][a-z0-9_-]*", value):
        raise ValueError(f"row {row_number}: type must be a simple name such as lecture, break, or note")
    return value


def clean_color(value: str, row_number: int) -> str:
    value = value.strip()
    if value and not re.fullmatch(r"#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?", value):
        raise ValueError(f"row {row_number}: color must be a hex color such as #3a6ea5")
    return value


def clean_link(value: str, row_number: int) -> str:
    value = value.strip()
    if not value:
        return ""
    parsed = urlparse(value)
    absolute = parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    relative = (value.startswith("/") and not value.startswith("//")) or value.startswith("#")
    if not (absolute or relative):
        raise ValueError(f"row {row_number}: link must be http(s), root-relative, or an anchor")
    return value


def read_schedule(source: str | Path) -> tuple[list[Event], dict[str, Course]]:
    with io.StringIO(read_csv_text(str(source)), newline="") as handle:
        reader = csv.DictReader(handle)
        headers = {str(name).strip() for name in (reader.fieldnames or []) if name and name.strip()}
        missing = REQUIRED_COLUMNS - headers
        if missing:
            raise ValueError(f"missing CSV columns: {', '.join(sorted(missing))}")
        rows: list[tuple[int, dict[str, str]]] = []
        for row_number, raw in enumerate(reader, start=2):
            row = {str(k).strip(): (v or "").strip() for k, v in raw.items() if k and str(k).strip()}
            if any(row.values()):
                rows.append((row_number, row))

    courses: dict[str, Course] = {}
    for row_number, row in rows:
        if row["type"].casefold() != "course":
            continue
        key = row["course"].strip().casefold()
        if not key:
            raise ValueError(f"row {row_number}: a course definition needs a course key")
        if key in courses:
            raise ValueError(f"row {row_number}: duplicate course key {key!r}")
        courses[key] = Course(
            key=key,
            speaker=row["speaker"],
            label=row["label"],
            color=clean_color(row["color"], row_number),
            link=clean_link(row["link"], row_number),
            row_number=row_number,
        )

    explicit_dates = sorted({
        parse_date(row["date"], row_number)
        for row_number, row in rows
        if row["type"].casefold() != "course" and row["date"]
    })
    if not explicit_dates:
        raise ValueError("the CSV has no dated timetable rows")

    events: list[Event] = []
    for row_number, row in rows:
        event_type = clean_type(row["type"], row_number)
        if event_type == "course":
            continue
        start_time = parse_time(row["start"], row_number, "start")
        end_time = parse_time(row["end"], row_number, "end", optional=True)
        course_key = row["course"].casefold()
        course = courses.get(course_key) if course_key else None
        if course_key and course is None:
            raise ValueError(f"row {row_number}: unknown course key {course_key!r}")
        dates = [parse_date(row["date"], row_number)] if row["date"] else explicit_dates
        for event_date in dates:
            assert start_time is not None
            start = datetime.combine(event_date, start_time)
            end = datetime.combine(event_date, end_time) if end_time else None
            if end and end <= start:
                raise ValueError(f"row {row_number}: end must be after start")
            events.append(Event(
                start=start,
                end=end,
                type=event_type,
                course=course_key,
                speaker=row["speaker"] or (course.speaker if course else ""),
                label=row["label"],
                color=clean_color(row["color"], row_number) or (course.color if course else ""),
                link=clean_link(row["link"], row_number) or (course.link if course else ""),
                row_number=row_number,
            ))
    if not events:
        raise ValueError("the CSV contains no timetable events")
    return sorted(events, key=lambda item: (item.start, item.layout_end, item.label)), courses


def validate_no_overlaps(events: list[Event]) -> None:
    by_day: dict[date, list[Event]] = {}
    for event in events:
        if not event.is_featured:
            by_day.setdefault(event.start.date(), []).append(event)
    for day_events in by_day.values():
        for previous, current in zip(day_events, day_events[1:]):
            if current.start < previous.layout_end:
                raise ValueError(
                    f"rows {previous.row_number} and {current.row_number} overlap on {current.start.date()}"
                )


def minutes(value: datetime) -> int:
    return value.hour * 60 + value.minute


def format_time(value: datetime) -> str:
    return value.strftime("%H.%M")


def format_day(value: date, locale: str) -> str:
    return f"{DAY_NAMES[locale][value.weekday()]}, {value.day} {MONTH_NAMES[locale][value.month - 1]} {value.year}"


def event_color(event: Event) -> str:
    if event.color:
        return event.color
    key = event.course or event.speaker or event.type or event.label
    digest = hashlib.sha256(key.casefold().encode("utf-8")).digest()
    return FALLBACK_COLORS[digest[0] % len(FALLBACK_COLORS)]


def primary_html(primary: str, *, label_html: bool = False) -> str:
    content = safe_label(primary) if label_html else esc(primary)
    return f"<strong>{content}</strong>"


def clickable_content(event: Event, content: str) -> str:
    if event.link:
        return f'<a class="schedule-card__clickable" href="{esc(event.link)}">{content}</a>'
    return f'<div class="schedule-card__clickable">{content}</div>'


def render_event(event: Event, day_start: int, day_span: int) -> str:
    top = (minutes(event.start) - day_start) / day_span * 100
    height = max((minutes(event.layout_end) - minutes(event.start)) / day_span * 100, 4.5)
    time_label = format_time(event.start)
    if event.end:
        time_label += f" - {format_time(event.end)}"
    primary = event.speaker or event.label or event.type.title()
    secondary = safe_label(event.label) if event.speaker and event.label else ""
    content = (
        f'<div class="schedule-card__line"><time datetime="{esc(event.start.isoformat())}">{time_label}</time>'
        f'{primary_html(primary, label_html=not bool(event.speaker))}</div>'
        f'{f"<div class=\"schedule-card__label\">{secondary}</div>" if secondary else ""}'
    )
    return (
        f'<article class="schedule-card schedule-card--{esc(event.type)}" '
        f'style="--top:{top:.4f}%;--height:{height:.4f}%;--card-color:{event_color(event)}">'
        f'{clickable_content(event, content)}</article>'
    )


def render_featured(event: Event, day_index: int, locale: str) -> str:
    time_label = format_time(event.start)
    primary = event.speaker or event.label or event.type.title()
    secondary = safe_label(event.label) if event.speaker and event.label else ""
    content = (
        f'<div><time datetime="{esc(event.start.isoformat())}">{time_label}</time>'
        f'{primary_html(primary, label_html=not bool(event.speaker))}</div>'
        f'<small>{esc(format_day(event.start.date(), locale))}</small>'
        f'{f"<p>{secondary}</p>" if secondary else ""}'
    )
    return (
        f'<aside class="schedule-featured schedule-featured--{esc(event.type)}" '
        f'style="--day-column:{day_index + 1};--card-color:{event_color(event)}">'
        f'{clickable_content(event, content)}</aside>'
    )


def stylesheet() -> str:
    return """
.schedule-table{--ink:#141414;--line:#1a1a1a;--muted:#5d6268;color:var(--ink);font-family:Arial,Helvetica,sans-serif;max-width:1200px;margin:0 auto}
.schedule-table *{box-sizing:border-box}.schedule-scroll{overflow-x:auto;padding-bottom:.5rem}.schedule-grid{display:grid;grid-template-columns:repeat(var(--days),minmax(190px,1fr));border-top:1px solid var(--line);border-left:1px solid var(--line);min-width:950px}.schedule-day{min-width:0;border-right:1px solid var(--line)}.schedule-day h2{font-size:1rem;text-align:center;margin:0;height:44px;padding:.8rem .35rem;border-bottom:1px solid var(--line)}.schedule-day-track{height:540px;position:relative}.schedule-card{position:absolute;z-index:1;top:var(--top);height:var(--height);min-height:30px;left:0;right:0;padding:0;background:#eef1f3;background:color-mix(in srgb,var(--card-color) 22%,#fff);border-block:1px solid var(--line);border-left:4px solid var(--card-color);overflow:auto;overscroll-behavior:contain}.schedule-card__clickable{display:block;width:100%;height:100%;padding:.48rem .45rem;color:inherit;text-decoration:none;border-radius:2px}.schedule-card__clickable[href]:hover strong{text-decoration:underline;text-underline-offset:3px}.schedule-card__clickable[href]:focus-visible{outline:3px solid var(--card-color);outline-offset:-3px}.schedule-card__line{display:grid;grid-template-columns:minmax(94px,.75fr) minmax(0,1fr);gap:.35rem;align-items:baseline}.schedule-card time{white-space:nowrap}.schedule-card strong{font-size:.96rem}.schedule-card__label{font-size:.84rem;line-height:1.2;margin-top:.28rem}.schedule-card__label small{font-size:.75rem}.schedule-card--break,.schedule-card--note{background:#fff;border-left-color:#aaa}.schedule-featured-grid{display:grid;grid-template-columns:repeat(var(--days),minmax(190px,1fr));min-width:950px}.schedule-featured{grid-column:var(--day-column);border:1px solid var(--line);border-left:4px solid var(--card-color);margin-top:2.25rem;padding:0}.schedule-featured>.schedule-card__clickable{padding:.55rem}.schedule-featured>.schedule-card__clickable>div:first-child{display:grid;grid-template-columns:minmax(86px,.7fr) 1fr;gap:.5rem}.schedule-featured small{display:block;color:var(--muted);margin-top:.25rem}.schedule-featured p{font-size:.86rem;font-style:italic;margin:.65rem 0 0;line-height:1.25}.schedule-empty{color:var(--muted);display:grid;place-items:center;height:100%;padding:1rem;text-align:center}
@media(max-width:760px){.schedule-scroll{overflow:visible}.schedule-grid,.schedule-featured-grid{display:block;min-width:0;border:0}.schedule-day{border:1px solid var(--line);margin-bottom:1rem}.schedule-day-track{height:auto;position:static}.schedule-card{position:static;height:auto!important;min-height:0;border-left-width:4px;border-right:0;padding:0}.schedule-card>.schedule-card__clickable{padding:.75rem}.schedule-day h2{height:auto}.schedule-empty{height:auto}.schedule-featured{margin-top:1rem}.schedule-card__line{grid-template-columns:minmax(105px,.65fr) 1fr}}
@media print{.schedule-table{max-width:none}.schedule-scroll{overflow:visible}.schedule-grid,.schedule-featured-grid{min-width:0}.schedule-card{overflow:hidden}}
""".strip()


def render(events: list[Event], locale: str) -> str:
    validate_no_overlaps(events)
    dates = sorted({event.start.date() for event in events})
    regular = [event for event in events if not event.is_featured]
    featured = [event for event in events if event.is_featured]
    day_start = min((minutes(event.start) for event in regular), default=8 * 60 + 30)
    day_end = max((minutes(event.layout_end) for event in regular), default=18 * 60)
    day_start = (day_start // 30) * 30
    day_end = ((day_end + 29) // 30) * 30
    span = max(day_end - day_start, 60)
    day_sections: list[str] = []
    for event_date in dates:
        cards = "".join(render_event(event, day_start, span) for event in regular if event.start.date() == event_date)
        if not cards:
            cards = '<p class="schedule-empty">No scheduled events</p>'
        day_sections.append(
            f'<section class="schedule-day"><h2>{esc(format_day(event_date, locale))}</h2>'
            f'<div class="schedule-day-track">{cards}</div></section>'
        )
    featured_html = "".join(render_featured(event, dates.index(event.start.date()), locale) for event in featured)
    return (
        f'<div class="schedule-table" role="region" aria-label="Event schedule">'
        f'<div class="schedule-scroll" tabindex="0" aria-label="Scrollable schedule">'
        f'<div class="schedule-grid" style="--days:{len(dates)}">{"".join(day_sections)}</div>'
        f'{f"<div class=\"schedule-featured-grid\" style=\"--days:{len(dates)}\">{featured_html}</div>" if featured_html else ""}'
        f'</div></div>\n'
    )


def inject_timetable(target: Path, fragment: str) -> None:
    """Atomically replace only the content between the timetable markers."""
    raw = target.read_bytes()
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    if text.count(START_MARKER) != 1 or text.count(END_MARKER) != 1:
        raise ValueError(
            f"{target} must contain exactly one {START_MARKER} and one {END_MARKER}"
        )
    start = text.index(START_MARKER) + len(START_MARKER)
    end = text.index(END_MARKER)
    if end < start:
        raise ValueError(f"{target}: timetable end marker appears before start marker")
    newline = "\r\n" if "\r\n" in text else "\n"
    embedded = f"<style>{stylesheet()}</style>{newline}{fragment.rstrip()}"
    updated = text[:start] + newline * 2 + embedded + newline * 2 + text[end:]
    payload = (b"\xef\xbb\xbf" if has_bom else b"") + updated.encode("utf-8")

    target.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{target.name}.", suffix=".tmp", dir=target.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(file_descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, target.stat().st_mode)
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", help="local CSV path for offline use")
    parser.add_argument("output", nargs="?", type=Path, help="generated Hugo HTML fragment")
    parser.add_argument("--sheet", help="Google spreadsheet ID")
    parser.add_argument("--gid", help="numeric gid of the Google Sheets tab")
    parser.add_argument("--locale", choices=sorted(DAY_NAMES), default="en")
    parser.add_argument("--css-output", type=Path, help="optionally write the table stylesheet")
    parser.add_argument(
        "--inject-into",
        type=Path,
        help="inject CSS and table HTML between TIMETABLE markers in this Hugo content file",
    )
    parser.add_argument(
        "--standalone-preview",
        action="store_true",
        help="wrap the table and CSS in a complete browser-previewable HTML page",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.sheet:
        if args.input:
            print("error: do not provide a local INPUT together with --sheet", file=sys.stderr)
            return 2
        if args.gid is None:
            print("error: --sheet and --gid must be provided together", file=sys.stderr)
            return 2
    elif args.gid is not None:
        print("error: --sheet and --gid must be provided together", file=sys.stderr)
        return 2
    elif not args.input:
        print("error: provide a local INPUT or both --sheet and --gid", file=sys.stderr)
        return 2
    if bool(args.output) == bool(args.inject_into):
        print("error: provide either OUTPUT or --inject-into, but not both", file=sys.stderr)
        return 2
    if args.inject_into and args.standalone_preview:
        print("error: --standalone-preview cannot be combined with --inject-into", file=sys.stderr)
        return 2
    try:
        source = google_csv_url(args.sheet, args.gid) if args.sheet else args.input
        assert source is not None
        events, _courses = read_schedule(source)
        output = render(events, args.locale)
        if args.standalone_preview:
            output = (
                '<!doctype html><html lang="' + esc(args.locale) + '"><head>'
                '<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                '<style>' + stylesheet() + '</style>'
                '</head><body><main style="padding:clamp(1rem,3vw,3rem)">' + output + '</main></body></html>\n'
            )
        if args.inject_into:
            inject_timetable(args.inject_into, output)
        else:
            assert args.output is not None
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output, encoding="utf-8")
        if args.css_output:
            args.css_output.parent.mkdir(parents=True, exist_ok=True)
            args.css_output.write_text(stylesheet() + "\n", encoding="utf-8")
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.inject_into:
        print(f"updated {args.inject_into}")
    else:
        print(f"wrote {args.output}")
    if args.css_output:
        print(f"wrote {args.css_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
