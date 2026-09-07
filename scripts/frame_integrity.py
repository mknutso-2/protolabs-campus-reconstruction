"""Validate a completed PNG before resuming an expensive frame sequence.

Uses only Python's standard library. Checks complete chunk framing and CRCs,
IHDR, IDAT ordering, zlib stream completion, decoded scanline lengths/filter
bytes (including Adam7), and an exact terminal IEND. No image is modified.
"""
from pathlib import Path
import struct
import zlib

SIGNATURE = b'\x89PNG\r\n\x1a\n'


def inspect_png(path, expected_size=None):
    """Return ``valid`` and a diagnostic ``reason``; malformed files never pass.

    ``expected_size`` is the renderer's (width, height). The 512 MiB decoded
    ceiling bounds accidental or hostile allocation from malformed headers.
    """
    result = {'valid': False, 'reason': 'unread', 'width': None, 'height': None}
    def fail(reason):
        result['reason'] = reason
        return result
    try:
        data = Path(path).read_bytes()
    except OSError as error:
        return fail('Cannot read PNG: ' + str(error))
    if not data.startswith(SIGNATURE): return fail('Invalid PNG signature')
    offset = len(SIGNATURE)
    chunks = 0
    image_data = []
    seen_idat = False
    idat_ended = False
    seen_plte = False
    header = None
    while offset < len(data):
        if len(data) - offset < 12: return fail('Truncated PNG chunk header or CRC')
        length = struct.unpack_from('>I', data, offset)[0]
        kind = data[offset + 4:offset + 8]
        if length > 0x7fffffff or length > len(data) - offset - 12:
            return fail('Truncated or oversized PNG chunk')
        payload = data[offset + 8:offset + 8 + length]
        stored_crc = struct.unpack_from('>I', data, offset + 8 + length)[0]
        actual_crc = zlib.crc32(payload, zlib.crc32(kind)) & 0xffffffff
        if actual_crc != stored_crc:
            return fail('PNG chunk CRC mismatch: ' + kind.decode('ascii', errors='replace'))
        if len(kind) != 4 or not all(65 <= b <= 90 or 97 <= b <= 122 for b in kind):
            return fail('Invalid PNG chunk type')
        if kind[2] & 32: return fail('Invalid PNG chunk reserved bit')
        if chunks == 0 and kind != b'IHDR': return fail('IHDR is not the first chunk')
        offset += length + 12
        chunks += 1
        if kind == b'IHDR':
            if header is not None or length != 13: return fail('Invalid or repeated IHDR')
            width, height, depth, color, compression, filtering, interlace = struct.unpack('>IIBBBBB', payload)
            result.update(width=width, height=height)
            if width < 1 or height < 1 or width > 0x7fffffff or height > 0x7fffffff:
                return fail('Invalid PNG dimensions')
            if expected_size is not None and (width, height) != tuple(expected_size):
                return fail('PNG dimensions do not match the renderer')
            valid_depths = {0: (1, 2, 4, 8, 16), 2: (8, 16), 3: (1, 2, 4, 8), 4: (8, 16), 6: (8, 16)}
            if color not in valid_depths or depth not in valid_depths[color]:
                return fail('Invalid PNG color type or bit depth')
            if compression != 0 or filtering != 0 or interlace not in (0, 1):
                return fail('Unsupported PNG compression, filter, or interlace method')
            header = (width, height, depth, color, interlace)
        elif kind == b'PLTE':
            if seen_plte or seen_idat or length == 0 or length % 3 or length > 768:
                return fail('Invalid PNG palette')
            seen_plte = True
        elif kind == b'IDAT':
            if idat_ended: return fail('PNG IDAT chunks are not consecutive')
            seen_idat = True
            image_data.append(payload)
        elif kind == b'IEND':
            if length != 0 or not seen_idat: return fail('Invalid IEND or missing IDAT')
            if offset != len(data): return fail('Trailing data after PNG IEND')
            break
        else:
            if seen_idat: idat_ended = True
            if not kind[0] & 32: return fail('Unknown critical PNG chunk')
    else:
        return fail('Missing terminal PNG IEND')
    width, height, depth, color, interlace = header
    if color == 3 and not seen_plte: return fail('Indexed PNG has no palette')
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color]
    passes = [(0, 0, 1, 1)] if not interlace else [
        (0, 0, 8, 8), (4, 0, 8, 8), (0, 4, 4, 8), (2, 0, 4, 4),
        (0, 2, 2, 4), (1, 0, 2, 2), (0, 1, 1, 2)]
    rows = []
    for x, y, dx, dy in passes:
        pass_width = max(0, (width - x + dx - 1) // dx)
        pass_height = max(0, (height - y + dy - 1) // dy)
        if pass_width and pass_height:
            rows.append(((pass_width * channels * depth + 7) // 8, pass_height))
    decoded_size = sum((row_bytes + 1) * count for row_bytes, count in rows)
    if decoded_size > 512 * 1024 * 1024: return fail('Decoded PNG exceeds validation memory limit')
    try:
        decoder = zlib.decompressobj()
        decoded = decoder.decompress(b''.join(image_data), decoded_size + 1)
    except zlib.error:
        return fail('Corrupt PNG zlib image stream')
    if len(decoded) != decoded_size or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
        return fail('Incomplete, oversized, or trailing PNG zlib stream')
    offset = 0
    for row_bytes, count in rows:
        for _ in range(count):
            if decoded[offset] > 4: return fail('Invalid PNG scanline filter byte')
            offset += row_bytes + 1
    result.update(valid=True, reason='Complete PNG; chunk CRCs and image stream verified',
                  chunks=chunks, file_bytes=len(data), decoded_bytes=decoded_size)
    return result
