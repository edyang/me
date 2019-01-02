---
layout: post
title: "彻底卸载 Navicat Premium for Mac"
subtitle: '小计安装过程'
author: "edyang"
header-style: text
tags:
  - 日常
  - mac
---

数据库连接信息存放在

    ~/Library/Application\ Support/PremiumSoft\ CyberTech/preference.plist
可以尝试以下方法，在卸载navicat后将残留文件彻底删除：
打开终端，依次输入以下命令：

    sudo rm -Rf /Applications/Navicat\ Premium.app

    sudo rm -Rf /private/var/db/BootCaches/CB6F12B3-2C14-461E-B5A7-A8621B7FF130/app.com.prect.NavicatPremium.playlist

    sudo rm -Rf ~/Library/Caches/com.apple.helpd/SDMHelpData/Other/English/HelpSDMIndexFile/com.prect.NavicatPremium.help

    sudo rm -Rf ~/Library/Caches/com.apple.helpd/SDMHelpData/Other/zh_CN/HelpSDMIndexFile/com.prect.NavicatPremium.help

    sudo rm -Rf ~/Library/Preferences/com.prect.NavicatPremium.plist 

    sudo rm -Rf ~/Library/Application\ Support/CrashReporter/Navicat\ Premium_54EDA2E9-528D-5778-A528-BBF9A4CE8BDC.plist

    sudo rm -Rf ~/Library/Application\ Support/PremiumSoft\ CyberTech