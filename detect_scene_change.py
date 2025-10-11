import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Callable, Optional


class DetectedSegment:
    def __init__(self, start: float, end: float):
        self.start = start
        self.end = end


def get_video_duration(file_path: str) -> float:
    """Get the total duration of the video using ffprobe"""
    args = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        file_path,
    ]

    try:
        result = subprocess.run(args, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"Warning: Could not get video duration for {file_path}: {e}")
        return 0


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
    scene_change_times = []

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
                scene_change_times.append(time)
                segment = DetectedSegment(
                    start=from_time + last_time, end=from_time + time
                )
                segments.append(segment)
                if on_segment_detected:
                    on_segment_detected(segment)
                last_time = time

    # Get video duration to add the final segment
    if to_time > 0:
        video_duration = to_time
    else:
        video_duration = get_video_duration(file_path)

    # Add the final segment from last scene change to end of video
    if video_duration > 0 and last_time < video_duration:
        final_segment = DetectedSegment(
            start=from_time + last_time, end=from_time + video_duration
        )
        segments.append(final_segment)
        if on_segment_detected:
            on_segment_detected(final_segment)
        print(
            f"Added final segment: {final_segment.start:.2f}s - {final_segment.end:.2f}s"
        )

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


def main():
    parser = argparse.ArgumentParser(
        description="Detect scene changes in MP4 files and generate LLC files"
    )
    parser.add_argument(
        "files_dir", type=str, help="Directory containing MP4 files to process"
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default=None,
        help="Output directory for LLC files (defaults to files_dir)",
    )
    parser.add_argument(
        "--min-change",
        type=float,
        default=0.3,
        help="Minimum change threshold for scene detection (default: 0.3)",
    )

    args = parser.parse_args()

    files_dir = Path(args.files_dir)
    files_dir.mkdir(parents=True, exist_ok=True)

    # Use files_dir if out_dir is not provided
    llc_out_dir = Path(args.out_dir if args.out_dir is not None else args.files_dir)
    llc_out_dir.mkdir(parents=True, exist_ok=True)

    min_change = args.min_change

    def progress_callback(progress: float):
        print(f"Progress: {progress:.1%}")

    def segment_callback(segment: DetectedSegment):
        print(f"Scene change: {segment.start:.2f}s - {segment.end:.2f}s")

    for file_path in files_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix == ".mp4":
            print(f"Processing: {file_path}")
            segments = detect_scene_changes_sync(
                file_path=str(file_path),
                min_change=min_change,
                on_segment_detected=segment_callback,
            )
            print(f"Detected {len(segments)} segments")
            llc = export_to_llc(segments, file_path.name)

            llc_path = llc_out_dir / make_llc_file_name(file_path)
            llc_path.write_text(json.dumps(llc, indent=2))
            print(f"Saved LLC file: {llc_path}\n")


if __name__ == "__main__":
    main()
