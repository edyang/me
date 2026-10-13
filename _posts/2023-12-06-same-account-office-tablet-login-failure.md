---
layout: post
title: 同一账号异地登录结果不同：研究请求路径
subtitle: 办公室通过远程入口能登录，现场平板却提示用户名或密码错误。
date: 2023-12-06 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Web
- 网络
- 故障排查
tech_note: true
note_id: same-account-office-tablet-login-failure
source_date: '2026-10-12'
source_dates:
- '2026-10-12'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/10/12/same-account-office-tablet-login-failure/
excerpt: 办公室通过远程入口能登录，现场平板却提示用户名或密码错误。
archive_date: '2023-12-06'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/same-account-office-tablet-login-failure.svg
---

办公室通过远程入口能登录，现场平板却提示用户名或密码错误。我想先查两个入口是否真的请求同一个后端，因为统一的页面提示也可能掩盖网络、代理或服务异常。

## 研究与排查过程

方案从页面来源、API 基址、端口和代理路径对照开始，特别检查 localhost 是否在平板上错误地指向自身，以及页面是否来自旧缓存。随后将两端方法、路径、状态码和时间与后端日志对应。无请求时先查地址网络，收到但拒绝再查认证，成功后跳回则查会话状态。

![同一账号异地登录结果不同：研究请求路径研究路径示意](/img/tech-notes/same-account-office-tablet-login-failure.svg)

## 涉及的技术与取舍

技术涉及前端请求定位、反向代理、浏览器存储与鉴权响应分类。HTTP 5xx 或超时不能直接解释成密码错误，办公室成功也不能证明现场使用同一账号库。记录请求时只保留必要字段和是否存在，不公开密码、Cookie、token 或内部地址，避免排查资料成为敏感数据副本。

## 这轮研究的结论

结论是先确定请求到达预期服务，再决定是否重置或检查密码。现有记录只有现象，没有现场请求与后端日志，根因尚未确定。下一步应取得一对同时间操作记录，用实际响应缩小范围，而不是仅凭页面文案判断。
