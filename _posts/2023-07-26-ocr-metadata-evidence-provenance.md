---
layout: post
title: OCR 结果核验：为什么相同字段不能自证正确
subtitle: 图像文件名、底部信息栏和结构化字段给出了相同文本，看起来像多个来源互相验证。
date: 2023-07-26 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- OCR
- 数据质量
- 视觉检测
tech_note: true
note_id: ocr-metadata-evidence-provenance
source_date: '2026-08-31'
source_dates:
- '2026-08-31'
- '2026-10-10'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: notes
privacy_reviewed: true
permalink: /tech/2026/08/31/ocr-metadata-evidence-provenance/
excerpt: 图像文件名、底部信息栏和结构化字段给出了相同文本，看起来像多个来源互相验证。
archive_date: '2023-07-26'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/ocr-metadata-evidence-provenance.svg
---

图像文件名、底部信息栏和结构化字段给出了相同文本，看起来像多个来源互相验证。但我在讨论中指出，如果这些值原本都来自另一次 OCR，那么它们只是同一识别结果的复制，不能当作真值。

## 研究与排查过程

研究先追踪来源，而不是先计算一致次数。一个字段从哪张图、哪个区域产生，是否复用了另一个结果，需要分别记录。元数据可以帮助找到目标，却不能自动证明文本正确。随后把一致性检查与独立核验分开：前者发现冲突，后者需要原始可读区域或独立标注支持。

![OCR 结果核验：为什么相同字段不能自证正确研究路径示意](/img/tech-notes/ocr-metadata-evidence-provenance.svg)

## 涉及的技术与取舍

通用方案使用来源标记与派生关系，保存 source_kind、source_image、region 和 derived_from 等概念。相同 OCR 结果被复制到几个位置时，仍归为同一观测。质量评价同时检查清晰度、目标归属和人工标注，避免多个相关字段给同一个错误增加虚假的可信度。

### 辅助检查示例

以下为通用示例，用于理解上述检查；变量、设备和参数需对应实际环境。

```json
{
  "value": "示例文本",
  "source_kind": "image_ocr",
  "derived_from": "original_observation"
}
```

## 这轮研究的结论

这轮结论是数据一致不等于识别正确。该原则可以用于车牌、条码、编号和票据，但公开笔记只讨论来源追踪，不披露真实图片或业务算法。后续验证应专门加入“错误结果被多个字段共同引用”的样本，检查系统是否仍把它误当作独立证据。
