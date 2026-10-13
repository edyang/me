---
layout: post
title: 初步研究数字人各种方案
subtitle: 这次研究的起点，是把技术文章持续做成口播视频。
date: 2023-12-13 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 视频
- 声音克隆
- Agent
tech_note: true
note_id: talking-video-avatar-voice-pipeline
source_date: '2026-10-12'
source_dates:
- '2026-10-12'
published_at: '2026-10-12T12:51:43+08:00'
updated_at: '2026-10-13T17:59:15+08:00'
verification: proposal
privacy_reviewed: true
permalink: /tech/2026/10/12/talking-video-avatar-voice-pipeline/
excerpt: 这次研究的起点，是把技术文章持续做成口播视频。
archive_date: '2023-12-13'
date_basis: simulated_weekly_archive
content_revision: 2
images:
- /img/tech-notes/talking-video-avatar-voice-pipeline.svg
---

这次研究的起点，是把技术文章持续做成口播视频。我希望主内容使用横屏画面，放进 9:16 竖屏背景，顶部显示当天标题，数字人位于画面左下区域，并使用自己的声音。这个目标包含稿件、声音、人物、时间轴和合成，直接找一个大而全的项目，很难判断哪部分效果不满意。因此我先收窄范围：优先解决数字人和声音克隆，再考虑接入自动制作系统。

## 研究与排查过程

第一步按素材来源分两条路线。有真人视频时，保留原有姿态，再由音频驱动口型；只有照片时，则需要模型生成头部运动与表情。原交流优先讨论 MuseTalk 1.5 与 EchoMimicV3-Flash。MuseTalk 官方将它描述为音频驱动的潜空间口型修补，适合进入已有视频的对照测试；EchoMimicV3 则作为照片动画路线的候选。两者输出任务不同，不能拿不同素材的演示片直接排出第一名。

第二步把声音独立出来，先研究 CosyVoice 3 与 GPT-SoVITS。CosyVoice 进入中文语音生成候选，GPT-SoVITS 则用于比较参考音频的零样本路线与少量材料微调路线。官方仓库能够证明这些能力属于项目研究范围，但不能证明在我的设备、声音和稿件上已经达到满意效果。原讨论也提到了其它备选项目，不过这轮先集中验证主候选，避免安装很多环境却没有统一样片。

![初步研究数字人各种方案研究路径示意](/img/tech-notes/talking-video-avatar-voice-pipeline.svg)

## 涉及的技术与取舍

目前拟比较的技术关系如下：

| 环节 | 主候选 | 输入与用途 | 首轮重点 |
| --- | --- | --- | --- |
| 视频口型 | MuseTalk 1.5 | 人物视频和驱动音频 | 嘴部稳定、融合边缘、音画同步 |
| 照片动画 | EchoMimicV3-Flash | 人物照片和驱动音频 | 身份保持、运动自然、长片稳定 |
| 中文配音 | CosyVoice 3 | 文本及相应参考材料 | 发音、音色、停顿与稳定性 |
| 声音克隆 | GPT-SoVITS | 参考音频，或经整理的微调数据 | 零样本与微调差异、中文读音 |

验证方案先用统一约 15 秒稿件与合法自有素材，再扩展到 90 秒。稿件刻意加入数字、英文缩写、多音字和长句，声音比较关注读音与韵律，人物比较关注嘴型、脸部一致与边缘伪影。同时记录显存峰值、初始化与生成时间。两张 V100 每卡容量独立，不能把它们直接当作一块大显卡；BF16、注意力算子及精度路径还要按项目具体实现验证。

自动制作的后半段仍属于拟定方案：先确认最终音频，再做时间对齐，之后才安排字幕和画面。计划时码不能当成实际音频时码。背景、标题、人物区域和横屏主画面应由确定的布局参数合成，可以研究 FFmpeg 等工具；模型负责声音与人物生成，合成端负责执行已确认的时间轴。

## 这轮研究的结论

本轮结论是先完成两条人物路线和两条声音路线的可比样片，声音确认后再驱动人物，最后接时间轴与版式。优先候选已经明确，但尚没有本地安装结果、统一对比样片或 90 秒稳定性记录，因而不能宣布某个项目已经胜出。官方能力、研究建议与个人实测在文章中分别记录。下一轮的交付应是能播放的样片及资源记录，再据此选择真正进入自动化系统的组合。

## 参考资料

- [MuseTalk 官方仓库](https://github.com/TMElyralab/MuseTalk)
- [EchoMimicV3 官方仓库](https://github.com/antgroup/echomimic_v3)
- [CosyVoice 官方仓库](https://github.com/QwenAudio/CosyVoice)
- [GPT-SoVITS 官方仓库](https://github.com/RVC-Boss/GPT-SoVITS)

项目能力按整理时的官方资料核对；模拟归档日期不表示上述版本在该年已经发布。
