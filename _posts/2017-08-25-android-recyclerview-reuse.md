---
layout: post
title: Android 列表：RecyclerView 复用时必须重绑完整状态
subtitle: 快速滚动后某行出现别人的勾选或图片，通常是复用视图残留了旧状态。
date: 2017-08-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Android
- 移动开发
tech_note: true
note_id: android-recyclerview-reuse
permalink: /tech/2017/08/25/android-recyclerview-reuse/
excerpt: 快速滚动后某行出现别人的勾选或图片，通常是复用视图残留了旧状态。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/android-recyclerview-reuse.svg
technology_since: '2017-03-06'
---

快速滚动后某行出现别人的勾选或图片，通常是复用视图残留了旧状态。

本文使用Android Studio 2.3、JDK 8、Gradle 3.3、Android Gradle Plugin 2.3.0，compileSdk 25。演示应用使用 Java 与传统 Activity，不使用 AndroidX、后来的 Jetpack 组件或新版本插件 DSL。工具版本、编译 SDK 与运行设备版本要分别记录。

## 1. 从现象推到机制

RecyclerView（可回收列表组件）复用 ViewHolder，绑定时不能只处理某些为真的分支。每次应按当前数据设置完整展示状态，点击事件要使用有效位置或稳定业务身份，不能永久捕获过期下标。

![Android 列表：RecyclerView 复用时必须重绑完整状态的处理、反馈与观察关系](/img/tech-notes/android-recyclerview-reuse.svg)

图中的四个节点分别表示数据模型、视图复用、完整绑定、点击处理。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

使用 support-v7 25.3.1 的列表依赖，准备有图无图和不同选中状态的演示数据。快速滚动后逐行对照模型。

```java
public void onBindViewHolder(RowHolder h, int position) {
  Row row = rows.get(position);
  h.title.setText(row.title);
  h.checked.setChecked(row.selected);
  h.image.setImageResource(row.hasImage ? R.drawable.demo : R.drawable.empty);
}
```

先在模拟器运行，再用独立测试设备核对。代码片段需补齐类、资源和清单声明；需要外部数据的地方使用本地演示接口，安装成功与用户任务完成分别验收。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 旧行选中而新行未选中 | 绑定必须显式清除选中状态 |
| 异步图片晚于复用返回 | 不能写入已属于另一行的视图 |
| 列表删除使位置变化 | 旧下标不能作为永久业务编号 |

### 对照 1：旧行选中而新行未选中

绑定必须显式清除选中状态。观察时记录每次 bind 设置的全部属性。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：异步图片晚于复用返回

不能写入已属于另一行的视图。观察时记录请求标识与当前业务身份。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：列表删除使位置变化

旧下标不能作为永久业务编号。观察时记录点击时的有效位置或稳定 id。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

复用提升滚动效率，也要求状态归属清楚。选中状态应保存于数据模型或明确状态容器，不只存在控件里。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“列表删除使位置变化”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Android 深入：旋转屏幕后为什么重新创建页面](/tech/2017/08/05/android-activity-lifecycle-state/)
- [Android 界面：dp、sp 与真实像素分开设计](/tech/2017/08/15/android-layout-density-units/)

## 参考资料

1. [Android Studio 2.3 发布说明](https://developer.android.com/studio/releases/past-releases/as-2-3-0-release-notes)
2. [Android Gradle Plugin 2.3.0 说明](https://developer.android.com/build/releases/agp-2-3-0-release-notes)
3. [Android 7.1 平台说明](https://developer.android.com/about/versions/nougat/android-7.1)
