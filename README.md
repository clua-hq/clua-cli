# Clua CLI

Command-line access to Clua: sign in, call the product modules and the API.

## Install

```console
uv tool install clua
```

The CLI needs Python 3.14; [uv](https://docs.astral.sh/uv/) downloads it when
the machine does not have it. With pipx, name the interpreter yourself:
`pipx install --python 3.14 clua`. Update with `uv tool upgrade clua`.
The CLI runs on macOS and Linux.

## Use

```console
clua login
clua doctor
clua tasks list --json
clua --help
```

The CLI talks to the production API (`https://api.clua.nulara.de/v1/app`)
unless `--api-url`, `CLUA_API_URL` or the nearest `.clua.toml`
(`api_url = "…"`) names another one.

`clua login` opens the browser for consent, or prints a code to approve on
another device when no browser can be opened here. It stores an hour-long token
and its refresh token in the operating-system keyring (service `clua-cli`) and
renews it automatically. For automation, set `CLUA_API_TOKEN` to a personal
access token from the app's API key settings instead. Which workspace a command
acts as is kept in `~/.config/clua/state.json` (`$XDG_CONFIG_HOME/clua/` when
that is set); the file holds no secrets.

`clua.nulara.de` runs without a language model, so `clua agent run` and the
`agents`, `skills` and `threads` commands answer 404 there.

## Claude Code

```console
clua claude-code install
```

installs a skill that teaches Claude Code the CLI: signing in, `--json`,
`--dry-run` and `--yes`, the exit codes, `--all` and `describe`. It goes to
`~/.claude/skills/clua/`; `--project` puts it into `.claude/skills/` of the
current directory instead. `clua claude-code show` prints it for other agents.

## Scripts and agents

Every command that prints data takes `--json` and then writes exactly one JSON
document to stdout. A failure writes one JSON object to stderr instead and
exits with a code that names the kind of failure:

| Exit | `error`                    | Meaning                                         |
| ---- | -------------------------- | ----------------------------------------------- |
| 0    |                            | Success                                         |
| 1    | `runtime_error`            | Local failure, e.g. a mutation without `--yes`  |
| 2    | `configuration_error`      | Configuration or workspace selection is invalid |
| 3    | `authentication_error`     | No token, or the API rejected it (401)          |
| 4    | `authorization_error`      | The token may not do this (403)                 |
| 5    | `api_error`                | Any other API error response                    |
| 7    | `thread_protocol_error`    | The agent stream broke its protocol             |
| 8    | `thread_expectation_error` | An agent run missed an expectation              |
| 9    | `usage_error`              | The command line did not parse                  |
| 10   | `network_error`            | The API could not be reached                    |
| 11   | `rate_limit_error`         | Still rate limited after the retries (429)      |

A command that changes data asks for confirmation; in a script pass `--yes`,
and `--dry-run` prints the request without sending it. `clua describe tasks
create` prints a command's arguments, options, request schema and an example
command line as JSON, without signing in.

## Layout

The product-neutral core is the package
[`xiii-cli-core`](https://github.com/xiii-hq/xiii-cli-core), which the
Nulara CLI shares: `clua` builds a `xiii_cli_core.config.Product` and hands
it to `xiii_cli_core.main.build_app`. `src/clua/spec.json` is the command
manifest, generated from the app API's OpenAPI document; it is never edited by
hand.

## Development

```console
uv sync --locked
uv run pytest --cov=clua
uv run ruff check && uv run ruff format --check && uv run pyright
```

A release is a GitHub release whose tag is `v<version>` from `pyproject.toml`;
`.github/workflows/publish.yml` builds, verifies and publishes it to PyPI with
an attestation.

## License

[Apache-2.0](LICENSE)
