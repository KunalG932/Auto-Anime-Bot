import re
from typing import Dict, Optional

def extract_info(input_string: str) -> Optional[Dict[str, str]]:
    pattern = r"\[SubsPlease\] (.+?)(?: S(\d+))? - (\d+)(?: \((\d+p)\) \[.+?\])?"
    match = re.match(pattern, input_string)

    if not match:
        return None

    title, season, episode, quality = match.groups()

    if season and episode:
        main_res = f"{title} Season {season} Episode {episode}"
        search_que = f"{title} Season {season}"
    elif episode:
        main_res = title
        search_que = title
    elif season:
        main_res = f"{title} Season {season}"
        search_que = f"{title} Season {season}"
    else:
        main_res = title
        search_que = title

    return {
        "main_res": main_res,
        "search_que": search_que,
        "episode": episode or "",
        "season": season or "",
        "quality": quality or ""
    }
