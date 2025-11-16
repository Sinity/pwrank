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
    except requests.Timeout as e:
        print(f"AniList request timed out for user '{username}': {e}")
        return []
    except requests.HTTPError as e:
        print(f"AniList HTTP error for user '{username}': {e}")
        return []
    except requests.RequestException as e:
        print(f"AniList request failed for user '{username}': {e}")
        return []

    try:
        data = response.json()
    except ValueError as e:
        print(f"Failed to parse AniList response as JSON: {e}")
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
        print(f"Steam request timed out for user '{steam_id}': {e}")
        return []
    except requests.HTTPError as e:
        print(f"Steam HTTP error for user '{steam_id}': {e}")
        return []
    except requests.RequestException as e:
        print(f"Steam request failed for user '{steam_id}': {e}")
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
        print(f"No games data found in Steam profile for '{steam_id}'")
        return []

    try:
        apps = json.loads(games_payload)
    except json.JSONDecodeError as e:
        print(f"Failed to parse Steam games data: {e}")
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
            print(f"Missing required field in Steam game data: {e}")
            continue
    return result


__all__ = ["extract_items_from_anilist", "extract_items_from_steam"]
