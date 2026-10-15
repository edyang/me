---
layout: post
title: 大型支付系统学习：对账不是只比较总金额
subtitle: 双方总金额一样，仍可能存在一笔多记、一笔少记。
date: 2013-10-15 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- 支付系统
- 系统设计
tech_note: true
note_id: payment-reconciliation-differences
permalink: /tech/2013/10/15/payment-reconciliation-differences/
excerpt: 双方总金额一样，仍可能存在一笔多记、一笔少记。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/payment-reconciliation-differences.svg
technology_since: '2011-07-28'
---

双方总金额一样，仍可能存在一笔多记、一笔少记。对账需要逐笔身份与汇总校验结合。

本文使用Java 7 与支持事务、唯一约束的关系数据库，代码为设计伪代码。支付系统同时面对用户请求、外部通道和本地账务，三者不共享一个事务。网络异常下必须保留“不确定”状态，并用查询、流水和对账逐步消除差异。

## 1. 从现象推到机制

先按通道流水、业务日期和币种对齐数据，再比较状态、金额和手续费。对账单缺失、时间切点不同与业务真的漏记是不同原因。差异要形成可跟踪记录，不能为了让报表平衡直接覆盖账务。

![大型支付系统学习：对账不是只比较总金额的处理、反馈与观察关系](/img/tech-notes/payment-reconciliation-differences.svg)

图中的四个节点分别表示双方流水、口径统一、逐笔匹配、差异处理。顺着实线检查输入如何变成输出，再沿虚线核对反馈条件。图示表达的是本文讨论的关系，不是实测曲线或现场截图。

## 2. 最小实现与输入条件

准备两份虚构流水文件，分别制造缺失、重复、金额不等与跨日状态变化。输出差异类别及来源行号。

```text
for key in union(local_keys, channel_keys):
    if key not in local: report("local_missing", key)
    elif key not in channel: report("channel_missing", key)
    elif local[key].amount != channel[key].amount:
        report("amount_mismatch", key)
```

示例使用虚构订单和金额，不能连接真实支付通道。实现时需要替换数据库访问与验签适配，并明确事务提交点；外部接口的签名字段和响应约定以通道协议为准。

## 3. 用对照区分原因

下表列出需要主动改变的条件。预期行为来自机制分析，复现时还需记录运行环境和原始输出，不能将预期当作已经测得的结果。

| 改变的条件 | 需要验证的行为 |
| --- | --- |
| 一笔多记且另一笔少记 | 总额相同仍应检出逐笔差异 |
| 通道按另一时区切日 | 先统一业务日边界再判断 |
| 手续费单独结算 | 不能把净额与交易额直接比较 |

### 对照 1：一笔多记且另一笔少记

总额相同仍应检出逐笔差异。观察时记录业务键匹配结果。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 2：通道按另一时区切日

先统一业务日边界再判断。观察时记录原始交易时刻与账单区间。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。
### 对照 3：手续费单独结算

不能把净额与交易额直接比较。观察时记录字段定义与费用分录。把这个条件与基准情形分开，有助于判断变化来自哪一层；若得到相反结果，应先核对前提，再修改实现。

## 4. 适用条件与取舍

差异修复应有依据和审核轨迹。对账程序负责发现和分类，并不应在未知原因时自动补出一笔收入或支出。

一次正常运行只覆盖了这组输入。继续扩展前，应把上面的异常对照保留下来，尤其关注“手续费单独结算”这一分支。后续方案若改变了图中任意一处依赖，原来的判断就要重新验证，不能仅凭界面相似或返回值相同沿用结论。

## 同月延伸

- [大型支付系统学习：金额精度与账务分录](/tech/2013/10/05/payment-ledger-minor-units/)
- [大型支付系统学习：超时、重试与结果未知](/tech/2013/10/25/payment-timeouts-retry-budget/)

## 参考资料

1. [Java 7 BigDecimal](https://docs.oracle.com/javase/7/docs/api/java/math/BigDecimal.html)
2. [RFC 2104：HMAC](https://www.rfc-editor.org/rfc/rfc2104)
