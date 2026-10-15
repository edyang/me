---
layout: post
title: 文档小目标研究：输入缩小后还剩多少像素
subtitle: 原图里清楚的印章，缩到网络输入后只剩很少像素，模型再复杂也无法利用已经丢掉的细节。
date: 2019-07-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- YOLOv3
- 机器视觉
tech_note: true
note_id: vision-small-object-document-scale
permalink: /tech/2019/07/15/vision-small-object-document-scale/
excerpt: 原图里清楚的印章，缩到网络输入后只剩很少像素，模型再复杂也无法利用已经丢掉的细节。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/vision-small-object-document-scale.svg
technology_since: '2018-05-06'
---

原图里清楚的印章，缩到网络输入后只剩很少像素，模型再复杂也无法利用已经丢掉的细节。

本文使用2018 年固定 Darknet 提交、YOLOv3 与独立文档数据划分。继续研究检测模型时，先保证数据定义、预处理和评估口径稳定。文中方法和预期不代表已经获得某个准确率或部署成绩，真实结论必须来自记录完整的实验。

## 1. 从现象推到机制

先按实际缩放比例计算目标宽高，再看是否足以支持类别与边界判断。提高输入分辨率增加计算和内存，局部裁剪则增加覆盖与坐标归并成本。应在相同数据上比较整体任务效果。

![文档小目标研究：输入缩小后还剩多少像素的处理、反馈与观察关系](/img/tech-notes/vision-small-object-document-scale.svg)

图中的四个节点分别表示原图目标、输入缩放、方案比较、资源效果。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

统计原图与网络图中的目标尺寸分布，分别保存小目标失败例。不要只给出原图分辨率而忽略真正进入模型的尺寸。

```text
scale = min(network_width / image_width, network_height / image_height)
target_width_in_network = original_box_width * scale
target_height_in_network = original_box_height * scale
compare full-page, higher-resolution and tiled approaches
```

每次只改变一组关键因素，保存配置、权重、数据清单与输出。训练、验证和测试职责分离，难例分析保留匿名原始证据，不通过删除失败样本改善表面指标。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 整页分辨率很高但输入很小 | 细节仍可能在缩放时丢失 |
| 提高网络尺寸 | 资源成本与效果都需观察 |
| 采用局部裁剪 | 需要覆盖边界与全局坐标恢复 |

### 对照 1：整页分辨率很高但输入很小

细节仍可能在缩放时丢失。观察时记录网络图中的实际目标像素。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：提高网络尺寸

资源成本与效果都需观察。观察时记录内存吞吐和检测结果。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：采用局部裁剪

需要覆盖边界与全局坐标恢复。观察时记录切片范围与原图映射。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

小目标还受模糊和对比度影响，不能只按像素宽度设万能阈值。成像条件改善有时比继续调网络更有效。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“采用局部裁剪”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [视觉评估研究：阈值选择要对应业务代价](/tech/2019/07/05/vision-threshold-pr-curve/)
- [大幅文档切片：边缘目标和重复框怎样合并](/tech/2019/07/25/vision-tiling-boundary-merge/)

## 参考资料

1. [YOLOv3 论文](https://arxiv.org/abs/1804.02767)
2. [Darknet 历史实现](https://github.com/pjreddie/darknet/tree/f6d861736038da22c9eb0739dca84003c5a5e275)
3. [OpenCV 3.4.0](https://docs.opencv.org/3.4.0/)
