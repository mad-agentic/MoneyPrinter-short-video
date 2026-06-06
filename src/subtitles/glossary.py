from dataclasses import dataclass


@dataclass(frozen=True)
class GlossaryTerm:
    source: str
    target: str


def parse_glossary(text: str) -> list[GlossaryTerm]:
    """Parse newline glossary entries in `source = target` or `source: target` form."""
    terms: list[GlossaryTerm] = []
    for raw_line in str(text or "").splitlines():
        line = raw_line.strip().lstrip("-*").strip()
        if not line:
            continue
        separator = "=" if "=" in line else ":" if ":" in line else ""
        if not separator:
            continue
        source, target = [part.strip() for part in line.split(separator, 1)]
        if source and target:
            terms.append(GlossaryTerm(source=source, target=target))
    return terms


def format_glossary_context(terms: list[GlossaryTerm]) -> str:
    if not terms:
        return ""
    lines = ["Glossary terms to preserve:"]
    lines.extend(f"- {term.source} -> {term.target}" for term in terms)
    return "\n".join(lines)


def apply_glossary(text: str, terms: list[GlossaryTerm]) -> str:
    result = str(text or "")
    for term in terms:
        result = result.replace(term.source, term.target)
    return result
