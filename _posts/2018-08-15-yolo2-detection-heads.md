---
layout: post
title: Darknet 与 YOLOv2：检测头输出的是什么
subtitle: 检测框和类别不是图像里所有语义。
date: 2018-08-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Darknet
- 机器视觉
tech_note: true
note_id: yolo2-detection-heads
permalink: /tech/2018/08/15/yolo2-detection-heads/
excerpt: 检测框和类别不是图像里所有语义。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/yolo2-detection-heads.svg
technology_since: '2018-05-06'
---

检测框和类别不是图像里所有语义。理解网络输出，才能判断能否迁移到文档标题与印章。

本文使用原版 Darknet 固定历史提交、YOLOv2/YOLOv3 与演示图片。目标检测回答对象类别与位置，不自动识别全部文字或判断印章真伪。文中的训练与部署方案属于可复现方法，没有给出未经测试的准确率、速度或客户验收成绩。

## 1. 从现象推到机制

YOLOv2（第二代单阶段检测器）在网格位置预测边界框与类别相关值，训练目标依赖标注框。它不会直接输出标题文字内容。小目标、长宽比与输入缩放都会影响定位，文档任务需要重新定义类别与数据。

![Darknet 与 YOLOv2：检测头输出的是什么的处理、反馈与观察关系](/img/tech-notes/yolo2-detection-heads.svg)

图中的四个节点分别表示图像特征、候选框、类别得分、业务解释。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先用合成文档框解释类别与位置，再检查模型输出如何变回像素坐标。不要把自然图像预训练类别当成已经支持印章识别。

```text
input image -> feature map
anchors and offsets -> candidate boxes
objectness and class values -> detection scores
postprocessing -> boxes in original image coordinates
```

先保存源码提交、构建选项、配置、权重和输入图片，再对照原始输出。图片只用合成文档或已获授权数据，真实文档中的姓名、编号和印章图样不进入公开训练素材。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 预训练模型没有印章类别 | 不能直接声称能识别印章 |
| 标题宽而矮 | 需要关注输入缩放后的几何 |
| 框到了标题区域 | 仍未完成文字转录 |

### 对照 1：预训练模型没有印章类别

不能直接声称能识别印章。观察时记录类别清单与输出维度。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：标题宽而矮

需要关注输入缩放后的几何。观察时记录目标尺寸与长宽比分布。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：框到了标题区域

仍未完成文字转录。观察时记录定位结果与 OCR 输出分别验证。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

预训练权重有助于初始化，不替代目标数据。迁移效果要在独立测试集验证，不能用训练样本上的框图作为准确率。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“框到了标题区域”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Darknet 研究：先跑通 CPU，再核对 GPU 构建](/tech/2018/08/05/darknet2018-cpu-first-build/)
- [Darknet 自定义数据：路径、类别与标注一一对应](/tech/2018/08/25/darknet-dataset-layout/)

## 参考资料

1. [Darknet 2018 历史源码](https://github.com/pjreddie/darknet/tree/f6d861736038da22c9eb0739dca84003c5a5e275)
2. [YOLOv3 论文](https://arxiv.org/abs/1804.02767)
3. [YOLO9000 论文](https://arxiv.org/abs/1612.08242)
