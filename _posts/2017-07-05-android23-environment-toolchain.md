---
layout: post
title: Android 开发起步：JDK、SDK、Gradle 与 IDE 的关系
subtitle: 安装 Android Studio 后，工程仍可能因为 SDK 或 Gradle 版本不匹配而无法构建。
date: 2017-07-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Android
- 移动开发
tech_note: true
note_id: android23-environment-toolchain
permalink: /tech/2017/07/05/android23-environment-toolchain/
excerpt: 安装 Android Studio 后，工程仍可能因为 SDK 或 Gradle 版本不匹配而无法构建。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/android23-environment-toolchain.svg
technology_since: '2017-03-06'
---

安装 Android Studio 后，工程仍可能因为 SDK 或 Gradle 版本不匹配而无法构建。各工具承担不同任务。

本文使用Android Studio 2.3、JDK 8、Gradle 3.3、Android Gradle Plugin 2.3.0，compileSdk 25。演示应用使用 Java 与传统 Activity，不使用 AndroidX、后来的 Jetpack 组件或新版本插件 DSL。工具版本、编译 SDK 与运行设备版本要分别记录。

## 1. 从现象推到机制

JDK 运行编译工具，Android SDK 提供平台 API 与打包工具，Gradle 执行构建，Android 插件连接平台任务。工程 wrapper 固定 Gradle 版本，不能只看系统安装的 gradle。模拟器系统版本与 compileSdk 也不同。

![Android 开发起步：JDK、SDK、Gradle 与 IDE 的关系的处理、反馈与观察关系](/img/tech-notes/android23-environment-toolchain.svg)

图中的四个节点分别表示开发工具、构建执行、平台工具、运行设备。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先创建空工程，固定 wrapper 与插件，再核对 SDK Manager 中 API 25 平台。下载来源和许可按官方工具处理，不使用来路不明的整包替换。

```text
IDE: Android Studio 2.3
JDK: 8
Gradle wrapper: 3.3
Android plugin: 2.3.0
compileSdkVersion: 25
Build Tools: 25.0.2
```

先在模拟器运行，再用独立测试设备核对。代码片段需补齐类、资源和清单声明；需要外部数据的地方使用本地演示接口，安装成功与用户任务完成分别验收。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 系统 Gradle 与 wrapper 不同 | 工程通常按 wrapper 声明执行 |
| 缺少编译平台 | 无法解析需要的平台资源 |
| 模拟器版本较低 | 运行能力还受 minSdk 与 API 使用影响 |

### 对照 1：系统 Gradle 与 wrapper 不同

工程通常按 wrapper 声明执行。观察时记录gradle-wrapper.properties。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：缺少编译平台

无法解析需要的平台资源。观察时记录SDK Manager 已安装项目。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：模拟器版本较低

运行能力还受 minSdk 与 API 使用影响。观察时记录编译和运行版本分别记录。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

历史工具链需要匹配当时依赖，不适合直接照搬到今天的新工程。这里的版本组合用于理解这一阶段的构建关系。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“模拟器版本较低”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Android 工程结构：模块、Manifest 和资源目录](/tech/2017/07/15/android23-gradle-project-structure/)
- [Android 从零到应用：让第一个 Activity 真正在设备运行](/tech/2017/07/25/android23-first-activity-install/)

## 参考资料

1. [Android Studio 2.3 发布说明](https://developer.android.com/studio/releases/past-releases/as-2-3-0-release-notes)
2. [Android Gradle Plugin 2.3.0 说明](https://developer.android.com/build/releases/agp-2-3-0-release-notes)
3. [Android 7.1 平台说明](https://developer.android.com/about/versions/nougat/android-7.1)
