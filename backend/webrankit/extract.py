from __future__ import annotations

import json
import logging
import re
from typing import Dict, List, Sequence

import requests
from bs4 import BeautifulSoup

from .constants import EXTERNAL_API_CONNECT_TIMEOUT, EXTERNAL_API_READ_TIMEOUT

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = (EXTERNAL_API_CONNECT_TIMEOUT, EXTERNAL_API_READ_TIMEOUT)
SESSION = requests.Session()


def extract_items_from_anilist(username: str, statuses: Sequence[str]) -> List[Dict]:
    query = """
    query ($username: String, $statuses: [MediaListStatus]) {
      MediaListCollection(userName: $username, status_in: $statuses, type: ANIME) {
        lists {
          status
          entries {
            id
            score
            media {
              title { userPreferred }
              coverImage { extraLarge color }
            }
          }
        }
      }
    }
    """

    variables = {
        "username": username,
        "statuses": list(statuses),
    }
    url = "https://graphql.anilist.co"

    try:
        response = SESSION.post(
            url, json={"query": query, "variables": variables}, timeout=DEFAULT_TIMEOUT
        )
        response.raise_for_status()
    except requests.Timeout as e:
        logger.error(f"AniList request timed out for user '{username}': {e}")
        return []
    except requests.HTTPError as e:
        logger.error(f"AniList HTTP error for user '{username}': {e} - Response: {response.text[:200]}")
        return []
    except requests.RequestException as e:
        logger.error(f"AniList request failed for user '{username}': {e}")
        return []

    try:
        data = response.json()
        logger.info(f"Successfully fetched {len(data.get('data', {}).get('MediaListCollection', {}).get('lists', []))} lists from AniList for user '{username}'")
    except ValueError as e:
        logger.error(f"Failed to parse AniList response as JSON: {e}")
        return []

    lists = data.get("data", {}).get("MediaListCollection", {}).get("lists", [])
    entries = [entry for medialist in lists for entry in medialist.get("entries", [])]
    return entries


def extract_items_from_steam(steam_id: str) -> List[Dict[str, str]]:
    url = f"https://steamcommunity.com/id/{steam_id}/games/?tab=all&sort=playtime"
    try:
        response = SESSION.get(url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
    except requests.Timeout as e:
        logger.error(f"Steam request timed out for user '{steam_id}': {e}")
        return []
    except requests.HTTPError as e:
        logger.error(f"Steam HTTP error for user '{steam_id}': {e}")
        return []
    except requests.RequestException as e:
        logger.error(f"Steam request failed for user '{steam_id}': {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    script_pattern = re.compile(r"var rgGames = (.*);")
    games_payload = ""

    for script in soup.find_all("script"):
        match = script_pattern.search(str(script))
        if match:
            games_payload = match.group(1)
            break

    if not games_payload:
        logger.warning(f"No games data found in Steam profile for '{steam_id}'")
        return []

    try:
        apps = json.loads(games_payload)
        logger.info(f"Successfully fetched {len(apps)} games from Steam for user '{steam_id}'")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Steam games data: {e}")
        return []

    result: List[Dict[str, str]] = []
    for app in apps:
        try:
            result.append(
                {
                    "label": app["name"],
                    "img_url": app["logo"].replace("capsule_184x69", "header"),
                }
            )
        except KeyError as e:
            logger.warning(f"Missing required field in Steam game data: {e} - Skipping game")
            continue

    logger.info(f"Extracted {len(result)} valid games from Steam for '{steam_id}'")
    return result


__all__ = ["extract_items_from_anilist", "extract_items_from_steam"]
