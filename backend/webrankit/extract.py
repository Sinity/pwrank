from __future__ import annotations

import json
import re
from typing import Dict, List, Sequence

import requests
from bs4 import BeautifulSoup

DEFAULT_TIMEOUT = (3.05, 10)  # (connect, read) seconds
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
    except requests.RequestException:
        return []

    data = response.json()
    lists = data.get("data", {}).get("MediaListCollection", {}).get("lists", [])
    entries = [entry for medialist in lists for entry in medialist.get("entries", [])]
    return entries


def extract_items_from_steam(steam_id: str) -> List[Dict[str, str]]:
    url = f"https://steamcommunity.com/id/{steam_id}/games/?tab=all&sort=playtime"
    try:
        response = SESSION.get(url, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException:
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
        return []

    apps = json.loads(games_payload)
    result: List[Dict[str, str]] = []
    for app in apps:
        result.append(
            {
                "label": app["name"],
                "img_url": app["logo"].replace("capsule_184x69", "header"),
            }
        )
    return result


__all__ = ["extract_items_from_anilist", "extract_items_from_steam"]
