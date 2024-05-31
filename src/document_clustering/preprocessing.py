#!/usr/bin/env -S python3 -i
# ruff: noqa: D103, F401, TCH003, T201, ANN001, ANN201
"""Experimenting and Messy Code."""

from __future__ import annotations

import logging
import operator
import re
from collections import Counter
from collections.abc import Callable, Generator, Iterable
from functools import reduce
from string import ascii_letters

import rich
from glassplitter import Tokenizer

from document_clustering import arxiv_dataset
from document_clustering.pdf_extract import PdfDocument, unbox_text

if __name__ == "__name__":
    logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


def bag_of_words(): ...  # TODO (leogott): implement this


def bag_of_chars(arg: str):
    characters = Counter(arg)
    chars_sans_letters = {key: count for key, count in characters.items() if key not in ascii_letters}
    print(chars_sans_letters, sort_dicts=True)


def replace_ligatures(text: str) -> str:
    """For a given string, replace each ligature with its corresponding characters."""
    ligatures = {
        "ﬀ": "ff",
        "ﬁ": "fi",
        "ﬂ": "fl",
        "ﬃ": "ffi",
        "ﬄ": "ffl",
        "ﬅ": "ft",
        "ﬆ": "st",
        # "Ꜳ": "AA",
        # "Æ": "AE",
        # "ꜳ": "aa",
    }
    return text.translate(ligatures)


def font_size_filter(min_font_size=0, max_font_size=10):
    def filter_font_size(item):
        if item["font_size"] >= max_font_size or item["font_size"] <= min_font_size:
            logger.debug("Discarded item with text: %s", item["text"])
            return False
        return True

    return filter_font_size


def font_name_filter(font_list: list, *, accept=True):
    def filter_font_name(item):
        if item["font_name"] in font_list:
            logger.debug("Font matched on item with text %s", item["text"])
            return accept
        return not accept

    return filter_font_name


def _debug_replace_urls(text: str) -> str:
    def repl(m):
        print(m.group(0))
        return ""

    return replace_urls(text, repl)


def replace_urls(text: str, replace_with: str | Callable[..., str] = "") -> str:
    """Replace urls using the given string or function."""
    p = re.compile(r"(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)")
    return re.sub(p, replace_with, text)


def recombine(sentence_list, text_boxes):
    """Re-attach (potentially un-hashable) data-objects.

    Take an iterable of lists of tuples (obj, i),
    and a mapping of i to data,
    enumerate the group data and re-attach it.
    """
    group_data = dict(enumerate(text_boxes))
    for sentence in sentence_list:
        yield [(a, group_data[i]) for a, i in sentence]


def tokenize_with_data(tokenizer: Tokenizer, text_boxes):
    """Tokenize text-boxes.

    Wrap glassplitter tokenizer and re-attach data.
    """
    spans = unbox_text(text_boxes)
    sentence_list = tokenizer.split(spans, trim=True)

    return list(recombine(sentence_list, text_boxes))


def filter_text_boxes(text_boxes, filters: list[Callable[..., bool]]):
    """Apply each filter."""
    for fun in filters:
        text_boxes = list(filter(fun, text_boxes))
    return text_boxes


if __name__ == "__main__":
    # spans = [("I am a ", {"line": 1}), ("split sentence!", {"line": 2})]
    tokenizer = Tokenizer(lang="en", clean=True, doc_type="pdf")
    # [[("", 0), ("I", 0), ("am", 0), ("a", 0), ("split", 1), ("sentence", 1), ("!", 1), ("", 1)]]
    paper = arxiv_dataset.get("2301.06511")
    spans = PdfDocument(paper).poppler_textboxes_flat()[:99]

    spans = filter_text_boxes(
        spans,
        [
            font_name_filter(["Times-Roman"], accept=False),
            font_size_filter(),
        ],
    )

    out = list(tokenize_with_data(tokenizer, spans))
    rich.print(out)
