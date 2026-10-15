---
layout: post
title: Android 网络：请求放到后台，结果回到有效界面
subtitle: 界面卡住或抛网络线程异常，说明请求执行位置需要与 UI 更新位置分开。
date: 2017-09-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Android
- 移动开发
tech_note: true
note_id: android-network-main-thread
permalink: /tech/2017/09/05/android-network-main-thread/
excerpt: 界面卡住或抛网络线程异常，说明请求执行位置需要与 UI 更新位置分开。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/android-network-main-thread.svg
technology_since: '2017-03-06'
---

界面卡住或抛网络线程异常，说明请求执行位置需要与 UI 更新位置分开。

本文使用Android Studio 2.3、JDK 8、Gradle 3.3、Android Gradle Plugin 2.3.0，compileSdk 25。演示应用使用 Java 与传统 Activity，不使用 AndroidX、后来的 Jetpack 组件或新版本插件 DSL。工具版本、编译 SDK 与运行设备版本要分别记录。

## 1. 从现象推到机制

主线程负责界面事件，耗时网络工作会影响响应。后台结果返回时，原 Activity 可能已销毁或切换到其他查询。连接和读取应有超时，错误状态不能伪装成空列表。

![Android 网络：请求放到后台，结果回到有效界面的处理、反馈与观察关系](/img/tech-notes/android-network-main-thread.svg)

图中的四个节点分别表示界面触发、后台执行、结果回传、界面有效性。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

用受控执行器进行 HttpURLConnection 请求，通过主线程处理器更新界面。代码为流程示意，还需关闭流、断开连接和处理生命周期。

```text
worker: connect with connect/read timeouts
worker: parse demo response and close resources
main thread: verify screen and request identity
main thread: render data or explicit error
```

先在模拟器运行，再用独立测试设备核对。代码片段需补齐类、资源和清单声明；需要外部数据的地方使用本地演示接口，安装成功与用户任务完成分别验收。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 请求期间旋转或离开页面 | 旧结果不应更新失效实例 |
| 服务器迟迟不响应 | 有界超时避免永久等待 |
| 网络错误却返回空数组 | 会误导用户认为没有数据 |

### 对照 1：请求期间旋转或离开页面

旧结果不应更新失效实例。观察时记录页面与请求身份。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：服务器迟迟不响应

有界超时避免永久等待。观察时记录连接和读取超时分别设置。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：网络错误却返回空数组

会误导用户认为没有数据。观察时记录错误分支与真实空结果。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

后台线程也有数量上限。重复点击和重试要合并或限制，不能每次动作都创建无限新线程。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“网络错误却返回空数组”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Android 本地存储：SQLite 建表与版本升级](/tech/2017/09/15/android-sqlite-upgrade/)
- [Android 权限：清单声明与运行时授权分别处理](/tech/2017/09/25/android-runtime-permission/)

## 参考资料

1. [Android Studio 2.3 发布说明](https://developer.android.com/studio/releases/past-releases/as-2-3-0-release-notes)
2. [Android Gradle Plugin 2.3.0 说明](https://developer.android.com/build/releases/agp-2-3-0-release-notes)
3. [Android 7.1 平台说明](https://developer.android.com/about/versions/nougat/android-7.1)
