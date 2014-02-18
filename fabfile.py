# -*- coding: utf-8 -*-
from fabric.api import local, task, run, env, hosts
from fabric.context_managers import lcd, cd
import os


def migrate():
    """ 将 Model 的结构同步到数据库. 使用 south 组件"""
    local("./manage.py syncdb")
    local("./manage.py schemamigration kinger --auto")
    local("./manage.py migrate kinger")


def update():
    """ 更新合并开发分支 """
    local("git fetch")
    local("git rebase origin/dev")


def sae():
    """ 运行 SAE 模拟环境 """
    local("dev_server.py --mysql=user:root@192.168.1.222:3306 --storage-path=media")


def s():
    """ 运行本地开发服务器 """
    local("./manage.py runserver")


def bs():
    """ 后台运行本地开发服务器 """
    local('nohup ./manage.py runserver 192.168.1.222:8000 > kinger.log 2>&1 &')


def dump():
    """ 导出数据库数据到 api/fixtures/kinger_testdata.json """
    local("./manage.py dumpdata --indent=4 > api/fixtures/kinger_testdata.json")


def doc(action=None):
    """ 生成项目文档. :reset - 清空旧文档 """
    options = ("reset",)
    if action and action not in options:
        return False
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kinger.settings")
    if action == "reset":
        local("rm doc/build/ -rf")
    local("sphinx-apidoc -o doc/source/api api -f")
    local("sphinx-apidoc -o doc/source/kinger kinger -f")
    local("sphinx-apidoc -o doc/source/manage manage -f")
    with lcd("doc"):
        local("make html")


def ttt():
    """ 连接到开发服务器 """
    local("ssh root@192.168.1.222")


@hosts('root@192.168.1.222')
def deploy(action=None):
    """ 部署到开发服务器 """
    options = ("doc", "all")
    if action and action not in options:
        return False
    code_dir = "/data0/htdocs/kinger"
    with cd(code_dir):
        run("git merge dev")
        run("touch index.wsgi")
        if action in ("doc", "all"):
            run("fab doc:reset")
