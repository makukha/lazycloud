<!-- docsub: begin -->
<!-- docsub: help lazycloud -->
<!-- docsub: lines after 2 upto -1 -->
<!-- docsub: strip -->
```shell
$ lazycloud --help
Usage: lazycloud [OPTIONS] COMMAND [ARGS]...

Visual tag manager for cloud infrastructure.

╭─ Options ──────────────────────────────────────────────────────────╮
│ --help      Show this message and exit.                            │
╰────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────╮
│ aws     Manage Amazon Web Services resources.                      │
╰────────────────────────────────────────────────────────────────────╯
```
<!-- docsub: end -->

## Amazon Web Services

<!-- docsub: begin -->
<!-- docsub: help lazycloud aws -->
<!-- docsub: lines after 2 upto -1 -->
<!-- docsub: strip -->
```shell
$ lazycloud aws --help
Usage: lazycloud aws [OPTIONS] COMMAND [ARGS]...

Manage Amazon Web Services resources.

╭─ Options ──────────────────────────────────────────────────────────╮
│ --help      Show this message and exit.                            │
╰────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────╮
│ tag      Edit tags for AWS resources.                              │
╰────────────────────────────────────────────────────────────────────╯
```
<!-- docsub: end -->


### `aws tag`

<!-- docsub: begin -->
<!-- docsub: help lazycloud aws tag -->
<!-- docsub: lines after 2 upto -1 -->
<!-- docsub: strip -->
```shell
$ lazycloud aws tag --help
Usage: lazycloud aws tag [OPTIONS]

Edit tags for AWS resources.

╭─ Options ──────────────────────────────────────────────────────────╮
│ *  --tag       -t  TEXT  Tag "key=value" pair. [required]          │
│    --unset     -u  TEXT  When unchecked, set tag to this value     │
│                          instead of removing.                      │
│    --iam-user            Load "iam user" resources.                │
│    --iam-role            Load "iam role" resources.                │
│    --help                Show this message and exit.               │
╰────────────────────────────────────────────────────────────────────╯
```
<!-- docsub: end -->
