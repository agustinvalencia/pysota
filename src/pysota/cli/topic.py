import warnings
from pathlib import Path
from typing import Annotated

import typer
import yaml
from rich import print
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)
from typer import Typer

from pysota.core import Persistence
from pysota.process.topic_modeler import TopicModelingPipeline

warnings.filterwarnings('ignore')
app = Typer(no_args_is_help=True, invoke_without_command=True)
console = Console(stderr=True)
progress = Progress(
    SpinnerColumn(),
    TextColumn('[bold blue]{task.description}', justify='right'),
    BarColumn(),
    '[progress.percentage]{task.percentage:>3.1f}%',
    '•',
    TimeRemainingColumn(compact=True, elapsed_when_finished=True),
)


# fmt: off
@app.command(help='Model the topic for a collection of articles')
def topics(
    folder: Annotated[Path, typer.Option('--folder', '-f', help='Folder of the DB to cluster')],
    exc: Annotated[Path, typer.Option('--exclude', '-exc', help='Terms to exclude in topic modelling')],
    topic_min: Annotated[int, typer.Option('--topic-min', help='Min number of topics for random search')] = 2,
    topic_max: Annotated[int, typer.Option('--topic-max', help='Max number of topics for random search')] = 15,
    passes_min: Annotated[int, typer.Option('--passes-min', help='Min number of passes for random search')] = 50,
    passes_max: Annotated[int, typer.Option('--passes-max', help='Max number of passes for random search')] = 300,
    num_evals: Annotated[int, typer.Option('--num-evals', help='Number of random evaluations')] = 20,
    iterations: Annotated[int, typer.Option('--iterations', help='Iterations for LDA EM algorithm')] = 50,
    random_seed: Annotated[int, typer.Option('--seed', help='Random seed for reproducibility')] = 42,
):
# fmt: on
    try:
        with open(exc, 'r') as f:
            exc_terms = yaml.safe_load(f)
        exc_terms = exc_terms['terms']
    except FileNotFoundError:
        print(f'[bold red]Error: Exclude file not found at {exc}[/bold red]')
        return
    except yaml.YAMLError as e:
        print(f'[bold red]Error parsing exclude file {exc}: {e}[/bold red]')
        return

    base_output_dir = Path('results/topic_modeling_outputs')
    base_log_dir = base_output_dir / 'logs'
    base_plot_dir = base_output_dir / 'plots'
    base_log_dir.mkdir(parents=True, exist_ok=True)
    base_plot_dir.mkdir(parents=True, exist_ok=True)

    clus_folders = sorted(list(folder.glob('cluster_*')))
    if not clus_folders:
        print(f"[bold red]No 'cluster_*' folders found in {folder}[/bold red]")
        return

    with progress:
        task_id = progress.add_task('Analyzing Clusters', total=len(clus_folders))

        for clust_path in clus_folders:
            cluster_name = clust_path.name

            # Update the progress bar description for the current cluster
            progress.update(
                task_id, description=f'Analyzing [bold yellow]{cluster_name}[/bold yellow]'
            )

            print(f'\n[bold white]--- Processing Cluster: {cluster_name} ---[/bold white]')

            publs = Persistence.load_files(clust_path)
            abstracts = [pub.abstract for pub in publs]
            print(f'In {cluster_name} found {len(abstracts)} files')

            if not abstracts:
                print(f'[bold yellow]Skipping {cluster_name}: No abstracts found.[/bold yellow]')
                progress.advance(task_id)  # Advance even if skipped
                continue

            modeller = TopicModelingPipeline(
                random_state=random_seed,
                exclude_words=exc_terms,
                log_output_dir=base_log_dir,
                plot_output_dir=base_plot_dir,
                cluster_name=cluster_name,
            )

            modeller.prepare_data(abstracts)

            # Perform random search for optimal hyperparameters
            # TODO: add another nested progress bar here for random search evaluations
            optimal_topics, optimal_passes, best_coherence, search_results = (
                modeller.random_search_hyperparameters(
                    topic_range=(topic_min, topic_max),
                    passes_range=(passes_min, passes_max),
                    num_evaluations=num_evals,
                    iterations=iterations,
                )
            )
            modeller.plot_coherence_results(search_results, plot_name_prefix='random_search_coherence')

            # Train the final model with the optimal parameters found
            if optimal_topics and optimal_passes:
                print(
                    f'\n[bold green]Training final model for {cluster_name} with Optimal Topics={optimal_topics}, Passes={optimal_passes} (Coherence={best_coherence:.4f})[/bold green]'
                )

                final_lda_model = modeller.train_lda_model(optimal_topics, optimal_passes, iterations=iterations)

                modeller.evaluate_model_coherence(final_lda_model)
                modeller.display_topics(final_lda_model, num_words=5)
                modeller.visualize_topics(
                    final_lda_model,
                    output_html_path=base_plot_dir
                    / f'{cluster_name}_lda_visualization_optimal.html',
                )
                modeller.save_topics_to_txt(
                    final_lda_model,
                    output_txt_path=base_output_dir / f"{cluster_name}_topics_table.txt",
                    num_words=5
                )
            else:
                print(
                    f'[bold yellow]Could not determine optimal parameters for {cluster_name}. Skipping final model training and visualization.[/bold yellow]'
                )

            progress.advance(task_id)

    print(
        "\n[bold green]Topic modeling process complete for all clusters. Check 'results/topic_modeling_outputs' for logs and plots.[/bold green]"
    )
