from __future__ import annotations

import logging
from collections.abc import Callable, Generator, Iterable
from pathlib import Path
from typing import Any, Optional

import poppler
import poppler.page
from glassplitter import Tokenizer
from poppler.page import TextBox

from document_clustering.utils import execution_time

logger = logging.getLogger(__name__)

def is_pdf(data: bytes) -> bool:
    """Verify that the data starts with the correct magic bytes."""
    return data.startswith(b"%PDF")


class PdfDocument:
    """Wrapper for pdf utilities."""

    def __init__(self, file: bytes):
        self.content = file
        if not is_pdf(self.content):
            msg = "file must be a PDF document"
            raise ValueError(msg)

    @classmethod
    def from_file(cls, path: Path | str) -> PdfDocument:
        """Alternative constructor from path or path-like."""
        return cls(Path(path).read_bytes())

    def pypdf_extract_text(self) -> str:
        """Return the entire text data of a pdf using pypdf."""
        from pypdf import PdfReader  # noqa: PLC0415

        # https://pypdf.readthedocs.io/en/stable/user/post-processing-in-text-extraction.html
        # https://pypdf.readthedocs.io/en/stable/user/extract-text.html
        reader = PdfReader(self.content)
        pages = [page.extract_text() for page in reader.pages]
        # print(reader.metadata)
        return " ".join(pages)

    def pdfminersix_extract_text(self) -> str:
        """Return the entire text data of a pdf using pdfminer.six."""
        from pdfminer.high_level import extract_text  # noqa: PLC0415

        # https://pdfminersix.readthedocs.io/en/latest/topic/converting_pdf_to_text.html
        # https://www.unixuser.org/~euske/python/pdfminer/programming.html
        return extract_text(self.content)

    def poppler_extract_text(self) -> str:
        """Return the entire text data of a pdf using poppler."""
        pdf_document = poppler.load_from_data(self.content)
        text_pages = []
        for page_index in range(pdf_document.pages):
            pdf_page = pdf_document.create_page(page_index)
            text_pages += pdf_page.text()
        return " ".join(text_pages)

    def poppler_textboxes_flat(self) -> list[poppler.page.TextBox]:
        """Return a list of TextBox objects with attached style information.

        It may be useful to have another method that returns a generator.
        Name and output not final.
        """
        pdf_data = self.content
        try:
            pdf_document = poppler.load_from_data(pdf_data)
        except ValueError:
            logger.exception(
                f"Poppler didn't like this pdf file of length {len(pdf_data)}."
            )
            logger.debug(f"File starts with: {pdf_data[:500]}")
            raise

        # Possibly replace with itertools chain
        boxes = []
        for p, page_index in enumerate(range(pdf_document.pages)):
            pdf_page = pdf_document.create_page(page_index)
            boxes.extend(
                [
                    {
                        "text": box.text,
                        "page": p,
                        "font_size": box.get_font_size(),
                        "font_name": _get_font_name(box),
                    }
                    for box in pdf_page.text_list(
                        pdf_page.TextListOption.text_list_include_font
                    )
                ]
            )
        return boxes


def _get_font_name(box: poppler.page.TextBox):
    """Wrap get_font_name method in a try-except.

    fixes problem with paper 0704.0014
    """
    try:
        return box.get_font_name()
    except UnicodeDecodeError:
        logger.exception()
        return "Error"


def unbox_text(text_boxes: Iterable[TextBox]) -> Generator[tuple[str, int], Any, None]:
    """Take the output from poppler_textboxes_flat and turn it into something glassplitter can digest."""
    for item in text_boxes:
        yield item["text"]


def custom_analyzer(
    tokenizer: Tokenizer,
    *,
    filter_textboxes: Callable[[TextBox], bool] | None = None,
    transform_sentences: Callable[[str], str] = lambda snt: snt,
    filter_tokens: list[str] | None = None,
) -> Callable[[bytes], list[str]]:
    """Turn a pdf into a list of str tokens.

    Preprocessor and tokenizer in one.
    """
    if filter_tokens is None:
        filter_tokens = []
    if filter_textboxes is None:

        def filter_textboxes(_tbx: poppler.page.TextBox):
            return True

    def wrapped_custom_analyzer(pdf: bytes):
        # No sentence segmentation, assume each text-box contains exactly one sentence
        textboxes = PdfDocument(pdf).poppler_textboxes_flat()

        filtered_textboxes = filter(filter_textboxes, textboxes)

        sentences = unbox_text(filtered_textboxes)

        transformed_sentences = map(transform_sentences, sentences)

        tokens = tokenizer.split_flat(transformed_sentences)

        filtered_tokens = filter(lambda t: t not in filter_tokens, tokens)
        return list(filtered_tokens)

    return wrapped_custom_analyzer


# Tokenizer

tokenizer = Tokenizer(lang="en", clean=True, doc_type="pdf")


def preprocess(corpus: list[bytes], filenames: Optional[list[str]] = None) -> list[str]:
    """Analyze and Tokenize corpus.

    corpus: list of pdfs
    """
    # Preprocessor

    stop_words = ["", "the"]
    # TODO(leogott): insert preproc pipeline here
    # TODO(leogott): String Transformation / str.lower
    analyzer = custom_analyzer(tokenizer, filter_tokens=stop_words)
    data = []
    with execution_time() as t:
        for i, pdf in enumerate(corpus):
            pdf_name = str(i) if (filenames is None) else filenames[i]
            logger.debug("Analyzing pdf %s", pdf_name)
            try:
                data.append(analyzer(pdf))
            except:
                logger.exception(
                    "An error occured while handling %s", pdf_name
                )
                raise
    logger.info(f"Tokenized {len(data)=} PDFs in {t()}")
    return data
