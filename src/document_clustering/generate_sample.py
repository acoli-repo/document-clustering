#!/usr/bin/env python3

import logging
from pathlib import Path

import pandas as pd
from rich.logging import RichHandler

from document_clustering.arxiv_dataset import fetch_arxiv_sample
from document_clustering.clustering import cluster, transform
from document_clustering.pdf_extract import preprocess

# Logger
if __name__ == "__name__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[RichHandler(log_time_format="%X")],
    )
    logger = logging.getLogger(__name__)
    logger.addHandler(RichHandler(log_time_format="%X"))
    logger.setLevel(logging.DEBUG)
else:
    logger = logging.getLogger(__name__)


# Config


if __name__ == "__name__":
    # Data, Metadata
    arxiv_sample = fetch_arxiv_sample(Path("src/document_clustering/sample/50_ids.txt"))
    metadata = pd.DataFrame(
        {
            "arxiv_id": arxiv_sample.ids,
            "title": arxiv_sample.titles,
            "date": arxiv_sample.dates,
        }
    )
    corpus = arxiv_sample.data

    data = preprocess(corpus)
    pipeline = cluster(data)
    cluster_metadata = transform(pipeline, metadata)
    logger.info(cluster_metadata)
