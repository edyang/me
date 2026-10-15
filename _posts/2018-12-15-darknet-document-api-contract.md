---
layout: post
title: Darknet 应用服务：输入、任务状态与结果文件
subtitle: 把命令行包成 HTTP 接口后，还需要处理并发、文件归属和进程失败。
date: 2018-12-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Darknet
- 机器视觉
tech_note: true
note_id: darknet-document-api-contract
permalink: /tech/2018/12/15/darknet-document-api-contract/
excerpt: 把命令行包成 HTTP 接口后，还需要处理并发、文件归属和进程失败。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/darknet-document-api-contract.svg
technology_since: '2018-05-06'
---

把命令行包成 HTTP 接口后，还需要处理并发、文件归属和进程失败。一个 success 字段不够。

本文使用原版 Darknet 固定历史提交、YOLOv2/YOLOv3 与演示图片。目标检测回答对象类别与位置，不自动识别全部文字或判断印章真伪。文中的训练与部署方案属于可复现方法，没有给出未经测试的准确率、速度或客户验收成绩。

## 1. 从现象推到机制

请求接受、模型执行和结果保存是不同阶段。每个任务有独立目录与输入摘要，结果包含页号、框和模型身份。大文件可采用异步任务，查询接口返回明确状态，不让上一个任务的文件混入下一次。

![Darknet 应用服务：输入、任务状态与结果文件的处理、反馈与观察关系](/img/tech-notes/darknet-document-api-contract.svg)

图中的四个节点分别表示请求受理、有限执行、结果保存、状态查询。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先做单工作进程、有限队列的演示服务，固定输入格式与大小。进程退出时把任务标为失败或待恢复，不返回旧结果文件。

```text
task_id -> isolated input directory
QUEUED -> RUNNING -> SUCCEEDED | FAILED
result -> page_id, boxes, model_version, input_digest
cleanup -> retention rule after verified completion
```

先保存源码提交、构建选项、配置、权重和输入图片，再对照原始输出。图片只用合成文档或已获授权数据，真实文档中的姓名、编号和印章图样不进入公开训练素材。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 两个任务文件名相同 | 仍应按任务身份隔离 |
| 推理进程异常退出 | 任务不能停留在假成功 |
| 结果保存失败 | 执行完成也不等于交付完成 |

### 对照 1：两个任务文件名相同

仍应按任务身份隔离。观察时记录真实存储目录与结果归属。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：推理进程异常退出

任务不能停留在假成功。观察时记录退出码与结果文件完整性。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：结果保存失败

执行完成也不等于交付完成。观察时记录落盘状态与查询响应。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

服务容量需要按模型内存与耗时测量。不要为每次请求无限加载新模型，也不要让无界队列积压整页文档。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“结果保存失败”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [文档应用：标题定位、裁剪与 OCR 怎样衔接](/tech/2018/12/05/document-detection-ocr-pipeline/)
- [视觉模型交付：权重、阈值和数据口径一起版本化](/tech/2018/12/25/vision-model-release-record/)

## 参考资料

1. [Darknet 2018 历史源码](https://github.com/pjreddie/darknet/tree/f6d861736038da22c9eb0739dca84003c5a5e275)
2. [YOLOv3 论文](https://arxiv.org/abs/1804.02767)
3. [YOLO9000 论文](https://arxiv.org/abs/1612.08242)
