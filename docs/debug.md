## `$index dp` 输出目标 Pod 的 describe 信息

![](//static.xabc.io/ki/debug-1.png)

## `ki $ns e` 输出目标 Namespace 的 Event 信息

![](//static.xabc.io/ki/debug-2.png)

## `$index dbg` 调试没有 shell 的 Pod

distroless、scratch 等精简镜像里没有 sh,`$index` 登录会失败,这时 ki 会提示使用 `dbg`. `$index dbg` 通过 `kubectl debug` 给目标 Pod 注入一个临时调试容器(默认 busybox,可通过 `KI_DEBUG_IMAGE` 指定),与目标容器共享进程命名空间,可以用 ps、netstat、wget 等工具查看目标容器的进程和网络

```
select:5 dbg   kubectl --insecure-skip-tls-verify -n test-api debug -it noshell-6977f45df5-zk88q --image=busybox --target=noshell -- sh
/ # ps
PID   USER     TIME  COMMAND
    1 65535     0:00 /pause
   13 root      0:00 sh
```

!> 需要 k8s 1.23 及以上版本(临时容器默认开启);临时容器注入后会一直保留在 Pod 中,直到 Pod 被重建

## `$index v` 查看上一次崩溃退出的日志

容器反复重启(CrashLoopBackOff)时,当前日志往往看不到原因, `$index v` 输出上一次退出的容器日志(--previous),默认 4096 行, `$index v 100` 指定行数

## `ki -r $ns` 按重启次数排序

输出 Pod 列表并按重启次数排序,重启次数最多的排在最后,快速找到不稳定的 Pod
