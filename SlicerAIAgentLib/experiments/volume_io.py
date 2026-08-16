"""Read a saved ``.nrrd`` volume without Slicer: the array and its IJK->RAS map.

A flat scene save writes the CT beside the models (``Statistic/scene/<name>.nrrd``),
and scoring a screw path means sampling that CT at points given in RAS. Slicer
would do both for us, but keeping this Slicer-free is what lets the whole
ReverseShoulderArthroplasty analysis -- including its density integral -- be
checked against the real saved runs by ``scripts/check_rsa_analysis.py``, outside
Slicer. That check is the only thing standing between a mirrored path and a
plausible-looking number, so it is worth a reader of our own.

Two properties of these files are load-bearing and neither announces itself:

* ``encoding: gzip``. The bytes after the header are a DEFLATE stream. Reading
  raw ``int16`` from that offset returns garbage rather than an error.
* ``space: left-posterior-superior``. The direction vectors and origin are in
  LPS, so rows 0 and 1 must be negated to get IJK->RAS. Skipping the flip maps a
  right-shoulder path onto indices that are still *inside* the array, so no
  bounds error reveals it -- the density integral simply comes out of the wrong
  half of the patient.

Deliberately NOT read from ``scene.mrml``: it rounds spacing and origin to six
significant figures (``0.351562`` for a true ``0.3515625``), which is a third of
a voxel over 300 slices.
"""

from __future__ import annotations

import logging
import re
import zlib
from typing import Any, Dict, Tuple

import numpy as np

logger = logging.getLogger(__name__)

#: NRRD ``type:`` -> numpy base dtype. Spelled out rather than passed to
#: ``np.dtype`` directly, so an unknown type raises here instead of silently
#: reinterpreting the buffer.
_TYPES = {
    "signed char": "i1", "int8": "i1", "int8_t": "i1",
    "uchar": "u1", "unsigned char": "u1", "uint8": "u1", "uint8_t": "u1",
    "short": "i2", "signed short": "i2", "short int": "i2",
    "int16": "i2", "int16_t": "i2",
    "ushort": "u2", "unsigned short": "u2", "uint16": "u2", "uint16_t": "u2",
    "int": "i4", "signed int": "i4", "int32": "i4", "int32_t": "i4",
    "uint": "u4", "unsigned int": "u4", "uint32": "u4", "uint32_t": "u4",
    "float": "f4", "double": "f8",
}

_NUMBER = re.compile(r"[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?")


def _numbers(text: str):
    return [float(x) for x in _NUMBER.findall(text or "")]


def _parse_header(text: str) -> Dict[str, str]:
    """``key: value`` fields only.

    ``key:=value`` is NRRD's *key/value* metadata -- a ``.seg.nrrd`` carries
    dozens of them (segment names, extents, colours) and one is literally
    ``Segmentation_MasterRepresentation:=Binary labelmap``. Treating those as
    fields would let a metadata key shadow a real one.
    """
    fields: Dict[str, str] = {}
    for line in text.splitlines():
        if not line or line.startswith("#") or ":=" in line:
            continue
        key, separator, value = line.partition(":")
        if separator:
            fields[key.strip()] = value.strip()
    return fields


def read_nrrd(path: str) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    """``(array[k, j, i], ijk_to_ras 4x4, header)`` for a 3-D NRRD.

    The array is indexed ``[k, j, i]`` -- the reverse of ``sizes:`` -- which is
    the same order ``slicer.util.arrayFromVolume`` hands back, so a sampler
    written against one works against the other.
    """
    with open(path, "rb") as handle:
        blob = handle.read()

    cut = blob.find(b"\n\n")
    if cut < 0:
        raise ValueError("%s: no blank line ending the NRRD header" % path)
    fields = _parse_header(blob[:cut].decode("latin-1"))
    payload = blob[cut + 2:]

    if int(fields.get("dimension", "0")) != 3:
        raise ValueError("%s: expected a 3-D volume, got dimension %s"
                         % (path, fields.get("dimension")))

    sizes = [int(x) for x in fields["sizes"].split()]
    if len(sizes) != 3:
        raise ValueError("%s: sizes %r is not three numbers" % (path, fields["sizes"]))
    ni, nj, nk = sizes

    base = _TYPES.get(fields.get("type", "").strip().lower())
    if base is None:
        raise ValueError("%s: unsupported NRRD type %r" % (path, fields.get("type")))
    if base[-1] == "1":
        dtype = np.dtype(base)                       # single byte: no endianness
    else:
        endian = fields.get("endian", "").strip().lower()
        if endian not in ("little", "big"):
            # Required rather than defaulted: guessing wrong byte-swaps every
            # voxel into a finite but meaningless value.
            raise ValueError("%s: multi-byte type %r with no 'endian:' field"
                             % (path, fields.get("type")))
        dtype = np.dtype(("<" if endian == "little" else ">") + base)

    encoding = fields.get("encoding", "raw").strip().lower()
    if encoding in ("gzip", "gz"):
        raw = zlib.decompress(payload, 16 + zlib.MAX_WBITS)
    elif encoding in ("raw", "identity"):
        raw = payload
    else:
        raise ValueError("%s: unsupported NRRD encoding %r" % (path, encoding))

    expected = ni * nj * nk * dtype.itemsize
    if len(raw) < expected:
        # A short read must be loud. numpy would happily reshape a truncated
        # buffer's prefix if we sliced first, and the missing slices would read
        # as whatever the last complete one contained.
        raise ValueError("%s: voxel data is %d bytes, expected %d"
                         % (path, len(raw), expected))
    array = np.frombuffer(raw[:expected], dtype=dtype).reshape(nk, nj, ni)

    columns = [_numbers(part) for part in fields["space directions"].split(")")
               if "(" in part]
    if len(columns) != 3 or any(len(c) != 3 for c in columns):
        raise ValueError("%s: cannot read 'space directions' %r"
                         % (path, fields.get("space directions")))
    origin = _numbers(fields.get("space origin", ""))
    if len(origin) != 3:
        raise ValueError("%s: cannot read 'space origin' %r"
                         % (path, fields.get("space origin")))

    ijk_to_ras = np.eye(4)
    for index, column in enumerate(columns):
        ijk_to_ras[:3, index] = column
    ijk_to_ras[:3, 3] = origin

    space = re.sub(r"[^a-z]+", " ", fields.get("space", "").lower()).strip()
    if space in ("left posterior superior", "lps"):
        ijk_to_ras[0, :] *= -1.0
        ijk_to_ras[1, :] *= -1.0
    elif space not in ("right anterior superior", "ras"):
        # Never assume. Every other anatomical space would need its own flip,
        # and the wrong one lands inside the array rather than out of it.
        raise ValueError("%s: unhandled NRRD space %r" % (path, fields.get("space")))

    return array, ijk_to_ras, fields


def sample_nearest(array: np.ndarray, ras_to_ijk: np.ndarray,
                   points: np.ndarray, out_of_bounds: float
                   ) -> Tuple[np.ndarray, np.ndarray]:
    """``(values, inside)`` at ``points`` (N,3 in RAS), nearest neighbour.

    ``np.rint`` -- half-to-even, matching Python's own ``round`` and therefore
    ``int(round(...))`` in the extension being reproduced. ``astype(int)``
    truncates and ``int(x + 0.5)`` rounds half-up; on a 0.35 mm grid a screw
    path lands on exact ties often enough for either to shift the score.

    Out-of-bounds samples take ``out_of_bounds`` rather than being clamped or
    dropped, because the extension's own sampler returns a sentinel there and
    that sentinel is carried into its sum.
    """
    points = np.asarray(points, dtype=np.float64).reshape(-1, 3)
    homogeneous = np.concatenate([points, np.ones((points.shape[0], 1))], axis=1)
    ijk = homogeneous @ np.asarray(ras_to_ijk, dtype=np.float64).T
    index = np.rint(ijk[:, :3]).astype(np.int64)

    nk, nj, ni = array.shape
    limit = np.array([ni, nj, nk], dtype=np.int64)
    inside = np.logical_and((index >= 0).all(axis=1), (index < limit).all(axis=1))

    values = np.full(points.shape[0], float(out_of_bounds), dtype=np.float64)
    if inside.any():
        chosen = index[inside]
        values[inside] = array[chosen[:, 2], chosen[:, 1], chosen[:, 0]]
    return values, inside
