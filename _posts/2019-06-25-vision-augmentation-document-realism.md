---
layout: post
title: 视觉训练研究：文档增强要像真实成像
subtitle: 把图片旋转、变色和裁剪到很夸张，不一定让模型更强。
date: 2019-06-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- YOLOv3
- 机器视觉
tech_note: true
note_id: vision-augmentation-document-realism
permalink: /tech/2019/06/25/vision-augmentation-document-realism/
excerpt: 把图片旋转、变色和裁剪到很夸张，不一定让模型更强。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/vision-augmentation-document-realism.svg
technology_since: '2018-05-06'
---

把图片旋转、变色和裁剪到很夸张，不一定让模型更强。增强应覆盖可能发生的成像变化。

本文使用2018 年固定 Darknet 提交、YOLOv3 与独立文档数据划分。继续研究检测模型时，先保证数据定义、预处理和评估口径稳定。文中方法和预期不代表已经获得某个准确率或部署成绩，真实结论必须来自记录完整的实验。

## 1. 从现象推到机制

扫描、拍照与复印的退化机制不同。亮度、轻微倾斜、压缩和模糊可以对应真实问题，但随机水平翻转会产生不符合自然文档的文字。增强后标签也必须同步，不能只追求变体数量。

![视觉训练研究：文档增强要像真实成像的处理、反馈与观察关系](/img/tech-notes/vision-augmentation-document-realism.svg)

图中的四个节点分别表示失败来源、增强策略、标签同步、验证对照。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

从真实匿名失败类型制定有限增强方案，只对训练组生成。比较原始与增强数据的尺寸、可见性和人工可读性。

```text
observed failure -> plausible transformation
geometry change -> transform annotations together
photometric change -> preserve label meaning
validation -> untouched independent examples
```

每次只改变一组关键因素，保存配置、权重、数据清单与输出。训练、验证和测试职责分离，难例分析保留匿名原始证据，不通过删除失败样本改善表面指标。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 增强使文字完全不可读 | 可能偏离目标输入分布 |
| 几何变换未更新框 | 训练会得到错误位置监督 |
| 验证集也做随机增强 | 前后比较口径可能不稳定 |

### 对照 1：增强使文字完全不可读

可能偏离目标输入分布。观察时记录变换强度与真实成像。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：几何变换未更新框

训练会得到错误位置监督。观察时记录叠加标注的可视检查。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：验证集也做随机增强

前后比较口径可能不稳定。观察时记录固定评估输入清单。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

增强不能替代新来源数据。遇到全新模板或相机条件，应补充合法独立样本，而不只反复加工原有少量图片。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“验证集也做随机增强”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [YOLOv3 文档研究：锚框要与目标尺寸分布匹配](/tech/2019/06/05/yolov3-anchor-document-shapes/)
- [视觉训练研究：负样本与类别不均衡怎样观察](/tech/2019/06/15/vision-class-imbalance-negative/)

## 参考资料

1. [YOLOv3 论文](https://arxiv.org/abs/1804.02767)
2. [Darknet 历史实现](https://github.com/pjreddie/darknet/tree/f6d861736038da22c9eb0739dca84003c5a5e275)
3. [OpenCV 3.4.0](https://docs.opencv.org/3.4.0/)
