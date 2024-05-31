# ruff:noqa:F401


def test_import_all() -> None:
    """Verify all modules can be imported without error."""
    from document_clustering import arxiv_dataset
    from document_clustering import clustering
    from document_clustering import generate_sample
    from document_clustering import preprocessing
    from document_clustering import pdf_extract
    from document_clustering import utils
