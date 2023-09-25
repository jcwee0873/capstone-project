import re
import bs4

MAP_REGIX = re.compile("se-module-map")
DIV_OR_A = re.compile('div|a')

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
        "se-main-container": (DIV_OR_A, {"class": "se-module"}),
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
    children = [tag] + [t for t in tag.descendants]
    names = [child.name for child in children]
    attrs = []
    for t in children:
        if isinstance(t, bs4.element.NavigableString): continue
        attr = t.attrs
        if attr.get('id'): attrs.append(attr['id'])
        attrs += attr.get('class', [])

    if 'se-module-video' in attrs:
        name = 'video'
    elif [a for a in attrs if MAP_REGIX.match(a)]:
        name = 'map'
    elif 'video' in names:
        name = 'gif'
    elif 'img' in names:
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
    
    elif name == 'gif':
        for child in tag.find_all('video'):
            result.append({
                "info": "gif",
                "content": child.get('data-gif-url')
            })

    
    elif name == 'map':
        text = tag.text.strip()

        if text != "":
            result.append({
                "info": "map",
                "content": text
            })

    elif name == 'video':
        result.append({
            "info": "video",
            "content": "video"
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


def extract_additional_info(
    soup: bs4.BeautifulSoup
) -> dict:
    selector_map = {
        "profile": ('p', {"class": "caption align"}),
        "article_cnt": ('span', {"class": "num cm-col1"}),
        "love_cnt": ('em', {"class": "u_cnt _count"}),
        "comment_cnt": ('em', {"class": "_commentCount"}),
        "hash_tags": ("a", {"class": "item pcol2 itemTagfont _setTop"}),
        "ad_post": ("div", {"class": "ssp-adcontent"}),
        "video": ("div", {"class": "se-video"})
    }

    count_key = ["hash_tags", "ad_post", "video"]

    result = {}

    for name, selector in selector_map.items():
        result[name] = soup.find_all(selector[0], selector[1])

        if name in count_key:
            result[name] = len(result[name])
        else:
            try:
                result[name] = result[name][0].text.strip()
            except:
                result[name] = None

    return result
    