---
layout: post
title: 自动发布文章：统一内容源与最终文件校验都要有
subtitle: 发布任务受理、仓库提交与线上内容可见，应当分别记录。
date: 2026-09-23 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Agent
- 自动化
- GitHub
tech_note: true
note_id: article-publishing-package-hash
source_date: '2026-09-23'
source_dates:
- '2026-09-23'
- '2026-10-09'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-12T12:51:43+08:00'
verification: notes
privacy_reviewed: true
permalink: /tech/2026/09/23/article-publishing-package-hash/
excerpt: 发布任务受理、仓库提交与线上内容可见，应当分别记录。
---

同一篇文章要发到多个入口时，若每个平台各维护一份源，修改很容易漏同步。先保留唯一的图文内容源，再由适配层处理平台差异，可以减少内容漂移。

## 稿件、页面和素材保留关联

内容包应明确正文来源、标题、摘要、标签和图片。页面构建完成后再计算最终文件摘要，避免摘要绑定的是构建前内容。图片也要能完整解码，不能仅凭扩展名判断。

## 状态不能只叫成功或失败

稿件准备、已提交、进入草稿、公开发布和线上核验，描述的是不同阶段。保存每阶段的真实回执；未知状态先查询，避免盲目重复发送。

## 去重应使用稳定内容标识

同一篇内容更新时保留稳定 ID 与 URL，记录修改时间。重试任务要复用内容 ID，避免每次失败都创建新文章。历史补档还应保留原始讨论日期，与实际发布日期分开。

## 发布后检查读者真正看到的内容

核对文章 URL、标题、日期、正文片段和图片地址。仓库有文件不代表站点已经部署；文章可打开但图片丢失，也不算完整发布。

本文是通用发布工程经验，不公开平台账号、投递接口或内部内容包结构。将生成、提交与部署分开记录，能够让自动任务更容易恢复。

## 参考资料

- [GitHub Pages 与 Jekyll](https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll/about-github-pages-and-jekyll)
