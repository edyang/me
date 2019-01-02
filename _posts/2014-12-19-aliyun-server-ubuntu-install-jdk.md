---
layout: post
title: "阿里云服务器Ubuntu安装jdk7"
subtitle: '小计安装过程'
author: "edyang"
header-style: text
tags:
  - 阿里云
  - 服务器
  - linux
  - ubuntu
  - jdk
---

## 一、下载jdk
可以先下载到本地，然后ftp到服务器
官方Oracle的下载页面：
>http://www.oracle.com/technetwork/java/javase/downloads/jdk7-downloads-1880260.html

也可以直接在服务器下载（请区分64位的jdk还是32位的jdk，本例是64位jdk，如果需要32位jdk请留言，我会回复）

    wget http://download.oracle.com/otn-pub/java/jdk/7u79-b15/jdk-7u79-linux-x64.tar.gz?AuthParam=1481610758_ecadd4da30283185ac4a5efb872b0ff7 

写这篇文章的时候发现官网的下载页面可以打开，但是无法下载jdk，这样的话最好用迅雷到官方的下载页面先下载下来，然后再ftp到服务器上。或者可以到我的共享云盘下载

>http://yunpan.cn/Qa9pJCiXLCX7V  提取码 983c
## 二、解压安装
先建jdk的安装目录
    mkdir /usr/lib/jvm

再解压jdk到安装目录
    tar zxvf jdk-7u67-linux-x64.tar.gz  -C /usr/lib/jvm

然后改名为jdk7
    cd /usr/lib/jvm
    mv jdk-7u67-linux-x64.tar.gz jdk7

## 三、配置环境变量

    vi ~/.bashrc

在该文件最底部新增以下配置

    export JAVA_HOME=/usr/lib/jvm/jdk7 
    export JRE_HOME=${JAVA_HOME}/jre  
    export CLASSPATH=.:${JAVA_HOME}/lib:${JRE_HOME}/lib  
    export PATH=${JAVA_HOME}/bin:$PATH

保存后退出vi编辑，然后执行如下命令，使环境变量的配置立即生效。

    source ~/.bashrc


## 四、安装完毕，测试是否成功 键入命令

    java -version

如果出来如截图，则代表安装jdk7成功。