---
layout: post
title: Android 交付：用一张场景表验证完整软件
subtitle: 一台手机上点通一次，不足以说明应用可以交付。
date: 2017-10-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Android
- 移动开发
tech_note: true
note_id: android-release-acceptance-matrix
permalink: /tech/2017/10/25/android-release-acceptance-matrix/
excerpt: 一台手机上点通一次，不足以说明应用可以交付。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/android-release-acceptance-matrix.svg
technology_since: '2017-03-06'
---

一台手机上点通一次，不足以说明应用可以交付。需要覆盖安装、升级、异常和生命周期。

本文使用Android Studio 2.3、JDK 8、Gradle 3.3、Android Gradle Plugin 2.3.0，compileSdk 25。演示应用使用 Java 与传统 Activity，不使用 AndroidX、后来的 Jetpack 组件或新版本插件 DSL。工具版本、编译 SDK 与运行设备版本要分别记录。

## 1. 从现象推到机制

测试范围按真实使用条件组织：最低系统、目标分辨率、权限拒绝、网络中断和旋转重建。每项记录输入、实际现象和版本，不把计划执行写成已通过。修复后验证原问题及直接受影响路径。

![Android 交付：用一张场景表验证完整软件的处理、反馈与观察关系](/img/tech-notes/android-release-acceptance-matrix.svg)

图中的四个节点分别表示发布产物、环境矩阵、业务场景、结果记录。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

为笔记演示应用准备新装、旧数据升级、空数据、长文本和快速重复操作场景。使用相同待发布 APK，避免测试的是另一份调试包。

```text
artifact -> exact release APK identity
scenarios -> install, upgrade, lifecycle, permissions, offline
record -> input, device, actual result, issue
acceptance -> confirmed task completion
```

先在模拟器运行，再用独立测试设备核对。代码片段需补齐类、资源和清单声明；需要外部数据的地方使用本地演示接口，安装成功与用户任务完成分别验收。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 调试包通过而发布包未测 | 结论不能自动沿用 |
| 系统回收后数据仍正确 | 说明相应恢复路径得到覆盖 |
| 只记通过不留输入 | 后续难以复验 |

### 对照 1：调试包通过而发布包未测

结论不能自动沿用。观察时记录产物签名与配置差异。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：系统回收后数据仍正确

说明相应恢复路径得到覆盖。观察时记录真实恢复过程与数据来源。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：只记通过不留输入

后续难以复验。观察时记录设备版本与具体操作条件。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

场景表应与应用风险匹配，不靠堆数量。最终交付还要包含安装说明、数据保存位置与可处理故障范围。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“只记通过不留输入”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Android 小应用实作：从列表、编辑到本地保存闭环](/tech/2017/10/05/android-app-complete-notes/)
- [Android 发布：调试包与正式签名包的区别](/tech/2017/10/15/android-apk-signing-release/)

## 参考资料

1. [Android Studio 2.3 发布说明](https://developer.android.com/studio/releases/past-releases/as-2-3-0-release-notes)
2. [Android Gradle Plugin 2.3.0 说明](https://developer.android.com/build/releases/agp-2-3-0-release-notes)
3. [Android 7.1 平台说明](https://developer.android.com/about/versions/nougat/android-7.1)
