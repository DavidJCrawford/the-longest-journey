"""Read .xlsx without a dependency.

LAWA publishes its monitoring data as Excel, and the Waikato/Northland file is
27 MB compressed and a quarter of a gigabyte of XML open. openpyxl would be the
obvious answer and it is exactly the answer the siblings' rule forbids: a
pipeline that needs a virtualenv is a pipeline that stops working.

An .xlsx is a zip of XML, so zipfile and xml.etree are enough. The only care
needed is to stream rather than parse the whole sheet into memory, and to
resolve the shared-string table that Excel uses for repeated text.
"""
from __future__ import annotations

import zipfile
from xml.etree.ElementTree import iterparse

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def shared_strings(z: zipfile.ZipFile) -> list[str]:
    out: list[str] = []
    if "xl/sharedStrings.xml" not in z.namelist():
        return out
    with z.open("xl/sharedStrings.xml") as fh:
        for _, el in iterparse(fh, ("end",)):
            if el.tag == NS + "si":
                out.append("".join(t.text or "" for t in el.iter(NS + "t")))
                el.clear()
    return out


def rows(z: zipfile.ZipFile, sheet: str, ss: list[str], limit: int | None = None):
    """Yield each row as a list of strings. Cells are not coerced: dates arrive
    as Excel serials and numbers as their literal text, because deciding what a
    value means is the caller's job and guessing here would hide it."""
    with z.open(sheet) as fh:
        n = 0
        for _, el in iterparse(fh, ("end",)):
            if el.tag != NS + "row":
                continue
            row = []
            for c in el.findall(NS + "c"):
                t, v = c.get("t"), c.find(NS + "v")
                if t == "s" and v is not None:
                    row.append(ss[int(v.text)])
                elif t == "inlineStr":
                    inline = c.find(NS + "is")
                    row.append("".join(x.text or "" for x in inline.iter(NS + "t")) if inline is not None else "")
                else:
                    row.append(v.text if v is not None else "")
            yield row
            el.clear()
            n += 1
            if limit and n >= limit:
                return


def excel_date(serial: str) -> str | None:
    """Excel serial -> ISO date. 1899-12-30 is the epoch Excel actually uses,
    because of the 1900 leap-year bug it inherited from Lotus."""
    import datetime
    try:
        f = float(serial)
    except (TypeError, ValueError):
        return None
    return (datetime.datetime(1899, 12, 30) + datetime.timedelta(days=f)).date().isoformat()
