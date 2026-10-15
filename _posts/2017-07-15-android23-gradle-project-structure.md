---
layout: post
title: Android 工程结构：模块、Manifest 和资源目录
subtitle: 找不到入口页面、资源引用失败或依赖没有生效，常常是修改了错误层级的文件。
date: 2017-07-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Android
- 移动开发
tech_note: true
note_id: android23-gradle-project-structure
permalink: /tech/2017/07/15/android23-gradle-project-structure/
excerpt: 找不到入口页面、资源引用失败或依赖没有生效，常常是修改了错误层级的文件。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/android23-gradle-project-structure.svg
technology_since: '2017-03-06'
---

找不到入口页面、资源引用失败或依赖没有生效，常常是修改了错误层级的文件。

本文使用Android Studio 2.3、JDK 8、Gradle 3.3、Android Gradle Plugin 2.3.0，compileSdk 25。演示应用使用 Java 与传统 Activity，不使用 AndroidX、后来的 Jetpack 组件或新版本插件 DSL。工具版本、编译 SDK 与运行设备版本要分别记录。

## 1. 从现象推到机制

根工程管理公共仓库与插件，app 模块定义应用构建。Manifest（应用清单）声明组件与权限，res 目录按类型与限定符保存资源。R 类由构建生成，不应手工编辑生成结果。

![Android 工程结构：模块、Manifest 和资源目录的处理、反馈与观察关系](/img/tech-notes/android23-gradle-project-structure.svg)

图中的四个节点分别表示根工程、应用模块、资源清单、生成产物。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

从空 Activity 工程检查文件位置，再改一个字符串资源验证。应用标识与 Java 包名有联系但不是可随意混用的同一字段。

```text
root build.gradle -> repositories and plugin classpath
app/build.gradle -> applicationId, SDK, dependencies
app/src/main/AndroidManifest.xml -> components
app/src/main/res/layout -> XML layout
app/src/main/res/values -> strings and styles
```

先在模拟器运行，再用独立测试设备核对。代码片段需补齐类、资源和清单声明；需要外部数据的地方使用本地演示接口，安装成功与用户任务完成分别验收。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 把模块配置写到根层级 | 可能无法形成预期构建任务 |
| 手工修改生成的 R 类 | 下一次构建会覆盖且不能治本 |
| 不同环境需要不同值 | 可使用受控资源或构建配置 |

### 对照 1：把模块配置写到根层级

可能无法形成预期构建任务。观察时记录插件应用位置与错误信息。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：手工修改生成的 R 类

下一次构建会覆盖且不能治本。观察时记录真正的资源定义错误。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：不同环境需要不同值

可使用受控资源或构建配置。观察时记录最终 APK 中实际打包内容。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

工程可配置不等于应把密钥放进构建文件。签名凭据和环境私密值通过受控本地配置或发布环境提供。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“不同环境需要不同值”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Android 开发起步：JDK、SDK、Gradle 与 IDE 的关系](/tech/2017/07/05/android23-environment-toolchain/)
- [Android 从零到应用：让第一个 Activity 真正在设备运行](/tech/2017/07/25/android23-first-activity-install/)

## 参考资料

1. [Android Studio 2.3 发布说明](https://developer.android.com/studio/releases/past-releases/as-2-3-0-release-notes)
2. [Android Gradle Plugin 2.3.0 说明](https://developer.android.com/build/releases/agp-2-3-0-release-notes)
3. [Android 7.1 平台说明](https://developer.android.com/about/versions/nougat/android-7.1)
