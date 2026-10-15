---
layout: post
title: 视觉评估研究：阈值选择要对应业务代价
subtitle: 同一模型把阈值调高，误检少了，漏检可能同时增加。
date: 2019-07-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- YOLOv3
- 机器视觉
tech_note: true
note_id: vision-threshold-pr-curve
permalink: /tech/2019/07/05/vision-threshold-pr-curve/
excerpt: 同一模型把阈值调高，误检少了，漏检可能同时增加。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/vision-threshold-pr-curve.svg
technology_since: '2018-05-06'
---

同一模型把阈值调高，误检少了，漏检可能同时增加。不能只展示其中有利的一项。

本文使用2018 年固定 Darknet 提交、YOLOv3 与独立文档数据划分。继续研究检测模型时，先保证数据定义、预处理和评估口径稳定。文中方法和预期不代表已经获得某个准确率或部署成绩，真实结论必须来自记录完整的实验。

## 1. 从现象推到机制

对固定预测结果扫置信度阈值，可以观察精确率与召回率的变化。不同类别的代价可能不同，标题漏检和印章误检不一定采用同一工作点。检测分数也不是经校准的业务风险概率。

![视觉评估研究：阈值选择要对应业务代价的处理、反馈与观察关系](/img/tech-notes/vision-threshold-pr-curve.svg)

图中的四个节点分别表示固定预测、阈值扫描、错误代价、独立报告。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

用固定验证集选择候选工作点，再在独立测试集报告。记录匹配 IoU、类别规则和样本量，避免换口径比较。

```text
for threshold in predefined_values:
    filter predictions
    perform class-aware one-to-one matching
    report TP, FP, FN and per-class metrics
select by agreed business error cost
```

每次只改变一组关键因素，保存配置、权重、数据清单与输出。训练、验证和测试职责分离，难例分析保留匿名原始证据，不通过删除失败样本改善表面指标。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 只提高阈值报告误检下降 | 应同时展示漏检变化 |
| 不同类别共用一个工作点 | 可能不符合各自代价 |
| 把分数当正确概率 | 需要另行校准证据 |

### 对照 1：只提高阈值报告误检下降

应同时展示漏检变化。观察时记录同一清单下的 TP FP FN。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：不同类别共用一个工作点

可能不符合各自代价。观察时记录按类别拆分的错误影响。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：把分数当正确概率

需要另行校准证据。观察时记录评分定义与真实统计。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

工作点不是永久常量。输入分布变化后，应重新验证其适用性，同时保留旧版本和选择依据。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“把分数当正确概率”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [文档小目标研究：输入缩小后还剩多少像素](/tech/2019/07/15/vision-small-object-document-scale/)
- [大幅文档切片：边缘目标和重复框怎样合并](/tech/2019/07/25/vision-tiling-boundary-merge/)

## 参考资料

1. [YOLOv3 论文](https://arxiv.org/abs/1804.02767)
2. [Darknet 历史实现](https://github.com/pjreddie/darknet/tree/f6d861736038da22c9eb0739dca84003c5a5e275)
3. [OpenCV 3.4.0](https://docs.opencv.org/3.4.0/)
