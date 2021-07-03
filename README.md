# Key Generator

## Development Setup

Copy the `.env.example` file to `.env` and modify the values with your own

Then start your dev-env with `docker-compose up -d`

### Linting

The project is set up with [pre-commit](https://pre-commit.com/#install). For it to work, it needs to be outside docker.

To activate it for a project run:
```shell
pre-commit install
```

The next time you commit, it is going to lint and check your files. Sometimes you need to review the changes and do the commit again. If you want to commit without checks
```shell
git commit --no-verify
```