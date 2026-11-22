---
name: clua
description: Work in a Clua workspace through the `clua` command-line tool. Use when the user asks to read, create or change tasks, projects, companies, contacts, deals, time entries, calendar events, knowledge articles or other Clua data, or to read anything from their Clua workspace.
---

# Clua CLI

`clua` calls the Clua API for the workspace the user signed in to. Every
product module is a command group (`clua tasks …`, `clua time-entries …`)
whose commands mirror the API one to one.

## Rules

- Pass `--json` to every command. Data goes to stdout as one JSON document; a
  failure is one JSON object on stderr and a non-zero exit code. Never parse
  the human output.
- A command that changes data refuses to run without `--yes` outside a
  terminal. Before the first change, show the user what you will do; run the
  same command with `--dry-run` to print the request without sending it.
- Never guess a command or option. Ask the CLI:
  - `clua describe` lists the modules and their commands,
  - `clua describe <module>` lists one module's commands,
  - `clua describe <module> <command>` prints arguments, options, the
    request schema, required fields and an example command line.
- A list that pages takes `--all` and then prints `{"items": […], "total": n}`;
  add `--max-items N` to stop early. Without `--all` you get one page.
- A field whose value is JSON, or a whole body, can be passed as a file with
  `--input body.json` (or `--input -` for stdin) instead of single options.
- A command that returns a file (an export, an attachment) needs
  `--output <path>`; with `--json` it reports where the file went.
- `clua.nulara.de` runs without a language model. `clua agent run` and the
  `agents`, `skills` and `threads` commands answer 404 there; you are the
  model, so use the typed commands.

## Sign in

Check first: `clua doctor --json`. Exit 0 means ready. Exit 3 means the user
has to sign in; ask them to run `clua login` themselves (it opens a browser
for their consent). In CI the environment variable `CLUA_API_TOKEN` holds an
API key instead. `clua workspace use <name>` switches between workspaces the
user signed in to; `--workspace <name>` overrides it for one command.

## Exit codes

| Exit | `error`                | What to do                                                 |
| ---- | ---------------------- | ---------------------------------------------------------- |
| 0    |                        | Success                                                    |
| 1    | `runtime_error`        | Read `message`; often a missing `--yes`                    |
| 2    | `configuration_error`  | Configuration or workspace selection is wrong              |
| 3    | `authentication_error` | Ask the user to run `clua login`                           |
| 4    | `authorization_error`  | The user or key lacks the right; tell the user             |
| 5    | `api_error`            | The API refused; `code` names why, `detail` has the fields |
| 9    | `usage_error`          | The command line was wrong; check `describe`               |
| 10   | `network_error`        | The API was unreachable; retry later                       |
| 11   | `rate_limit_error`     | Wait `retry_after` seconds, then retry                     |

Reads are retried on network errors and server errors already, and every
request on a rate limit, so do not wrap commands in your own retry loop.
A 422 `api_error` lists the invalid fields in `detail`; fix them and send the
command again.

## Common work

```console
clua tasks list --all --json
clua tasks create --title "Angebot nachfassen" --project-id <project-id> --yes --json
clua time-entries start-timer --dry-run --json
clua time-entries get-timesheet --week-start 2026-11-23 --json
clua companies list --search "<name>" --json
clua deals list --all --json
```

Check every option with `clua describe <module> <command>` before the first
call; the examples above only show the shape.
