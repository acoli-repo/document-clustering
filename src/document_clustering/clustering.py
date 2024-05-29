import logging
import numpy as np
from document_clustering.utils import execution_time

from typing import Optional
from functools import partial

from sklearn import set_config
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import make_pipeline

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline, make_pipeline


from collections.abc import Iterable

logger = logging.getLogger(__name__)

# Tfidf Vectorizer
set_config(transform_output="pandas")

tfidf_vectorizer = make_pipeline(
    CountVectorizer(
        # max_df=0.5, # Percentage of docs
        # min_df=3, # Absolute number of docs to contain feature (word)
        #
        # vectorizer expects documents to be of str, so some trickery is required here
        preprocessor=partial(map, str.lower),
        tokenizer=lambda x: x,  # documents are tokenized already
        token_pattern=None,
        max_features=5000,
        # stop_words and ngram_range are not used when analyzer in use
        stop_words="english",
        # ngram_range=(1, 2),
    ),
    TfidfTransformer(sublinear_tf=True),
)


def cluster(data: Iterable[Iterable[str]], n_clusters=5):
    """data is expected to be tokenized"""

    # KMeans Clustering

    kmeans = KMeans(n_clusters=n_clusters, random_state=0)

    # Tfidf Vectorizer

    with execution_time() as t:
        tfidf_matrix = tfidf_vectorizer.fit_transform(data)
    logger.info(f"Vectorization done in {t()}")

    # KMeans Clustering

    with execution_time() as t:
        kmeans.fit(tfidf_matrix)
    logger.info(f"Clustering done in {t()}")

    kmeans_pipeline = make_pipeline(tfidf_vectorizer, kmeans)
    return kmeans_pipeline


def transform(
    fitted_pipeline: Pipeline,
    data: Iterable[Iterable[str]],
    metadata: Optional[pd.DataFrame],
):
    """
    fitted_pipeline + data -> document_df

    """
    kmeans = fitted_pipeline.named_steps.kmeans
    tfidf_vectorizer = fitted_pipeline.named_steps.tfidf_vectorizer  # TODO fix name

    # Analysis: Documents

    cluster_distances: pd.DataFrame = fitted_pipeline.transform(data)
    # cluster_distances = cluster_distances.assign(cluster=kmeans_pipeline.predict(data))
    cluster_distances = cluster_distances.assign(cluster=kmeans.labels_)

    if metadata is None:
        return cluster_distances
    else:
        cluster_metadata = cluster_distances.join(metadata)
        return cluster_metadata


def extract(fitted_pipeline: Pipeline):
    """
    fitted_pipeline -> cluster_df
    evtl perspektivisch:
    document_df (+ data) -> cluster_df
    """
    kmeans: KMeans = fitted_pipeline.named_steps.kmeans
    n_clusters = kmeans.get_params()["n_clusters"]

    # Analysis: Clusters

    _cluster_ids, cluster_sizes = np.unique(kmeans.labels_, return_counts=True)
    logger.info(f"Number of elements assigned to each cluster: {cluster_sizes}")

    original_space_centroids = kmeans.cluster_centers_
    order_centroids = original_space_centroids.argsort()[:, ::-1]
    terms = tfidf_vectorizer.get_feature_names_out()
    # terms = kmeans_pipeline.named_steps.tfidf_vectorizer.get_feature_names_out()

    for i in range(n_clusters):
        line = f"Cluster {i}: " + "".join(
            [f"'{terms[ind]}' " for ind in order_centroids[i, :10]]
        )
        logger.info(line)

    # { "topics" : {"id":"1", "top 5": ["bag", "image", "cup"] }}
    topics = {
        "kmeans": [
            {
                "cluster": str(i),
                "size": cluster_sizes[i],
                "top 5": [terms[tid] for tid in order_centroids[i, :5]],
            }
            for i in range(n_clusters)
        ]
    }
    return topics
