# Key Generator

_Generates keys and sends them to the key server_

## Development Setup

Copy the `.env.example` file to `.env` and modify the values with your own

Then start your dev-env with `docker-compose up -d`

## Commands
There are 3 ways to run the generator.
1. Without arguments - Daemon mode  
   In this mode, the geberator periodically creates new keys and uploads them.
2. `generate`  
   Using the `generate` command, the generator produces one new key, sends it to the api and then exist immediately again.
3. `upload`  
   Using the `upload` command, the generator tries to upload all failed keys in its queue file.

## Linting

The project is set up with [pre-commit](https://pre-commit.com/#install). For it to work, it needs to be outside docker.

To activate it for a project run:
```shell
pre-commit install
```

The next time you commit, it is going to lint and check your files. Sometimes you need to review the changes and do the commit again. If you want to commit without checks
```shell
git commit --no-verify
```