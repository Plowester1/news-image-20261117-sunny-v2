"""news-image-20261117 entry (@sunny-heron-22): copy the bundled image to
/output/entry.png.

Deterministic: a pure file copy — no network, no randomness, no timestamps
— so both runs write identical bytes. The image (entry.png, beside this
file) is a 1024x1024 light-newspaper infographic summing up Tuesday
17 November 2026's world news in eight stories, composed programmatically
with PIL (see build_image.py).
"""
import hashlib
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
DST_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if not os.path.isfile(SRC):
        raise SystemExit("entry.png missing next to main.py: nothing to copy")
    # Competition limit is 1 MiB; refuse to ship an empty or oversize image
    # rather than silently submitting something the judge rejects.
    src_size = os.path.getsize(SRC)
    if src_size == 0 or src_size > 1024 * 1024:
        raise SystemExit("entry.png size %d bytes is outside the allowed range"
                         % src_size)
    os.makedirs(DST_DIR, exist_ok=True)
    DST = os.path.join(DST_DIR, "entry.png")
    shutil.copyfile(SRC, DST)

    # Fail loudly rather than silently submitting a truncated copy: the
    # competition runs this program twice and both runs must write the same
    # bytes, so confirm the output is byte-identical to the source.
    if _sha256(DST) != _sha256(SRC):
        raise SystemExit("entry.png copy mismatch: output differs from source")
    print("wrote %s (%d bytes, sha256 %s)"
          % (DST, src_size, _sha256(DST)[:16]))


if __name__ == "__main__":
    main()
