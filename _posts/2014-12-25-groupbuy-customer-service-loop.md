---
layout: post
title: 团购网站创业：把客服问题变成可追踪的产品反馈
subtitle: 同一问题反复由客服口头解释，意味着规则、页面或流程可能有缺口。
date: 2014-12-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 团购网站
- 产品设计
tech_note: true
note_id: groupbuy-customer-service-loop
permalink: /tech/2014/12/25/groupbuy-customer-service-loop/
excerpt: 同一问题反复由客服口头解释，意味着规则、页面或流程可能有缺口。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/groupbuy-customer-service-loop.svg
technology_since: '2013-01-01'
---

同一问题反复由客服口头解释，意味着规则、页面或流程可能有缺口。反馈要能回到具体业务状态。

本文使用团购业务的虚构订单与关系数据模型，伪代码不连接真实支付。团购把用户购买、平台收款、商家履约与结算连接起来。下单、支付、成团、消费和退款必须保留各自状态，不能用一个布尔字段表达整个生命周期。

## 1. 从现象推到机制

工单关联订单、券与退款身份，区分事实、用户诉求和处理建议。先查看支付及核销证据，再决定解释、补偿或升级。问题分类应服务于发现重复原因，不是简单统计客服处理数量。

![团购网站创业：把客服问题变成可追踪的产品反馈的处理、反馈与观察关系](/img/tech-notes/groupbuy-customer-service-loop.svg)

图中的四个节点分别表示用户反馈、业务证据、处理动作、产品改进。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

建立一个包含现象、业务状态、证据来源和下一步的最小工单。结案时记录实际结果，并检查是否需要修改页面说明或系统规则。

```text
ticket: order_id, symptom, requested_outcome
evidence: payment_state, voucher_state, rule_version
action: owner_role, next_step, due_condition
closure: verified_result, recurring_cause
```

先列业务事件与允许的状态迁移，再用少量匿名订单演算。涉及金额的地方保存成交快照，涉及并发的地方使用数据库约束，外部支付行为按支付协议另行实现。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 用户称付款而订单未确认 | 先查通道交易和本地记录 |
| 同类预约投诉反复出现 | 需要回看售前规则展示 |
| 工单标记已处理但用户仍受阻 | 结案要核对真实任务完成 |

### 对照 1：用户称付款而订单未确认

先查通道交易和本地记录。观察时记录资金事实与页面状态。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：同类预约投诉反复出现

需要回看售前规则展示。观察时记录问题批次与共同套餐版本。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：工单标记已处理但用户仍受阻

结案要核对真实任务完成。观察时记录处理动作与最终业务结果。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

工单记录应控制访问范围。技术复盘可以保留匿名原因与流程证据，没必要复制用户完整联系方式和支付资料。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“工单标记已处理但用户仍受阻”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [团购网站创业：商家上线先把履约条件说清楚](/tech/2014/12/05/groupbuy-merchant-onboarding/)
- [团购网站创业：浏览、支付与核销分别看转化](/tech/2014/12/15/groupbuy-funnel-definition/)

## 参考资料

1. [Spring 3.2.6 事务管理](https://docs.spring.io/spring-framework/docs/3.2.6.RELEASE/spring-framework-reference/htmlsingle/)
2. [Hibernate 4.3 事务与并发](https://docs.hibernate.org/orm/4.3/manual/en-US/html_single/)
