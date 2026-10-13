---
layout: post
title: 工业镜头选型：研究视野、焦距与光圈
subtitle: 我在比较镜头时，对焦距、光圈与可覆盖范围的关系产生疑问。
date: 2023-08-30 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 工业相机
- 光学
tech_note: true
note_id: lens-focal-length-aperture-fov
source_date: '2026-09-21'
source_dates:
- '2026-09-21'
- '2026-10-08'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: notes
privacy_reviewed: true
permalink: /tech/2026/09/21/lens-focal-length-aperture-fov/
excerpt: 我在比较镜头时，对焦距、光圈与可覆盖范围的关系产生疑问。
archive_date: '2023-08-30'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/lens-focal-length-aperture-fov.svg
---

我在比较镜头时，对焦距、光圈与可覆盖范围的关系产生疑问。研究目标是先判断目标能否进入画面，再看清晰度与曝光，避免看到焦距大或 F 值大就直接推断视野更宽。

## 研究与排查过程

讨论先用传感器尺寸、工作距离和焦距估算视野，再核对厂家工作距离的测量基准、最近对焦、像圈与接口。近距离和广角场景会偏离简单薄透镜模型，因此估算只能筛选候选。之后固定物距，分别调整焦点和光圈，比较中心、边缘以及不同深度。

![工业镜头选型：研究视野、焦距与光圈研究路径示意](/img/tech-notes/lens-focal-length-aperture-fov.svg)

## 涉及的技术与取舍

技术上 F 值近似为焦距除以入瞳直径，数值变大一般表示孔径变小；景深、亮度和衍射需要共同考虑。旋转物体还受到曝光时间造成的运动模糊限制。视野估算不包含全部镜组细节，最终应使用实际目标，在预期运动与照明下验证。

## 这轮研究的结论

结论是焦距回答视野与放大率，光圈参与景深和曝光，两个旋钮承担不同作用。原交流没有统一镜头方案验收，因此不把理论覆盖范围写成实际检出能力。后续需对照最小缺陷和边缘清晰度，再完成选择。

## 参考资料

- [Edmund Optics 视野与焦距](https://www.edmundoptics.com/knowledge-center/application-notes/imaging/understanding-focal-length-and-field-of-view/)
