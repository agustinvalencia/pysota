---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.17.1
  kernelspec:
    display_name: .venv
    language: python
    name: python3
---

```python
!python -m spacy download en_core_web_lg
```

```python
import spacy
```

```python
nlp = spacy.load("en_core_web_md")  # make sure to use larger package!
doc1 = nlp("I like salty fries and hamburgers.")
doc2 = nlp("Fast food tastes very good.")

# Similarity of two documents
print(doc1, "<->", doc2, doc1.similarity(doc2))
# Similarity of tokens and spans
french_fries = doc1[2:4]
burgers = doc1[5]
print(french_fries, "<->", burgers, french_fries.similarity(burgers))
```

```python
abstract_1 ="'<jats:p>The global demographic shift towards an aging population has intensified the prevalence of diseases like osteoporosis, characterized by fragile bones and heightened fracture risk, particularly in the spine, hips, and wrists. This condition, more common in women, results from low bone mass and poor structure, leading to weakened bones and increased susceptibility to fractures. While Dual Energy X-ray Absorptiometry (DEXA) has been a traditional diagnostic tool, its limited availability, cost, and radiation exposure pose challenges. However, Computer- Aided Diagnosis (CAD) has elevated diagnostic accuracy.  In modern medical education, Deep Learning, Machine Learning, and Artificial Intelligence have revolutionized healthcare. These technologies enable precise osteoporosis diagnosis by analyzing clinical data and images using Convolutional Neural Networks (CNNs) and Recurrent Neural Networks (RNNs). By combining advanced algorithms with medical expertise, these systems offer automated detection and diagnosis, improving early intervention and reducing osteoporosis's impact on individuals and healthcare systems. This integration underscores the critical role of technology in healthcare advancement.        Keywords: AI, deep learning, feature extraction, ML, osteoporosis</jats:p>"
```

```python
abstract_2 = "<jats:p>Despite widespread skepticism of data analytics and artificial intelligence (AI) in adjudication, the Social Security Administration (SSA) pioneered path-breaking AI tools that became embedded in multiple levels of its adjudicatory process. How did this happen? What lessons can we draw from the SSA experience for AI in government? We first discuss how early strategic investments by the SSA in data infrastructure, policy, and personnel laid the groundwork for AI. Second, we document how SSA overcame a wide range of organizational barriers to develop some of the most advanced use cases in adjudication. Third, we spell out important lessons for AI innovation and governance in the public sector. We highlight the importance of leadership to overcome organizational barriers, “blended expertise” spanning technical and domain knowledge, operational data, early piloting, and continuous evaluation. AI should not be conceived of as a one-off IT product, but rather as part of continuous improvement. AI governance is quality assurance.</jats:p"
```

```python
abstract_3 = "The processing pipeline consists of one or more pipeline components that are called on the Doc in order. The tokenizer runs before the components. Pipeline components can be added using Language.add_pipe. They can contain a statistical model and trained weights, or only make rule-based modifications to the Doc. spaCy provides a range of built-in components for different language processing tasks and also allows adding custom components."
```

```python
doc1 = nlp(abstract_1)
doc2 = nlp(abstract_2)
doc3 = nlp(abstract_3)
print(doc1.similarity(doc2))
print(doc1.similarity(doc3))
```

```python
from sklearn.cluster import DBSCAN
import numpy as np


nlp = spacy.load('en_core_web_lg')
documents = [abstract_1, abstract_2, abstract_3]
doc_vectors = [nlp(doc).vector for doc in documents]

X = np.array(doc_vectors)

dbscan = DBSCAN(eps=2.9, min_samples=2)
dbscan.fit(X)

# Group documents by their cluster labels
clusters = {}
for idx, label in enumerate(dbscan.labels_):
    clusters.setdefault(label, []).append(documents[idx])

# Print the clusters; note that label -1 indicates noise points
for cluster_id, docs in clusters.items():
    if cluster_id == -1:
        print("Noise:")
    else:
        print(f"Cluster {cluster_id}:")
    for doc in docs:
        print(f"  - {doc}")

```

```python
import spacy
from sklearn.cluster import DBSCAN
import numpy as np

# Load a spaCy model with word vectors
nlp = spacy.load('en_core_web_lg')

# Sample text documents
documents = [
    "I love cats and dogs.",
    "Dogs are great companions.",
    "The sky is blue and beautiful.",
    "The weather is bright and sunny.",
    "I enjoy reading about science.",
    "Science and technology are fascinating subjects."
]

# Process documents and extract their vector representations
doc_vectors = [nlp(doc).vector for doc in documents]
X = np.array(doc_vectors)

# Configure DBSCAN clustering
# eps: maximum distance between two samples for them to be considered as in the same neighborhood.
# min_samples: the number of samples (or total weight) in a neighborhood for a point to be considered as a core point.
dbscan = DBSCAN(eps=2.9, min_samples=2)
dbscan.fit(X)

# Group documents by their cluster labels
clusters = {}
for idx, label in enumerate(dbscan.labels_):
    clusters.setdefault(label, []).append(documents[idx])

# Print the clusters; note that label -1 indicates noise points
for cluster_id, docs in clusters.items():
    if cluster_id == -1:
        print("Noise:")
    else:
        print(f"Cluster {cluster_id}:")
    for doc in docs:
        print(f"  - {doc}")
```

```python
import re

def clean_string(input_string):
    # Remove all non-word characters except spaces
    cleaned_string = re.sub(r'[^\w\s]', '', input_string)
    # Replace multiple consecutive whitespace characters with a single space
    cleaned_string = re.sub(r'\s+', ' ', cleaned_string)
    # Strip leading and trailing whitespace
    cleaned_string = cleaned_string.strip()
    return cleaned_string


# Example usage
if __name__ == "__main__":
    sample_text = "Hello,\n\n\tWorld!  This is a\ttest: 123.\n\n"
    cleaned_text = clean_string(sample_text)
    print("Original text:", repr(sample_text))
    print("Cleaned text:", repr(cleaned_text))

```
