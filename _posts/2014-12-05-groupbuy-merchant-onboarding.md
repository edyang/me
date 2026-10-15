---
layout: post
title: 团购网站创业：商家上线先把履约条件说清楚
subtitle: 商家愿意提供优惠，不等于已经具备线上售卖条件。
date: 2014-12-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 团购网站
- 产品设计
tech_note: true
note_id: groupbuy-merchant-onboarding
permalink: /tech/2014/12/05/groupbuy-merchant-onboarding/
excerpt: 商家愿意提供优惠，不等于已经具备线上售卖条件。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/groupbuy-merchant-onboarding.svg
technology_since: '2013-01-01'
---

商家愿意提供优惠，不等于已经具备线上售卖条件。售前确认要覆盖消费者真正会遇到的限制。

本文使用团购业务的虚构订单与关系数据模型，伪代码不连接真实支付。团购把用户购买、平台收款、商家履约与结算连接起来。下单、支付、成团、消费和退款必须保留各自状态，不能用一个布尔字段表达整个生命周期。

## 1. 从现象推到机制

可用门店、预约要求、不可用时段、套餐包含项与退款条件都影响履约。规则藏在长描述中容易被忽略，关键限制应结构化展示，并进入订单快照。平台审核的是可执行承诺，而不是只检查图片好看。

![团购网站创业：商家上线先把履约条件说清楚的处理、反馈与观察关系](/img/tech-notes/groupbuy-merchant-onboarding.svg)

图中的四个节点分别表示商家承诺、结构化规则、上线演练、版本留存。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

用一张商家上线表核对库存、核销账号和异常联系人角色。上线前让另一人按消费者路径走一次演示购买与预约。

```text
offer: included_items, excluded_items
usage: stores, booking_required, usable_periods
fulfillment: verification_role, exception_process
release: reviewed_version
```

先列业务事件与允许的状态迁移，再用少量匿名订单演算。涉及金额的地方保存成交快照，涉及并发的地方使用数据库约束，外部支付行为按支付协议另行实现。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 套餐需预约但页面未提示 | 用户即使买到也可能无法消费 |
| 核销账号未配置 | 门店无法完成在线核销 |
| 规则上线后被调整 | 历史订单仍按成交规则解释 |

### 对照 1：套餐需预约但页面未提示

用户即使买到也可能无法消费。观察时记录售前展示与实际使用条件。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：核销账号未配置

门店无法完成在线核销。观察时记录账号权限与演示消费结果。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：规则上线后被调整

历史订单仍按成交规则解释。观察时记录发布版本与订单快照。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

商家资料不是收集越多越好。只采集履约与结算必需内容，权限按岗位分配，避免把私人联系方式放进公开页面。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“规则上线后被调整”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [团购网站创业：浏览、支付与核销分别看转化](/tech/2014/12/15/groupbuy-funnel-definition/)
- [团购网站创业：把客服问题变成可追踪的产品反馈](/tech/2014/12/25/groupbuy-customer-service-loop/)

## 参考资料

1. [Spring 3.2.6 事务管理](https://docs.spring.io/spring-framework/docs/3.2.6.RELEASE/spring-framework-reference/htmlsingle/)
2. [Hibernate 4.3 事务与并发](https://docs.hibernate.org/orm/4.3/manual/en-US/html_single/)
