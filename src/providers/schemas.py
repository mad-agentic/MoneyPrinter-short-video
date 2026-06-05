from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratedFile:
    path: str
    provider: str
    model: str


@dataclass(frozen=True)
class SearchResult:
    title: str
    url: str
    body: str = ""
    published: str = ""

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "url": self.url,
            "body": self.body,
            "published": self.published,
        }
