---
layout: post
title: YOLOv3 文档研究：锚框要与目标尺寸分布匹配
subtitle: 自然图像的默认锚框未必适合宽标题和小印章。
date: 2019-06-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- YOLOv3
- 机器视觉
tech_note: true
note_id: yolov3-anchor-document-shapes
permalink: /tech/2019/06/05/yolov3-anchor-document-shapes/
excerpt: 自然图像的默认锚框未必适合宽标题和小印章。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/yolov3-anchor-document-shapes.svg
technology_since: '2018-05-06'
---

自然图像的默认锚框未必适合宽标题和小印章。先看标注尺寸分布，再考虑调整。

本文使用2018 年固定 Darknet 提交、YOLOv3 与独立文档数据划分。继续研究检测模型时，先保证数据定义、预处理和评估口径稳定。文中方法和预期不代表已经获得某个准确率或部署成绩，真实结论必须来自记录完整的实验。

## 1. 从现象推到机制

锚框提供预测的初始几何参考，目标宽高应在实际网络输入尺度下统计。聚类指标与普通欧氏距离不同，长宽比分布和小目标比例都会影响结果。换锚框后还要保持掩码与检测层配置一致。

![YOLOv3 文档研究：锚框要与目标尺寸分布匹配的处理、反馈与观察关系](/img/tech-notes/yolov3-anchor-document-shapes.svg)

图中的四个节点分别表示训练标注、输入尺度、锚框提案、独立比较。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

只用训练集标注统计宽高，验证集不参与参数拟合。先画尺寸与比例分布，再比较默认和自定义方案的独立结果。

```text
training boxes -> map to actual input geometry
width / height distribution -> inspect long titles and small seals
anchor proposal -> update anchors and masks consistently
evaluate -> fixed validation set and thresholds
```

每次只改变一组关键因素，保存配置、权重、数据清单与输出。训练、验证和测试职责分离，难例分析保留匿名原始证据，不通过删除失败样本改善表面指标。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 统计用原图尺寸但训练缩放不同 | 得到的锚框可能不匹配实际输入 |
| 验证集也参与聚类 | 会侵蚀独立调参边界 |
| 只改 anchors 未检查 mask | 检测头可能使用错误分组 |

### 对照 1：统计用原图尺寸但训练缩放不同

得到的锚框可能不匹配实际输入。观察时记录预处理后的目标尺度。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：验证集也参与聚类

会侵蚀独立调参边界。观察时记录拟合数据清单。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：只改 anchors 未检查 mask

检测头可能使用错误分组。观察时记录各头掩码与输出结构。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

锚框优化不能补回缩放后丢失的像素。目标太小时还需要评估输入分辨率、裁剪和成像条件。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“只改 anchors 未检查 mask”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [视觉训练研究：负样本与类别不均衡怎样观察](/tech/2019/06/15/vision-class-imbalance-negative/)
- [视觉训练研究：文档增强要像真实成像](/tech/2019/06/25/vision-augmentation-document-realism/)

## 参考资料

1. [YOLOv3 论文](https://arxiv.org/abs/1804.02767)
2. [Darknet 历史实现](https://github.com/pjreddie/darknet/tree/f6d861736038da22c9eb0739dca84003c5a5e275)
3. [OpenCV 3.4.0](https://docs.opencv.org/3.4.0/)
