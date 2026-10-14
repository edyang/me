---
layout: post
title: 用 Docker Compose 部署 Web 服务：网络、数据与故障恢复
subtitle: 从一个可验证的小服务开始，把容器网络、持久化、健康检查和故障恢复的条件写清楚。
date: 2020-01-05 08:00:00 +0800
author: edyang
header-style: text
catalog: true
tags:
- Docker
- 部署
tech_note: true
note_id: compose-web-foundations
permalink: /tech/2020/01/05/compose-web-foundations/
excerpt: 从一个可验证的小服务开始，把容器网络、持久化、健康检查和故障恢复的条件写清楚。
privacy_reviewed: true
content_revision: 3
images:
- /img/tech-notes/compose-web-foundations.svg
technology_since: '2019-01-01'
---

把程序放进容器并不难，难的是换一台机器仍能启动，重建服务以后数据还在，出了问题能够判断故障发生在哪一层。对于一套由 Web 应用和缓存组成的小系统，部署方案至少要回答四个问题：应用如何连接依赖，哪些端口对外开放，数据存在哪里，以及服务异常后怎样恢复。

这篇以一个简单的 Python Web 服务为例，讨论如何用 Docker Compose 管理应用与 Redis。重点放在部署边界和可验证的行为，避免把“容器正在运行”当作整个系统已经可用。

## 1. 先确定部署范围

示例面向单台 Linux 主机：Web 服务接收 HTTP 请求，Redis 保存演示计数，Docker Compose 负责创建容器、网络和数据卷。它不涉及多主机调度，也不解决高可用问题。如果主机本身故障，这套配置无法把业务自动迁到另一台机器。

各部分的责任应当清楚：镜像提供程序与运行环境，容器承担进程运行，网络提供服务间访问，数据卷保存需要跨容器生命周期保留的文件。Compose 将这些关系写成配置，便于检查与复现，但配置文件本身不能证明运行状态。

示例采用以下版本范围：

| 组件 | 示例版本 | 作用 |
| --- | --- | --- |
| Docker Engine | 19.03 系列 | 容器、网络与存储运行环境 |
| Docker Compose | 1.25.0 | 描述和管理单机多服务 |
| Python | 3.7.6 | 应用运行时 |
| Gunicorn | 20.0.4 | 承载 WSGI 应用 |
| Redis | 5.0.7 | 保存演示计数与验证依赖访问 |
| redis-py | 3.3.11 | Python Redis 客户端 |

命令使用独立的 `docker-compose` 程序。固定版本便于解释行为，不过镜像标签仍可能被重新构建；需要严格复现时，还应记录镜像实际摘要以及依赖锁定文件。不同 CPU 架构、存储驱动和主机内核也属于部署条件。

## 2. 网络设计：外部入口和内部依赖分开

![Web 与 Redis 通信及命名卷关系](/img/tech-notes/compose-web-foundations.svg)

图中 Web 与 Redis 接入同一条用户自定义 bridge 网络。Web 通过服务名 `redis` 访问缓存，外部请求通过宿主机端口映射到 Web。Redis 不发布宿主机端口，数据目录挂载到独立命名卷。

这里有三个容易混淆的地址：浏览器使用宿主机地址，Web 容器使用 `redis:6379`，Web 进程自己监听容器内的 `0.0.0.0:8000`。端口映射只处理宿主机入口，不会把应用连接串里的 `localhost` 自动改成另一个服务。

在 Web 容器中，`localhost` 指向 Web 容器自身。即使宿主机上另有一个 Redis，用 `localhost:6379` 也不能因此访问它。容器之间使用服务名与容器端口，宿主机或浏览器使用发布地址，这两条路径要分别验证。

也不应把容器 IP 固定写进应用。服务重建后 IP 可能变化，服务名仍可作为访问入口；但是已有 TCP 连接不一定能继续使用，应用仍须在连接失效时重新连接。

## 3. 准备一个足够小的应用

为了让部署行为容易检查，示例只保留两个接口：`/` 增加一次演示访问计数，`/health` 检查 Redis 是否可访问。计数通过 Redis 的 `INCR` 原子操作完成，不采用应用端“读取再写回”，避免多个工作进程互相覆盖。

`app.py`：

```python
import json
import os

import redis

cache = redis.Redis.from_url(
    os.environ.get("REDIS_URL", "redis://redis:6379/0"),
    socket_connect_timeout=2,
    socket_timeout=2,
)


def application(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    if path not in ("/", "/health"):
        status, data = "404 Not Found", {"error": "not_found"}
    else:
        try:
            if path == "/health":
                cache.ping()
                data = {"status": "ready"}
            else:
                data = {"visits": cache.incr("demo:visits")}
            status = "200 OK"
        except redis.exceptions.RedisError:
            status = "503 Service Unavailable"
            data = {"status": "dependency_unavailable"}

    body = json.dumps(data).encode("utf-8")
    start_response(status, [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(body))),
    ])
    return [body]
```

这段代码采用标准 WSGI 接口，交给 Gunicorn 管理工作进程。Redis 暂时不可达时返回 503，而不是输出一个看似正常的计数。连接与读取都有超时，避免依赖异常让请求无限等待。

`/health` 表达的是包含依赖的就绪状态。它不是对所有业务功能的验收，更不能证明写入持久化或备份正确。如果一个真实应用可以在缓存故障时降级运行，就绪条件还要按业务设计调整。

`requirements.txt`：

```text
gunicorn==20.0.4
redis==3.3.11
```

`Dockerfile`：

```dockerfile
FROM python:3.7.6-slim-buster

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py ./

RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --no-create-home app
USER app

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", \
     "--workers", "2", "--timeout", "30", \
     "--access-logfile", "-", "--error-logfile", "-", \
     "app:application"]
```

先复制依赖清单再复制业务代码，是为了利用镜像构建缓存。应用代码变更时，依赖层不必每次重新安装。运行时切换为普通用户，Gunicorn 在前台运行，访问与错误日志送往标准输出和标准错误，便于容器运行环境收集。

`EXPOSE` 只是镜像中的端口说明，不会自动发布端口。真正的宿主机映射放在 Compose 配置中。工作进程数量为演示值，生产环境需要结合 CPU、内存、阻塞操作和请求负载调整。

## 4. 用 Compose 把边界写清楚

项目目录中放入 `app.py`、`requirements.txt`、`Dockerfile` 和下面的 `docker-compose.yml`：

```yaml
version: "3.7"

services:
  web:
    build: .
    image: demo-web:v1
    restart: unless-stopped
    ports:
      - "127.0.0.1:8080:8000"
    environment:
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - redis
    networks:
      - app_net
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()"]
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 20s
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  redis:
    image: redis:5.0.7
    restart: unless-stopped
    command: ["redis-server", "--appendonly", "yes", "--appendfsync", "everysec"]
    volumes:
      - redis_data:/data
    networks:
      - app_net
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 15s
      timeout: 3s
      retries: 3
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

networks:
  app_net:
    driver: bridge

volumes:
  redis_data:
```

这份配置有几项需要单独理解。

**宿主机只绑定回环入口。** `127.0.0.1:8080:8000` 适合本机验证或由同一主机上的反向代理转发，局域网其它设备不能直接通过主机网卡地址访问它。确需直接开放时，再结合防火墙与访问范围规划监听地址。

**Redis 只承担内部服务。** 没有 `ports` 并不阻止同网络的容器访问 Redis，也不表示 Redis 获得了独立的身份认证机制。服务网络是访问边界的一部分，不应把无须公开的数据库和缓存端口发布到外网。

**启动顺序不等于就绪顺序。** 在这份 v3.7 配置中，`depends_on` 描述依赖启动顺序，不会等待 Redis 的健康检查通过。应用需要能够处理短暂连接失败与后续重连。这里通过有界超时与 503 表达未就绪，Redis 恢复后新的请求再尝试连接。

**健康状态不等于自动恢复动作。** Docker 可以标记容器为 unhealthy，但这份 `restart` 策略并不会因为 unhealthy 自动重启容器。重启策略主要围绕进程退出工作；进程活着却不再正常响应，需要另外设计监测和有边界的处置，不能把两种机制混为一谈。

## 5. 启动以后，按层验证

先检查配置，再构建并启动：

```bash
docker-compose config
docker-compose build web
docker-compose up -d
docker-compose ps
docker-compose logs --tail=100 web redis
```

`config` 可以提前暴露 YAML 结构、变量替换和部分配置问题，但不会验证业务功能。构建成功说明镜像生成完成，容器启动说明入口进程已执行，还需要继续检查请求与依赖。

从宿主机确认两个接口：

```bash
curl -i http://127.0.0.1:8080/health
curl -i http://127.0.0.1:8080/
```

依赖正常时，健康接口应返回 200 和 ready；计数接口应返回一个数值。连续调用计数接口，检查数值是否增长。预期行为用于验证配置，不代表系统的性能指标；吞吐和并发能力需要单独测试。

再从 Web 容器确认内部访问：

```bash
docker-compose exec web python -c "import socket; print(socket.gethostbyname('redis'))"
docker-compose exec web python -c "import os, redis; print(redis.Redis.from_url(os.environ['REDIS_URL'], socket_connect_timeout=2, socket_timeout=2).ping())"
```

第一条验证服务名解析，第二条验证 Redis 协议响应。DNS 有结果不证明端口可用，TCP 可连接也不证明认证、数据库编号和业务操作正确。分开验证可以避免看到某一步成功，就跳过后续步骤。

## 6. 数据卷、持久化和备份是三件事

Redis 在内存中处理数据，命名卷将 `/data` 与容器生命周期分开。AOF 开启后，写操作会进入持久化日志；`appendfsync everysec` 通常按秒同步，异常掉电时仍可能丢失最近约一秒的数据，实际结果还受系统 I/O 条件影响。

命名卷使容器重建后有机会继续读取原数据，不表示数据已经备份到另一台机器。卷被误删、主机磁盘损坏或数据本身被错误覆盖，仍需要备份与恢复方案。对于订单、凭据等核心数据，还要评估合适的数据系统与一致性要求，不能直接套用这个演示计数的持久化策略。

验证时可以先写入一组固定数据，再停止并重新启动服务，检查数据是否保留。接着重建 Redis 容器，确认仍挂载同一个卷。Compose 项目名会影响自动生成的资源名称；更换项目目录或项目名后，应先核对实际使用的卷，避免连到一个新空卷并误认为旧数据丢失。

还应区分正常重启验证与异常断电验证。前者通过不证明后者无数据损失，AOF 文件存在也不证明恢复流程可用。备份需要在一致性条件下取得，并在独立环境演练恢复。带 `-v` 的清理操作会涉及删除项目卷，不能当作普通重启手段。

## 7. 常见故障按证据定位

| 现象 | 优先检查 | 不足以单独下结论的证据 |
| --- | --- | --- |
| 宿主机打不开页面 | 容器状态、进程监听、端口映射与冲突 | 镜像已经构建 |
| 其它设备打不开页面 | 宿主机绑定地址、路由与防火墙 | 本机 curl 成功 |
| Web 无法连接 Redis | 服务名、共同网络、端口和客户端配置 | Redis 容器是 Up |
| 启动初期返回 503 | Redis 就绪时间、应用连接与超时 | depends_on 已配置 |
| 容器反复退出 | 退出码、入口命令、依赖和错误日志 | restart 策略存在 |
| 重建后数据为空 | 项目名、实际卷、挂载路径和持久化配置 | Compose 声明了 volumes |
| 运行一段时间磁盘满 | 日志增长、卷数据与镜像占用 | 容器数量没有增加 |

端口冲突可以从宿主机监听信息开始：

```bash
sudo ss -lntp 'sport = :8080'
docker-compose ps
```

先确认占用进程的用途，再决定调整映射或停止服务。左侧宿主机端口变更，通常不要求修改容器内的 8000，但入口代理、调用地址和监测配置要同步。

服务退出时，把退出码、最后一段错误日志与启动命令对照。不断增加重启次数只会重复触发同一个错误；如果进程没有退出，则看实际响应与健康检查，而不是只盯着容器 Up 状态。

磁盘问题同样需要区分日志、应用数据和镜像。限制 json-file 日志增长可以减少一类风险，但不会限制应用自己写在数据目录里的文件，也不会代替业务保留周期与备份管理。

## 8. 更新和回退需要保留完整条件

更新 Web 服务前，保存当前镜像标识、Compose 配置与必要的业务备份。配置变更后使用 `up -d` 让 Compose 按差异重建服务；单纯 `restart` 不会把新的环境变量、端口或挂载配置写进已有容器。

```bash
docker-compose build web
docker-compose up -d --no-deps web
```

这两条适用于只更新应用、依赖服务保持原状的情况。单实例重建可能中断请求，不是零停机方案。需要更高可用性时，必须另行设计多实例、流量切换与数据兼容，而不是靠多写一个重启参数实现。

镜像标签也不应始终覆盖为同一个 `latest`。保留可识别的发布版本或摘要，才能明确回到哪个程序。应用旧版本能重新启动，不代表它能够读取新版本已改变的数据；涉及结构或数据格式变更时，回退条件必须与迁移方案一起确认。

## 结语

这套部署方法的核心是把几个边界固定下来：应用访问依赖使用服务名，外部访问使用明确的发布入口，状态与数据分别保存，进程退出和业务未就绪分别处理。Compose 把关系写清楚，日志、健康检查和实际请求再证明它们是否按预期工作。

对于单机小系统，这样的方案已经足以建立清晰的部署与排查起点。它的能力范围也很明确：容器重建与进程恢复不等于主机高可用，数据卷不等于备份，启动成功不等于业务验收。只有把这些条件逐项验证，部署才会从一次手工操作变成可重复的工程过程。

## 参考资料

1. [Docker Engine 19.03 发布记录](https://docs.docker.com/engine/release-notes/19.03/)
2. [Docker Compose 1.25.0 版本记录](https://github.com/docker/compose/blob/1.25.0/CHANGELOG.md)
3. [Gunicorn 20.0.4 使用文档](https://docs.gunicorn.org/en/20.0.4/run.html)
4. [Redis 5.0.7 源码与版本说明](https://github.com/redis/redis/tree/5.0.7)
