---
layout: post
title: "阿里云服务器Ubuntu安装tomcat"
subtitle: '小计安装过程'
author: "edyang"
header-style: text
tags:
  - 阿里云
  - 服务器
  - linux
  - ubuntu
---

## 一、下载tomcat
可以先下载到本地，然后ftp到服务器
官方 Apache Tomcat 的下载页面(下面的链接是apache自己的镜像服务器的地址，不同网络连接的话，apache会给出不同的镜像地址)：

    http://tomcat.apache.org/download-70.cgi
也可以直接在服务器下载（windows版本的区分32位与64位，ubuntu（linux）版本的不区分）

    wget http://mirrors.hust.edu.cn/apache/tomcat/tomcat-7/v7.0.73/bin/apache-tomcat-7.0.73.tar.gz?crazycache=1
或者可以到我的共享云盘下载
>http://yunpan.cn/Qa4vWeVafiDXn  提取码 ab05
## 二、解压安装
先解压

    tar zxvf apache-tomcat-7.0.55.tar.gz -C /alidata/server/
然后改名为tomcat7

    cd /alidata/server/ 
    mv apache-tomcat-7.0.55.tar.gz tomcat7
更改用户

    cd /alidata/server/tomcat7
    chown -R root .
    chgrp -R root .

## 三、配置环境变量
    vi /etc/profile
在最后面加上如下两句

    CATALINA_HOME=/alidata/server/tomcat7
    export CATALINA_HOME

保存后退出vi 刷新变量使配置立即生效

    source /etc/profile

进入tomcat的bin目录

    cd $CATALINA_HOME/bin

修改catalina.sh

    vi catalina.sh

 
找到这行

    # OS specific support. $var _must_ be set to either true or false. 

在这行下面新增如下配置语句 
指定tomcat的目录以及jdk的目录 
关于ubuntu下jdk的安装请参考 阿里云服务器Ubuntu安装jdk7

    CATALINA_HOME=/alidata/server/tomcat7
    JAVA_HOME=/usr/lib/jvm/jdk7

保存后退出vi 尝试下启动tomcat是否成功
(因为我们本来就在tomcat下的bin目录，所以直接运行startup.sh)

    sh startup.sh  或./startup.sh

## 四、安装tomcat服务 
当前所在目录是tomcat的bin目录哦

    cp catalina.sh /etc/init.d/tomcat

让tomcat在启动服务器时就启动，配置以下语句

    update-rc.d –f tomcat defaults

启动tomcat

    service tomcat start

关闭tomcat

    service tomcat stop

## 五、查看tomcat日志 
当然得保证自己所在目录是tomcat下的logs目录哦 即/alidata/server/tomcat7/logs

    tail -500 catalina.out

ok
