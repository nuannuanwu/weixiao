Fab
***

简介
====

| 项目使用 `Fabric <http://fabric.readthedocs.org/>`_ 作项目管理辅助工具.
查看已经支持的命令::
    
    fab -l

会有类似的输出::
    
    Available commands:

        bs       后台运行本地开发服务器
        deploy   部署到开发服务器
        doc      生成项目文档. :reset - 清空旧文档
        dump     导出数据库数据到 api/fixtures/kinger_testdata.json
        migrate  将 Model 的结构同步到数据库. 使用 south 组件
        s        运行本地开发服务器
        sae      运行 SAE 模拟环境
        ttt      连接到开发服务器
        update   更新合并开发分支

使用示例
========

* 同步代码::

    fab update

* 提交修改并推送到开发服务器::

    git status
    git add .
    git commit -m "some commints"
    git push

* 同步到 222 开发服务器::

    fab deploy

然后就可以打开 222 测试地址查看变更

.. note:: 部署可能导致项目服务停止工作，需要手动重新启动.
