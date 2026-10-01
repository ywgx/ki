## 即刻开始

推荐全局安装`ki`工具,在你日常管理 k8s 的 Linux 主机上执行

```bash
curl xabc.io/ki | bash
```

上面指令将下载安装两个文件 `/usr/local/bin/ki`和`/etc/profile.d/zki.sh`,当然也可以手动下载 [github.com/ywgx/ki](https://github.com/ywgx/ki) ,根据自己的习惯放到可以执行的路径即可

!> 需要注意的是默认 `ki` 的解释器路径是`/usr/bin/python3`,请查看你所在主机 python3 所在路径,如有差异,请修改 `/usr/local/bin/ki` 第一行`#!/usr/bin/python3
`即可

## 列出当前 k8s 的 Namespace

这里有3个 k8s 集群,当前 config 软连接指向 `/root/.kube/kubeconfig-edge`

![](//static.xabc.io/ki/ki-1.png)

## 相似匹配

最相似匹配,`ki sys` 匹配到 kube-system 这个 Namespace,实际上 `ki sy` 在这里也可以匹配到

![](//static.xabc.io/ki/ki-2.png)

## 过滤搜索

全列表字符串过滤,可以不断缩小过滤范围,比如过滤搜索某个关键字 str 或者某个机器 14.8 的 Pod

![](//static.xabc.io/ki/ki-3.png)

## 自动切换 $KUBECONFIG

请留意,起初在 edge 集群下,`$ ki test`的时候因为当前 k8s 找不到任何匹配的 Namespace,自动寻找下一个,第2次就找到了,在 test 这个集群里有一个 test 的非空 Namespace,并且切换了 $KUBECONFIG,实时终端提示当前 $KUBECONFIG 为 kubeconfig-test

![](//static.xabc.io/ki/ki-8.png)

## 主动切换 $KUBECONFIG

有时候我们需要查看某个 Namespace,而这个 Namespace 在多个 k8s 集群中都存在,所以我们可以主动切换 $KUBECONFIG,有两种方式,一种是在参数中匹配自动切换一次到位 `ki $k8s.$ns`,另一种是先主动切换到目标 k8s `ki -s`

请留意起初`ki sys`查看的是 test 集群下的 kube-system,而`ki ho.sys`则会查看 hongkong 集群下的 kube-system, ki 可以分开解析 ho.sys, ho 可以相似度匹配到 kubeconfig-hongkong, sys 可以相似度匹配到 kube-system

![](//static.xabc.io/ki/ki-19.png)

当我们有海量的 k8s 集群的情况下,我们使用`ki -s` 过滤搜索选择要切换的目标 k8s

![](//static.xabc.io/ki/ki-20.png)

## **目标 Pod 的系列动作**

一般建议 Deployment(StatefulSet)/Service/Ingress 三类资源对象,命名最好一致,简洁明了,也有很多优点

### `$index` 回车直接登录 Pod

优先使用 bash,镜像中没有 bash 时使用 sh;镜像没有任何 shell(distroless 等)时 ki 会提示改用 [`$index dbg`](debug?id=index-dbg-调试没有-shell-的-pod)

![](//static.xabc.io/ki/ki-4.png)

### `$index l` 输出 Pod 实时日志

默认输出最新 200 行,`l` 后指定过的行数会被记住,下次直接 `l` 沿用

![](//static.xabc.io/ki/ki-5.png)

### `$index l 10000` 输出 Pod 实时日志

l 后加一个数字,代表要输出最新多少行日志

![](//static.xabc.io/ki/ki-6.png)

### `$index l chunked` 输出 Pod 实时日志的过滤

l 后加一个字符串,代表在最新 1024 行日志中过滤该字符串;`$index g chunked` 在全部日志中过滤,`$index c chunked` 同时输出匹配行前后各 10 行

![](//static.xabc.io/ki/ki-7.png)

### `$index e` 自动识别资源对象,进入编辑模式

![](//static.xabc.io/ki/ki-9.png)

### `$index es` 编辑目标 Pod 同名的 Service 资源

![](//static.xabc.io/ki/ki-10.png)

### `$index ei` 编辑目标 Pod 同名的 Ingress 资源

![](//static.xabc.io/ki/ki-11.png)

### `$index r` 重启目标 Pod

请留意这里重启的是目标 Pod 所属的资源对象

![](//static.xabc.io/ki/ki-12.png)

### `$index del` 删除目标 Pod

这里删除的是目标 Pod,一般根据 k8s 的调度规则很快就新拉起一个

![](//static.xabc.io/ki/ki-13.png)

### `$index cle` 清理目标 Pod 所属资源对象

!>请注意清理的是目标 Pod 所属的资源对象,所以清理就是彻底删除,清理(cle) 有意设计需要输入三个字符,期望你了解当前动作的意义,减少误操作

![](//static.xabc.io/ki/ki-14.png)

### Pod 动作速查

| 动作 | 说明 |
|---|---|
| `$index` | 登录 Pod,优先 bash,其次 sh |
| `$index l` / `$index l 500` / `$index 500` | 实时日志,指定行数会被记住 |
| `$index l xxx` / `g xxx` / `c xxx` | 日志过滤:最新 1024 行 / 全部日志 / 全部日志并输出前后 10 行 |
| `$index v` / `$index v 100` | 上一次崩溃退出的容器日志(--previous) |
| `$index e` / `es` / `ei` | 编辑所属资源对象 / 同名 Service / 同名 Ingress,同理 `eg` `eh` `eV` `eD` `eE` |
| `$index d` / `dp` / `ds` | describe 所属资源对象 / Pod / 同名 Service |
| `$index o` / `os` / `oi` | 输出所属资源对象 / 同名 Service / 同名 Ingress 的 yml 文件到当前目录 |
| `$index r` / `$index u` | 重启(rollout restart) / 回滚(rollout undo)所属资源对象 |
| `$index s3` | 设置所属 Deployment/StatefulSet 副本数为 3(需确认) |
| `$index del` / `delf` | 删除 Pod / 强制删除 Pod |
| `$index cle` / `destroy` | 删除所属资源对象 / 连同同名 Service、Ingress 一起删除(需确认) |
| `$index n` | ssh 登录 Pod 所在的 Node |
| `$index dbg` | 用临时调试容器进入没有 shell 的 Pod,详见[调试](debug?id=index-dbg-调试没有-shell-的-pod) |

## 其他资源的系列动作

上面默认都是输出目标 Namespace 的 Pods 列表,然后选择进一步动作,当然我们也可以直接选择目标资源对象列表, Deployment/StatefulSet/DaemonSet/Service/Ingress/ConfigMap/Secret/PV/PVC 等, 然后下一步动作和 Pod 动作类似,可以过滤/编辑(e)/describe(d)/输出 yml(o)/删除(cle)

- ki test d (输出 Deployment 列表)
- ki test f (输出 StatefulSet 列表)
- ki test a (输出 DaemonSet 列表)
- ki test s (输出 Service 列表)
- ki test i (输出 Ingress 列表)
- ki test c (输出 ConfigMap 列表)
- ki test t (输出 Secret 列表)
- ki test v (输出 PV 列表)
- ki test p (输出 PVC 列表)
- ki test e (输出 Event )
- ki test j (输出 CronJob 列表), ki test b (输出 Job 列表), ki test r (输出 ReplicaSet 列表), ki test q (输出 ResourceQuota)
- ki test g / h (输出 Gateway / HTTPRoute 列表), ki test V / D / E (输出 Istio VirtualService / DestinationRule / EnvoyFilter 列表)
- ki test A (输出 all 资源)

## 快捷选择

在选择列表中,除了 `$index` 和过滤字符串,还可以使用以下符号,后面同样可以跟随 l/e/r/del 等动作

- `[` 查看当前 k8s/ns 历史操作最多的资源的日志,列表中以红色 `[` 标记
- `]` 查看历史操作次多的资源的日志,列表中以蓝色 `]` 标记
- `~` `!` `@` `#` `$` 等其他符号,登录历史操作最多的资源
- `:` 选择列表中的最后一个,Pod 列表按创建时间排序,也就是最新的 Pod
- `*` 每 3 秒刷新列表,实时查看资源变化,`Ctrl+C` 返回选择

?> 历史按所属工作负载统计,Pod 重建后名字变化依然能选中同一个 Deployment/StatefulSet 的 Pod;当前 k8s/ns 还没有历史时选择最新的一个

![](//static.xabc.io/ki/ki-25.png)

## Node 资源的系列动作

想查看目标 k8s 的 Node 主机时,只需要多一个参数 n,如 `ki test n` 则输出 Node 机器列表,请注意中间参数 test 依然模糊匹配 Namespace,在这种情况就是代表了要输出的包含有 test 这个非空 Namespace 的 k8s 主机列表

### `$index` 回车默认是远程登录目标主机

一般我们建议把管控机器的 ssh-key 公钥数据打到 Node 机器,方便我们直接登录

![](//static.xabc.io/ki/ki-15.png)

### `$index e` 编辑 Node 资源对象

![](//static.xabc.io/ki/ki-16.png)

### `$index c` 设定目标 Node 资源对象不可调度,`$index u` 设定目标 Node 资源对象可调度

![](//static.xabc.io/ki/ki-17.png)

## 高级操作(非必要)

### Namespace 的特征短字符串

- `ki` 高亮紫色为 Feature Hashing 特征短字符串

![](//static.xabc.io/ki/hash.png)

### 一步到位,登录/查看日志/编辑

有些用户场景下,比如开发人员或者数据库管理人员日常只关注自己负责的某个或者某几个 Pod,`ki -i[leo] $ns $pod` 可以一步到位匹配到目标 Pod

- `ki -i d sql` -i 参数代表本次操作将一步到位登录匹配 Pod, d 参数匹配 Namespace, sql 参数匹配最相似 Pod
- `ki -l d sql` -l 参数代表本次操作将一步到位查看匹配 Pod 的实时日志, d 参数匹配 Namespace, sql 参数匹配最相似 Pod
- `ki -e d sql` -e 参数代表本次操作将一步到位编辑匹配 Pod 所属资源, d 参数匹配 Namespace, sql 参数匹配最相似 Pod, `-es` `-ei` 编辑同名 Service / Ingress
- `ki -o d sql` -o 参数代表本次操作将一步到位输出匹配 Pod 所属资源的 yml 文件, `-os` `-oi` 输出同名 Service / Ingress

![](//static.xabc.io/ki/ki-21.png)

### 跟随目录,自动切换

这是一种管理约定,请留意 ~/.kube/ 目录下3个 kubeconfig 文件名称的第2个字段和 /cache/sys/K8S/ 目录下对应的3个 k8s 目录名称的第一个字段的一致,保持这种命名约定,当在 `K8S` 这个目录下的时候,ki 就开始识别是否存在对应的多集群各自独立管理目录,进入自动跟随目录切换状态,这种跟随切换状态终端命令提示符为淡蓝色,如果有切换将出现一次淡红色 (switch) 提示,该模式下可以最大限度减少对集群操作的失误

![](//static.xabc.io/ki/ki-22.png)

临时锁定禁止跟随切换和解除锁定切换,比如有时候,我们期望把 A 集群目录下某个 yml 资源 apply 到 B 集群,所以我们可以通过 `ki --l` 临时禁止跟随目录自动切换,`ki --u` 解除锁定,需要提醒的是这种锁定只是针对跟随目录这种状态下,而不会禁止匹配 Namespace 自动切换,`ki -s` 主动选择切换,也被认为是临时锁定,锁定操作为1小时,1小时后自动解锁

![](//static.xabc.io/ki/ki-23.png)

## 资源对象操作的统计分析

$HOME/.history/ 目录下:

- `YYYY-MM-DD` 每天的操作记录,包含执行的命令、用户、来源 IP 和目标 k8s
- `.kube_dict` 历史切换集群的统计, `.last` 上一次切换操作的集群
- `.pod_dict` 每个 k8s/ns 资源对象的操作历史,用于 `[` `]` 等快捷选择
- `.line` 上一次 `l` 指定的日志行数

`ki --k` 输出每个 k8s/ns 最常操作的资源和集群切换统计

!> 注意 .ns_dict 是非空 Namespace 的缓存文件,可以加速 ki 的自动切换, ki 发现 Namespace 有变化时会在后台自动重建缓存(`KI_AUTO_CACHE=false` 关闭),也可以执行 `ki --c` 手动重建

![](//static.xabc.io/ki/ki-24.png)

## 资源排序与用量

- `ki -r test` 输出 Pod 列表并按重启次数排序,快速找到不稳定的 Pod
- `ki -t test` 输出 Pod 资源用量并按内存排序, `ki -t2 test` 按 CPU 排序,需要集群安装 metrics-server
- `ki -a` 输出整个集群的 Pod, `ki -a s` 输出整个集群的 Service,其他资源同理

## AI 分析

- `ki --ai` 收集节点、各 Namespace 的 Pod 状态、资源用量和最近事件,生成集群健康报告
- `ki --ai 问题` 运维、开发问题问答,生成的脚本或配置文件保存到 /tmp/ki/

?> 通过环境变量 `KI_AI_URL` `KI_AI_KEY` `KI_AI_MODEL` 配置兼容 OpenAI 接口的服务,依赖 Python requests 库

## 环境变量

| 变量 | 说明 |
|---|---|
| `KI_AUTO_SWITCH=false` | 当前 k8s 找不到匹配的 Namespace 时不自动切换到其他 k8s |
| `KI_AUTO_CACHE=false` | 不在后台自动重建 Namespace 缓存,手动 `ki --c` 依然可用 |
| `KI_LINE` | `$index l` 默认输出的日志行数 |
| `KI_DEBUG_IMAGE` | `$index dbg` 使用的调试镜像,默认 busybox |
| `KI_AI_URL` `KI_AI_KEY` `KI_AI_MODEL` | AI 服务的地址、密钥和模型 |

## 查看帮助

`ki --h` 查看全部用法,实际上只要了解 Pod 的登录和查看日志两个用法就可以满足日常90%的工作需求,其他操作慢慢自然了解

![](//static.xabc.io/ki/ki-18.png)
