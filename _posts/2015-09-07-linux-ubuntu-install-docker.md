---
layout: post
title: "Ubuntu 12.4 安装Docker"
subtitle: '小计安装过程'
author: "edyang"
header-style: text
tags:
  - 运维
  - 服务器
  - linux
  - ubuntu
  - docker
---

看下我们的Ubuntu版本命令：

    root@linuxidc:~# cat /etc/issueUbuntu 12.04.5 LTS \n \l

再来看下内核，命令：

    root@linuxidc:~# uname -r3.2.0-67-generic

很不幸我的内核版本没有达到官方要求，没关系，我们接下来用下面的命令升级内核：

    sudo apt-get install linux-image-generic-lts-raring linux-headers-generic-lts-raring
    sudo apt-get install --install-recommends linux-generic-lts-raring xserver-xorg-lts-raring libgl1-mesa-glx-lts-raring


未完待续