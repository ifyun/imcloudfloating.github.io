#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Generates HTML page for categories and tags by posts.
© 2018-2019 Cotes Chung
MIT License
'''

import os
import glob
import shutil
import sys

from ruamel.yaml import YAML
from utils.frontmatter_getter import get_yaml


DRAFTS_DIR = '_drafts'
POSTS_DIR = ['_posts']

CATEGORIES_DIR = 'categories'
CATEGORY_LAYOUT = 'category'

TAG_DIR = 'tags'
TAG_LAYOUT = 'tag'

LEVEL = 3  # Tree level for current script file.


def get_path(dir):
    path = os.path.abspath(__file__)
    count = LEVEL
    r_index = len(path)
    while r_index > 0:
        r_index -= 1
        if (path[r_index] == '/'):
            count -= 1
            if count == 0:
                return path[:r_index + 1] + dir


def get_categories():
    all_categories = []
    yaml = YAML()

    for dir in POSTS_DIR:
        path = get_path(dir)
        for file in glob.glob(os.path.join(path, '*.md')):
            meta = yaml.load(get_yaml(file)[0])

            if 'category' in meta:
                if type(meta['category']) == list:
                    err_msg = (
                        "[Error] File {} 'category' type"
                        " can not be LIST!").format(file)
                    raise Exception(err_msg)
                else:
                    if meta['category'] not in all_categories:
                        all_categories.append(meta['category'])
            else:
                if 'categories' in meta:
                    if type(meta['categories']) == str:
                        error_msg = (
                            "[Error] File {} 'categories' type"
                            " can not be STR!").format(file)
                        raise Exception(error_msg)

                    for ctg in meta['categories']:
                        if ctg not in all_categories:
                            all_categories.append(ctg)
                else:
                    err_msg = (
                        "[Error] File:{} at least "
                        "have one category.").format(file)
                    print(err_msg)

    return all_categories


def generate_category_pages(is_verbose):
    categories = get_categories()
    path = get_path(CATEGORIES_DIR)

    if os.path.exists(path):
        shutil.rmtree(path)

    os.makedirs(path)

    for category in categories:
        new_page = path + '/' + category.replace(' ', '-').lower() + '.html'
        with open(new_page, 'w+') as html:
            html.write("---\n")
            html.write("layout: {}\n".format(CATEGORY_LAYOUT))
            html.write("title: {}\n".format(category.encode('utf-8')))
            html.write("category: {}\n".format(category.encode('utf-8')))
            html.write("---")

            if is_verbose:
                print("[INFO] Created page: " + new_page)

    print("[INFO] Succeed! {} category-pages created."
          .format(len(categories)))


def get_all_tags():
    all_tags = []
    yaml = YAML()

    for dir in POSTS_DIR:
        path = get_path(dir)
        for file in glob.glob(os.path.join(path, '*.md')):
            meta = yaml.load(get_yaml(file)[0])

            if 'tags' in meta:
                for tag in meta['tags']:
                    if tag not in all_tags:
                        all_tags.append(tag)
            else:
                raise Exception("Cannot found 'tags' in \
                  post '{}' !".format(file))

    return all_tags


def generate_tag_pages(is_verbose):
    all_tags = get_all_tags()
    tag_path = get_path(TAG_DIR)

    if os.path.exists(tag_path):
        shutil.rmtree(tag_path)

    os.makedirs(tag_path)

    for tag in all_tags:
        tag_page = tag_path + '/' + tag.replace(' ', '-').lower() + '.html'
        with open(tag_page, 'w+') as html:
            html.write("---\n")
            html.write("layout: {}\n".format(TAG_LAYOUT))
            html.write("title: {}\n".format(tag.encode('utf-8')))
            html.write("tag: {}\n".format(tag.encode('utf-8')))
            html.write("---")

            if is_verbose:
                print("[INFO] Created page: " + tag_page)

    print("[INFO] Succeed! {} tag-pages created.".format(len(all_tags)))


def help():
    print("Usage: "
          "python pages_generator.py [ -d | --drafts ] [ -v | --verbose ]\n\n"
          "Optional arguments:\n"
          "-d, --drafts         Enable drafts\n"
          "-v, --verbose        Print verbose logs\n")


def main():
    is_verbose = False

    if len(sys.argv) > 1:
        for arg in sys.argv:
            if arg != sys.argv[0]:
                if arg == '-d' or arg == '--drafts':
                    POSTS_DIR.insert(0, DRAFTS_DIR)
                elif arg == '-v' or arg == '--verbose':
                    is_verbose = True
                else:
                    print("Oops! Unknown argument: '{}'\n".format(arg))
                    help()
                    return

    generate_category_pages(is_verbose)
    generate_tag_pages(is_verbose)


main()
