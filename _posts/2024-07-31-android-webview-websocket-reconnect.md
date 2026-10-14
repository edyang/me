---
layout: post
title: Android WebView 实时断线：页面生命周期
subtitle: 浏览器正常而 WebView 周期断开，需检查是否定时 reload 销毁连接。
date: 2024-07-31 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 前端
- Web
tech_note: true
note_id: android-webview-websocket-reconnect
permalink: /tech/2024/07/31/android-webview-websocket-reconnect/
excerpt: 浏览器正常而 WebView 周期断开，需检查是否定时 reload 销毁连接。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/android-webview-websocket-reconnect.svg
technology_since: '2019-01-01'
---

浏览器正常而 WebView 周期断开，需检查是否定时 reload 销毁连接。

loadUrl、reload、组件销毁和后台行为影响 socket。服务端握手日志可以区分未连接与连接后立即退出。

![Android WebView 实时断线：页面生命周期：处理路径与验证条件](/img/tech-notes/android-webview-websocket-reconnect.svg)

## 一、问题的范围与前提

浏览器所看到的页面、实际请求地址与服务器收到的路径要对应起来。页面来源、代理、缓存、Cookie 和连接生命周期分别影响行为。桌面浏览器、平板与嵌入式 WebView 可能具有不同访问条件，不能把某一端成功直接视为所有终端都已通过。

## 二、技术分析与方案取舍

服务端没有握手先查URL与网络策略，周期性握手后立即关闭再查页面reload与后台。WebView源码缺失时只列检查方向，不直接指定根因。清理socket和定时器还需禁止旧回调复活，恢复后核对只有一条订阅。连接状态、最后有效消息与业务数据时间分别展示。

实现时明确入口和 API 基址，页面或组件销毁后清理连接与定时器。版本更新需要考虑旧页面并存，错误提示保留网络、鉴权和依赖异常的区别。若采用代理，路径替换和协议头按预期上游核对，不能同时在多处随意拼接前缀。

## 三、实现与排查的顺序

1. 对照握手日志。
2. 检查页面刷新。
3. 清理旧资源。
4. 验证前后台恢复。

按这个顺序保留中间结果，可以区分输入条件、处理过程和最终输出。前一阶段的条件不成立时，先解释对应错误，再继续后面的试验；单次返回成功不足以覆盖整条链路。

### 最小示例

```javascript
let retryTimer = null;
let socket = null;
function cleanup() {
  if (retryTimer !== null) clearTimeout(retryTimer);
  if (socket !== null) socket.close();
  retryTimer = null;
  socket = null;
}
```

清理片段属于连接管理的一部分，并非完整重连实现。实际代码还要禁止关闭后再次触发旧定时器，维护组件有效标记并恢复订阅或缺失消息。

示例聚焦当前技术关系。引用的图片、数据库、消息对象或处理函数，需要由调用环境提供；它不包含完整服务的认证、持久化与并发管理。验证时先用受控输入检查，再纳入应用。

## 四、验证和结果解释

一组完整的排查资料应能展示请求方法、路径、响应状态与时间，以及相关后端记录。只展示一个登录失败截图，无法判断请求是否到达目标服务。共享记录时移除凭据和个人信息，仅保留非敏感字段、状态与必要结构。

| 需要验证的结果 | 保留的对照 | 不能由此推出的结论 |
| --- | --- | --- |
| 周期断开原因可解释 | 固定输入与配置、对应输出 | 一次成功代表所有条件成功 |
| 只有一个有效连接 | 中断前后状态与错误阶段 | 没有报错代表结果正确 |
| 数据时间正确 | 恢复后的同条件复测 | 临时恢复代表根因已经消失 |

验证应覆盖首次打开、缓存命中、刷新、断网恢复与后台切换。连接状态和最后有效数据分别显示，旧数据不能因页面仍打开而永久看作实时。发布后的页面和静态资源还应逐项核对，不仅检查仓库文件是否存在。

## 五、适用边界与结论

没有源码时 reload 只是检查方向，不能提前认定唯一根因。

这条路径把“对照握手日志”与“验证前后台恢复”连在一起，中间保留可复查的条件。实施时优先确认“周期断开原因可解释”，再检查“数据时间正确”；两者都满足，才能在当前样本与配置范围内评价方案。设备、数据或软件版本改变以后，相关假设需要重新验证。

## 参考资料

- [技术说明与实现资料 1](https://developer.mozilla.org/en-US/docs/Web)
