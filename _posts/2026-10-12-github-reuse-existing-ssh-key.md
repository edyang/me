---
layout: post
title: Linux 配置 GitHub SSH：已有密钥就先复用
subtitle: 先确认密钥和公钥，再分别验证 SSH 身份认证与仓库访问。
date: 2026-10-12 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Git
- Linux
- SSH
tech_note: true
note_id: github-reuse-existing-ssh-key
source_date: '2026-10-12'
source_dates:
- '2026-10-12'
published_at: '2026-10-13T08:02:56+08:00'
updated_at: '2026-10-13T08:02:56+08:00'
verification: partial
privacy_reviewed: true
permalink: /tech/2026/10/12/github-reuse-existing-ssh-key/
excerpt: 先确认密钥和公钥，再分别验证 SSH 身份认证与仓库访问。
---

这次配置 GitHub SSH 时，我检查到机器上已经有一份 Ed25519 私钥。后续应该先核对并复用它，不能把重新生成密钥当成默认第一步。覆盖原文件可能影响已有连接，也不能解决远程地址仍使用 HTTPS 的问题。

## 先确认手上有什么

下面是通用示例，不含实际公钥和个人路径：

```bash
ls -l ~/.ssh/id_ed25519 ~/.ssh/id_ed25519.pub
ssh-keygen -lf ~/.ssh/id_ed25519.pub
```

第二条用于查看公钥指纹，不会更换密钥。如果只有私钥文件，先确认它的来源和用途，再从私钥推导公钥；不要直接覆盖同名文件。私钥、口令及完整调试日志都不应贴进公开笔记。

GitHub 账号里登记的是公钥。添加后，可以用明确指定密钥的方式测试，减少机器上多份密钥带来的歧义：

```bash
ssh -o IdentitiesOnly=yes -i ~/.ssh/id_ed25519 -T -l git github.com
```

首次连接时，先对照 GitHub 官方公布的主机指纹确认服务器身份，再接受提示。不要为了省掉提示关闭主机身份校验。

## 身份认证成功，还要检查仓库入口

GitHub 的 SSH 测试成功时会说明认证成功，并提示不提供 shell；官方文档也注明，此测试退出码为 1。因此不能只凭非零退出码判断失败，要结合输出内容。

```bash
git remote -v
```

如果远程地址仍是 HTTPS，Git 操作就不会因 SSH 测试成功而自动切换。确认目标仓库后，才将对应 remote 改成 SSH 地址。只读访问测试和写入权限也应分别确认；能够认证到账号，并不代表能够向任意仓库推送。

本次可确认的事实只有已有密钥。添加公钥、SSH 测试和实际 Git 访问仍是操作建议，没有后续成功回执，不能写成已经完成免密配置。带口令的私钥是否仍会提示输入，还取决于本机 ssh-agent 的状态。

## 参考资料

- [GitHub：检查已有 SSH 密钥](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/checking-for-existing-ssh-keys)
- [GitHub：添加公钥](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account)
- [GitHub：测试 SSH 连接](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/testing-your-ssh-connection)
