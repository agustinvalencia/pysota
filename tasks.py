import os
import shutil
from invoke import task


def log_section(msg):
    """
    Log a section header to the console.
    """
    print(f"\n{'=' * len(msg)}\n{msg}\n{'=' * len(msg)}")


def log_action(msg):
    """
    Log an action to the console.
    """
    print(f"\n(task) > {msg}")


@task
def check(c):
    """
    Check the code style.
    """
    log_section("Checking code quality")
    log_action("Code style has been checked.")
    c.run("uvx ruff check", echo=True)
    log_action("Type checking")
    c.run("uvx mypy src", echo=True)


@task
def clean(c):
    """
    Recursively delete all __pycache__ directories under the src folder.
    """
    log_section("Cleaning up the project")
    targets = [
        ".venv",
        ".ruff_cache",
        ".uv_cache",
    ]
    for t in targets:
        if os.path.exists(t):
            shutil.rmtree(t)
            log_action(f"Deleted the {t} directory.")

    caches_list = ""
    src_dir = "src"
    for root, dirs, files in os.walk(src_dir):
        for d in dirs:
            if d == "__pycache__":
                path = os.path.join(root, d)
                caches_list += f"{path}\n"
                shutil.rmtree(path)
    if caches_list:
        log_action(f"Cleaned up the __pycache__ directories. : \n{caches_list}")

    log_action("uv clean")
    c.run("uv clean", echo=True)


@task
def install(c):
    """
    Install the required dependencies.
    """
    log_section("Installing dependencies")
    c.run("uv sync --force-reinstall", echo=True)
    log_action("Dependencies have been installed.")


@task
def test(c):
    """
    Run the test suite.
    """
    log_section("Running the simple test ")

    log_action("uv run main.py --query 'neutrino' --save results")
    c.run("uv run main.py --query 'neutrino' --save results", echo=True)

    log_action(
        "uv run main.py --query 'explainable reinforcement learning' --save results"
    )
    c.run(
        "uv run main.py --query 'explainable reinforcement learning' --save results",
        echo=True,
    )

    log_action("Tests have been run.")
