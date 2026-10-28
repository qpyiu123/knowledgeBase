---
title: 云环境取证（AWS CloudTrail、K8s audit log）
category: forensics
tags: [cloud, cloudtrail, kubernetes, audit-log, iam, detection]
signals: [附件是 cloudtrail 的 json gz 日志, 题目问哪个 access key 创建了新的 iam 用户, 日志里 eventSource 字段重复出现同一个异常服务, 要求还原攻击者在云上的完整操作链, 给了 k8s 的 audit log json 每行一个 records, 出现了 ListBuckets 之后再 GetObject 的大量请求, 题目说云上数据被下载了要找出下载了多少]
difficulty: medium
source: "AWS CloudTrail 用户指南 / Kubernetes 官方 Auditing 文档 / apiserver-audit v1 API"
tools: [python, jq, awscli, kubectl, grep, zeek, elastic]
updated: 2026-10-22
exec_yaml: ok
relates_to: [ai/backdoor-and-poisoning.md]
---

## 一、识别信号（题面长什么样）

- 附件是 `*.json.gz` 一堆小文件，路径形如 `AWSLogs/<account>/CloudTrail/<region>/<year>/<month>/<day>/`。
- 正文里有 `"eventSource": "iam.amazonaws.com"`、`"eventName": "CreateUser"`、`"userIdentity"`、`"errorCode": "AccessDenied"`。
- 附件是 k8s 的 `audit.log`，每行一个 JSON，含 `"kind":"Event"`、`"verb":"create"`、`"user":{"username":...}`。
- 题目问"攻击者用哪个 IAM 用户做了什么""从哪个 IP 登录的""删掉了哪个 namespace"。
- 时间都是 UTC，带有 `eventTime` 或 `requestReceivedTimestamp`。
- 出现 `AssumeRole` → `GetCallerIdentity` → `ListBuckets` 这种典型侦察序列。

## 二、原理

- **CloudTrail**：每 5 分钟打包一批记录，字段核心是 `userIdentity`（谁）、`eventSource`+`eventName`（做了什么）、`sourceIPAddress`（从哪来）、`responseElements`（结果）、`errorCode`（失败原因）。`userIdentity` 有三种典型形态：`IAMUser`（长期 AK）、`AssumedRole`（含 `sessionContext.sessionIssuer`）、`AWSService`。
- **攻击链特征**：
  - 侦察：`GetCallerIdentity`、`ListUsers`、`ListBuckets`、`DescribeInstances`。
  - 权限维持：`CreateUser`、`CreateAccessKey`、`AttachUserPolicy`、`CreateLoginProfile`。
  - 数据外带：`GetObject`、`GetSecretValue`、`GenerateDataKey`。
  - 反取证：`StopLogging`、`DeleteTrail`、`PutEventSelectors`。
- **K8s audit**：rule 决定记录级别（`None`/`Metadata`/`Request`/`RequestResponse`）；事件里 `objectRef` 定位资源，`user.username` 区分普通用户与 `system:serviceaccount:<ns>:<sa>`。
- **时间线对齐**：CloudTrail 里 `eventTime` 与 `requestParameters` 里的桶名/密钥名一起看，才能拼出"从哪到哪"。

## 三、操作步骤

1. **解压并合并**：多个 `.json.gz` 合并成一个 JSONL（每行一个 `Records` 元素）。
2. **建立时间线**：按 `eventTime` 排序，打印 `时间|user|eventSource:eventName|IP|关键参数`。
3. **筛 IAM 高危动作**：`grep -E 'CreateUser|CreateAccessKey|Attach.*Policy|StopLogging'`。
4. **关联 AK**：追踪 `userIdentity.accessKeyId` 的全生命周期（何时出现、被谁创建）。
5. **找外带**：按 `eventName=GetObject` 统计对象数与字节数，或 `responseElements` 里的 `Location`。
6. **K8s**：按 `verb`+`objectRef.resource` 聚合，找 `create secrets`、`delete pods`、`exec` 进入容器。
7. **写结论**：把事件按"侦察 → 提权 → 持久化 → 外带 → 清理"分组输出。

## 四、命令 / 脚本

```bash
# 合并 CloudTrail 日志为 JSONL
for f in $(find logs -name '*.json.gz'); do zcat "$f"; done \
  | jq -c '.Records[]' > ct.jsonl
# 高危事件概览
jq -r '[.eventTime, .userIdentity.type, (.userIdentity.arn // .userIdentity.userName),
        .eventSource, .eventName, .sourceIPAddress, (.errorCode // "OK")] | @tsv' ct.jsonl \
  | sort | grep -Ei 'CreateUser|CreateAccessKey|Attach|PutUserPolicy|StopLogging|DeleteTrail'
# 谁在调 GetObject，取了多少
jq -r 'select(.eventName=="GetObject") | [.eventTime, .userIdentity.arn, .requestParameters.bucketName, .requestParameters.key] | @tsv' ct.jsonl | head -30
# 失败的访问尝试（权限提升探测）
jq -r 'select(.errorCode!=null) | [.eventTime, .userIdentity.arn, .eventName, .errorCode] | @tsv' ct.jsonl | sort | uniq -c | sort -rn | head
```

```python
#!/usr/bin/env python3
# CloudTrail 时间线 + 攻击链分类
import json, sys, collections, datetime

CRIT = {
    'Discovery': ['GetCallerIdentity', 'ListUsers', 'ListRoles', 'ListBuckets',
                  'DescribeInstances', 'DescribeFlowLogs'],
    'Persistence': ['CreateUser', 'CreateAccessKey', 'CreateLoginProfile',
                    'AttachUserPolicy', 'PutUserPolicy', 'CreateRole'],
    'Exfil': ['GetObject', 'GetSecretValue', 'DownloadDBLogFilePortion', 'SelectObjectContent'],
    'AntiForensics': ['StopLogging', 'DeleteTrail', 'UpdateTrail', 'PutEventSelectors'],
}
REV = {v: k for k, vs in CRIT.items() for v in vs}

def load(path):
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        if line:
            yield json.loads(line)

def timeline(path):
    rows = sorted(load(path), key=lambda r: r.get('eventTime', ''))
    stage_count = collections.Counter()
    for r in rows:
        ev = r.get('eventName', '')
        stage = REV.get(ev)
        if not stage:
            continue
        stage_count[stage] += 1
        ui = r.get('userIdentity', {})
        arn = ui.get('arn') or ui.get('userName') or ui.get('type')
        print('%s %-13s %-45s %-26s %s' % (r.get('eventTime'), stage, arn, ev,
                                           r.get('sourceIPAddress')))
    print('\n阶段统计:', dict(stage_count))

if __name__ == '__main__':
    timeline(sys.argv[1])
```

```bash
# Kubernetes audit log 分析
jq -r '[."requestReceivedTimestamp", .user.username, .verb,
        (.objectRef.resource // ""), (.objectRef.name // ""), (.objectRef.namespace // ""),
        (.responseStatus.code // 0)] | @tsv' audit.log \
  | sort | grep -E '\b(create|delete|patch|get)\b' | head -50
# 谁 exec 进了容器
jq -r 'select(.objectRef.subresource=="exec") | [."requestReceivedTimestamp", .user.username, .objectRef.name] | @tsv' audit.log
# 审计级别为 None 的豁免项（反取证尝试）
jq -r 'select(.level=="None") | [.verb, .objectRef.resource, .user.username] | @tsv' audit.log | sort -u
```

## 五、常见坑 / 变体

- **CloudTrail 记录中有个外层结构**：`.Records[]`，直接 `jq .eventName` 会得到 null。
- **`sourceIPAddress` 可能是服务名**：`cloudtrail.amazonaws.com`、`AWS Internal`，不代表真实客户端 IP。
- **多账号/多 region 分散**：同一操作可能跨 region 留下多条记录，`userIdentity.principalId` 唯一化后再聚合。
- **时区**：CloudTrail 全 UTC，K8s 的 `requestReceivedTimestamp` 也 UTC（带 Z）；题目给的本地时间要换算。
- **Data event 默认不开**：`GetObject` 属于数据事件，若日志里没有，不代表没发生——可能只是没开。
- **K8s `RequestResponse` 级别**：只有该级别才有 `requestObject`/`responseObject` 正文，`Metadata` 级别看不到 Secret 内容。
- **变体**：Azure Activity Log（`operationName` + `properties`）、GCP Cloud Audit（`protoPayload.methodName`）、阿里云 ActionTrail。

## 六、参考来源

- [AWS CloudTrail 日志文件示例（字段结构与命名规则）](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-examples.html)
- [Kubernetes 官方 Auditing 文档（audit policy 与四个级别）](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/)
- [kube-apiserver Audit Configuration v1（Event 结构定义）](https://kubernetes.io/docs/reference/config-api/apiserver-audit.v1/)
- [Hack The Box：CloudTrail 日志分析实战技巧](https://www.hackthebox.com/blog/securing-the-cloud-expert-tips-for-analyzing-cloudtrail-logs)
- [MITRE ATT&CK Cloud 矩阵（对应技术编号）](https://attack.mitre.org/matrices/enterprise/cloud/)
