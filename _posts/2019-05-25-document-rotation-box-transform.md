---
layout: post
title: 文档视觉：旋转图片时标注框也要一起旋转
subtitle: 增强后的图片方向正确，标签仍留在旧位置，模型就会被错误监督。
date: 2019-05-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- OpenCV
- 文档视觉
tech_note: true
note_id: document-rotation-box-transform
permalink: /tech/2019/05/25/document-rotation-box-transform/
excerpt: 增强后的图片方向正确，标签仍留在旧位置，模型就会被错误监督。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/document-rotation-box-transform.svg
technology_since: '2017-12-22'
---

增强后的图片方向正确，标签仍留在旧位置，模型就会被错误监督。图像和几何必须同步变换。

本文使用OpenCV 3.4 与合成几何标尺图。图像预处理会改变坐标，模型结果要回到业务使用的原图基准。本文保存每一步尺寸和变换，不凭最终框看起来大致正确就认定映射无误。

## 1. 从现象推到机制

旋转后的矩形通常不再轴对齐，需要先变换四个角，再按标注约定生成外接框。是否扩大画布会改变平移项，边缘裁剪还会改变可见面积。只旋转中心点和保持宽高不变不够。

![文档视觉：旋转图片时标注框也要一起旋转的处理、反馈与观察关系](/img/tech-notes/document-rotation-box-transform.svg)

图中的四个节点分别表示原始框、共同变换、外接范围、可见检查。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

用已知角点的矩形验证仿射矩阵，再绘制变换后多边形和外接框。大角度增强是否合理要服从真实输入分布。

```text
box -> four corner points
apply same affine matrix as image
if expanded canvas -> include translated origin
new axis-aligned box -> min/max transformed corners
clip and review visibility policy
```

先用已知位置的矩形和标尺做正反向检查，再使用匿名文档。原图、处理图和结果分别保存，重复压缩与插值会影响细节，不能无记录地覆盖源文件。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 只变换中心点 | 框的宽高和范围可能错误 |
| 旋转时扩大画布 | 标签还要包含新增平移 |
| 大部分目标被裁出画面 | 是否保留标签要有统一规则 |

### 对照 1：只变换中心点

框的宽高和范围可能错误。观察时记录四角实际位置与新外接框。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：旋转时扩大画布

标签还要包含新增平移。观察时记录真实图像变换矩阵。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：大部分目标被裁出画面

是否保留标签要有统一规则。观察时记录可见比例与标注策略。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

外接框会随旋转增加背景区域，可能影响长条标题训练。需要在验证集上检查增强是否真正有益，而不是默认越多越好。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“大部分目标被裁出画面”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [视觉几何：等比例缩放补边后的框怎样还原](/tech/2019/05/05/vision-letterbox-inverse-mapping/)
- [文档视觉：透视矫正需要可靠的四角对应](/tech/2019/05/15/document-perspective-rectification/)

## 参考资料

1. [OpenCV 3.4.0 几何变换](https://docs.opencv.org/3.4.0/da/d54/group__imgproc__transform.html)
2. [OpenCV 3.4.0 文档](https://docs.opencv.org/3.4.0/)
