---
layout: post
title: Android 小应用实作：从列表、编辑到本地保存闭环
subtitle: 把控件分别跑通之后，需要一个完整用户任务来验证应用是否真正可用。
date: 2017-10-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Android
- 移动开发
tech_note: true
note_id: android-app-complete-notes
permalink: /tech/2017/10/05/android-app-complete-notes/
excerpt: 把控件分别跑通之后，需要一个完整用户任务来验证应用是否真正可用。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/android-app-complete-notes.svg
technology_since: '2017-03-06'
---

把控件分别跑通之后，需要一个完整用户任务来验证应用是否真正可用。这里用匿名笔记工具串起开发链路。

本文使用Android Studio 2.3、JDK 8、Gradle 3.3、Android Gradle Plugin 2.3.0，compileSdk 25。演示应用使用 Java 与传统 Activity，不使用 AndroidX、后来的 Jetpack 组件或新版本插件 DSL。工具版本、编译 SDK 与运行设备版本要分别记录。

## 1. 从现象推到机制

列表显示已保存记录，编辑页维护草稿，保存动作提交本地数据库，返回列表后重新查询。空标题、取消编辑和重复点击都有明确规则。页面内存数据与数据库事实分开，可以避免返回后出现幽灵记录。

![Android 小应用实作：从列表、编辑到本地保存闭环的处理、反馈与观察关系](/img/tech-notes/android-app-complete-notes.svg)

图中的四个节点分别表示已存列表、编辑草稿、保存事务、返回刷新。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

先完成新增与修改，再加删除和搜索。每条记录使用稳定数据库编号，列表位置不能代替业务身份。

```text
list -> open draft editor
save -> validate -> database transaction
success -> finish editor -> reload list
cancel -> discard draft without changing saved record
```

先在模拟器运行，再用独立测试设备核对。代码片段需补齐类、资源和清单声明；需要外部数据的地方使用本地演示接口，安装成功与用户任务完成分别验收。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 编辑后点击取消 | 已保存记录不应被污染 |
| 快速重复点击保存 | 不应生成多条同一编辑结果 |
| 应用退出后重新打开 | 已确认记录仍能从数据库读回 |

### 对照 1：编辑后点击取消

已保存记录不应被污染。观察时记录草稿与持久记录是否独立。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：快速重复点击保存

不应生成多条同一编辑结果。观察时记录按钮状态和保存身份。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：应用退出后重新打开

已确认记录仍能从数据库读回。观察时记录重启后的真实数据。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

这个闭环只涵盖本地笔记，不等于云同步产品。同步、账号和附件会引入新的冲突与隐私问题，应作为后续明确范围。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“应用退出后重新打开”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Android 发布：调试包与正式签名包的区别](/tech/2017/10/15/android-apk-signing-release/)
- [Android 交付：用一张场景表验证完整软件](/tech/2017/10/25/android-release-acceptance-matrix/)

## 参考资料

1. [Android Studio 2.3 发布说明](https://developer.android.com/studio/releases/past-releases/as-2-3-0-release-notes)
2. [Android Gradle Plugin 2.3.0 说明](https://developer.android.com/build/releases/agp-2-3-0-release-notes)
3. [Android 7.1 平台说明](https://developer.android.com/about/versions/nougat/android-7.1)
