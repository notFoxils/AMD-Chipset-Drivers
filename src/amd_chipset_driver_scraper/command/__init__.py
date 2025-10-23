import typer

from .check_for_new_driver import app as check_for_new_driver_app
from .download import app as download_app

app: typer.Typer = typer.Typer()
app.add_typer(check_for_new_driver_app)
app.add_typer(download_app)

__all__ = [
    "app"
]
