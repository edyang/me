---
layout: post
title: "Linux tomcat https访问设置"
subtitle: '小计安装过程'
author: "edyang"
header-style: text
tags:
  - 运维
  - 服务器
  - linux
  - ubuntu
  - tomcat
---

记录tomcat https 配置

    keytool -export -trustcacerts -alias tomcat -file server.cer -keystore server.keystore -storepass 900930

    sudo /usr/lib/jvm/jdk7/bin/keytool -import -trustcacerts -alias tomcat -file ./server.cer -keystore /usr/lib/jvm/jdk7/jre/lib/security/cacerts -storepass 900930

## 1.使用jdk工具生成key文件
 
    [plain] view plaincopyprint?
    keytool -genkey -alias tomcat -keyalg RSA -keypass changeit -storepass changeit -keystore server.keystore -validity 3600 
 
## 2.到tomcat/config/server.xml中找到
 
 
    <!-- Define a SSL HTTP/1.1 Connector on port 8443 
        This connector uses the JSSE configuration, when using APR, the  
        connector should be using the OpenSSL style configuration 
        described in the APR documentation --> 
    <!-- 
    <Connector port="8443" protocol="HTTP/1.1" SSLEnabled="true" 
            maxThreads="150" scheme="https" secure="true" 
            clientAuth="false" sslProtocol="TLS" /> 
    --> 
去掉注释,加入key文件配置
 
 
    <Connector port="8443" protocol="HTTP/1.1" SSLEnabled="true" 
            maxThreads="150" scheme="https" secure="true" 
            clientAuth="false" sslProtocol="TLS"  
    keystoreFile="server.keystore"     
    keystorePass="changeit"/> 
 
保存后重启tomcat可通过https://ip:8443/webproject(你的web项目)通过https访问,以上使用8443端口,若改为443在访问时可不加端口，因为443是https默认端口
 
 
强制https访问
 
在tomcat\conf\web.xml中的</welcome-file-list>后面加上以下配置:
 
 
    <login-config> 
        <!-- Authorization setting for SSL --> 
        <auth-method>CLIENT-CERT</auth-method> 
        <realm-name>Client Cert Users-only Area</realm-name> 
    </login-config> 
    <security-constraint> 
        <!-- Authorization setting for SSL --> 
        <web-resource-collection > 
            <web-resource-name >SSL</web-resource-name> 
            <url-pattern>/*</url-pattern> 
        </web-resource-collection> 
        <user-data-constraint> 
            <transport-guarantee>CONFIDENTIAL</transport-guarantee> 
        </user-data-constraint> 
    </security-constraint> 
 
这样输入http://ip:8080/webproject会强制转到https://ip:8443/webproject
 
 
若https端口配置为其它端口了记得把http转接端口一起改了
 
    <Connector port="8080" protocol="HTTP/1.1"  
           connectionTimeout="20000"  
           redirectPort="<span style="color:#FF0000;">8443</span>" URIEncoding="UTF-8" /> 