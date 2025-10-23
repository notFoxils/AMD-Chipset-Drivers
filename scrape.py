#!/usr/bin/env python3
from dataclasses import dataclass
from functools import total_ordering
import os
from pathlib import Path
import sys
import tomllib
from typing import Annotated, Any, Final, Self, final, override

import bs4
import requests
import typer

Config = dict[str, Any] # pyright: ignore[reportExplicitAny]
Headers = dict[str, str]
PageElements = bs4.BeautifulSoup
Url = str

@final
@dataclass
@total_ordering
class DriverVersion:
    version_elements: Final[tuple[int, ...]]

    def __init__(self, version_elements: tuple[int, ...]) -> None:
        self.version_elements = version_elements

    def __gt__(self, other: Self) -> bool:
        self_num_elements: Final[int] = len(self.version_elements)
        less_specific_driver_version_num_elements: Final[int] = min(self_num_elements, len(other.version_elements))

        for version_element_index in range(less_specific_driver_version_num_elements):
            if self.version_elements[version_element_index] == other.version_elements[version_element_index]:
                continue
                    
                # If (element of self) is greater than (element of other), return true
            return self.version_elements[version_element_index] > other.version_elements[version_element_index]
                
        # If self is more specific, return true
        return self_num_elements > less_specific_driver_version_num_elements

    @override
    def __str__(self) -> str:
        return str.join(
            ".",
            map(str, self.version_elements)
        )

    @staticmethod
    def from_string(string: str) -> '(DriverVersion | None)':
        try:
            return DriverVersion(tuple(
                map(int, string.split('.'))
            ))
        except ValueError:
            return None

BASE_DIR: Final[Path] = Path(__file__).parent.resolve(True)

DEFAULT_OUTPUT_DIR: Final[Path] = BASE_DIR.joinpath("output")
DEFAULT_CONFIG_PATH: Final[Path] = BASE_DIR.joinpath("scrape_config.toml")

DEFAULT_DRIVER_VERSION: Final[DriverVersion] = DriverVersion(tuple([0]))

def init_config(config_path: Path) -> Config:
    config: Final[Config];

    with open(config_path, "r+b") as config_bytes:
        config = tomllib.load(config_bytes)

    return config

def get_html_page_elements(page_url: Url, headers: Headers) -> PageElements:
    driver_page_response: requests.Response = requests.get(
        url=page_url,
        headers=headers,
    )

    if driver_page_response.status_code != 200:
        print('big bad')
        sys.exit(1)

    return bs4.BeautifulSoup(
        markup=driver_page_response.content,
        features='html.parser',
    )

def parse_driver_version(page_elements: bs4.BeautifulSoup, driver_version_paragraph_selector: str) -> DriverVersion:
    selected_paragraph: (bs4.Tag | None) = page_elements.select_one(driver_version_paragraph_selector)

    if selected_paragraph is None:
        print('big bad')
        sys.exit(2)

    driver_version = DriverVersion.from_string(
        selected_paragraph.decode_contents()
    )

    if driver_version is None:
        print('big bad')
        sys.exit(3)

    return driver_version

def parse_anchor_link(page_elements: bs4.BeautifulSoup, anchor_selector: str) -> Url:
    selected_anchor: (bs4.Tag | None) = page_elements.select_one(anchor_selector)

    if selected_anchor is None:
        print('big bad')
        sys.exit(4)

    anchor_href = selected_anchor.attrs.get('href')

    if anchor_href is None:
        print('big bad')
        sys.exit(5)

    return str(anchor_href)

def main(
    config_path:
        Annotated[Path, typer.Option(exists=True, dir_okay=False, resolve_path=True)] = DEFAULT_CONFIG_PATH,
    output_dir: 
        Annotated[Path, typer.Option(file_okay=False, writable=True, resolve_path=True)] = DEFAULT_OUTPUT_DIR,
    previous_driver_version:
        Annotated[(DriverVersion | None), typer.Option(parser=DriverVersion.from_string)] = None
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
    #       create output-folder
    #       downloading driver
    #       downloading release notes
    #       creating hash-files for downloads
    #       send version, downloads, download-hashes, and release-notes to output-folder
    #       exit
    # Workflow continues: TODO
    #   Check if output folder has files/exists: TODO
    #       If folder does not exist: TODO
    #           stop workflow
    #       If folder does exist: TODO
    #           continue to making new release

    # TODO: Revisit config; parse into a dataclass instead of a dict[str, Any]
    config: Config = init_config(config_path)

    driver_download_page_elements: PageElements = get_html_page_elements(
        str(config.get('driver_download_page_url')),
        dict(config.get('driver_download_page_headers', {})), # pyright: ignore[reportAny]
    )

    driver_version: DriverVersion = parse_driver_version(
        driver_download_page_elements,
        str(config.get('driver_version_paragraph_selector')),
    )

    if (previous_driver_version is not None) and (driver_version <= previous_driver_version):
        print(
            f"The scrapable driver ({driver_version}) is " +
            ("older than " if driver_version < previous_driver_version else "equal to ") +
            f"the previous version ({previous_driver_version})."
        )
        print("If you want to scrape this driver remove the 'previous-driver-version' option and try again.")
        sys.exit()

    if not output_dir.exists():
        os.mkdir(output_dir)
    else:
        print(
            f"The output directory already exists{" as a file" if output_dir.is_file() else ""}; " +
            'remove it and try again.'
        )
        sys.exit()

    driver_download_link: str = parse_anchor_link(
        driver_download_page_elements,
        str(config.get('driver_download_anchor_selector')),
    )

    driver_release_notes_page_link: str = parse_anchor_link(
        driver_download_page_elements,
        str(config.get('driver_release_notes_page_anchor_selector')),
    )

    print(driver_download_link)
    print(driver_release_notes_page_link)

if __name__ == "__main__":
    typer.run(main)
