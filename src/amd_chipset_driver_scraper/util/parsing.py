import sys

import bs4
import requests

from amd_chipset_driver_scraper.util.config import Headers
from amd_chipset_driver_scraper.util.driver_version import DriverVersion

Url = str

def get_html_page_elements(page_url: Url, headers: Headers) -> bs4.BeautifulSoup:
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

