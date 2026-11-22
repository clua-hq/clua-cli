from importlib.metadata import version
from importlib.resources import files

from xiii_cli_core.config import Product, Surface
from xiii_cli_core.main import build_app, run

PRODUCT = Product(
    name="clua",
    display_name="Clua",
    api_url="https://api.clua.nulara.de/v1/app",
    oauth_client_id="clua-cli",
    manifest=files(__name__).joinpath("spec.json"),
    version=version("clua"),
    skill=files(__name__).joinpath("skill/SKILL.md"),
)


def main() -> None:
    run(lambda: build_app(PRODUCT, Surface.CUSTOMER))


__all__ = ["PRODUCT", "main"]
