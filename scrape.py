#!/usr/bin/env python3
import hashlib
from pathlib import Path
import sys
import tomllib
from typing import Any, Final

import bs4
import requests

BASE_DIR: Final[Path] = Path(__file__).parent.resolve(True)

CONFIG_PATH: Final[Path] = BASE_DIR.joinpath("scrape_config.toml")

Config = dict[str, Any] # pyright: ignore[reportExplicitAny]
Headers = dict[str, str]
PageElements = bs4.BeautifulSoup
Url = str

def init_config() -> Config:
    # Probably should de-serialize into an actual dataclass.
    #   Would be better than just using random keys
    config: Final[Config];

    with open(CONFIG_PATH, "r+b") as config_bytes:
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

def parse_anchor_link(page_elements: bs4.BeautifulSoup, anchor_selector: str) -> str:
    selected_anchor: (bs4.Tag | None) = page_elements.select_one(anchor_selector)

    if selected_anchor is None:
        print('big bad')
        sys.exit(2)

    anchor_href = selected_anchor.attrs.get('href')

    if anchor_href is None:
        print('big bad')
        sys.exit(3)

    return str(anchor_href)

def main():
    config: Config = init_config()

    driver_download_page_elements: PageElements = get_html_page_elements(
        str(config.get('driver_download_page_url')),
        dict(config.get('driver_download_page_headers', {})), # pyright: ignore[reportAny]
    )
    driver_download_link: str = parse_anchor_link(
        driver_download_page_elements,
        str(config.get('driver_download_anchor_selector'))
    )

    # Check if driver-version is newer:
    #   get previous version from args
    #   get potentially new version from website scrape
    #   compare all numbers between '.'s
    #   If not-new proceed to:
    #       print-message
    #       exit
    #   If new proceed to:
    #       downloading driver
    #       downloading release notes
    #       creating hash-files for downloads
    #       outputting version, downloads, and download-hashes to .gitignored output-folder
    #       exit
    # Workflow continues:
    #   Check if output folder has files/exists:
    #   If folder does not exist:
    #       stop workflow
    #   If folder does exist
    #       continue to making new release

    driver_release_notes_page_link: str = parse_anchor_link(
        driver_download_page_elements,
        str(config.get('driver_release_notes_page_anchor_selector'))
    )

    print(driver_download_link)
    print(driver_release_notes_page_link)

if __name__ == "__main__":
    main()
