#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

# dev_server.py --mysql=root:111111@192.168.1.222:3306 --storage-path=/data0/htdocs/storage/data --port=8888
app_root = os.path.dirname(__file__)

# 两者取其一
sys.path.append(os.path.join(app_root, 'system'))
# sys.path.insert(0, os.path.join(app_root, 'system.bundle.zip'))

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kinger.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
