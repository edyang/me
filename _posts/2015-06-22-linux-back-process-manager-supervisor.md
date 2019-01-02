---
layout: post
title: "Linux后台进程管理利器：supervisor"
subtitle: '小计安装过程'
author: "edyang"
header-style: text
tags:
  - 运维
  - 服务器
  - linux
  - ubuntu
---

Linux的后台进程运行有好几种方法，例如nohup，screen等，但是，如果是一个服务程序，要可靠地在后台运行，我们就需要把它做成daemon，最好还能监控进程状态，在意外结束时能自动重启。
supervisor就是用Python开发的一套通用的进程管理程序，能将一个普通的命令行进程变为后台daemon，并监控进程状态，异常退出时能自动重启。
安装supervisor

Debian / Ubuntu可以直接通过apt安装：

    # apt-get install supervisor

然后，给我们自己开发的应用程序编写一个配置文件，让supervisor来管理它。每个进程的配置文件都可以单独分拆，放在/etc/supervisor/conf.d/目录下，以.conf作为扩展名，例如，app.conf定义了一个gunicorn的进程：

    [program:app]
    command=/usr/bin/gunicorn -w 1 wsgiapp:application
    directory=/srv/www
    user=www-data

其中，进程app定义在[program:app]中，command是命令，directory是进程的当前目录，user是进程运行的用户身份。
重启supervisor，让配置文件生效，然后运行命令supervisorctl启动进程：

    # supervisorctl start app

停止进程：

    # supervisorctl stop app

如果要在命令行中使用变量，就需要自己先编写一个shell脚本：

    #!/bin/sh
    /usr/bin/gunicorn -w `grep -c ^processor /proc/cpuinfo` wsgiapp:application

然后，加上x权限，再把command指向该shell脚本即可。
supervisor还有许多选项，默认的autorestart为unexpected（异常退出），具体请参考supervisor文档。