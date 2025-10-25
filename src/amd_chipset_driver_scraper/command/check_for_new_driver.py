from typing import Annotated

import typer

from amd_chipset_driver_scraper.util import DriverVersion

DEFAULT_DRIVER_VERSION: DriverVersion = DriverVersion(tuple([0]))

app: typer.Typer = typer.Typer()


@app.command()
def check_for_new_driver(
    previous_driver_version:
        Annotated[DriverVersion, typer.Option(parser=DriverVersion.typer_parse)] = DEFAULT_DRIVER_VERSION
):
    print(f"previous: {previous_driver_version}")
