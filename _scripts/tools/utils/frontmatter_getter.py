#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Read the posts and return a tuple that consisting of
Front Matter and its line number.
© 2018-2019 Cotes Chung
MIT License
'''


def get_yaml(path):
    end = False
    yaml = ""
    num = 0

    with open(path, 'r') as f:
        for line in f.readlines():
            if line.strip() == '---':
                if end:
                    break
                else:
                    end = True
                    continue
            else:
                num += 1

            yaml += line

    return yaml, num
