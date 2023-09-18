import bs4
from bs4 import BeautifulSoup


def extract_article_body(
    soup: bs4.BeautifulSoup,
) -> tuple[str, bs4.element.Tag]:
    selector_candidates = [
        "se-main-container",
        "view"
    ]

    tag = None
    version = None
    for selector in selector_candidates:
        tag = soup.find("div", {"class": selector})

        if tag:
            version = selector
            break

    return (version, tag)



def extract_paragraph(
    tag: bs4.element.Tag,
    version: str = "se-main-container"
)-> list[bs4.element.Tag]:
    selector_candidates = {
        "se-main-container": ("div", {"class": "se-module"}),
        "view": ("p", {"class": None})
    }

    tags = []
    selector = selector_candidates.get(version)

    tags = tag.find_all(selector[0], selector[1])

    return tags




