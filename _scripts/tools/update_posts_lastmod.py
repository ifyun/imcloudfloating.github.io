#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Update (create if not existed) YAML 'lastmod' in posts
according to their last git log date.

Dependencies:
  - git
  - ruamel.yaml

© 2018-2019 Cotes Chung
Licensed under MIT
"""

import sys
import glob
import os
import subprocess
import shutil

from utils.frontmatter_getter import get_yaml
from ruamel.yaml import YAML

POSTS_PATH = "_posts"


def update_lastmod(verbose):
    count = 0
    yaml = YAML()

    for post in glob.glob(os.path.join(POSTS_PATH, "*.md")):

        ps = subprocess.Popen(("git", "log", "--pretty=%ad", post),
                              stdout=subprocess.PIPE)
        git_log_count = subprocess.check_output(('wc', '-l'), stdin=ps.stdout)
        ps.wait()

        if git_log_count.strip() == "1":
            continue

        git_lastmod = subprocess.check_output([
            "git", "log", "-1", "--pretty=%ad", "--date=iso", post]).strip()

        if not git_lastmod:
            continue

        frontmatter, line_num = get_yaml(post)
        meta = yaml.load(frontmatter)

        if 'lastmod' in meta:
            if meta['lastmod'] == git_lastmod:
                continue
            else:
                meta['lastmod'] = git_lastmod
        else:
            meta.insert(line_num, 'lastmod', git_lastmod)

        output = 'new.md'
        if os.path.isfile(output):
            os.remove(output)

        with open(output, 'w') as new, open(post, 'r') as old:
            new.write("---\n")
            yaml.dump(meta, new)
            new.write("---\n")
            line_num += 2

            lines = old.readlines()

            for line in lines:
                if line_num > 0:
                    line_num -= 1
                    continue
                else:
                    new.write(line)

        shutil.move(output, post)
        count += 1

        if verbose:
            print "[INFO] update 'lastmod' for:" + post

    print ("[INFO] Success to update lastmod for {} post(s).").format(count)

    # I don't even need to commit these. HO HO HO !
    # if count > 0:
    #     subprocess.call(["git", "add", POSTS_PATH])
    #     subprocess.call(["git", "commit", "-m",
    #                      "[Automation] Update lastmod for post(s)."])


def help():
    print("Usage: "
          "python update_posts_lastmod.py [ -v | --verbose ]\n\n"
          "Optional arguments:\n"
          "-v, --verbose        Print verbose logs\n")


def main():
    verbose = False

    if len(sys.argv) > 1:
        for arg in sys.argv:
            if arg == sys.argv[0]:
                continue
            else:
                if arg == '-v' or arg == '--verbose':
                    verbose = True
                else:
                    print("Oops! Unknown argument: '{}'\n".format(arg))
                    help()
                    return

    update_lastmod(verbose)


main()
