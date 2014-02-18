现有代码仓库
************

云端仓库
========

**kinger** 项目的代码仓库托管在 `Bitbucket <bitbucket.org>`_ 上

* http 地址: https://bitbucket.org/huanghuibin/kinger
* 代码仓库地址: git@bitbucket.org:huanghuibin/kinger.git
  ::
    git clone git@bitbucket.org:huanghuibin/kinger.git

开发服务器仓库
==============
| 由于 *bitbucket* 的速度很慢，为了加快速度并且优化工作流程。
| 我们在开发服务器上搭建与云端仓库异步跟新的开发仓库.

* 代码仓库地址: git@192.168.1.222:/data0/htdocs/kinger
  ::
    git clone git@192.168.1.222:/data0/htdocs/kinger


工作流程
********

简单步骤
========

1. 所有开发人员在 **dev** 分支(branch) 进行开发
   ::
    git clone git@192.168.1.222:/data0/htdocs/kinger
    git checkout -b dev origin/dev

2. 每个开发人员提交到本地的仓库，累计到一定数量的更改提交后推送到 *开发服务器仓库*
3. 相关人员根据情况到 *222* 服务器将 **dev** 分支合并到 **master** 主分支上.测试人员将测试主分支的代码.
   ::
    git merge dev

4. 定期将所有的变更推送的 *云端仓库*

.. note:: 开发人员推送代码到开发服务器或者要开始新工作的时候，最好更新并 *rebase* 一下其他开发人员的工作. 下面将介绍具体如何操作

.. note:: 一般开发人员不要直接对 *master* 分支直接操作


添加访问权限
============
目前只能通过 `ssh` 方式访问

1. 以 `git` 身份登录开发服务器::
    
    ssh git@192.168.1.222

2. 复制访问者的 **public key** (etc. id_rsa.pub) 到认证列表文件里::

    echo "xxxxxxxxxxxxxxxxxxxx" >> ~/.ssh/authorized_keys

   
如何同步最好
============

由于不停有开发人员向 *开发服务器仓库* 推送数据。所以在你提交前要合并别人的更新.

1. 首先同步仓库
   ::
    git fetch

2. 合并更新
   ::
    git rebase origin/dev

3. 如果没有出现冲突，那么就可以开始工作或者推送代码. 关于 **rebase** 的操作和概念请自行 google.
   当然，如果你不想知道为什么我们现在用 **rebase** 比 **merge** 好，那你就直接.
   ::
    git merge origin/dev
