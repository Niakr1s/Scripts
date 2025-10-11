import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable, Optional


class DetectedSegment:
    def __init__(self, start: float, end: float):
        self.start = start
        self.end = end


def detect_scene_changes_sync(
    file_path: str,
    stream_id: Optional[int] = None,
    min_change: float = 0.3,
    on_progress: Optional[Callable[[float], None]] = None,
    on_segment_detected: Optional[Callable[[DetectedSegment], None]] = None,
    from_time: float = 0,
    to_time: float = 0,
) -> list[DetectedSegment]:
    """
    Synchronous version of scene change detection
    """

    def get_input_seek_args():
        args = []
        if from_time > 0:
            args.extend(["-ss", str(from_time)])
        if to_time > 0:
            args.extend(["-to", str(to_time)])
        args.extend(["-i", file_path])
        return args

    # Build ffmpeg arguments
    args = [
        "ffmpeg",
        "-hide_banner",
        *get_input_seek_args(),
        "-map",
        f"0:{stream_id}" if stream_id is not None else "v:0",
        "-filter:v",
        f"select='gt(scene,{min_change})',metadata=print:file=-:direct=1",
        "-f",
        "null",
        "-",
    ]
    print(args)

    last_time: float = 0
    line_pattern = re.compile(r"^frame:\d+\s+pts:\d+\s+pts_time:([\d.]+)")

    segments: list[DetectedSegment] = []

    with subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True,
    ) as process:
        assert process.stdout
        # Read stdout line by line
        for line in process.stdout:
            line = line.strip()

            # Parse scene change timestamps
            match = line_pattern.match(line)
            if match:
                time = float(match.group(1))
                segment = DetectedSegment(
                    start=from_time + last_time, end=from_time + time
                )
                segments.append(segment)
                if on_segment_detected:
                    on_segment_detected(segment)
                last_time = time
            # if process.poll() is not None:
            #     break

    return segments


def export_to_llc(segments: list[DetectedSegment], file_name: str):
    cutSegments = []
    for segment in segments:
        cutSegments.append(
            {
                "start": segment.start,
                "end": segment.end,
                "name": "",
            }
        )

    llc = {
        "version": 1,
        "mediaFileName": file_name,
        "cutSegments": cutSegments,
    }

    return llc


def make_llc_file_name(mp4_path: Path) -> str:
    return f"{mp4_path.stem}-proj.llc"


# Example synchronous usage
if __name__ == "__main__":

    def progress_callback(progress: float):
        print(f"Progress: {progress:.1%}")

    def segment_callback(segment: DetectedSegment):
        print(f"Scene change: {segment.start:.2f}s - {segment.end:.2f}s")

    files_dir = Path(sys.argv[1])
    files_dir.mkdir(parents=True, exist_ok=True)

    llc_out_dir = Path(sys.argv[1] if not len(sys.argv) == 3 else sys.argv[2])
    llc_out_dir.mkdir(parents=True, exist_ok=True)

    for file_path in files_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix == ".mp4":
            segments = detect_scene_changes_sync(
                file_path=str(file_path),
                min_change=0.3,
                on_segment_detected=segment_callback,
            )
            print(f"Detected {len(segments)} segments")
            llc = export_to_llc(segments, file_path.name)

            llc_path = llc_out_dir / make_llc_file_name(file_path)
            llc_path.write_text(json.dumps(llc))
