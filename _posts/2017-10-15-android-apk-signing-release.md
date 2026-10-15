---
layout: post
title: Android 发布：调试包与正式签名包的区别
subtitle: 调试安装没问题，替换正式包却失败，可能是签名身份不一致。
date: 2017-10-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Android
- 移动开发
tech_note: true
note_id: android-apk-signing-release
permalink: /tech/2017/10/15/android-apk-signing-release/
excerpt: 调试安装没问题，替换正式包却失败，可能是签名身份不一致。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/android-apk-signing-release.svg
technology_since: '2017-03-06'
---

调试安装没问题，替换正式包却失败，可能是签名身份不一致。应用升级依赖稳定发布身份。

本文使用Android Studio 2.3、JDK 8、Gradle 3.3、Android Gradle Plugin 2.3.0，compileSdk 25。演示应用使用 Java 与传统 Activity，不使用 AndroidX、后来的 Jetpack 组件或新版本插件 DSL。工具版本、编译 SDK 与运行设备版本要分别记录。

## 1. 从现象推到机制

APK 签名标识发布者，升级需要符合签名与包身份要求。debug keystore（调试密钥库）不应作为正式长期发布凭据。版本号区分展示版本与用于升级判断的内部版本，二者需要一起维护。

![Android 发布：调试包与正式签名包的区别的处理、反馈与观察关系](/img/tech-notes/android-apk-signing-release.svg)

图中的四个节点分别表示应用身份、版本编号、发布签名、安装升级。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

在离线受控环境保管正式签名文件，通过构建配置生成 release 包。示例只列非敏感字段，不公开密钥路径与密码。

```text
applicationId = stable application identity
versionCode = monotonically increased release number
versionName = user-visible version label
signing material = controlled backup, excluded from source
```

先在模拟器运行，再用独立测试设备核对。代码片段需补齐类、资源和清单声明；需要外部数据的地方使用本地演示接口，安装成功与用户任务完成分别验收。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 相同包名但签名不同 | 通常不能作为原应用正常升级 |
| 只改显示版本文字 | 内部升级编号仍需正确增加 |
| 签名文件丢失 | 会影响后续同身份发布 |

### 对照 1：相同包名但签名不同

通常不能作为原应用正常升级。观察时记录实际证书身份与安装错误。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：只改显示版本文字

内部升级编号仍需正确增加。观察时记录versionCode 与 versionName。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：签名文件丢失

会影响后续同身份发布。观察时记录备份与访问责任。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

发布包还要检查日志、测试入口和私密配置。能生成 release APK 只是构建结果，不代表已经通过商店或用户验收。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“签名文件丢失”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [Android 小应用实作：从列表、编辑到本地保存闭环](/tech/2017/10/05/android-app-complete-notes/)
- [Android 交付：用一张场景表验证完整软件](/tech/2017/10/25/android-release-acceptance-matrix/)

## 参考资料

1. [Android Studio 2.3 发布说明](https://developer.android.com/studio/releases/past-releases/as-2-3-0-release-notes)
2. [Android Gradle Plugin 2.3.0 说明](https://developer.android.com/build/releases/agp-2-3-0-release-notes)
3. [Android 7.1 平台说明](https://developer.android.com/about/versions/nougat/android-7.1)
