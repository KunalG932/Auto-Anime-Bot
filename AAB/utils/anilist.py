# Licensed under GNU General Public License
# Copyright (C) 2024  Dhruv-Tara
# Using Anilist for anime info

import requests
from typing import Dict, Optional
from AAB import LOG

URL = "https://graphql.anilist.co"

ANIME_QUERY = '''
query ($search: String) {
    Media (type: ANIME, search: $search) {
        title {
            english
            romaji
        }
        status
        coverImage {
            extraLarge
        }
    }
}
'''

def anime(anime_name: str) -> Optional[Dict[str, str]]:
    """
    Fetch anime information from Anilist GraphQL API.

    Args:
    anime_name (str): The name of the anime to search for.

    Returns:
    Optional[Dict[str, str]]: A dictionary containing the anime's image URL, name, and status,
                              or None if the anime is not found or an error occurs.
    """
    variables = {'search': anime_name}

    try:
        response = requests.post(
            URL,
            json={'query': ANIME_QUERY, 'variables': variables},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        LOG.error(f"Failed to fetch data from Anilist: {e}")
        return None

    try:
        media = data['data']['Media']
        return {
            "image": media['coverImage']['extraLarge'],
            "name": media['title']['english'] or media['title']['romaji'],
            "status": media['status']
        }
    except KeyError as e:
        LOG.error(f"Failed to parse Anilist response: {e}")
        return None
