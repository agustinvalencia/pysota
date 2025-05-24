# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.1
#   kernelspec:
#     display_name: .venv
#     language: python
#     name: python3
# ---

# %%
from pathlib import Path
from pysota.core import Publication
from pysota.process import Persistence
from gensim import corpora
from gensim.models import LdaModel
import pandas as pd
import spacy
from gensim.models import CoherenceModel

nlp = spacy.load('en_core_web_lg')

# db: list[Publication] = Persistence.load_files(path=Path('../results/clustered/euclidean'), query_name='cluster_4')

# %%
word1 = 'robots'
word2 = 'weapons'
word3 = 'dog'

vector = nlp(word1.lower())[0].vector + nlp(word2.lower())[0].vector # + nlp(word3.lower())[0].vector
res = nlp.vocab.vectors.most_similar(vector.reshape(1, -1))
nlp.vocab[res[0][0][0]].text

# %%
# from sklearn.decomposition import LatentDirichletAllocation
# from sklearn.feature_extraction.text import CountVectorizer

# # Sample documents
# documents = [doc.abstract for doc in db]

# # Convert documents into a document-term matrix
# vectorizer = CountVectorizer(stop_words='english')
# dtm = vectorizer.fit_transform(documents)

# # Set the number of topics
# n_topics = 10

# # Initialize and fit the LDA model
# lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
# lda.fit(dtm)

# # Display the top words for each topic
# n_top_words = 3
# feature_names = vectorizer.get_feature_names_out()

# for topic_idx, topic in enumerate(lda.components_):
#     print(f"Topic {topic_idx}:")
#     top_features = [feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]]
#     print(" ".join(top_features))


# %%
exclude = [
    "representation", 
    "learning", 
    "learn", 
    "training", 
    "train", 
    "supervision",
    "supervised",
    "supervise",
    "method", 
    "model", 
    "datum", 
    "self" ,
    "task", 
]


# %%
def preprocess(text, exclude=exclude):
    doc = nlp(text.lower())
    tokens = [
        token.lemma_ for token in doc
        if not token.is_stop and not token.is_punct and token.is_alpha and token.lemma_ not in exclude and token.lemma_ != 'ADV'
    ]
    return tokens


# Preprocess each document
# texts = [preprocess(doc.abstract) for doc in db]

# %%
def train_lda(dictionary, num_topics=10, passes=100):
    # Create a dictionary and corpus
    # dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    # Filter out words that occur less than 2 documents, or more than 50% of the documents
    # dictionary.filter_extremes(no_below=2)
    # Train the LDA model
    lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=passes)
    return lda_model



# %%
def coherence(lda_model, texts, dictionary):
    # Compute Coherence Score
    coherence_model_lda = CoherenceModel(model=lda_model, texts=texts, dictionary=dictionary, coherence='c_v')
    coherence_score = coherence_model_lda.get_coherence()
    print(f'Coherence Score: {coherence_score}')



# %%
def lda_topics_to_dataframe(lda_model, num_words=5):
    # Extract topics from the LDA model
    topics = lda_model.show_topics(num_topics=-1, num_words=num_words, formatted=False)
    
    # Initialize a list to hold the parsed data
    data = []
    
    # Iterate over each topic
    for topic_num, terms in topics:
        for term, weight in terms:
            data.append([topic_num, term, weight])
    
    # Create a DataFrame
    df = pd.DataFrame(data, columns=['Topic', 'Term', 'Weight'])
    
    # Sort the DataFrame by Topic and Weight in descending order
    df = df.sort_values(by=['Topic', 'Weight'], ascending=[True, False]).reset_index(drop=True)
    
    return df

# Example usage
# Assuming you have an LdaModel object named 'lda_model'
# df_topics = lda_topics_to_dataframe(lda_model, num_words=5)


# %%
for cluster in range(10): 
    db: list[Publication] = Persistence.load_files(path=Path('../results/clustered/euclidean'), query_name=f'cluster_{cluster}')

    msg = f"Cluster {cluster} has {len(db)} documents"
    print(f"\n{msg}")
    print('-' * len(msg))

    texts = [preprocess(doc.abstract) for doc in db]
    dictionary = corpora.Dictionary(texts)
    lda_model = train_lda(dictionary, num_topics=5, passes=100)
    coherence(lda_model, texts, dictionary)
    df_topics = lda_topics_to_dataframe(lda_model, num_words=5)

    for topic in df_topics.Topic.unique():
        terms = df_topics[df_topics.Topic == topic].Term.tolist()
        print(f"Topic {topic}: {', '.join(terms)} ")
