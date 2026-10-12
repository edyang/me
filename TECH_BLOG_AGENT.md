# 个人技术分享发布规则

## 任务目标

将与 ChatGPT 的可访问技术交流整理成 edyang 的个人技术文章，发布到 edyang/me 的 master，由现有 GitHub Pages 展示在 https://edyang.me/。已有授权包含新增、修正文稿和必要的归档配套；不需要为每次正常发布重复确认。与其它企业官网或多平台发布任务分别运行。

## 内容来源与范围

先读取本文件、AGENTS.md、_data/tech_notes.yml 和 _data/tech_note_runs.yml，再通过可用的个人上下文检索新增技术交流。检索工具不是全量聊天导出，不能声称覆盖不可访问内容。使用明确时间范围并保留内部来源依据，但不把原始检索结果提交到公共仓库。

技术内容包括开发、部署、运维、硬件排查、工业通信、通用视觉方法、CAD 和自动化经验。跳过家庭、孩子、财务、账号纠纷、人事与客户沟通。不对日常寒暄或重复问题单独发文。没有足够正文依据的主题暂缓；有价值的未解决问题可以写排查笔记并明确验证边界。

## 脱敏

脱敏必须在提交到公共分支之前完成，公共 PR 和 Git 历史同样会永久留存材料。去除或泛化客户及机构名称、人员身份、人脸、真实车牌、声音样本、私人邮件和电话、内部域名、IP/MAC、设备序列号、Wi-Fi 名称、用户名、个人路径、账号、token、密码、Cookie、证书私钥以及商业金额和未公开产品细节。曾明确要求不得公开的算法组合、参数、控制接线、内部接口和文档，不得因这次博客整理而披露。

示例使用 loopback 或清楚的占位符，不复制真实部署配置。不能只删名字却保留可识别的完整场景。原理图重新绘制为通用图，不把生成图冒充现场照片。不上传原始聊天、客户附件和未经逐项检查的截图。

## 写作与事实

使用自然的第一人称技术笔记，围绕具体问题写背景、证据、排查过程、解释和验证范围。减少口号和重复句。示例代码标明适用范围，危险控制动作不自动执行。

区分用户实际反馈、助手建议和公开文档；建议不能写成已落地，目标不能写成实测指标。需要当前版本行为时查官方文档；保留参考链接。没有记录就写未确认，禁止补造准确率、性能或成功反馈。

## 文章与日期

沿用 _layouts/post.html，新增文章存 _posts/YYYY-MM-DD-slug.md。稳定 note_id 和 permalink 用于去重，原题有后续进展优先更新原文并保留 published_at。

必需 front matter：layout=post、title、excerpt、tags、tech_note=true、note_id、source_date、source_dates、date、published_at、updated_at、verification、privacy_reviewed=true、permalink。source_date 是原始交流日期；date 用该日排序，页面绝不能将它称为首次发布日期。published_at 是实际首次发出的本地时间，updated_at 是实际本轮更新时间，均含 +08:00。若原始日期无法确认，不能猜一个日期；先待补证据。

verification：observed=有实际现象/结果，partial=部分待验证，proposal=方案笔记，notes=通用方法。observed 不等于所有问题解决。

同步 _data/tech_notes.yml 中的同名条目及最终文件 sha256。_data/tech_note_runs.yml 只记录已完成的实际工作，不含 raw messages、conversation IDs 或 private URLs。

## 增量与补档

检索最近三天的交流并与 registry 对照，留重叠窗口避免漏掉补充内容。无新内容则不发文章、不写空提交。先更新已发表主题；同题只在新事实或独立问题出现时另发。

同时检查尚未覆盖的历史主题，按可访问记录继续补档；不要用一个最近日期当作所有历史已扫描的证明。未取得全量导出时，coverage 保持 accessible_retrieval_only。每次优先完成可验证稿件，不以写选题列表代替实际产出。

## 配图

准确的机制、流程或几何关系使用 SVG；有必要的插画可调用图像生成工具。所有文件放 img/tech-notes/，检查实际格式和可解码性，文章引用本仓库路径并提供 alt。图示标明通用示意。缺少原图时不假称已经脱敏使用原图。

## 验证与发布

执行 python3 scripts/validate_tech_notes.py，检查重复、日期、脱敏线索、registry hash、图片引用和 SVG。正则检测只是辅助，仍需人工语义复核。

有 CI 时先创建分支和 PR，等待 Content and Jekyll validation 成功后正常合并 master，保留 expected head，不能强推或绕过规则。如果 Actions 无法执行但仓库允许正常提交，在确认源文件检查通过后仍可依现有 Pages 构建发布，并如实标明构建验证范围。

GitHub 提交成功只表示仓库已更新。核验 https://edyang.me/tech-notes/、本轮文章标题/日期/正文、配图及首页入口。部署期间继续查看构建；失败记录真实错误，未知状态先查询而不重复发布。核验成功后更新整理记录为 published，保留真实 verified_at。不能把草稿、PR 或构建排队说成上线。

每轮最终给出新增/更新篇数、可访问链接和必要阻塞。任务触发后按规则执行，Pages 构建完成时间可能晚于触发时刻。

