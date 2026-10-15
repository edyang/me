---
layout: post
title: 视觉训练研究：负样本与类别不均衡怎样观察
subtitle: 多数页面没有印章，少数页面有多个印章。
date: 2019-06-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- YOLOv3
- 机器视觉
tech_note: true
note_id: vision-class-imbalance-negative
permalink: /tech/2019/06/15/vision-class-imbalance-negative/
excerpt: 多数页面没有印章，少数页面有多个印章。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/vision-class-imbalance-negative.svg
technology_since: '2018-05-06'
---

多数页面没有印章，少数页面有多个印章。只看总损失，很难知道少数类是否被学到。

本文使用2018 年固定 Darknet 提交、YOLOv3 与独立文档数据划分。继续研究检测模型时，先保证数据定义、预处理和评估口径稳定。文中方法和预期不代表已经获得某个准确率或部署成绩，真实结论必须来自记录完整的实验。

## 1. 从现象推到机制

样本数量、目标数量和难度分布需要分别统计。负样本能帮助抑制红字等误检，但标注漏掉的真实目标会被错误当成背景。重采样可以改变训练频率，也可能增加对少量样本的记忆。

![视觉训练研究：负样本与类别不均衡怎样观察的处理、反馈与观察关系](/img/tech-notes/vision-class-imbalance-negative.svg)

图中的四个节点分别表示数据统计、负样本审查、训练采样、分类评估。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

按类别和来源建立统计表，先复核疑似负样本。固定测试集中保留真实比例，再单独报告少数类表现。

```text
count images by source and class presence
count objects by class and size
review negatives for missing annotations
change sampling policy only in training
report per-class precision and recall
```

每次只改变一组关键因素，保存配置、权重、数据清单与输出。训练、验证和测试职责分离，难例分析保留匿名原始证据，不通过删除失败样本改善表面指标。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 负样本包含漏标印章 | 会提供矛盾监督 |
| 少数类重复采样很多次 | 不等于增加了真实多样性 |
| 总体指标很高 | 仍可能掩盖少数类失败 |

### 对照 1：负样本包含漏标印章

会提供矛盾监督。观察时记录原图复核与标签完整性。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：少数类重复采样很多次

不等于增加了真实多样性。观察时记录独立原件数量与重复次数。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：总体指标很高

仍可能掩盖少数类失败。观察时记录每类样本量和错误类型。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

数据比例要接近目标用途，优化采样也应保留记录。不能为了提高测试分数，删掉业务中真实存在的大量负页。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“总体指标很高”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [YOLOv3 文档研究：锚框要与目标尺寸分布匹配](/tech/2019/06/05/yolov3-anchor-document-shapes/)
- [视觉训练研究：文档增强要像真实成像](/tech/2019/06/25/vision-augmentation-document-realism/)

## 参考资料

1. [YOLOv3 论文](https://arxiv.org/abs/1804.02767)
2. [Darknet 历史实现](https://github.com/pjreddie/darknet/tree/f6d861736038da22c9eb0739dca84003c5a5e275)
3. [OpenCV 3.4.0](https://docs.opencv.org/3.4.0/)
