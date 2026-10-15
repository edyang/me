---
layout: post
title: Android 界面：dp、sp 与真实像素分开设计
subtitle: 同一像素宽度在不同手机上显示大小不同。
date: 2017-08-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Android
- 移动开发
tech_note: true
note_id: android-layout-density-units
permalink: /tech/2017/08/15/android-layout-density-units/
excerpt: 同一像素宽度在不同手机上显示大小不同。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/android-layout-density-units.svg
technology_since: '2017-03-06'
---

同一像素宽度在不同手机上显示大小不同。布局需要考虑密度和用户字体设置。

本文使用Android Studio 2.3、JDK 8、Gradle 3.3、Android Gradle Plugin 2.3.0，compileSdk 25。演示应用使用 Java 与传统 Activity，不使用 AndroidX、后来的 Jetpack 组件或新版本插件 DSL。工具版本、编译 SDK 与运行设备版本要分别记录。

## 1. 从现象推到机制

dp（密度无关尺寸）用于常规布局，sp（可缩放文字尺寸）还受字体缩放影响。图片像素与显示尺寸不等价，固定高度遇到大字体可能裁切。不同资源限定符可以为设备条件提供适合版本。

![Android 界面：dp、sp 与真实像素分开设计的处理、反馈与观察关系](/img/tech-notes/android-layout-density-units.svg)

图中的四个节点分别表示设计尺寸、设备密度、字体缩放、实际布局。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

做一个标签加输入框的布局，测试窄屏和较大字体。触控区域与视觉图标大小分别检查，不只比较截图。

```xml
<TextView
 android:layout_width="match_parent"
 android:layout_height="wrap_content"
 android:textSize="16sp"
 android:padding="12dp"
 android:text="演示说明"/>
```

先在模拟器运行，再用独立测试设备核对。代码片段需补齐类、资源和清单声明；需要外部数据的地方使用本地演示接口，安装成功与用户任务完成分别验收。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 设备密度变化 | dp 对应像素数会不同 |
| 用户放大系统字体 | 文本高度可能增加 |
| 使用固定像素布局 | 不同设备体验可能明显不同 |

### 对照 1：设备密度变化

dp 对应像素数会不同。观察时记录密度与最终像素尺寸。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：用户放大系统字体

文本高度可能增加。观察时记录sp 缩放与容器裁切。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：使用固定像素布局

不同设备体验可能明显不同。观察时记录实际屏幕密度与可用空间。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

布局自适应不意味着所有设备都一套固定尺寸。重要任务应在真实目标屏幕和字体设置下验证，资源体积也需要控制。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“使用固定像素布局”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Android 深入：旋转屏幕后为什么重新创建页面](/tech/2017/08/05/android-activity-lifecycle-state/)
- [Android 列表：RecyclerView 复用时必须重绑完整状态](/tech/2017/08/25/android-recyclerview-reuse/)

## 参考资料

1. [Android Studio 2.3 发布说明](https://developer.android.com/studio/releases/past-releases/as-2-3-0-release-notes)
2. [Android Gradle Plugin 2.3.0 说明](https://developer.android.com/build/releases/agp-2-3-0-release-notes)
3. [Android 7.1 平台说明](https://developer.android.com/about/versions/nougat/android-7.1)
