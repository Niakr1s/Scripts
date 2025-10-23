import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import requests
from unidecode import unidecode

STYLES = {
    "0": "Blues/Funk/Soul",
    "1": "Classical",
    "2": "Country",
    "3": "Electronic",
    "4": "Ethnic/Folk/Spiritual",
    "5": "Jazz",
    "6": "Metal/Hardcore",
    "7": "Miscellaneous",
    "8": "Pop",
    "9": "Rap/Hip Hop",
    "10": "Reggae/Ska",
    "11": "Rock",
    "12": "WAHCOH",
}

OUT_DIR = Path("out")
RADIOS_JSON_FILE_PATH = OUT_DIR / Path("caprice_radios.json")
RADIOS_JSON_URL = "https://github.com/drocheam/caprice/raw/refs/heads/main/radios.json"


def get_radios_json() -> dict:
    if RADIOS_JSON_FILE_PATH.exists():
        return json.loads(RADIOS_JSON_FILE_PATH.read_text())

    got = requests.get(RADIOS_JSON_URL)
    if got.status_code != 200:
        print(f"got status code: {got.status_code}")
        exit(1)

    radios = got.json()["radios"]
    RADIOS_JSON_FILE_PATH.write_text(json.dumps(radios, indent="  "), encoding="utf8")
    return radios


def normalize_style(style: str) -> str:
    return unidecode(style).replace("/", "_").replace(" ", "")


@dataclass
class Stream:
    title: str
    url: str


class M3U:
    TITLE = "#EXTM3U"

    def __init__(self):
        self.streams: list[Stream] = []

    @staticmethod
    def _normalize_title(title: str) -> str:
        return unidecode(title)

    def add_stream(self, title: str, url: str):
        self.streams.append(Stream(title, url))

    def sort_by_title(self):
        self.streams.sort(key=lambda s: s.title)

    def save_to_file(self, dir: Path, file_stem: Path):
        contents = [self.TITLE]
        for stream in self.streams:
            contents.append(f"#EXTINF:-1,{self._normalize_title(stream.title)}")
            contents.append(stream.url.strip())

        filepath = dir / file_stem.with_suffix(".m3u")
        filepath.write_text("\n".join(contents))


if __name__ == "__main__":
    radios = get_radios_json()

    m3us: defaultdict[str, M3U] = defaultdict(M3U)
    for radio in radios:
        name = radio["name"]
        style = radio["style"]
        url = radio["url"]
        m3us[style].add_stream(title=name, url=url)

    for style, m3u in m3us.items():
        file_stem = "Caprice__" + normalize_style(STYLES[style])
        try:
            m3u.save_to_file(OUT_DIR, Path(file_stem))
        except Exception as e:
            print(f"couldn't save to file {style}: {e}")
