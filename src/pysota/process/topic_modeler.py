import logging
import random
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pyLDAvis
import pyLDAvis.gensim_models
import spacy
import spacy.cli
from gensim import corpora
from gensim.models import LdaModel
from gensim.models.coherencemodel import CoherenceModel
from rich.progress import Progress


class TopicModelingPipeline:
    """
    A pipeline for performing topic modeling on a list of text abstracts.
    Includes random search for hyperparameter optimization, logging, and plotting.
    """

    def __init__(
        self,
        random_state=100,
        exclude_words=None,
        log_output_dir=None,
        plot_output_dir=None,
        cluster_name='default_cluster',
        progress_tracker: Progress = None,
    ):
        """
        Initializes the TopicModelingPipeline.

        Args:
            random_state (int): Seed for reproducibility.
            exclude_words (list): A list of additional words (lemmas) to exclude during pre-processing.
            log_output_dir (Path): Directory where log files will be saved.
            plot_output_dir (Path): Directory where plot PNGs will be saved.
            cluster_name (str): A unique name for the current cluster, used for naming logs/plots.
            progress_tracker (Progress): An optional rich.progress.Progress instance for progress updates.
        """
        self.random_state = random_state
        random.seed(self.random_state)
        np.random.seed(self.random_state)

        self.exclude_words = set(exclude_words) if exclude_words else set()

        try:
            self.nlp = spacy.load('en_core_web_lg')
        except OSError:
            print("Downloading spaCy model 'en_core_web_lg'...")
            spacy.cli.download('en_core_web_lg')
            self.nlp = spacy.load('en_core_web_lg')

        self.dictionary = None
        self.corpus = None
        self.lda_model = None
        self.processed_docs = None

        self.log_output_dir = Path(log_output_dir) if log_output_dir else Path('./logs')
        self.plot_output_dir = Path(plot_output_dir) if plot_output_dir else Path('./plots')
        self.cluster_name = cluster_name
        self.progress_tracker = progress_tracker

        self._setup_logging()

    def _setup_logging(self):
        """Sets up a logger for the current cluster."""
        self.log_output_dir.mkdir(parents=True, exist_ok=True)
        log_file = self.log_output_dir / f'{self.cluster_name}_log.txt'

        if self.cluster_name not in logging.Logger.manager.loggerDict:
            self.logger = logging.getLogger(self.cluster_name)
            self.logger.setLevel(logging.INFO)

            file_handler = logging.FileHandler(log_file)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        else:
            self.logger = logging.getLogger(self.cluster_name)

        self.logger.info(f'Logging initialized for cluster: {self.cluster_name}')
        self.logger.info(f'Log file: {log_file}')

    def _preprocess_text(self, text):
        """Cleans and tokenizes text using spaCy."""
        doc = self.nlp(text.lower())
        tokens = [
            token.lemma_
            for token in doc
            if not token.is_stop
            and not token.is_punct
            and token.is_alpha
            and token.lemma_ not in self.exclude_words
            and token.lemma_ != 'ADV'
        ]
        return tokens

    def prepare_data(self, abstracts_list):
        """Prepares the data for topic modeling."""
        self.logger.info('Starting data pre-processing using spaCy...')
        self.processed_docs = [self._preprocess_text(abstract) for abstract in abstracts_list]
        self.logger.info(f'Processed {len(self.processed_docs)} documents.')

        self.logger.info('Creating Gensim dictionary and corpus...')
        self.dictionary = corpora.Dictionary(self.processed_docs)
        self.dictionary.filter_extremes(no_below=2, no_above=0.9, keep_n=100000)
        self.corpus = [self.dictionary.doc2bow(doc) for doc in self.processed_docs]
        self.logger.info(f'Corpus created with {len(self.dictionary)} unique tokens.')

    def train_lda_model(self, num_topics, passes, iterations=50):
        """Trains the Latent Dirichlet Allocation (LDA) model."""
        if not self.corpus or not self.dictionary:
            raise ValueError('Data not prepared. Call prepare_data() first.')

        self.logger.info(f'Training LDA model with {num_topics} topics (passes={passes})...')
        lda_model = LdaModel(
            corpus=self.corpus,
            id2word=self.dictionary,
            num_topics=num_topics,
            random_state=self.random_state,
            passes=passes,
            iterations=iterations,
        )
        self.logger.info('LDA model training complete.')
        return lda_model

    def evaluate_model_coherence(self, lda_model):
        """Evaluates the trained LDA model using CoherenceModel."""
        if not lda_model:
            raise ValueError('LDA model not provided for evaluation.')
        if not hasattr(self, 'processed_docs') or not self.processed_docs:
            self.logger.warning(
                'No pre-processed texts found for coherence evaluation. Call prepare_data() first.'
            )
            return None

        self.logger.info('Calculating model coherence (c_v)...')
        coherence_model_lda = CoherenceModel(
            model=lda_model, texts=self.processed_docs, dictionary=self.dictionary, coherence='c_v'
        )
        coherence_lda = coherence_model_lda.get_coherence()
        self.logger.info(f'Coherence Score: {coherence_lda:.4f}')
        return coherence_lda

    def display_topics(self, lda_model, num_words=5):
        """Prints the top words for each topic."""
        if not lda_model:
            raise ValueError('LDA model not provided for display.')

        self.logger.info('\nTop topics and their keywords:')
        for idx, topic in lda_model.print_topics(num_words=num_words):
            words = [word.split('*')[1].strip().replace('"', '') for word in topic.split('+')]
            self.logger.info(f'Topic {idx}: {", ".join(words)}')

    def visualize_topics(self, lda_model, output_html_path):
        """Generates an interactive visualization of the topics using pyLDAvis."""
        if not lda_model or not self.corpus or not self.dictionary:
            raise ValueError('LDA model, corpus, or dictionary not available for visualization.')

        self.logger.info(f'Attempting to generate pyLDAvis visualization to {output_html_path}...')

        try:
            # Ensure topic-term distributions (expElogbeta) are real-valued
            topic_term_dists = lda_model.expElogbeta
            if np.iscomplexobj(topic_term_dists):
                self.logger.warning(
                    'Complex numbers detected in topic-term distributions (expElogbeta). Converting to real part for visualization.'
                )
                topic_term_dists = np.real(topic_term_dists)

            # Ensure document-topic distributions are real-valued
            doc_topic_dists = np.array([[y for x, y in lda_model[doc]] for doc in self.corpus])
            if np.iscomplexobj(doc_topic_dists):
                self.logger.warning(
                    'Complex numbers detected in document-topic distributions. Converting to real part for visualization.'
                )
                doc_topic_dists = np.real(doc_topic_dists)

            # Extract vocabulary and term frequencies
            vocab = list(self.dictionary.values())
            doc_lengths = [
                sum(cnt for _, cnt in doc) for doc in self.corpus
            ]  # Sum of word counts per document
            term_frequency = [
                self.dictionary.cfs.get(i, 0) for i in range(len(self.dictionary))
            ]  # Total frequency of each term in the corpus

            # Use pyLDAvis.prepare directly with explicitly controlled inputs
            vis = pyLDAvis.prepare(
                topic_term_dists=topic_term_dists,
                doc_topic_dists=doc_topic_dists,
                doc_lengths=doc_lengths,
                vocab=vocab,
                term_frequency=term_frequency,
            )

            pyLDAvis.save_html(vis, str(output_html_path))
            self.logger.info(
                'pyLDAvis visualization saved successfully. Open the HTML file in your browser to view.'
            )

        except Exception as e:
            # The mapping to real-valued distributions still is a hack and I'm not sure why it remains
            # looks like something under the hood in pyLDAvis, though it is just visualisation sugar
            # do not really affect the results, so instead of panicking will just continue to the next
            # TODO: FIXME
            self.logger.error(
                f'Failed to generate or save pyLDAvis visualization for {self.cluster_name}: {e}. '
                'This is likely a visualization-specific issue and may not affect core topic modeling results.'
            )
            print(
                f'[bold red]Warning: Failed to save pyLDAvis visualization for {self.cluster_name}: {e}[/bold red]'
            )

    def random_search_hyperparameters(
        self, topic_range=(2, 15), passes_range=(50, 200), num_evaluations=10, iterations=50
    ):
        """
        Performs a random search to find optimal LDA hyperparameters.
        Includes a dedicated progress bar for the search evaluations.
        """
        if not self.corpus or not self.dictionary or not self.processed_docs:
            raise ValueError(
                'Data not prepared. Call prepare_data() first before tuning hyperparameters.'
            )

        results = []
        best_coherence = -1.0
        optimal_num_topics = None
        optimal_passes = None

        self.logger.info(
            f'\nStarting random search for hyperparameters ({num_evaluations} evaluations)...'
        )
        self.logger.info(f'  Topic range: {topic_range}, Passes range: {passes_range}')

        if self.progress_tracker:
            search_task_id = self.progress_tracker.add_task(
                f'[cyan]Searching for optimal HPs for {self.cluster_name}',
                total=num_evaluations,
                parent=self.progress_tracker.tasks[0].id,
            )

        for i in range(num_evaluations):
            num_topics_k = random.randint(topic_range[0], topic_range[1])
            num_passes_p = random.randint(passes_range[0], passes_range[1])

            self.logger.info(
                f'  Evaluation {i + 1}/{num_evaluations}: Testing Topics={num_topics_k}, Passes={num_passes_p}'
            )

            current_lda_model = self.train_lda_model(num_topics_k, num_passes_p, iterations)
            coherence = self.evaluate_model_coherence(current_lda_model)

            result_entry = {
                'num_topics': num_topics_k,
                'passes': num_passes_p,
                'coherence': coherence,
            }
            results.append(result_entry)
            self.logger.info(
                f'  Result: Topics={num_topics_k}, Passes={num_passes_p}, Coherence={coherence:.4f}'
            )

            if coherence > best_coherence:
                best_coherence = coherence
                optimal_num_topics = num_topics_k
                optimal_passes = num_passes_p

            if self.progress_tracker:
                self.progress_tracker.update(search_task_id, advance=1)

        if self.progress_tracker:
            self.progress_tracker.remove_task(search_task_id)

        self.logger.info('\n--- Random Search Tuning Results ---')
        for res in results:
            self.logger.info(
                f'Topics: {res["num_topics"]}, Passes: {res["passes"]}, Coherence: {res["coherence"]:.4f}'
            )

        if optimal_num_topics is not None:
            self.logger.info(
                f'\nOptimal Hyperparameters Found: Topics={optimal_num_topics}, Passes={optimal_passes} (Coherence: {best_coherence:.4f})'
            )
        else:
            self.logger.warning('Could not determine optimal hyperparameters during random search.')

        return optimal_num_topics, optimal_passes, best_coherence, results

    def plot_coherence_results(self, results, plot_name_prefix='coherence'):
        """
        Generates and saves plots of coherence scores against number of topics and passes.
        """
        if not results:
            self.logger.warning('No results available for plotting coherence.')
            return

        self.plot_output_dir.mkdir(parents=True, exist_ok=True)

        topics = [res['num_topics'] for res in results]
        passes = [res['passes'] for res in results]
        coherence_scores = [res['coherence'] for res in results]

        optimal_idx = np.argmax(coherence_scores)
        optimal_topics = topics[optimal_idx]
        optimal_passes = passes[optimal_idx]
        max_coherence = coherence_scores[optimal_idx]

        # Plot 1: Coherence vs. Number of Topics
        plt.figure(figsize=(10, 6))
        plt.scatter(topics, coherence_scores, alpha=0.6, label='Evaluations')
        plt.plot(
            optimal_topics,
            max_coherence,
            'ro',
            markersize=10,
            label=f'Optimal ({optimal_topics} topics, {max_coherence:.4f})',
        )
        plt.title(f'Coherence vs. Number of Topics for {self.cluster_name}')
        plt.xlabel('Number of Topics')
        plt.ylabel('Coherence Score (c_v)')
        plt.grid(True)
        plt.legend()
        plt.xticks(sorted(list(set(topics))))
        plot_path_topics = (
            self.plot_output_dir / f'{self.cluster_name}_{plot_name_prefix}_topics.png'
        )
        plt.savefig(plot_path_topics)
        plt.close()
        self.logger.info(f'Coherence vs. Topics plot saved to: {plot_path_topics}')

        # Plot 2: Coherence vs. Number of Passes
        plt.figure(figsize=(10, 6))
        plt.scatter(passes, coherence_scores, alpha=0.6, label='Evaluations')
        plt.plot(
            optimal_passes,
            max_coherence,
            'ro',
            markersize=10,
            label=f'Optimal ({optimal_passes} passes, {max_coherence:.4f})',
        )
        plt.title(f'Coherence vs. Number of Passes for {self.cluster_name}')
        plt.xlabel('Number of Passes')
        plt.ylabel('Coherence Score (c_v)')
        plt.grid(True)
        plt.legend()
        plt.xticks(sorted(list(set(passes))))
        plot_path_passes = (
            self.plot_output_dir / f'{self.cluster_name}_{plot_name_prefix}_passes.png'
        )
        plt.savefig(plot_path_passes)
        plt.close()
        self.logger.info(f'Coherence vs. Passes plot saved to: {plot_path_passes}')

    def save_topics_to_txt(self, lda_model, output_txt_path, num_words=10):
        """
        Saves the resulting topics and their top words to a plain text file in a table format.

        Args:
            lda_model: The trained LDA model.
            output_txt_path (Path): The file path to save the text output.
            num_words (int): The number of top words to include for each topic.
        """
        if not lda_model:
            self.logger.warning('No LDA model provided to save topics.')
            return

        self.log_output_dir.mkdir(parents=True, exist_ok=True)

        try:
            with open(output_txt_path, 'w', encoding='utf-8') as f:
                f.write(f'--- Topic Modeling Results for Cluster: {self.cluster_name} ---\n\n')
                f.write(f'Optimal Number of Topics: {lda_model.num_topics}\n')
                f.write(f'Optimal Passes: {lda_model.passes}\n\n')

                f.write(
                    f'{"Topic ID":<10} | {"Coherence Score":<20} | {"Top Words (and Weights)":<80}\n'
                )
                f.write('-' * 115 + '\n')

                final_coherence = self.evaluate_model_coherence(lda_model)
                if final_coherence is None:
                    final_coherence_str = 'N/A'
                else:
                    final_coherence_str = f'{final_coherence:.4f}'

                for idx, topic_words_str in lda_model.print_topics(num_words=num_words):
                    words_with_weights = []
                    for term_weight_pair in topic_words_str.split('+'):
                        weight, term = term_weight_pair.strip().split('*')
                        clean_term = term.strip().replace('"', '')
                        formatted_term_weight = f'{clean_term} ({float(weight):.3f})'
                        words_with_weights.append(formatted_term_weight)
                    f.write(
                        f'{idx:<10} | {final_coherence_str:<20} | {", ".join(words_with_weights)}\n'
                    )

            self.logger.info(f'Topics table saved to: {output_txt_path}')
            print(f'[bold green]Topics table saved to: {output_txt_path}[/bold green]')
        except IOError as e:
            self.logger.error(f'Error saving topics to text file {output_txt_path}: {e}')
            print(f'[bold red]Error saving topics table: {e}[/bold red]')
