---
layout: post
title: OCR 结果不能自证正确：相同字符串未必是独立证据
subtitle: 文件名、覆盖文字和字段值，可能都来自同一次识别。比较它们相同，不能证明识别正确。
date: 2026-08-31 08:00:00 +0800
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
updated_at: '2026-10-12T12:51:43+08:00'
verification: notes
privacy_reviewed: true
permalink: /tech/2026/08/31/ocr-metadata-evidence-provenance/
excerpt: 文件名、覆盖文字和字段值，可能都来自同一次识别。比较它们相同，不能证明识别正确。
---

处理带文字信息的图像时，很容易把文件名、图像底栏和结构化字段当成三个来源。如果它们实际上来自同一 OCR 结果，三个字符串完全相同，也只说明复制一致。

## 来源比字段名称更重要

元数据可以辅助定位目标，但不能自动成为真值。独立证据应来自不同的观测或可信标注。判断是否独立，需要追踪字段从哪里生成、经过哪些转换，以及是否引用了另一个识别结果。

![数据来源一致与独立验证的区别](/img/tech-notes/evidence-provenance.svg)

## 给结果保存来源标记

通用数据处理中，可以记录 `source_kind`、`source_image`、`region` 和 `derived_from`。这里列出的是示意字段，不涉及任何产品接口。若某个字段复用了另一个结果，应明确记录复用关系。

```json
{
  "value": "示例文本",
  "source_kind": "image_ocr",
  "derived_from": "original_observation"
}
```

## 一致性与正确性分别评价

一致性检查可以发现字段之间冲突，却不能单独证明正确。质量评估仍需查看原始图像是否清晰、目标归属是否明确，以及独立人工标注是否支持该结果。

这条经验适用于车牌、条码、设备编号和票据字段。本文只分享公开通用的数据质量原则，不公开业务规则、实际证据图、具体算法组合和人员信息。
