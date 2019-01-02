---
layout: post
title: "阿里云服务器Ubuntu安装mysql"
subtitle: '小计安装过程'
author: "edyang"
header-style: text
tags:
  - 阿里云
  - 服务器
  - linux
  - ubuntu
  - mysql
---

这里首先吐槽一下阿里云，我作为公司的唯一懂服务器架设的后台开发人员，经再三考究之后选择了阿里云的云服务器。购买成功后就着手准备服务器的环境，因为是java web项目，所以需要安装 JDK7 + Tomcat 7 + mysql + nginx 等软件。当我在阿里云的帮助页面寻找安装教程时，才发现官方竟然只提供了php环境的安装教程，偌大的一个阿里云居然不提供java这么主流的环境安装教程，这让我很是郁闷。
不过还好，既然有php环境的安装教程，那么我只好举一反三，去其糟怕，取其精华。今天介绍的就是 mysql 的安装，希望能帮助到大家。
## 一、先下载mysql软件
这个下载地址是在阿里云php安装脚本中找到的，通过这个地址下载的话，因为是走的阿里云的局域网环境，下载速度应该会相对更快一点。看下图红框显示的速度，我的服务器带宽只有1M哦，这个速度是阿里云内部局域网的速度，总之是非常快了。
运行命令：

    wget http://oss.aliyuncs.com/aliyunecs/onekey/mysql/mysql-5.5.35-linux2.6-x86_64.tar.gz


## 二、解压

    tar zxvf mysql-5.5.35-linux2.6-x86_64.tar.gz  -C /alidata/server/ 

然后改名为mysql

    cd /alidata/server
    mv mysql-5.5.35-linux2.6-x86_64.tar.gz mysql 

## 三、顺序执行以下命令

    groupadd mysql
    useradd -g mysql -s /sbin/nologin mysql
    /alidata/server/mysql/scripts/mysql_install_db --datadir=/alidata/server/mysql/data/ --basedir=/alidata/server/mysql --user=mysql 

执行上一行代码会打印如下图 


然后继续执行以下命令

    chown -R mysql:mysql /alidata/server/mysql/
    chown -R mysql:mysql /alidata/server/mysql/data/
    chown -R mysql:mysql /var/log/mysql
    \cp -f /alidata/server/mysql/support-files/mysql.server /etc/init.d/mysql
    sed -i 's#^basedir=$#basedir=/alidata/server/mysql#' /etc/init.d/mysql
    sed -i 's#^datadir=$#datadir=/alidata/server/mysql/data#' /etc/init.d/mysql
    \cp -f /alidata/server/mysql/support-files/my-medium.cnf /etc/my.cnf
    sed -i 's#skip-locking#skip-external-locking\nlog-error=/var/log/mysql/error.log#' /etc/my.cnf
    chmod 755 /etc/init.d/mysql 



好的，过程中如果提示目录不存在，那么请自行创建目录。
接下来试试启动mysql

    root@AY14061309211937343aZ:/alidata/server/mysql# service mysql start
    Starting MySQL
    ... * 
    root@AY14061309211937343aZ:/alidata/server/mysql# service mysql stop
    Shutting down MySQL
    ... * 

这样的话mysql服务应该就起来了，也能够顺利关闭了。
如果起不来的话：
先修改以下两个变量  

     basedir=  
     datadir=  
     再使用 service mysql start 来尝试启动，

若报错：#Couldn't find MySQL server (/usr/bin/mysqld_safe)，路径不对，不应该到/usr/bin下寻找mysqld_safe，怀疑mysql启动时加载配置文件出错，mysql配置文件的读取顺序为: 

    /etc/my.cnf 
    /etc/mysql/my.cnf 
    /usr/local/mysql/etc/my.cnf 
    ~/.my.cnf  
挨个查看my.cnf文件，发现 /etc/mysql/my.cnf中的以上两个对应变量的值（basedir，datadir）不正确，修改后测试，发现可用service mysql start来启动mysql
或者可直接删掉   /etc/mysql  这个目录！！！！！！
mysql启动后，可以查看下端口，确认mysql已经正常启动

    netstat -tnl|grep 3306


这就是正常启动了。
## 四、增加链接
    ln -s /alidata/server/mysql/bin/mysql /usr/bin
    ln -s /alidata/server/mysql/bin/mysqladmin /usr/bin
以后就可以直接输入mysql -uroot -pabc123abc 就可以连接上了。
## 五、为root用户设置密码
    /alidata/server/mysql/bin/mysqladmin -u root password 'abc123abc'
## 六、用root登陆mysql
    mysql -uroot -pabc123abc

GRANT ALL PRIVILEGES ON .* TO root IDENTIFIED BY "196sf_mysql"
执行以上命令后，客户端工具可以通过远程连接到服务器mysql了,为用户root在所有地方登陆赋予权限，使用密码 abc123abc
注:乱码问题，用客户端工具（我用的是SQLyog）连接到mysql后，发现客户端中的汉字都变成了问号？
如遇乱码？？
可尝试修改/etc/my.cnf

    [mysqld]
    在这里添加以下3行
    character-set-server=utf8
    collation-server = utf8_unicode_ci
    init_connect = 'set collation_connection = utf8_unicode_ci;' 
最后，重启服务器（是Ubuntu重启）乱码问题即可解决