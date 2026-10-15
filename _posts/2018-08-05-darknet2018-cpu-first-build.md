---
layout: post
title: Darknet 研究：先跑通 CPU，再核对 GPU 构建
subtitle: 编译器、CUDA 和 cuDNN 同时变化时，出错很难定位。
date: 2018-08-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Darknet
- 机器视觉
tech_note: true
note_id: darknet2018-cpu-first-build
permalink: /tech/2018/08/05/darknet2018-cpu-first-build/
excerpt: 编译器、CUDA 和 cuDNN 同时变化时，出错很难定位。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/darknet2018-cpu-first-build.svg
technology_since: '2018-05-06'
---

编译器、CUDA 和 cuDNN 同时变化时，出错很难定位。先用最小计算路径确认代码与输入。

本文使用原版 Darknet 固定历史提交、YOLOv2/YOLOv3 与演示图片。目标检测回答对象类别与位置，不自动识别全部文字或判断印章真伪。文中的训练与部署方案属于可复现方法，没有给出未经测试的准确率、速度或客户验收成绩。

## 1. 从现象推到机制

Darknet 使用构建选项选择 CPU/GPU 和相关库。驱动、CUDA 工具链与实际链接库分别决定运行条件。CPU 推理成功说明部分代码与模型文件可用，不证明 GPU 依赖正确，也不说明速度满足业务。

![Darknet 研究：先跑通 CPU，再核对 GPU 构建的处理、反馈与观察关系](/img/tech-notes/darknet2018-cpu-first-build.svg)

图中的四个节点分别表示固定源码、CPU 基线、GPU 依赖、业务验证。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

固定历史提交，在独立目录先关闭 GPU 构建，再按官方文件准备示例。启用 GPU 时记录编译参数与库版本，清理旧对象后重新编译。

```text
source commit -> fixed historical revision
Makefile: GPU=0, CUDNN=0 for initial check
model cfg + matching weights + authorized sample
then verify driver, toolkit, headers and linked libraries
```

先保存源码提交、构建选项、配置、权重和输入图片，再对照原始输出。图片只用合成文档或已获授权数据，真实文档中的姓名、编号和印章图样不进入公开训练素材。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| CPU 路径正常而 GPU 失败 | 优先检查 GPU 构建和运行依赖 |
| 换选项但保留旧对象文件 | 可能混入不一致构建结果 |
| 示例图输出正常 | 还需验证自定义文档输入 |

### 对照 1：CPU 路径正常而 GPU 失败

优先检查 GPU 构建和运行依赖。观察时记录编译错误与加载库来源。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：换选项但保留旧对象文件

可能混入不一致构建结果。观察时记录实际重编译范围。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：示例图输出正常

还需验证自定义文档输入。观察时记录模型类别与业务目标差异。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

不能照搬官网某块显卡的速度。性能结论要附模型、分辨率、硬件与完整计时范围，模型加载也应单独记录。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“示例图输出正常”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Darknet 与 YOLOv2：检测头输出的是什么](/tech/2018/08/15/yolo2-detection-heads/)
- [Darknet 自定义数据：路径、类别与标注一一对应](/tech/2018/08/25/darknet-dataset-layout/)

## 参考资料

1. [Darknet 2018 历史源码](https://github.com/pjreddie/darknet/tree/f6d861736038da22c9eb0739dca84003c5a5e275)
2. [YOLOv3 论文](https://arxiv.org/abs/1804.02767)
3. [YOLO9000 论文](https://arxiv.org/abs/1612.08242)
