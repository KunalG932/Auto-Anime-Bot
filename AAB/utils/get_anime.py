# Licensed under GNU General Public License
# Copyright (C) 2024  Dhruv-Tara

import requests
from lxml import etree
from typing import Dict, List, Optional, TypedDict
from AAB import LOG

URL = "http://subsplease.org/rss"

class AnimeItem(TypedDict):
    name: str
    magnet: List[str]
    hash: List[str]
    quality: List[str]
    title: List[str]

class AnimeResult(TypedDict):
    array: List[AnimeItem]
    hash: str

def get_anime(hash: str, to_add: int) -> Optional[AnimeResult]:
    """
    Fetch and process anime data from the RSS feed.

    Args:
    hash (str): The hash to compare against for determining new entries.
    to_add (int): The maximum number of new entries to process.

    Returns:
    Optional[AnimeResult]: A dictionary containing the processed anime data and the newest hash,
                           or None if no new data is found or an error occurs.
    """
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        LOG.error(f"Failed to fetch data: {e}")
        return None

    try:
        root = etree.fromstring(response.content)
        items = root.xpath('//item')
    except etree.XMLSyntaxError as e:
        LOG.error(f"Failed to parse XML: {e}")
        return None

    array: List[AnimeItem] = []

    for item in items[:to_add]:
        current_hash = item.findtext('guid')
        if current_hash == hash:
            break

        name = item.findtext('category', '').split("-")[0]
        quality = item.findtext('category', '').split("-")[-1]
        
        new_item = {
            'name': name,
            'magnet': [item.findtext('link', '')],
            'hash': [current_hash],
            'quality': [quality],
            'title': [item.findtext('title', '')]
        }

        if array and array[-1]['name'] == name:
            for key in ['magnet', 'hash', 'quality', 'title']:
                array[-1][key].append(new_item[key][0])
        else:
            array.append(new_item)

    if not array:
        return None

    return {'array': array, 'hash': array[0]['hash'][0]}
