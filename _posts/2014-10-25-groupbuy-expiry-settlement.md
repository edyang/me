---
layout: post
title: 团购网站设计：券过期与商家结算不要共用一个状态
subtitle: 一张券过期，并不自动说明可以向商家结算。
date: 2014-10-25 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 团购网站
- 产品设计
tech_note: true
note_id: groupbuy-expiry-settlement
permalink: /tech/2014/10/25/groupbuy-expiry-settlement/
excerpt: 一张券过期，并不自动说明可以向商家结算。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/groupbuy-expiry-settlement.svg
technology_since: '2013-01-01'
---

一张券过期，并不自动说明可以向商家结算。消费资格、退款责任和资金结算是不同维度。

本文使用团购业务的虚构订单与关系数据模型，伪代码不连接真实支付。团购把用户购买、平台收款、商家履约与结算连接起来。下单、支付、成团、消费和退款必须保留各自状态，不能用一个布尔字段表达整个生命周期。

## 1. 从现象推到机制

券状态表示能否消费，结算状态表示某笔商家应付是否完成。到期任务要按业务时区和规则处理未使用券，并保留变更原因。结算依据应来自确认的消费或合同约定，不能直接拿支付总额计算。

![团购网站设计：券过期与商家结算不要共用一个状态的处理、反馈与观察关系](/img/tech-notes/groupbuy-expiry-settlement.svg)

图中的四个节点分别表示消费资格、到期处理、应付明细、结算批次。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

将券、退款和商家应付分别关联，建立一张可追溯明细而非只保存月度汇总。演示中先不处理复杂促销分摊。

```text
voucher: UNUSED -> USED | EXPIRED
refund: independent lifecycle
settlement_item: source_event, gross, fees, payable
settlement_batch: selected verified items
```

先列业务事件与允许的状态迁移，再用少量匿名订单演算。涉及金额的地方保存成交快照，涉及并发的地方使用数据库约束，外部支付行为按支付协议另行实现。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 券到期但存在退款处理中 | 不能简单纳入可结算收入 |
| 到期任务重跑 | 同一券只产生一次迁移 |
| 结算批次撤销后重建 | 明细不可重复支付 |

### 对照 1：券到期但存在退款处理中

不能简单纳入可结算收入。观察时记录退款责任与可结算口径。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：到期任务重跑

同一券只产生一次迁移。观察时记录变更前状态与事件唯一键。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：结算批次撤销后重建

明细不可重复支付。观察时记录结算项归属与支付状态。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

具体退款和结算条款需要业务与财务确认。技术文章只说明状态分离与追踪方式，不替代适用合同和法律判断。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“结算批次撤销后重建”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [团购网站设计：消费券核销怎样避免重复使用](/tech/2014/10/05/groupbuy-voucher-redemption/)
- [团购网站设计：退款申请不等于资金已退回](/tech/2014/10/15/groupbuy-refund-state-machine/)

## 参考资料

1. [Spring 3.2.6 事务管理](https://docs.spring.io/spring-framework/docs/3.2.6.RELEASE/spring-framework-reference/htmlsingle/)
2. [Hibernate 4.3 事务与并发](https://docs.hibernate.org/orm/4.3/manual/en-US/html_single/)
