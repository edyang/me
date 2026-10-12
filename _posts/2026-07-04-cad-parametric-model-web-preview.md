---
layout: post
title: 从工程图到网页三维预览：参数化模型应当保留
subtitle: 模型展示文件与可修改的工程模型用途不同，图像推断出的尺寸也需要校验。
date: 2026-07-04 08:00:00 +0800
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
updated_at: '2026-10-12T12:51:43+08:00'
verification: proposal
privacy_reviewed: true
permalink: /tech/2026/07/04/cad-parametric-model-web-preview/
excerpt: 模型展示文件与可修改的工程模型用途不同，图像推断出的尺寸也需要校验。
---

把二维图纸转换成三维模型再放到网页展示，是一条可拆分的工作链。识别图纸、建立参数化实体、导出展示格式和网页渲染，不宜挤进一个无法复查的黑盒步骤。

## 先明确输入的可信度

CAD 源文件可以提供结构化几何；PDF 和图片更偏向视觉表达。模型从图片推断出的关系应当标记不确定项，尺寸、单位和视图对应需要人工核验，不能把渲染效果当成工程精度。

## 先生成可改的工程模型

参数化模型保存尺寸与构造关系，便于修改。展示格式适合传输和浏览，但往往不能替代工程建模源。可以同时保存参数表、建模脚本、STEP 与网页使用的 GLB。

```text
输入图纸 → 尺寸与关系检查 → 参数化建模 → 实体校验
实体校验后分别导出工程交换格式与网页展示格式
```

## 网页端关注另一组问题

网页预览要处理单位、模型朝向、相机初始位置、网格规模和材料。显示出来只是最低要求；还要检查尺度是否正确、零件是否缺失、加载是否过慢。

原交流讨论过 LLM/VLM、CadQuery/FreeCAD 与 Three.js 的组合，但没有工程级自动转换验收记录。因此这里保留的是方案拆分，不把概念验证等同于可直接生产的图纸转换工具。

## 参考资料

- [CadQuery 导出文档](https://cadquery.readthedocs.io/en/latest/importexport.html)
- [Three.js GLTFLoader](https://threejs.org/docs/#examples/en/loaders/GLTFLoader)
