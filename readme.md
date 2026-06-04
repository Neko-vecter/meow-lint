# Meow Lint

## Exampe

### Github Actions

```yml
name: Lint Workflow

on:
  pull_request:
    branches: [ "main" ]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      # checkout repo
      - uses: actions/checkout@v6

      # run lint
      - name: Run Meow Linter
        uses: Neko-vecter/meow-lint@v1.0.1
        with:
          github_token: ${{ github.token }}
```

### CLI

```shell
python3 <path_to>/src/content_lint.py -i "<path_to>/file1.mdx" "<path_to>/file2.mdx"
```

## TODO

- [x] add multi file input
- [ ] add custom checker support for action workflow
