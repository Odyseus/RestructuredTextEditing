#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
"""
try:
    from docutils.core import publish_string
except (ImportError, SystemError):
    raise SystemExit("Required <docutils> Python module not found.")

import argparse
import os
import sys
import webbrowser


def rst_to_html(rst_text, extra_css=[]):
    overrides = {}

    if extra_css:
        overrides["stylesheet_path"] = ",".join(extra_css)

    return publish_string(source=rst_text, source_path=None,
                          writer_name="html5", settings_overrides=overrides)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("html_path", type=str)
    parser.add_argument("--extra-css", dest="extra_css", action="append")
    parser.add_argument("--open-in-browser", dest="open_in_browser", action="store_true")

    args = parser.parse_args()
    print(args)
    html_output = ""

    try:
        if sys.stdin.isatty():
            raise RuntimeError("No STDIN passed.")

        rst_data = sys.stdin.read().strip()

        if not rst_data:
            raise RuntimeError("STDIN is empty.")

        html_output = rst_to_html(rst_data, args.extra_css)
    except Exception as err:
        raise SystemExit(err)

    if html_output:
        os.makedirs(os.path.dirname(args.html_path), exist_ok=True)

        with open(args.html_path, "wb") as f:
            f.write(html_output)

        if args.open_in_browser:
            raise SystemExit(webbrowser.open("file://%s" % args.html_path, new=2, autoraise=True))

    raise SystemExit(0)
