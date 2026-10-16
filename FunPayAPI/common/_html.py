"""Общие функции разбора HTML для аккаунта и обработчика событий."""

import re

from selectolax.lexbor import LexborHTMLParser, LexborNode


_TAG_ATTRIBUTES = r'''(?:[^"'<>]|"[^"]*"|'[^']*')*'''
_PREFORMATTED_OPEN = re.compile(r"<(?:textarea|pre|listing)\b", re.IGNORECASE)
_INITIAL_NEWLINE = re.compile(r"\r\n|\r|\n|&#(?:0*10|x0*a);?|&NewLine;", re.IGNORECASE)
_LEADING_NEWLINE = re.compile(
    r"<!--.*?-->"
    rf"|(?P<raw_open><(?P<raw_tag>textarea|script|style|title|xmp|iframe|noembed|noframes)\b{_TAG_ATTRIBUTES}>)"
    r"(?P<raw_content>.*?)(?P<raw_close></(?P=raw_tag)\s*>)"
    rf"|(?P<opening><(?:pre|listing)\b{_TAG_ATTRIBUTES}>)(?P<newline>{_INITIAL_NEWLINE.pattern})",
    re.IGNORECASE | re.DOTALL,
)
_ASCII_WHITESPACE = " \t\n\r\f"


def _keep_leading_newline(match: re.Match) -> str:
    if match["opening"] is not None:
        return match["opening"] + "\n" + match["newline"]
    if (match["raw_tag"] or "").lower() == "textarea" and _INITIAL_NEWLINE.match(match["raw_content"]):
        return match["raw_open"] + "\n" + match["raw_content"] + match["raw_close"]
    return match[0]


def parse_html(source: str) -> LexborHTMLParser:
    # HTML5 удаляет первый перенос строки внутри этих элементов. Сохраняем его
    # в полях форм и форматированных сообщениях для совместимости с прежним API.
    if _PREFORMATTED_OPEN.search(source):
        source = _LEADING_NEWLINE.sub(_keep_leading_newline, source)
    return LexborHTMLParser(source)


def _collapse_whitespace(part: str) -> str:
    if part and not part.strip(_ASCII_WHITESPACE):
        return "\n" if "\n" in part else " "
    return part


def _text_parts(node: LexborNode, normalize_whitespace: bool = False) -> list[str]:
    if node.css_first("script, style, template, pre, textarea") is None:
        parts = node.text(separator="\0", strip=False).split("\0")
        return [_collapse_whitespace(part) for part in parts] if normalize_whitespace else parts

    # Сохраняем пробелы в форматированном тексте и исключаем невидимое
    # содержимое, не меняя HTML, возвращаемый через API.
    parts = []
    for child in node.traverse(include_text=True):
        if child.tag != "-text":
            continue
        parent = child.parent
        preserve = False
        visible = True
        while parent is not None:
            if parent.tag in ("script", "style", "template"):
                visible = False
                break
            preserve = preserve or parent.tag in ("pre", "textarea")
            if parent.mem_id == node.mem_id:
                break
            parent = parent.parent
        if visible:
            part = child.text(deep=False)
            parts.append(_collapse_whitespace(part) if normalize_whitespace and not preserve else part)
    return parts


def text(node: LexborNode) -> str:
    # Сохраняем пробелы между элементами и переносы строк. Сокращаем только
    # текстовые узлы из одних пробелов: обрезка всего результата изменит сообщения.
    return "".join(_text_parts(node, normalize_whitespace=True))


def first_text(node: LexborNode) -> str:
    return next((part.strip() for part in _text_parts(node) if part.strip()), "")


def single_text(node: LexborNode) -> str | None:
    """Текст метки с единственным текстовым узлом, в том числе вложенным."""
    child = node.child
    while child is not None and child.next is None:
        if child.tag == "-text":
            return child.text()
        child = child.child
    return None


def first_descendant(node: LexborNode, selector: str) -> LexborNode | None:
    # Selectolax включает текущий узел в результаты поиска по CSS.
    return next((match for match in node.css(selector) if match.mem_id != node.mem_id), None)


def ancestor(node: LexborNode, class_name: str) -> LexborNode | None:
    parent = node.parent
    while parent is not None:
        if class_name in (parent.attributes.get("class") or "").split():
            return parent
        parent = parent.parent
    return None
