#!/usr/bin/env python3
"""News image, Sunday 22 November 2026 — copy the finished front page.

The page itself is already rendered and stored next to this script as
``entry.png``.  This program does no drawing at all: it only checks that
the stored file is a whole, well-formed PNG of the expected size and
then copies its bytes unchanged to the output directory.

Only the Python standard library is used, so the program runs in a
bare container with no third-party packages installed.  There is no
network access, no clock reading and no randomness, so every run
writes exactly the same bytes.
"""

import binascii
import hashlib
import os
import struct
import sys

SOURCE_NAME = "entry.png"
TARGET_NAME = "entry.png"

# The competition caps the entry image at 1024 by 1024 pixels and 1 MiB.
MAX_WIDTH = 1024
MAX_HEIGHT = 1024
MAX_BYTES = 1024 * 1024

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
IHDR_LENGTH = 13


def fail(message):
    """Print an error to stderr and exit non-zero."""
    sys.stderr.write("error: %s\n" % message)
    return 1


def source_path():
    """Locate entry.png: beside this script, or under MAKEFUN_BOT_DIR."""
    bot_dir = os.environ.get("MAKEFUN_BOT_DIR")
    if bot_dir:
        return os.path.join(bot_dir, SOURCE_NAME)
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, SOURCE_NAME)


def output_path():
    """Locate the destination: MAKEFUN_OUTPUT_DIR/entry.png."""
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    return os.path.join(outdir, TARGET_NAME)


def check_png(data):
    """Validate the PNG bytes; return (width, height) or raise ValueError."""
    if len(data) > MAX_BYTES:
        raise ValueError(
            "file is %d bytes, over the %d byte limit" % (len(data), MAX_BYTES)
        )
    if len(data) < len(PNG_SIGNATURE) + 8 + IHDR_LENGTH + 12:
        raise ValueError("file is too short to be a PNG")
    if data[:8] != PNG_SIGNATURE:
        raise ValueError("missing PNG signature")

    # The first chunk must be IHDR: 4-byte length, "IHDR", 13 data bytes.
    length = struct.unpack(">I", data[8:12])[0]
    if data[12:16] != b"IHDR" or length != IHDR_LENGTH:
        raise ValueError("first chunk is not IHDR")
    width, height = struct.unpack(">II", data[16:24])
    if width < 1 or height < 1:
        raise ValueError("image has zero width or height")
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        raise ValueError(
            "image is %dx%d, over the %dx%d limit"
            % (width, height, MAX_WIDTH, MAX_HEIGHT)
        )

    # Walk the chunk list to the end: every chunk must fit inside the
    # file, carry a matching CRC, and the last one must be IEND.  A real
    # image also needs at least one IDAT chunk carrying pixel data.
    offset = 8
    seen_iend = False
    seen_idat = False
    while offset < len(data):
        if offset + 8 > len(data):
            raise ValueError("truncated chunk header at offset %d" % offset)
        chunk_len = struct.unpack(">I", data[offset:offset + 4])[0]
        chunk_type = data[offset + 4:offset + 8]
        end = offset + 12 + chunk_len
        if end > len(data):
            raise ValueError("chunk %r overruns the file" % chunk_type)
        stored_crc = struct.unpack(">I", data[offset + 8 + chunk_len: end])[0]
        actual_crc = binascii.crc32(data[offset + 4:offset + 8 + chunk_len])
        actual_crc &= 0xFFFFFFFF
        if stored_crc != actual_crc:
            raise ValueError("bad CRC in chunk %r" % chunk_type)
        if chunk_type == b"IDAT":
            seen_idat = True
        if chunk_type == b"IEND":
            if chunk_len != 0:
                raise ValueError("IEND chunk must be empty")
            if end != len(data):
                raise ValueError("trailing bytes after IEND")
            seen_iend = True
            break
        offset = end
    if not seen_iend:
        raise ValueError("missing IEND chunk")
    if not seen_idat:
        raise ValueError("no IDAT chunk: image carries no pixel data")
    return width, height


def main():
    src = source_path()
    try:
        with open(src, "rb") as handle:
            data = handle.read()
    except OSError as exc:
        return fail("cannot read %s: %s" % (src, exc))

    try:
        width, height = check_png(data)
    except ValueError as exc:
        return fail("%s is not a valid entry image: %s" % (src, exc))

    dest = output_path()
    if os.path.abspath(src) == os.path.abspath(dest):
        return fail("source and destination are the same file: %s" % src)
    try:
        parent = os.path.dirname(dest)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(dest, "wb") as handle:
            handle.write(data)
    except OSError as exc:
        return fail("cannot write %s: %s" % (dest, exc))

    # Read the copy back and confirm it matches the source byte for byte
    # before reporting success, so a truncated write can never pass.
    try:
        with open(dest, "rb") as handle:
            written = handle.read()
    except OSError as exc:
        return fail("cannot read back %s: %s" % (dest, exc))
    if written != data:
        return fail("written file differs from %s" % src)

    digest = hashlib.sha256(data).hexdigest()
    print("wrote %s (%dx%d, %d bytes, sha256 %s)" % (dest, width, height, len(data), digest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
