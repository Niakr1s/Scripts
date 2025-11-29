import re

RE = re.compile(r"^\[(.+?)\]\s*(.*?)\W*(\.mp4)?$")


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
    assert (
        "JUQ-111",
        "The second J-cup exclusive! She appears in a popular NTR work! Town Camping NTR – Wife’s [Warning] Cuckold Footage of tent creampie – Kana Kusakabe",
    ) == extract_id_and_description(
        "[JUQ-111] The second J-cup exclusive! She appears in a popular NTR work! Town Camping NTR – Wife’s [Warning] Cuckold Footage of tent creampie – Kana Kusakabe.mp4"
    )
