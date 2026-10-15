---
layout: post
title: Android 深入：旋转屏幕后为什么重新创建页面
subtitle: 旋转后输入消失，不一定是控件保存失效，而是页面经历了重新创建。
date: 2017-08-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Android
- 移动开发
tech_note: true
note_id: android-activity-lifecycle-state
permalink: /tech/2017/08/05/android-activity-lifecycle-state/
excerpt: 旋转后输入消失，不一定是控件保存失效，而是页面经历了重新创建。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/android-activity-lifecycle-state.svg
technology_since: '2017-03-06'
---

旋转后输入消失，不一定是控件保存失效，而是页面经历了重新创建。

本文使用Android Studio 2.3、JDK 8、Gradle 3.3、Android Gradle Plugin 2.3.0，compileSdk 25。演示应用使用 Java 与传统 Activity，不使用 AndroidX、后来的 Jetpack 组件或新版本插件 DSL。工具版本、编译 SDK 与运行设备版本要分别记录。

## 1. 从现象推到机制

配置变化可能销毁并重建 Activity。成员字段只属于当前实例，不能作为长期状态依据。短小 UI 状态可通过实例状态保存，持久业务数据放入合适存储，恢复时再从权威来源核对。

![Android 深入：旋转屏幕后为什么重新创建页面的处理、反馈与观察关系](/img/tech-notes/android-activity-lifecycle-state.svg)

图中的四个节点分别表示页面创建、用户编辑、配置变化、状态恢复。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

在生命周期回调打印匿名状态，输入文本后旋转并观察实例变化。不要简单禁止全部配置变化来掩盖状态设计。

```java
@Override protected void onSaveInstanceState(Bundle out) {
  out.putString("draft", draftText);
  super.onSaveInstanceState(out);
}
// onCreate 中从 state 恢复短小的界面状态
```

先在模拟器运行，再用独立测试设备核对。代码片段需补齐类、资源和清单声明；需要外部数据的地方使用本地演示接口，安装成功与用户任务完成分别验收。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 旋转触发页面重建 | 新实例字段不会天然继承旧值 |
| 进程被系统回收后回来 | 不能只依赖静态变量恢复 |
| 业务已在服务端完成 | 恢复界面应重新核对真实状态 |

### 对照 1：旋转触发页面重建

新实例字段不会天然继承旧值。观察时记录实例身份与生命周期日志。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：进程被系统回收后回来

不能只依赖静态变量恢复。观察时记录持久数据与保存状态。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：业务已在服务端完成

恢复界面应重新核对真实状态。观察时记录服务端记录而非旧按钮文本。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

实例状态不适合存放大图片和完整数据库。保存最小定位与编辑信息，再按生命周期恢复必要资源。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“业务已在服务端完成”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Android 界面：dp、sp 与真实像素分开设计](/tech/2017/08/15/android-layout-density-units/)
- [Android 列表：RecyclerView 复用时必须重绑完整状态](/tech/2017/08/25/android-recyclerview-reuse/)

## 参考资料

1. [Android Studio 2.3 发布说明](https://developer.android.com/studio/releases/past-releases/as-2-3-0-release-notes)
2. [Android Gradle Plugin 2.3.0 说明](https://developer.android.com/build/releases/agp-2-3-0-release-notes)
3. [Android 7.1 平台说明](https://developer.android.com/about/versions/nougat/android-7.1)
