"""What this package adds to the core: Clua's identity, manifest and skill."""

import json
import shlex
from importlib.metadata import version

import pytest
from xiii_cli_core.config import Surface
from xiii_cli_core.direct import load_manifest
from xiii_cli_core.main import build_app

import clua
from clua import PRODUCT


def test_the_product_names_clua_and_its_production_api() -> None:
    assert PRODUCT.name == "clua"
    assert PRODUCT.display_name == "Clua"
    assert PRODUCT.api_url == "https://api.clua.nulara.de/v1/app"
    assert PRODUCT.oauth_client_id == "clua-cli"
    assert PRODUCT.version == version("clua")


def test_main_runs_the_customer_surface(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[object] = []
    monkeypatch.setattr(clua, "run", calls.append)
    clua.main()
    monkeypatch.setattr(clua, "build_app", lambda *args: args)
    assert calls[0]() == (PRODUCT, Surface.CUSTOMER)  # type: ignore[operator]


def test_the_generated_manifest_registers_every_product_module() -> None:
    manifest = load_manifest(PRODUCT)
    assert manifest["product"] == "clua"
    assert manifest["module_count"] == len(manifest["modules"]) > 1
    operations = [
        operation
        for module in manifest["modules"]
        for operation in module["operations"]
    ]
    assert manifest["operation_count"] == len(operations)
    # The streaming routes belong to the thread protocol, never to the
    # generated one-response commands.
    excluded_streams = manifest["excluded_event_stream_operations"]
    assert {
        (operation["operation_id"], operation["method"], operation["path"])
        for operation in excluded_streams
    } == {
        ("chat_with_agent", "POST", "/threads/chat"),
        ("attach_thread_run", "GET", "/threads/{thread_id}/attach"),
        ("resume_agent_execution", "POST", "/threads/{thread_id}/resume"),
        ("start_thread_run", "POST", "/threads/{thread_id}/runs"),
        ("retry_thread_run", "POST", "/threads/{thread_id}/runs/retry"),
    }
    assert not {operation["operation_id"] for operation in excluded_streams} & {
        operation["operation_id"] for operation in operations
    }
    assert all(
        operation["dangerous"] == (operation["method"] not in {"GET", "HEAD"})
        for operation in operations
    )


def _skill() -> str:
    assert PRODUCT.skill is not None
    return PRODUCT.skill.read_text(encoding="utf-8")


def test_the_skill_names_itself_and_the_commands_it_teaches() -> None:
    skill = _skill()
    assert skill.startswith("---\nname: clua\ndescription: ")
    for command in ("clua describe", "--all", "--dry-run", "clua doctor"):
        assert command in skill


def _skill_examples() -> list[list[str]]:
    block = _skill().split("## Common work", 1)[1].split("```console\n", 1)[1]
    return [shlex.split(line) for line in block.split("```", 1)[0].splitlines()]


@pytest.mark.parametrize("example", _skill_examples(), ids=" ".join)
def test_every_skill_example_runs_against_the_manifest(
    example: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    # Placeholders stand for ids. A change runs as a dry run, which checks the
    # body against the schema without a token; a read only has to parse.
    tokens = [
        "00000000-0000-4000-8000-000000000001" if token.startswith("<") else token
        for token in example[1:]
    ]
    assert example[0] == "clua"
    app = build_app(PRODUCT, Surface.CUSTOMER)
    if "--yes" in tokens or "--dry-run" in tokens:
        tokens = [token for token in tokens if token != "--yes"]
        if "--dry-run" not in tokens:
            tokens.append("--dry-run")
        with pytest.raises(SystemExit) as result:
            app(tokens, exit_on_error=False)
        assert result.value.code == 0
        assert json.loads(capsys.readouterr().out)["operation_id"]
    else:
        command, bound, _ignored = app.parse_args(tokens, exit_on_error=False)
        assert callable(command)
        assert bound is not None
