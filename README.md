# Pending tasks

## todo

- [x] search
- [x] create db-build
- [x] create clusters

  - [x] load db from persistence
  - [x] create clusters
  - [x] write clusters to persistence

- [ ] define topics from clusters

# Steps

## Help

```
> uv run pysota --help

Usage: pysota [OPTIONS] COMMAND [ARGS]...

╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --debug                       Enable debug mode (requires debugpy)           │
│ --install-completion          Install completion for the current shell.      │
│ --show-completion             Show completion for the current shell, to copy │
│                               it or customize the installation.              │
│ --help                        Show this message and exit.                    │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ search                                                                       │
│ clean                                                                        │
│ db                                                                           │
│ cluster                                                                      │
│ version                                                                      │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## Searching

### Help

```
uv run pysota search  --help

 Usage: pysota search [OPTIONS] INCLUDE...

 Use the subscribed clients to search a query

╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    include      INCLUDE...  [default: None] [required]                     │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ *  --name                       TEXT     [default: None] [required]          │
│    --exclude    -x              TEXT                                         │
│    --save       -s                                                           │
│    --dir                        PATH     [default: results/raw]              │
│    --num-items  -n              INTEGER  [default: 10]                       │
│    --offset                     INTEGER  [default: 0]                        │
│    --all            --no-all             [default: no-all]                   │
│    --help                                Show this message and exit.         │
╰──────────────────────────────────────────────────────────────────────────────╯
```

Test command

```shell
uv run pysota search reinforcement learning --name rl -n 100 --save
```

## Building a database

```
 uv run pysota db-build -q rl --name rl-db
```

## Clustering

```
uv run pysota cluster --help

 Usage: pysota cluster [OPTIONS]

 Build clusters from a results database

╭─ Options ───────────────────────────────────────────────────────────────────────────────╮
│ *  --db          PATH  Folder to store the DB [default: None] [required]                │
│    --dir         PATH  [default: results/clusters]                                      │
│    --help              Show this message and exit.                                      │
╰─────────────────────────────────────────────────────────────────────────────────────────╯
```

Test command

```
uv run pysota cluster --db results/db/rl --dir results/clusters/rl
```
