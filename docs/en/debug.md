## `$index dp` Output Target Pod's Describe Information

![](//static.xabc.io/ki/debug-1.png)

## `ki $ns e` Output Target Namespace's Event Information

![](//static.xabc.io/ki/debug-2.png)

## `$index dbg` Debug Pods Without a Shell

Minimal images such as distroless or scratch have no sh, so `$index` login fails and ki suggests `dbg`. `$index dbg` uses `kubectl debug` to inject an ephemeral debug container into the target Pod (busybox by default, set `KI_DEBUG_IMAGE` to change it). It shares the process namespace with the target container, so tools like ps, netstat and wget can inspect the target container's processes and network.

```
select:5 dbg   kubectl --insecure-skip-tls-verify -n test-api debug -it noshell-6977f45df5-zk88q --image=busybox --target=noshell -- sh
/ # ps
PID   USER     TIME  COMMAND
    1 65535     0:00 /pause
   13 root      0:00 sh
```

!> Requires k8s 1.23 or later (ephemeral containers enabled by default); the ephemeral container stays in the Pod until the Pod is recreated

## `$index v` Logs of the Previous Crash

When a container keeps restarting (CrashLoopBackOff), the current logs often don't show the cause. `$index v` outputs the logs of the previously exited container (--previous), 4096 lines by default, `$index v 100` sets the line count.

## `ki -r $ns` Sort by Restart Count

Lists Pods sorted by restart count, the most restarted ones at the bottom, to quickly find unstable Pods.
