---
layout: post
title: Android 权限：清单声明与运行时授权分别处理
subtitle: 清单已经写了权限，功能仍然被拒绝，可能是运行系统与目标 SDK 采用了运行时授权机制。
date: 2017-09-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Android
- 移动开发
tech_note: true
note_id: android-runtime-permission
permalink: /tech/2017/09/25/android-runtime-permission/
excerpt: 清单已经写了权限，功能仍然被拒绝，可能是运行系统与目标 SDK 采用了运行时授权机制。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/android-runtime-permission.svg
technology_since: '2017-03-06'
---

清单已经写了权限，功能仍然被拒绝，可能是运行系统与目标 SDK 采用了运行时授权机制。

本文使用Android Studio 2.3、JDK 8、Gradle 3.3、Android Gradle Plugin 2.3.0，compileSdk 25。演示应用使用 Java 与传统 Activity，不使用 AndroidX、后来的 Jetpack 组件或新版本插件 DSL。工具版本、编译 SDK 与运行设备版本要分别记录。

## 1. 从现象推到机制

Android 6.0 起部分危险权限需要运行时请求，用户可以拒绝或后续撤销。请求应发生在真实功能需要时，并给出可理解用途。权限通过也不代表设备一定有对应硬件或资源当前可用。

![Android 权限：清单声明与运行时授权分别处理的处理、反馈与观察关系](/img/tech-notes/android-runtime-permission.svg)

图中的四个节点分别表示功能触发、权限检查、结果处理、资源访问。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

以相机演示先检查再请求，回调后继续相应动作。拒绝时保留替代路径，不在启动时一次索取所有未来可能使用的权限。

```text
user selects camera feature
check runtime permission
if not granted: request with clear purpose
on result: continue or show usable alternative
recheck before later protected access
```

先在模拟器运行，再用独立测试设备核对。代码片段需补齐类、资源和清单声明；需要外部数据的地方使用本地演示接口，安装成功与用户任务完成分别验收。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 用户首次拒绝 | 应用核心界面仍应可使用 |
| 用户在设置中撤销 | 后续访问需要再次检查 |
| 已授权但相机被占用 | 仍可能出现资源访问错误 |

### 对照 1：用户首次拒绝

应用核心界面仍应可使用。观察时记录拒绝分支与替代操作。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：用户在设置中撤销

后续访问需要再次检查。观察时记录当前权限状态而非旧缓存。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：已授权但相机被占用

仍可能出现资源访问错误。观察时记录权限与设备资源状态分别判断。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

不要让权限说明承诺超过实际用途。只申请本轮确实需要的权限，测试时也要覆盖拒绝和撤销场景。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“已授权但相机被占用”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Android 网络：请求放到后台，结果回到有效界面](/tech/2017/09/05/android-network-main-thread/)
- [Android 本地存储：SQLite 建表与版本升级](/tech/2017/09/15/android-sqlite-upgrade/)

## 参考资料

1. [Android Studio 2.3 发布说明](https://developer.android.com/studio/releases/past-releases/as-2-3-0-release-notes)
2. [Android Gradle Plugin 2.3.0 说明](https://developer.android.com/build/releases/agp-2-3-0-release-notes)
3. [Android 7.1 平台说明](https://developer.android.com/about/versions/nougat/android-7.1)
