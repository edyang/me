---
layout: post
title: 研究二维图纸转三维模型与网页展示
subtitle: 我希望把二维图纸变成可修改的三维模型，再放到网页中旋转查看。
date: 2023-05-24 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- CAD
- 三维
- 软件设计
tech_note: true
note_id: cad-parametric-model-web-preview
source_date: '2026-07-04'
source_dates:
- '2026-07-04'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: proposal
privacy_reviewed: true
permalink: /tech/2026/07/04/cad-parametric-model-web-preview/
excerpt: 我希望把二维图纸变成可修改的三维模型，再放到网页中旋转查看。
archive_date: '2023-05-24'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/cad-parametric-model-web-preview.svg
---

我希望把二维图纸变成可修改的三维模型，再放到网页中旋转查看。研究开始时就发现，工程几何正确和网页视觉漂亮是两个评价对象，不能用一次渲染成功替代尺寸校验。

## 研究与排查过程

讨论先区分 CAD 源文件、PDF 和图片能提供的依据。结构化 CAD 更容易取到几何，而图片主要依靠视图和尺寸推断，需要标记不确定项。方案先核对单位、尺寸和对应视图，再建立参数化实体，检查缺失构件与实体有效性，最后导出浏览器展示模型。

![研究二维图纸转三维模型与网页展示研究路径示意](/img/tech-notes/cad-parametric-model-web-preview.svg)

## 涉及的技术与取舍

涉及的技术包括 LLM/VLM 辅助理解、CadQuery 或 FreeCAD 参数化建模、STEP 工程交换与 GLB 网格展示，网页侧采用 Three.js 加载。尺寸表和建模脚本保存工程关系，GLB 则服务加载和交互；还需控制三角面数量、模型方向、材质和相机初始位置。

### 辅助检查示例

以下为通用示例，用于理解上述检查；变量、设备和参数需对应实际环境。

```text
输入图纸 → 尺寸与关系检查 → 参数化建模 → 实体校验
实体校验后分别导出工程交换格式与网页展示格式
```

## 这轮研究的结论

研究结论是保留工程源与展示文件两条输出，先做简单零件的可复现转换，再逐步扩大复杂度。原交流没有工程级自动转换验收，因此不能称为任意图纸自动建模。下一轮最值得检查的是尺寸误差、缺失零件和人工修正量，而不是页面是否能转动。

## 参考资料

- [CadQuery 导出文档](https://cadquery.readthedocs.io/en/latest/importexport.html)
- [Three.js GLTFLoader](https://threejs.org/docs/#examples/en/loaders/GLTFLoader)
