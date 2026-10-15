---
layout: post
title: Android 从零到应用：让第一个 Activity 真正在设备运行
subtitle: 编辑器能预览布局，不代表 APK 已安装，更不代表启动入口配置正确。
date: 2017-07-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Android
- 移动开发
tech_note: true
note_id: android23-first-activity-install
permalink: /tech/2017/07/25/android23-first-activity-install/
excerpt: 编辑器能预览布局，不代表 APK 已安装，更不代表启动入口配置正确。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/android23-first-activity-install.svg
technology_since: '2017-03-06'
---

编辑器能预览布局，不代表 APK 已安装，更不代表启动入口配置正确。

本文使用Android Studio 2.3、JDK 8、Gradle 3.3、Android Gradle Plugin 2.3.0，compileSdk 25。演示应用使用 Java 与传统 Activity，不使用 AndroidX、后来的 Jetpack 组件或新版本插件 DSL。工具版本、编译 SDK 与运行设备版本要分别记录。

## 1. 从现象推到机制

Activity（界面组件）通过清单参与应用启动，onCreate 中加载布局资源。安装包、启动意图与运行日志分别提供不同证据。模拟器运行成功后，真机还可能有权限、分辨率和厂商行为差异。

![Android 从零到应用：让第一个 Activity 真正在设备运行的处理、反馈与观察关系](/img/tech-notes/android23-first-activity-install.svg)

图中的四个节点分别表示设备连接、APK 安装、启动入口、交互结果。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

制作只有按钮和状态文字的页面，点击后更新文本。先用 adb 确认设备，再安装演示调试包，观察启动异常。

```java
public class MainActivity extends Activity {
  @Override public void onCreate(Bundle state) {
    super.onCreate(state);
    setContentView(R.layout.activity_main);
  }
}
```

先在模拟器运行，再用独立测试设备核对。代码片段需补齐类、资源和清单声明；需要外部数据的地方使用本地演示接口，安装成功与用户任务完成分别验收。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 设备没有出现在 adb 列表 | IDE 无法凭空完成安装 |
| 布局预览正常但启动崩溃 | 需要查看运行期异常 |
| 应用安装成功 | 仍要点击并验证交互结果 |

### 对照 1：设备没有出现在 adb 列表

IDE 无法凭空完成安装。观察时记录连接授权与设备状态。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：布局预览正常但启动崩溃

需要查看运行期异常。观察时记录logcat 中首个应用错误。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：应用安装成功

仍要点击并验证交互结果。观察时记录真实启动页面与按钮状态。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

安装失败应保留完整原因，签名冲突、空间不足与最低系统版本不同，不能都靠反复重装解决。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“应用安装成功”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Android 开发起步：JDK、SDK、Gradle 与 IDE 的关系](/tech/2017/07/05/android23-environment-toolchain/)
- [Android 工程结构：模块、Manifest 和资源目录](/tech/2017/07/15/android23-gradle-project-structure/)

## 参考资料

1. [Android Studio 2.3 发布说明](https://developer.android.com/studio/releases/past-releases/as-2-3-0-release-notes)
2. [Android Gradle Plugin 2.3.0 说明](https://developer.android.com/build/releases/agp-2-3-0-release-notes)
3. [Android 7.1 平台说明](https://developer.android.com/about/versions/nougat/android-7.1)
