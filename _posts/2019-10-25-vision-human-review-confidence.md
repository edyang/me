---
layout: post
title: 视觉应用：低置信度结果怎样进入人工复核
subtitle: 让模型必须给出一个确定答案，会把不确定输入包装成业务事实。
date: 2019-10-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- YOLOv3
- 机器视觉
tech_note: true
note_id: vision-human-review-confidence
permalink: /tech/2019/10/25/vision-human-review-confidence/
excerpt: 让模型必须给出一个确定答案，会把不确定输入包装成业务事实。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/vision-human-review-confidence.svg
technology_since: '2018-05-06'
---

让模型必须给出一个确定答案，会把不确定输入包装成业务事实。需要保留待复核状态。

本文使用2018 年固定 Darknet 提交、YOLOv3 与独立文档数据划分。继续研究检测模型时，先保证数据定义、预处理和评估口径稳定。文中方法和预期不代表已经获得某个准确率或部署成绩，真实结论必须来自记录完整的实验。

## 1. 从现象推到机制

复核触发可基于缺目标、多候选、质量异常和分数区间，但规则要由真实错误分析支持。人工界面展示原图、候选框与来源页，不能只给一个脱离上下文的标签。确认结果与模型原始输出分别保存。

![视觉应用：低置信度结果怎样进入人工复核的处理、反馈与观察关系](/img/tech-notes/vision-human-review-confidence.svg)

图中的四个节点分别表示原始输出、分流规则、人工界面、确认结果。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

为合成文档设计可接受、待复核和无法处理三种结果。人工修改保留版本与原因，后续回流仍需去重和授权。

```text
model_output -> immutable raw result
review_rule -> accepted / needs_review / unsupported
review_ui -> source page + boxes + uncertainty
confirmed_result -> reviewer decision linked to raw output
```

每次只改变一组关键因素，保存配置、权重、数据清单与输出。训练、验证和测试职责分离，难例分析保留匿名原始证据，不通过删除失败样本改善表面指标。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 没有检测到标题 | 应按业务规则进入缺失处理 |
| 出现多个接近候选 | 不能随意挑一个当事实 |
| 人工修改模型结论 | 原始结果仍需可追溯 |

### 对照 1：没有检测到标题

应按业务规则进入缺失处理。观察时记录原页与模型原始输出。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：出现多个接近候选

不能随意挑一个当事实。观察时记录候选列表与选择依据。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：人工修改模型结论

原始结果仍需可追溯。观察时记录确认版本与修改原因。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

人工复核也可能出错，应定义抽查与争议处理。不能把有人工按钮就表述为结果完全可靠。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“人工修改模型结论”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [视觉迭代：误检样本怎样进入下一轮数据](/tech/2019/10/05/vision-hard-negative-feedback/)
- [视觉泛化：换扫描仪后效果为何可能变化](/tech/2019/10/15/vision-domain-shift-scanner/)

## 参考资料

1. [YOLOv3 论文](https://arxiv.org/abs/1804.02767)
2. [Darknet 历史实现](https://github.com/pjreddie/darknet/tree/f6d861736038da22c9eb0739dca84003c5a5e275)
3. [OpenCV 3.4.0](https://docs.opencv.org/3.4.0/)
