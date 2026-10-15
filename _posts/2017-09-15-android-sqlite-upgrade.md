---
layout: post
title: Android 本地存储：SQLite 建表与版本升级
subtitle: 应用升级后本地表结构改变，直接删库重建会丢掉用户数据。
date: 2017-09-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Android
- 移动开发
tech_note: true
note_id: android-sqlite-upgrade
permalink: /tech/2017/09/15/android-sqlite-upgrade/
excerpt: 应用升级后本地表结构改变，直接删库重建会丢掉用户数据。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/android-sqlite-upgrade.svg
technology_since: '2017-03-06'
---

应用升级后本地表结构改变，直接删库重建会丢掉用户数据。升级需要有明确迁移路径。

本文使用Android Studio 2.3、JDK 8、Gradle 3.3、Android Gradle Plugin 2.3.0，compileSdk 25。演示应用使用 Java 与传统 Activity，不使用 AndroidX、后来的 Jetpack 组件或新版本插件 DSL。工具版本、编译 SDK 与运行设备版本要分别记录。

## 1. 从现象推到机制

SQLiteOpenHelper 根据数据库版本调用创建或升级逻辑。新增列、回填数据与约束变化需要考虑旧版本输入。数据库版本只能前进到明确结构，不能只把版本号加一却不定义实际变化。

![Android 本地存储：SQLite 建表与版本升级的处理、反馈与观察关系](/img/tech-notes/android-sqlite-upgrade.svg)

图中的四个节点分别表示旧版结构、迁移步骤、数据保留、目标结构。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

从第一版演示表升级增加备注列，使用独立测试数据库检查旧数据保留。新安装与旧版升级都要走一遍。

```java
public void onUpgrade(SQLiteDatabase db, int oldV, int newV) {
  if (oldV < 2) {
    db.execSQL("ALTER TABLE note ADD COLUMN remark TEXT");
  }
}
```

先在模拟器运行，再用独立测试设备核对。代码片段需补齐类、资源和清单声明；需要外部数据的地方使用本地演示接口，安装成功与用户任务完成分别验收。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 新装应用直接创建最新版 | 表结构应与迁移后目标一致 |
| 旧用户跨多个版本升级 | 每一步必要变化都不能遗漏 |
| 迁移中断或失败 | 应保留可恢复的数据状态 |

### 对照 1：新装应用直接创建最新版

表结构应与迁移后目标一致。观察时记录onCreate 与升级最终结构。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：旧用户跨多个版本升级

每一步必要变化都不能遗漏。观察时记录旧版本到目标的完整路径。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：迁移中断或失败

应保留可恢复的数据状态。观察时记录事务与失败处理。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

本地数据库不等于同步完成。若记录还要上传服务端，应单独保存待同步状态和幂等身份，避免升级时重复提交。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“迁移中断或失败”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Android 网络：请求放到后台，结果回到有效界面](/tech/2017/09/05/android-network-main-thread/)
- [Android 权限：清单声明与运行时授权分别处理](/tech/2017/09/25/android-runtime-permission/)

## 参考资料

1. [Android Studio 2.3 发布说明](https://developer.android.com/studio/releases/past-releases/as-2-3-0-release-notes)
2. [Android Gradle Plugin 2.3.0 说明](https://developer.android.com/build/releases/agp-2-3-0-release-notes)
3. [Android 7.1 平台说明](https://developer.android.com/about/versions/nougat/android-7.1)
