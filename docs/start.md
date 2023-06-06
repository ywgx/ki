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

![](//s.xabc.io/static/ki-1.png)

## 相似匹配

最相似匹配,`ki sys` 匹配到 kube-system 这个 Namespace,实际上 `ki sy` 在这里也可以匹配到

![](//s.xabc.io/static/ki-2.png)

## 过滤搜索

全列表字符串过滤,可以不断缩小过滤范围,比如过滤搜索某个关键字 str 或者某个机器 14.8 的 Pod

![](//s.xabc.io/static/ki-3.png)

## 自动切换 $KUBECONFIG

请留意,起初在 edge 集群下,`$ ki test`的时候因为当前 k8s 找不到任何匹配的 Namespace,自动寻找下一个,第2次就找到了,在 test 这个集群里有一个 test 的非空 Namespace,并且切换了 $KUBECONFIG,实时终端提示当前 $KUBECONFIG 为 kubeconfig-test

![](//s.xabc.io/static/ki-8.png)

## 主动切换 $KUBECONFIG

有时候我们需要查看某个 Namespace,而这个 Namespace 在多个 k8s 集群中都存在,所以我们可以主动切换 $KUBECONFIG,有两种方式,一种是在参数中匹配自动切换一次到位 `ki $k8s.$ns`,另一种是先主动切换到目标 k8s `ki -s`

请留意起初`ki sys`查看的是 test 集群下的 kube-system,而`ki ho.sys`则会查看 hongkong 集群下的 kube-system, ki 可以分开解析 ho.sys, ho 可以相似度匹配到 kubeconfig-hongkong, sys 可以相似度匹配到 kube-system

![](//s.xabc.io/static/ki-19.png)

当我们有海量的 k8s 集群的情况下,我们使用`ki -s` 过滤搜索选择要切换的目标 k8s

![](//s.xabc.io/static/ki-20.png)

## **目标 Pod 的系列动作**

一般建议 Deployment(StatefulSet)/Service/Ingress 三类资源对象,命名最好一致,简洁明了,也有很多优点

### `$index` 回车直接登录 Pod

![](//s.xabc.io/static/ki-4.png)

### `$index l` 输出 Pod 实时日志

默认输出最新 200 行

![](//s.xabc.io/static/ki-5.png)

### `$index l 10000` 输出 Pod 实时日志

l 后加一个数字,代表要输出最新多少行日志

![](//s.xabc.io/static/ki-6.png)

### `$index l chunked` 输出 Pod 实时日志的过滤

l 后加一个字符串,代表要输出过滤字符串的日志行

![](//s.xabc.io/static/ki-7.png)

### `$index e` 自动识别资源对象,进入编辑模式

![](//s.xabc.io/static/ki-9.png)

### `$index es` 编辑目标 Pod 同名的 Service 资源

![](//s.xabc.io/static/ki-10.png)

### `$index ei` 编辑目标 Pod 同名的 Ingress 资源

![](//s.xabc.io/static/ki-11.png)

### `$index r` 重启目标 Pod

请留意这里重启的是目标 Pod 所属的资源对象

![](//s.xabc.io/static/ki-12.png)

### `$index del` 删除目标 Pod

这里删除的是目标 Pod,一般根据 k8s 的调度规则很快就新拉起一个

![](//s.xabc.io/static/ki-13.png)

### `$index cle` 清理目标 Pod 所属资源对象

!>请注意清理的是目标 Pod 所属的资源对象,所以清理就是彻底删除,清理(cle) 有意设计需要输入三个字符,期望你了解当前动作的意义,减少误操作

![](//s.xabc.io/static/ki-14.png)

## 其他资源的系列动作

上面默认都是输出目标 Namespace 的 Pods 列表,然后选择进一步动作,当然我们也可以直接选择目标资源对象列表, Deployment/StatefulSet/DaemonSet/Service/Ingress/ConfigMap/Secret/PV/PVC, 然后下一步动作和 Pod 动作类似,可以过滤/编辑/删除

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

## 上次的选择和最新的选择

- `#` 符号代表上一次的选择对象,和`$index`一样后面可以继续跟随 l/e/del/cle 等动作
- `$` 符号代表选择最新运行的 Pod 对象,和`$index`一样后面可以继续跟随 l/e/del/cle 等动作

![](//s.xabc.io/static/ki-25.png)

## Node 资源的系列动作

想查看目标 k8s 的 Node 主机时,只需要多一个参数 n,如 `ki test n` 则输出 Node 机器列表,请注意中间参数 test 依然模糊匹配 Namespace,在这种情况就是代表了要输出的包含有 test 这个非空 Namespace 的 k8s 主机列表

### `$index` 回车默认是远程登录目标主机

一般我们建议把管控机器的 ssh-key 公钥数据打到 Node 机器,方便我们直接登录

![](//s.xabc.io/static/ki-15.png)

### `$index e` 编辑 Node 资源对象

![](//s.xabc.io/static/ki-16.png)

### `$index c` 设定目标 Node 资源对象不可调度,`$index u` 设定目标 Node 资源对象可调度

![](//s.xabc.io/static/ki-17.png)

## 高级操作(非必要)

### Namespace 的特征短字符串

- `ki` 高亮红色为 Feature Hashing 特征短字符串

![](//s.xabc.io/static/hash.png)

### 一步到位,登录/查看日志/编辑

有些用户场景下,比如开发人员或者数据库管理人员日常只关注自己负责的某个或者某几个 Pod,`ki -i[le] $ns $pod` 可以一步到位匹配到目标 Pod

- `ki -i d sql` -i 参数代表本次操作将一步到位登录匹配 Pod, d 参数匹配 Namespace, sql 参数匹配最相似 Pod
- `ki -l d sql` -l 参数代表本次操作将一步到位查看匹配 Pod 的实时日志, d 参数匹配 Namespace, sql 参数匹配最相似 Pod
- `ki -e d sql` -l 参数代表本次操作将一步到位编辑匹配 Pod 所属资源, d 参数匹配 Namespace, sql 参数匹配最相似 Pod

![](//s.xabc.io/static/ki-21.png)

### 跟随目录,自动切换

这是一种管理约定,请留意 ~/.kube/ 目录下3个 kubeconfig 文件名称的第2个字段和 /cache/sys/K8S/ 目录下对应的3个 k8s 目录名称的第一个字段的一致,保持这种命名约定,当在 `K8S` 这个目录下的时候,ki 就开始识别是否存在对应的多集群各自独立管理目录,进入自动跟随目录切换状态,这种跟随切换状态终端命令提示符为淡蓝色,如果有切换将出现一次淡红色 (switch) 提示,该模式下可以最大限度减少对集群操作的失误

![](//s.xabc.io/static/ki-22.png)

临时锁定禁止跟随切换和解除锁定切换,比如有时候,我们期望把 A 集群目录下某个 yml 资源 apply 到 B 集群,所以我们可以通过 `ki -l` 临时禁止跟随目录自动切换,`ki -u` 解除锁定,需要提醒的是这种锁定只是针对跟随目录这种状态下,而不会禁止匹配 Namespace 自动切换,`ki -s` 主动选择切换,也被认为是临时锁定,锁定操作为1小时,1小时后自动解锁

![](//s.xabc.io/static/ki-23.png)

## 资源对象操作的统计分析

在 $HOME/.history/ 存放每天的操作记录, .dict 是历史切换集群的统计, .last 是上一次切换操作的集群, .name_dict 是每个 k8s/ns 操作资源对象的历史操作分析

- 符号 ~ 或 ! 匹配当前 k8s/ns 上一次操作资源对象
- 符号 @ 或 # 匹配当前 k8s/ns 历史操作最多的资源对象
- 符号 $ 匹配当前 k8s/ns 最新发布的资源对象

!> 注意 .ns_dict 是 `ki -c` 执行后生成的非空 Namespace 缓存文件,这个缓存文件可以加速 ki 的自动切换,如果集群 Namespace 有新创建或者原来是空的,而现在非空了的时候需要重新执行一下 `ki -c`

![](//s.xabc.io/static/ki-24.png)

## 查看帮助

实际上只要了解 Pod 的登录和查看日志两个用法就可以满足日常90%的工作需求,其他操作慢慢自然了解

![](//s.xabc.io/static/ki-18.png)
