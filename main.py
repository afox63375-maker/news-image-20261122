#!/usr/bin/env python3
"""
main.py -- entrypoint for the make.fun bounty news-image-20261122.

The entry is a single newspaper front page, entry.png, bundled in this
repository next to this file. The picture itself is drawn by a separate
workshop script; this program's job is narrower: prove the bundled
file is a well-formed PNG inside the bounty's limits, then place an
unchanged copy where the grader looks for it.

Checks, in order:
  * the file exists and is at most 1 MiB;
  * it starts with the eight-byte PNG signature;
  * it parses as a sequence of chunks, each with a valid CRC;
  * the first chunk is IHDR and its dimensions are at most 1024x1024;
  * at least one IDAT chunk carries the picture data;
  * the last chunk is IEND and nothing follows it.

The copy lands in the directory named by MAKEFUN_OUTPUT_DIR
(default /output) as entry.png. Any failed check exits non-zero and
nothing is written.

Standard library only: binascii, os, struct, sys.
"""

import binascii
import os
import struct
import sys

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
SIZE_LIMIT = 1024 * 1024          # one mebibyte, the bounty's cap
SIDE_LIMIT = 1024                 # neither side may exceed this


def fail(message):
    print("main.py: " + message, file=sys.stderr)
    return 1


def read_chunks(blob):
    """Yield (kind, payload) for each chunk after the signature.

    Raises ValueError on any structural problem: a truncated header,
    a length that runs past the end of the file, or a CRC mismatch.
    """
    pos = len(PNG_MAGIC)
    end = len(blob)
    while pos < end:
        if pos + 8 > end:
            raise ValueError("truncated chunk header at byte %d" % pos)
        (length,) = struct.unpack(">I", blob[pos:pos + 4])
        kind = blob[pos + 4:pos + 8]
        payload_start = pos + 8
        payload_end = payload_start + length
        crc_end = payload_end + 4
        if crc_end > end:
            raise ValueError("chunk %r overruns the file" % kind)
        payload = blob[payload_start:payload_end]
        (stored_crc,) = struct.unpack(">I", blob[payload_end:crc_end])
        actual_crc = binascii.crc32(kind + payload) & 0xFFFFFFFF
        if stored_crc != actual_crc:
            raise ValueError("CRC mismatch in chunk %r" % kind)
        yield kind, payload
        pos = crc_end
    if pos != end:
        raise ValueError("trailing bytes after the final chunk")


def inspect(blob):
    """Return (width, height) if blob is an acceptable PNG, else raise."""
    if len(blob) > SIZE_LIMIT:
        raise ValueError("file is %d bytes, over the 1 MiB limit" % len(blob))
    if not blob.startswith(PNG_MAGIC):
        raise ValueError("missing PNG signature")
    kinds = []
    width = height = None
    for kind, payload in read_chunks(blob):
        kinds.append(kind)
        if kind == b"IHDR":
            if len(payload) != 13:
                raise ValueError("IHDR payload is not 13 bytes")
            width, height = struct.unpack(">II", payload[:8])
    if not kinds or kinds[0] != b"IHDR":
        raise ValueError("first chunk is not IHDR")
    if kinds[-1] != b"IEND":
        raise ValueError("last chunk is not IEND")
    if b"IDAT" not in kinds:
        raise ValueError("no IDAT chunk: the picture data is missing")
    if width is None or width < 1 or height < 1:
        raise ValueError("IHDR reports a degenerate picture size")
    if width > SIDE_LIMIT or height > SIDE_LIMIT:
        raise ValueError("picture is %dx%d, over the %dx%d limit"
                         % (width, height, SIDE_LIMIT, SIDE_LIMIT))
    return width, height


def source_path():
    """The bundled picture sits beside this file in the repository."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "entry.png")


def destination_path():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    return out_dir, os.path.join(out_dir, "entry.png")


def main():
    src = source_path()
    if not os.path.isfile(src):
        return fail("bundled entry.png not found next to main.py")
    with open(src, "rb") as handle:
        blob = handle.read()
    try:
        width, height = inspect(blob)
    except ValueError as problem:
        return fail("entry.png rejected: %s" % problem)

    out_dir, dst = destination_path()
    try:
        os.makedirs(out_dir, exist_ok=True)
        with open(dst, "wb") as handle:
            handle.write(blob)
    except OSError as problem:
        return fail("could not write %s: %s" % (dst, problem))

    # Read the copy back: the grader must receive the identical bytes.
    with open(dst, "rb") as handle:
        written = handle.read()
    if written != blob:
        return fail("written copy differs from the bundled picture")
    print("main.py: entry.png verified (%dx%d, %d bytes) and copied to %s"
          % (width, height, len(blob), dst))
    return 0


if __name__ == "__main__":
    sys.exit(main())
