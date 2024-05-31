# Selecting a sample of papers to process

In order to generate a sample, we first arbitrarily chose 50 preprints on arxiv.

Therefore I downloaded the arxiv-metadata-oai-snapshot json from [kaggle](https://www.kaggle.com/datasets/Cornell-University/arxiv/data) (Version 162)
and truncated the file to the first 50 entries.

`head -n 50 arxiv-metadata-oai-snapshot.json > arxiv_sample.json`

The original metadata file is approaching 4 Gigabytes in size — too large even open in most text editors —
and ordered by arxiv-id, resulting in a sample that is not all that representative of the dataset.

Each line is a valid json object though, containing the metadata of one submission.

Switching away from this approach required some extra complexity for fetching the metadata ourselves.

# Generating the Sample

https://www.kaggle.com/code/maartengr/topic-modeling-arxiv-abstract-with-bertopic/notebook
https://scikit-learn.org/stable/auto_examples/text/plot_document_clustering.html
