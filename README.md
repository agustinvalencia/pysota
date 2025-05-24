# Pending tasks

## todo

- [ ]

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
