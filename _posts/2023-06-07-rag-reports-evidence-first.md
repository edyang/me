---
layout: post
title: 研究 RAG 技术报告：把依据与分析过程连起来
subtitle: 整理技术报告时，文件、地图和结构化数据常常分开放，结论要靠人工重新组织。
date: 2023-06-07 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- RAG
- Agent
- 知识管理
tech_note: true
note_id: rag-reports-evidence-first
source_date: '2026-07-19'
source_dates:
- '2026-07-19'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: proposal
privacy_reviewed: true
permalink: /tech/2026/07/19/rag-reports-evidence-first/
excerpt: 整理技术报告时，文件、地图和结构化数据常常分开放，结论要靠人工重新组织。
archive_date: '2023-06-07'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/rag-reports-evidence-first.svg
---

整理技术报告时，文件、地图和结构化数据常常分开放，结论要靠人工重新组织。我希望模型辅助完成报告，但先研究它如何找到正确依据、调用计算工具，再生成可反查的文字。

## 研究与排查过程

思路从证据定位展开：材料保存版本、章节页码、时间范围与相关段落，数据查询保存条件与结果，地图分析保存图层、坐标系与处理过程。接着把每个章节拆成主张、支持证据与待确认项，先审查证据能否支持主张，再组织最终文本。

![研究 RAG 技术报告：把依据与分析过程连起来研究路径示意](/img/tech-notes/rag-reports-evidence-first.svg)

## 涉及的技术与取舍

方案讨论了文档检索、RAGFlow、空间数据库 PostGIS、报告模板与可复现的统计程序。数值统计和空间关系由工具计算，模型负责解释和组合，不在缺乏计算过程时补数字。图表与正文引用同一数据版本，避免模型段落已经更新、附件仍停在旧结果。

## 这轮研究的结论

初步结论是先用一份已完成报告回放，测试能否找回依据、重现计算和定位遗漏。原交流没有完整系统验收，因而这篇属于方案研究。后续衡量检索命中、引用正确和人工修改量，比单纯增加生成字数更有意义。

## 参考资料

- [PostGIS 官方文档](https://postgis.net/documentation/)
- [RAGFlow 官方仓库](https://github.com/infiniflow/ragflow)
