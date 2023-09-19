import bs4


def extract_article_body(
    soup: bs4.BeautifulSoup,
) -> tuple[str, bs4.element.Tag]:
    """
    Extract Article body HTML source

    Parameters
    ----------
    soup: bs4.BeautifulSoup
        Original Blog HTML Source

    Returns
    -------
    tuple[str, bs4.element.Tag]
        Return (version of blog editor, Body Tag)
    """
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
    """
    Tag list of paragraph from Article Body HTML source

    Parameters
    ----------
    tag: bs4.element.Tag
        Original Blog Article body HTML Source
    version: str
        Blog editor version(iframe class name)
    Returns
    -------
    list[bs4.element.Tag]
    """
    selector_candidates = {
        "se-main-container": ("div", {"class": "se-module"}),
        "view": ("p", {"class": None})
    }

    tags = []
    selector = selector_candidates.get(version)

    tags = tag.find_all(selector[0], selector[1])

    return tags


def identify_tag_name(
    tag: bs4.element.Tag,
) -> tuple[str, bs4.element.Tag]:
    """
    Identify tag contains 'img' or 'a' tag in their descendants.

    Parameters
    ----------
    tag: bs4.element.Tag
        HTML Tag

    Returns
    -------
    tuple[str, bs4.element.Tag]
        Return (tag name, tag)
    """
    children = [t for t in tag.descendants]
    names = [child.name for child in children]

    if 'img' in names:
        name = 'img'
    elif 'a' in names:
        name = 'a'

    else: name = 'text'

    return (name, tag)


def refine_paragraph_tag(
    tag: bs4.element.Tag
) -> list[dict]:
    """
    Extract img source or text from tag

    Parameters
    ----------
    tag: bs4.element.Tag
        HTML Tag

    Returns
    -------
    list[dict]
    """
    result = []

    name, tag = identify_tag_name(tag)

    if name == 'img':
        for child in tag.find_all('img'):
            lazy_source = child.get('data-lazy-src', "")
            source = lazy_source if lazy_source != "" else child.get('src')
            if len(source) > 1:
                result.append({
                    "info": "img",
                    "content": source
                })
    
    elif name == 'a':
        for child in tag.find_all('a'):
            result.append({
                "info": "link",
                "content": child.get('href')
            })
    
    else:
        text = []

        for child in tag.children:
            text.append(child.text.replace('\u200b', '\n').strip())
        
        text = '\n'.join(text).strip()

        if (len(text) > 0) and not (text == '\u200b'):
            result.append({
                "info": "text",
                "content": text
            })

    return result