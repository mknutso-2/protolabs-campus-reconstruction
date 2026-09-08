"""Encode contiguous rendered PNGs, preserving each input frame and resolution.

Usage:
  python3 work/video-tools/encode.py --frames-dir PATH --fps 24 --out PATH.mp4

No frame interpolation, looping, missing-frame substitution, scaling, or padding.
An existing output is preserved. FFmpeg is local to work/tools/video by default.
"""
from pathlib import Path
import argparse
import json
import math
import os
import re
import struct
import subprocess
import sys
import uuid


def png_size(path):
    with path.open('rb') as stream:
        header = stream.read(24)
    if len(header) != 24 or header[:8] != b'\x89PNG\r\n\x1a\n' or header[12:16] != b'IHDR':
        raise ValueError(f'Not a PNG with an IHDR header: {path.name}')
    return struct.unpack('>II', header[16:24])


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--frames-dir', type=Path, required=True)
    parser.add_argument('--fps', type=float, default=24.0)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--ffmpeg', type=Path,
                        default=Path(os.environ.get('FFMPEG', '/usr/bin/ffmpeg')))
    parser.add_argument('--threads', type=int, default=2)
    parser.add_argument('--expected-frames', type=int,
                        help='Fail if the folder is still incomplete or has extra frames')
    args = parser.parse_args()
    if not math.isfinite(args.fps) or args.fps <= 0:
        parser.error('--fps must be positive and finite')
    if args.threads < 1:
        parser.error('--threads must be at least 1')
    if not args.frames_dir.is_dir():
        parser.error('--frames-dir must be an existing directory')
    output = args.out.resolve()
    if output.suffix.lower() != '.mp4':
        parser.error('--out must end in .mp4')
    if output.exists():
        parser.error(f'Output already exists and will be preserved: {output}')
    ffmpeg = args.ffmpeg.resolve()
    if not ffmpeg.is_file() or not os.access(ffmpeg, os.X_OK):
        parser.error(f'FFmpeg is unavailable: {ffmpeg}; run prepare_ffmpeg.py first')
    matches = []
    pattern = re.compile(r'^frame_(\d+)\.png$')
    for path in args.frames_dir.glob('frame_*.png'):
        match = pattern.fullmatch(path.name)
        if not match:
            parser.error(f'Unexpected frame filename: {path.name}')
        matches.append((int(match[1]), len(match[1]), path.resolve()))
    if not matches:
        parser.error('No frame_NNNN.png images found')
    matches.sort()
    if args.expected_frames is not None and len(matches) != args.expected_frames:
        parser.error(f'Expected {args.expected_frames} frames, found {len(matches)}')
    first, padding, _ = matches[0]
    if any(width != padding for _, width, _ in matches):
        parser.error('All frame numbers must use the same zero padding')
    actual = [number for number, _, _ in matches]
    expected = list(range(first, matches[-1][0]+1))
    if actual != expected:
        missing = sorted(set(expected)-set(actual))
        parser.error(f'Frames must be contiguous without duplicates; missing numbers: {missing[:20]}')
    dimensions = {png_size(path) for _, _, path in matches}
    if len(dimensions) != 1:
        parser.error(f'Frame dimensions differ: {sorted(dimensions)}')
    width, height = dimensions.pop()
    if width % 2 or height % 2:
        parser.error('yuv420p requires even width and height; original frames will not be resized')
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.parent/f'.{output.stem}.encoding-{uuid.uuid4().hex}.mp4'
    sequence = str(args.frames_dir.resolve()/f'frame_%0{padding}d.png')
    command = [str(ffmpeg), '-hide_banner', '-nostdin', '-n', '-xerror',
               '-framerate', str(args.fps), '-start_number', str(first),
               '-i', sequence, '-map', '0:v:0', '-an', '-frames:v', str(len(matches)),
               '-fps_mode', 'passthrough', '-c:v', 'libx264', '-crf', '18',
               '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
               '-threads', str(args.threads), str(temporary)]
    try:
        subprocess.run(command, check=True)
        # Same-directory hard link publishes without overwriting a concurrent
        # writer's output. Remove only this process's temporary on completion.
        os.link(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)
    print(json.dumps({'output': str(output), 'frames': len(matches),
                      'first_frame': first, 'last_frame': actual[-1],
                      'fps': args.fps, 'duration_seconds': len(matches)/args.fps,
                      'width': width, 'height': height,
                      'codec': 'H.264/libx264', 'crf': 18, 'pixel_format': 'yuv420p',
                      'frame_interpolation': False, 'resized': False}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f'Encoding failed: {error}', file=sys.stderr)
        sys.exit(1)
