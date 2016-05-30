#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from optparse import OptionParser
from urllib.parse import urlparse
from services.import_services import export_entities


usage = "usage: %prog -t target -c content_types"
option_parser = OptionParser(usage)
option_parser.add_option("-t", "--target",
                     dest="target",
                     help="specify the path of the output directory",
                     metavar="PATH",
                     default=None)
option_parser.add_option("-c", "--content_types",
                     dest="content_types",
                     help="specify content types to import",
                     metavar="PATH",
                     default=None)
(options, args) = option_parser.parse_args()
target = options.target
content_types = options.content_types
if not target or not content_types:
    option_parser.error("you should provide options -t and -c")

content_types = content_types.split(',')
target_path = urlparse(target)
final_path = os.path.abspath(os.path.join(
                                  target_path.netloc, target_path.path))
if os.path.exists(final_path):
    os.remove(final_path)

export_entities(content_types, target)
