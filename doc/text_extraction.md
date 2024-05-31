# Comparing PDF libraries for Python

In preparation for later tasks I researched and compared several methods of obtaining the text content of "digitally born"¹ PDF documents.
Poppler was presented as the status quo.

After getting pretty far with the task, I discovered [an extensive benchmark](https://github.com/py-pdf/benchmarks) had already been done. And there also exists [a python module](https://pypi.org/project/sparclur/) just for comparing text extraction packages. I didn't really look into those yet, except for checking if I missed any major ones.

So far I got similar, acceptable results for the three main packages under test. We can probably stick to poppler (or any of them) until something breaks.

package | designation | library / based on | version (if tested) | comment / also known as
-|-|-|-|-
python-poppler| rendering | Poppler (freedesktop)|23.08.0|"pdftotext"
pdfminer.six|extracting information|pdfminer|20221105|
pypdf|pdf toolkit|…|3.16.4|"pyPDF2"
tika-python|content analysis toolkit?|Apache Tika|~~?~~|java runtime dependencies
pypdfium2|rendering|PDFium (Google)|~~?~~|
clips/pattern|web mining|pdfminer|~~3.6.0~~|outdated library?
pdfquery|pdf scraper|pdfminer, lxml and pyquery|~~?~~|wrapper
pikepdf|pdf toolkit|QPDF|~~?~~|can't do text extraction
PyMuPdf|-|-|~~?~~|
pdfplumber|-|pdfminer.six|~~?~~|can extract tables

¹) meaning they were created from digital text, and not scanned, OCRed, or whatever. This should apply to our use-case, scientific papers are commonly built with pdftex, I think? .

# About my code

I used conda to manage my python runtime environment.

`environment.yml` contains all the necessary info about which python packages to install.
Run `conda env create --file environment.yml` and `conda activate document-clustering` before running the interpreter.

When something changed, you may need to run
`conda env update --file environment.yml`
