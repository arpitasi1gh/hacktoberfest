"""Fetch small, public web-page excerpts linked from task notes."""

import asyncio
from html.parser import HTMLParser
import ipaddress
import re
import socket
from urllib.parse import urljoin, urlsplit

import httpx

MAX_REFERENCES = 4
MAX_REDIRECTS = 3
MAX_BODY_BYTES = 512_000
MAX_EXCERPT_CHARS = 4_000
FETCH_TIMEOUT_SECONDS = 8.0
URL_PATTERN = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
TRAILING_URL_PUNCTUATION = ".,;:!?)]}"
IGNORED_TAGS = {"script", "style", "noscript", "svg", "nav", "footer", "header"}
BLOCK_TAGS = {
    "article",
    "br",
    "div",
    "h1",
    "h2",
    "h3",
    "h4",
    "li",
    "main",
    "p",
    "section",
}
HEADING_TAGS = {"h1", "h2", "h3", "h4"}
STOP_WORDS = {
    "about", "after", "also", "and", "are", "before", "because", "been", "being",
    "between", "both", "but", "could", "currently", "daily", "from", "goal", "have",
    "into", "need", "notes", "only", "should", "some", "that", "their", "them",
    "then", "there", "these", "they", "this", "through", "under", "until", "what",
    "when", "where", "which", "while", "with", "work", "would",
}
NEXT_MARKER_PATTERN = re.compile(
    r"\b(?:next|continue(?:\s+with)?|proceed(?:\s+to|\s+with)?|"
    r"focus(?:\s+on)?|work\s+on|start\s+with)\b[:\s-]*(.+?)(?:[.;\n]|$)",
    re.IGNORECASE,
)
COMPLETED_MARKER_PATTERN = re.compile(
    r"\b(?:covered|completed|finished|done\s+with|up\s+to|till|through|"
    r"currently\s+at|progressed\s+to)\b[:\s-]*(.+?)"
    r"(?=,\s*(?:and\s+)?(?:need|want|plan)\s+to\s+|[.;\n]|$)",
    re.IGNORECASE,
)
COMPLETED_PROGRESS_PATTERN = re.compile(
    r"\b(?:currently\s+)?(?:covered|completed|finished)\s+"
    r"(?:up\s+to|till|through|until)\s+(?P<milestone>.+?)"
    r"(?=,\s*(?:and\s+)?(?:need|want|plan)\s+to\s+"
    r"(?:proceed|continue|move|start)\b|[.;\n]|$)",
    re.IGNORECASE,
)
NEXT_PROGRESS_PATTERN = re.compile(
    r"\b(?:need|want|plan)\s+to\s+(?:proceed|continue|move|start)\s+"
    r"(?:with|to|on)?\s*(?P<options>.+?)(?:[.;\n]|$)",
    re.IGNORECASE,
)
RECENT_DONE_PATTERN = re.compile(
    r"^Recently completed work:\s*(.+)$",
    re.IGNORECASE | re.MULTILINE,
)


class _PageTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self._in_title = False
        self._ignored_depth = 0
        self._ignored_tags: list[str] = []
        self._text: list[str] = []
        self._title_parts: list[str] = []
        self._sections: list[dict[str, str]] = []
        self._section_parts: list[str] = []
        self._section_heading = ""
        self._heading_parts: list[str] = []
        self._in_heading = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if (
            tag in IGNORED_TAGS
            or "hidden" in attributes
            or attributes.get("aria-hidden") == "true"
        ):
            self._ignored_depth += 1
            self._ignored_tags.append(tag)
        if tag == "title":
            self._in_title = True
        if tag in HEADING_TAGS:
            self._flush_section()
            self._in_heading = True
            self._heading_parts = []
        if self._ignored_depth == 0 and tag == "img" and attributes.get("alt"):
            self._text.append(attributes["alt"] or "")
            self._section_parts.append(attributes["alt"] or "")
        if tag in BLOCK_TAGS:
            self._text.append("\n")
            if tag not in HEADING_TAGS:
                self._flush_section()

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
            self.title = " ".join("".join(self._title_parts).split())
        if tag in HEADING_TAGS and self._in_heading:
            self._section_heading = " ".join("".join(self._heading_parts).split())
            self._in_heading = False
        if tag in self._ignored_tags:
            self._ignored_tags.remove(tag)
            self._ignored_depth -= 1
        if tag in BLOCK_TAGS:
            self._text.append("\n")
            self._flush_section()

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_parts.append(data)
        if self._ignored_depth == 0:
            self._text.append(data)
            if self._in_heading:
                self._heading_parts.append(data)
            else:
                self._section_parts.append(data)

    def _flush_section(self) -> None:
        text = " ".join("".join(self._section_parts).split())
        if text:
            self._sections.append({"heading": self._section_heading, "text": text})
        self._section_parts = []

    def sections(self) -> list[dict[str, str]]:
        self._flush_section()
        return self._sections

    def excerpt(self, notes: str) -> str:
        sections = self.sections()
        if not sections:
            return re.sub(r"[ \t]*\n[ \t]*", "\n", " ".join(self._text)).strip()[
                :MAX_EXCERPT_CHARS
            ]

        progress_context = extract_progress_context(notes)
        recent_done_match = RECENT_DONE_PATTERN.search(notes)
        next_match = NEXT_MARKER_PATTERN.search(notes) if not recent_done_match else None
        completed_match = COMPLETED_MARKER_PATTERN.search(notes)
        next_options = progress_context.get("next_step_options")
        next_terms = (
            _terms(" ".join(next_options))
            if isinstance(next_options, list)
            else _terms(next_match.group(1))
            if next_match
            else set()
        )
        completed_milestones = progress_context.get("completed_milestones")
        completed_text = (
            recent_done_match.group(1)
            if recent_done_match
            else " ".join(completed_milestones)
            if isinstance(completed_milestones, list)
            else completed_match.group(1)
            if completed_match
            else ""
        )
        completed_terms = _terms(completed_text)
        all_note_terms = _terms(notes)

        start_index = 0
        if isinstance(next_options, list) and next_options:
            option_indexes = [
                index
                for index, section in enumerate(sections)
                if any(
                    _overlap(
                        _terms(option),
                        _terms(section["heading"] + " " + section["text"]),
                    )
                    for option in next_options
                )
            ]
            if option_indexes:
                start_index = min(option_indexes)
        elif next_terms:
            best_index = max(
                range(len(sections)),
                key=lambda index: _overlap(
                    next_terms,
                    _terms(sections[index]["heading"] + " " + sections[index]["text"]),
                ),
            )
            if _overlap(
                next_terms,
                _terms(sections[best_index]["heading"] + " " + sections[best_index]["text"]),
            ):
                start_index = best_index
        elif completed_terms:
            completed_index = max(
                range(len(sections)),
                key=lambda index: _overlap(
                    completed_terms,
                    _terms(sections[index]["heading"] + " " + sections[index]["text"]),
                ),
            )
            if _overlap(
                completed_terms,
                _terms(
                    sections[completed_index]["heading"]
                    + " "
                    + sections[completed_index]["text"]
                ),
            ):
                start_index = min(completed_index + 1, len(sections) - 1)

        prioritized = sections[start_index:]
        focus_terms = next_terms or (all_note_terms - completed_terms)
        if focus_terms:
            prioritized = sorted(
                enumerate(prioritized),
                key=lambda item: (
                    -_overlap(
                        focus_terms,
                        _terms(item[1]["heading"] + " " + item[1]["text"]),
                    ),
                    item[0],
                ),
            )
            prioritized = [section for _, section in prioritized]

        excerpt_parts: list[str] = []
        char_count = 0
        for section in prioritized:
            label = f"{section['heading']}: " if section["heading"] else ""
            part = f"{label}{section['text']}"
            remaining = MAX_EXCERPT_CHARS - char_count
            if remaining <= 0:
                break
            excerpt_parts.append(part[:remaining])
            char_count += min(len(part), remaining) + 1
        return "\n".join(excerpt_parts).strip()


def _terms(text: str) -> set[str]:
    return {
        term
        for term in re.findall(r"[a-z0-9]+", text.casefold())
        if len(term) > 2 and term not in STOP_WORDS
    }


def _overlap(terms: set[str], content_terms: set[str]) -> int:
    return len(terms & content_terms)


def _split_options(value: str) -> list[str]:
    return [
        option.strip(" ,")
        for option in re.split(r"\s+or\s+|,\s*(?:or\s+)?", value, flags=re.IGNORECASE)
        if option.strip(" ,")
    ]


def extract_progress_context(notes: str) -> dict[str, object]:
    """Separate completed milestones from explicitly stated next-step options."""
    completed = COMPLETED_PROGRESS_PATTERN.search(notes)
    next_step = NEXT_PROGRESS_PATTERN.search(notes)
    result: dict[str, object] = {}
    if completed:
        result["completed_milestones"] = [completed.group("milestone").strip(" ,")]
    if next_step:
        options = _split_options(next_step.group("options"))
        if options:
            result["next_step_options"] = options
            result["next_step_requires_choice"] = len(options) > 1
    return result


def _extract_urls(notes: str) -> list[str]:
    urls: list[str] = []
    for match in URL_PATTERN.findall(notes):
        url = match.rstrip(TRAILING_URL_PUNCTUATION)
        if url and url not in urls:
            urls.append(url)
    return urls


async def _require_public_host(url: str) -> None:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Only public HTTP or HTTPS pages can be read.")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("URLs containing embedded credentials are not allowed.")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("The URL contains an invalid port.") from exc
    if port not in {None, 80, 443}:
        raise ValueError("Only standard HTTP and HTTPS ports can be read.")

    host = parsed.hostname.rstrip(".")
    try:
        addresses = {ipaddress.ip_address(host)}
    except ValueError:
        loop = asyncio.get_running_loop()
        records = await asyncio.wait_for(
            loop.getaddrinfo(
                host,
                port or (443 if parsed.scheme == "https" else 80),
                type=socket.SOCK_STREAM,
            ),
            timeout=3,
        )
        addresses = {
            ipaddress.ip_address(record[4][0])
            for record in records
        }
    if not addresses or any(not address.is_global for address in addresses):
        raise ValueError("The URL does not resolve exclusively to public addresses.")


def _page_excerpt(
    url: str,
    content_type: str,
    body: bytes,
    notes: str = "",
) -> dict[str, str]:
    if content_type == "text/plain":
        text = body.decode("utf-8", errors="replace")
        return {"url": url, "title": "", "text": " ".join(text.split())[:MAX_EXCERPT_CHARS]}
    if content_type != "text/html":
        return {
            "url": url,
            "title": "",
            "text": "Page not read: the link is not an HTML or plain-text page.",
        }

    parser = _PageTextParser()
    parser.feed(body.decode("utf-8", errors="replace"))
    text = parser.excerpt(notes)
    if not text:
        text = "Page opened, but no readable text was found."
    return {"url": url, "title": parser.title, "text": text}


async def _fetch_page(
    client: httpx.AsyncClient,
    original_url: str,
    notes: str = "",
) -> dict[str, str]:
    url = original_url
    for redirect_count in range(MAX_REDIRECTS + 1):
        await _require_public_host(url)
        async with client.stream("GET", url) as response:
            if response.is_redirect:
                location = response.headers.get("location")
                if location is None or redirect_count == MAX_REDIRECTS:
                    raise ValueError("The page redirected too many times.")
                url = urljoin(url, location)
                continue
            response.raise_for_status()

            content_type = response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
            content_length = response.headers.get("content-length")
            if content_length is not None and int(content_length) > MAX_BODY_BYTES:
                raise ValueError("The page is larger than the allowed reading limit.")

            chunks: list[bytes] = []
            body_size = 0
            async for chunk in response.aiter_bytes():
                body_size += len(chunk)
                if body_size > MAX_BODY_BYTES:
                    raise ValueError("The page is larger than the allowed reading limit.")
                chunks.append(chunk)
        return _page_excerpt(url, content_type, b"".join(chunks), notes)
    raise ValueError("The page redirected too many times.")


async def add_web_references(context: dict) -> dict:
    """Attach bounded text excerpts for public URLs found in task notes."""
    tasks = context.get("tasks", [])
    if not tasks:
        return context

    urls_by_task: list[list[str]] = []
    all_urls: list[str] = []
    reference_notes_by_task: list[str] = []
    progress_contexts: list[dict[str, object]] = []
    recent_suggestions = context.get("recent_suggestions", [])
    for task in tasks:
        urls = _extract_urls(task.get("notes") or "")
        urls_by_task.append(urls)
        for url in urls:
            if url not in all_urls:
                all_urls.append(url)
        task_title = (task.get("title") or "").casefold()
        completed_actions = [
            suggestion["action"]
            for suggestion in recent_suggestions
            if suggestion.get("outcome") == "done"
            and (suggestion.get("task_title") or "").casefold() == task_title
            and isinstance(suggestion.get("action"), str)
        ]
        task_context = task.get("notes") or ""
        progress_context = extract_progress_context(task_context)
        progress_contexts.append(progress_context)
        if isinstance(task.get("progress"), int):
            task_context += f"\nCurrent task progress: {task['progress']}%."
        if completed_actions:
            task_context = (
                "Recently completed work: "
                + completed_actions[0]
                + "\n"
                + task_context
            )
        reference_notes_by_task.append(task_context)

    selected_urls = all_urls[:MAX_REFERENCES]
    notes_by_url: dict[str, list[str]] = {}
    for task_context, urls in zip(reference_notes_by_task, urls_by_task):
        for url in urls:
            notes_by_url.setdefault(url, []).append(task_context)

    async def fetch(
        url: str,
        notes: str,
        client: httpx.AsyncClient,
    ) -> dict[str, str]:
        try:
            return await _fetch_page(client, url, notes)
        except (httpx.HTTPError, httpx.InvalidURL, OSError, TimeoutError, ValueError) as exc:
            return {"url": url, "title": "", "text": f"Page not read: {exc}"}

    if selected_urls:
        timeout = httpx.Timeout(FETCH_TIMEOUT_SECONDS)
        limits = httpx.Limits(max_connections=MAX_REFERENCES)
        async with httpx.AsyncClient(
            timeout=timeout,
            limits=limits,
            follow_redirects=False,
            trust_env=False,
            headers={"Accept": "text/html, text/plain;q=0.9"},
        ) as client:
            results = await asyncio.gather(
                *(
                    fetch(url, "\n".join(notes_by_url[url]), client)
                    for url in selected_urls
                )
            )
        fetched = dict(zip(selected_urls, results))

    enriched_tasks = []
    for task, urls, progress_context in zip(tasks, urls_by_task, progress_contexts):
        enriched_task = dict(task)
        if progress_context:
            enriched_task["progress_context"] = progress_context
        if urls:
            enriched_task["web_references"] = [
                fetched[url]
                if url in selected_urls
                else {
                    "url": url,
                    "title": "",
                    "text": "Page not fetched: the per-check-in URL limit was reached.",
                }
                for url in urls
            ]
        enriched_tasks.append(enriched_task)
    return {**context, "tasks": enriched_tasks}
