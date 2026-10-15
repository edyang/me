---
layout: post
title: 视觉模型交付：权重、阈值和数据口径一起版本化
subtitle: 同一个权重文件换了阈值，业务结果就可能变化。
date: 2018-12-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Darknet
- 机器视觉
tech_note: true
note_id: vision-model-release-record
permalink: /tech/2018/12/25/vision-model-release-record/
excerpt: 同一个权重文件换了阈值，业务结果就可能变化。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/vision-model-release-record.svg
technology_since: '2018-05-06'
---

同一个权重文件换了阈值，业务结果就可能变化。模型版本不能只用文件名表示。

本文使用原版 Darknet 固定历史提交、YOLOv2/YOLOv3 与演示图片。目标检测回答对象类别与位置，不自动识别全部文字或判断印章真伪。文中的训练与部署方案属于可复现方法，没有给出未经测试的准确率、速度或客户验收成绩。

## 1. 从现象推到机制

完整发布单元应包含预处理、网络配置、权重、类别顺序、阈值与后处理规则。数据集和评估口径也要能追溯。升级时对照固定样本和难例，判断变化来自模型还是处理流程。

![视觉模型交付：权重、阈值和数据口径一起版本化的处理、反馈与观察关系](/img/tech-notes/vision-model-release-record.svg)

图中的四个节点分别表示完整组合、发布清单、固定评估、受控回退。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

生成一份机器可读清单，保存各文件摘要与评估范围。发布前在目标运行环境验证，旧版本保留完整组合以便回退。

```text
release = source_revision + preprocessing + cfg + weights
        + class_order + thresholds + postprocessing
evaluation = dataset_revision + matching_policy + actual_results
rollback = previous complete release bundle
```

先保存源码提交、构建选项、配置、权重和输入图片，再对照原始输出。图片只用合成文档或已获授权数据，真实文档中的姓名、编号和印章图样不进入公开训练素材。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 权重不变但阈值提高 | 召回和误检仍可能变化 |
| 类别顺序换了 | 同一输出索引会被错误解释 |
| 只回退 weights | 可能与新预处理或配置不兼容 |

### 对照 1：权重不变但阈值提高

召回和误检仍可能变化。观察时记录发布清单中的阈值差异。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：类别顺序换了

同一输出索引会被错误解释。观察时记录names 与训练类别映射。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：只回退 weights

可能与新预处理或配置不兼容。观察时记录完整发布组合的一致性。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

没有实际验证的数据不得写入发布成绩。计划指标、当前测得结果和后续目标应分别记录，避免文件齐全被误当成效果达标。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“只回退 weights”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [文档应用：标题定位、裁剪与 OCR 怎样衔接](/tech/2018/12/05/document-detection-ocr-pipeline/)
- [Darknet 应用服务：输入、任务状态与结果文件](/tech/2018/12/15/darknet-document-api-contract/)

## 参考资料

1. [Darknet 2018 历史源码](https://github.com/pjreddie/darknet/tree/f6d861736038da22c9eb0739dca84003c5a5e275)
2. [YOLOv3 论文](https://arxiv.org/abs/1804.02767)
3. [YOLO9000 论文](https://arxiv.org/abs/1612.08242)
