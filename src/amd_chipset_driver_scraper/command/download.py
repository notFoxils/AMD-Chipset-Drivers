import os
import sys
from pathlib import Path
from urllib.parse import urlparse
from typing import Annotated, Final

import bs4
import typer
import requests

from amd_chipset_driver_scraper.util import DriverVersion
from amd_chipset_driver_scraper.util.config import Config, init_config
from amd_chipset_driver_scraper.util.parsing import get_html_page_elements, parse_anchor_link, parse_driver_version

BASE_DIR: Final[Path] = Path(__file__).parent.parent.parent.parent.resolve(True)

DEFAULT_CONFIG_PATH: Final[Path] = BASE_DIR.joinpath("scrape_config.toml")
DEFAULT_OUTPUT_DIR: Final[Path] = BASE_DIR.joinpath("output")

DEFAULT_DRIVER_VERSION: DriverVersion = DriverVersion(tuple([0]))

app: typer.Typer = typer.Typer()


@app.command()
def download(
    config_path:
        Annotated[Path, typer.Option(exists=True, dir_okay=False, resolve_path=True)] = DEFAULT_CONFIG_PATH,
    output_dir:
        Annotated[Path, typer.Option(file_okay=False, writable=True, resolve_path=True)] = DEFAULT_OUTPUT_DIR,
    previous_driver_version:
        Annotated[DriverVersion, typer.Option(parser=DriverVersion.typer_parse)] = DEFAULT_DRIVER_VERSION
):
    # parse config : Done
    # Check if driver-version is newer:
    #   get previous version from args : Done
    #   get potentially new version from website scrape : Done
    #   compare all numbers between '.'s : Done
    #   If not newer proceed to: Done
    #       print-message
    #       exit
    #   If new proceed to: TODO
    #       creating output-folder
    #       downloading driver
    #       downloading release notes
    #       creating hash-files for downloads
    #       send version, downloads, and download-hashes to output-folder
    #       exit
    # Workflow continues: TODO
    #   Check if output folder has files/exists: TODO
    #       If folder does not exist: TODO
    #           stop workflow
    #       If folder does exist: TODO
    #           continue to making new release

    # TODO: Revisit config; parse into a dataclass instead of a dict[str, Any]
    config: Config = init_config(config_path)

    driver_download_page_elements: bs4.BeautifulSoup = get_html_page_elements(
        str(config.get('driver_download_page_url')),
        dict(config.get('driver_download_page_headers', {})),  # pyright: ignore[reportAny]
    )

    driver_version: DriverVersion = parse_driver_version(
        driver_download_page_elements,
        str(config.get('driver_version_paragraph_selector')),
    )

    if driver_version <= previous_driver_version:
        print(
            f"The scrapable driver ({driver_version}) is " +
            ("older than " if driver_version < previous_driver_version else "equal to ") +
            f"the previous version ({previous_driver_version})."
        )
        print("If you want to scrape this driver remove the 'previous-driver-version' option and try again.")
        sys.exit()

    output_dir.mkdir(exist_ok=True)

    driver_download_link: str = parse_anchor_link(
        driver_download_page_elements,
        str(config.get('driver_download_anchor_selector')),
    )

    driver_release_notes_page_link: str = parse_anchor_link(
        driver_download_page_elements,
        str(config.get('driver_release_notes_page_anchor_selector')),
    )

    #! this download logic is definitely not the way you want it so please change it
    #! i probably shouldnt have even added this

    def download(url: str, headers, output_path: Path) -> None:
        response = requests.get(
            url=url,
            headers=headers,
            stream=True
        )

        with open(output_path, 'wb') as file:
            chunk: bytes | None
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)

    download(
        url=driver_download_link,
        headers=config.get('driver_download_page_headers', {}),
        output_path=(output_dir / os.path.basename(urlparse(driver_download_link).path))
    )

    download(
        url=driver_release_notes_page_link,
        headers=config.get('driver_release_notes_page_headers', {}),
        output_path=(output_dir / os.path.basename(urlparse(driver_release_notes_page_link).path))
    )
