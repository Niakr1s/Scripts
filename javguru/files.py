import re

RE = re.compile(r"^\[(.+)\]\W*(.*?)\W*(\.mp4)?$")


def extract_id_and_description(filename: str) -> tuple[str, str]:
    match = RE.search(filename)
    id = match.group(1)
    description = match.group(2)
    return id, description


if __name__ == "__main__":
    assert ("SOMEID-12345", "Some description") == extract_id_and_description(
        "[SOMEID-12345] Some description.mp4"
    )
    assert ("SOMEID-12345", "Some description") == extract_id_and_description(
        "[SOMEID-12345]              Some description         .mp4"
    )
    assert ("SOMEID-12345", "Some description") == extract_id_and_description(
        "[SOMEID-12345]Some description.mp4"
    )
