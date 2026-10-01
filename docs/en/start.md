## Getting Started

We recommend installing `ki` globally on your Linux host where you manage k8s daily:

```bash
curl xabc.io/ki | bash
```

This command will download and install two files: `/usr/local/bin/ki` and `/etc/profile.d/zki.sh`. You can also manually download from [github.com/ywgx/ki](https://github.com/ywgx/ki) and place it in your preferred executable path.

!> Note: The default interpreter path for `ki` is `/usr/bin/python3`. Please check your host's python3 path and modify the first line `#!/usr/bin/python3` in `/usr/local/bin/ki` if needed.

## List Namespaces of Current k8s

Here we have 3 k8s clusters, with the current config symlinked to `/root/.kube/kubeconfig-edge`

![](//static.xabc.io/ki/ki-1.png)

## Fuzzy Matching

Fuzzy matching finds the closest match. `ki sys` matches the kube-system namespace. In this case, `ki sy` would also work.

![](//static.xabc.io/ki/ki-2.png)

## Filter Search

Full list string filtering allows you to narrow down search results. For example, filter by keyword "str" or by machine IP "14.8" to find specific Pods.

![](//static.xabc.io/ki/ki-3.png)

## Auto-switch $KUBECONFIG

Notice that initially we're in the edge cluster. When running `$ ki test`, since no matching Namespace is found in the current k8s, it automatically searches the next one. On the second attempt, it finds a non-empty "test" Namespace in the test cluster and switches $KUBECONFIG accordingly. The terminal prompt updates to show kubeconfig-test.

![](//static.xabc.io/ki/ki-8.png)

## Manual $KUBECONFIG Switch

Sometimes we need to view a Namespace that exists in multiple k8s clusters. We can manually switch $KUBECONFIG in two ways: match and auto-switch in one step with `ki $k8s.$ns`, or first switch to the target k8s using `ki -s`.

Notice that `ki sys` initially shows kube-system from the test cluster, while `ki ho.sys` shows kube-system from the hongkong cluster. Ki parses "ho.sys" separately: "ho" fuzzy matches kubeconfig-hongkong, and "sys" fuzzy matches kube-system.

![](//static.xabc.io/ki/ki-19.png)

When managing many k8s clusters, use `ki -s` to filter and select the target k8s to switch to:

![](//static.xabc.io/ki/ki-20.png)

## **Pod Actions**

We recommend naming Deployment(StatefulSet)/Service/Ingress resources consistently for simplicity and better management.

### `$index` Enter to Login to Pod

bash is preferred, sh is used when the image has no bash. If the image has no shell at all (distroless, etc.), ki suggests [`$index dbg`](en/debug?id=index-dbg-debug-pods-without-a-shell) instead.

![](//static.xabc.io/ki/ki-4.png)

### `$index l` Output Real-time Pod Logs

Outputs the latest 200 lines by default. A line count given after `l` is remembered, so the next plain `l` uses it.

![](//static.xabc.io/ki/ki-5.png)

### `$index l 10000` Output Pod Logs with Line Count

Add a number after "l" to specify how many recent lines to output.

![](//static.xabc.io/ki/ki-6.png)

### `$index l chunked` Filter Pod Logs

Add a string after "l" to filter the latest 1024 log lines by that string. `$index g chunked` filters the full log, `$index c chunked` also prints 10 lines of context around each match.

![](//static.xabc.io/ki/ki-7.png)

### `$index e` Auto-detect Resource Type and Enter Edit Mode

![](//static.xabc.io/ki/ki-9.png)

### `$index es` Edit Service with Same Name as Target Pod

![](//static.xabc.io/ki/ki-10.png)

### `$index ei` Edit Ingress with Same Name as Target Pod

![](//static.xabc.io/ki/ki-11.png)

### `$index r` Restart Target Pod

Note: This restarts the resource object that owns the target Pod.

![](//static.xabc.io/ki/ki-12.png)

### `$index del` Delete Target Pod

This deletes the target Pod. According to k8s scheduling rules, a new one will be created quickly.

![](//static.xabc.io/ki/ki-13.png)

### `$index cle` Clean Up Resource Object Owning Target Pod

!> Note: This cleans up (completely deletes) the resource object that owns the target Pod. The "cle" command intentionally requires 3 characters to ensure you understand the action and reduce accidental operations.

![](//static.xabc.io/ki/ki-14.png)

### Pod Actions Quick Reference

| Action | Description |
|---|---|
| `$index` | Login to the Pod, bash preferred, then sh |
| `$index l` / `$index l 500` / `$index 500` | Real-time logs, the line count is remembered |
| `$index l xxx` / `g xxx` / `c xxx` | Filter logs: latest 1024 lines / full log / full log with 10 lines of context |
| `$index v` / `$index v 100` | Logs of the previous crashed container (--previous) |
| `$index e` / `es` / `ei` | Edit the owning resource / same-name Service / same-name Ingress, likewise `eg` `eh` `eV` `eD` `eE` |
| `$index d` / `dp` / `ds` | Describe the owning resource / the Pod / same-name Service |
| `$index o` / `os` / `oi` | Save the owning resource / same-name Service / same-name Ingress as a yml file in the current directory |
| `$index r` / `$index u` | Rollout restart / rollout undo the owning resource |
| `$index s3` | Scale the owning Deployment/StatefulSet to 3 replicas (confirm) |
| `$index del` / `delf` | Delete the Pod / force delete the Pod |
| `$index cle` / `destroy` | Delete the owning resource / also delete the same-name Service and Ingress (confirm) |
| `$index n` | ssh to the Node running the Pod |
| `$index dbg` | Enter a Pod without a shell via an ephemeral debug container, see [Debug](en/debug?id=index-dbg-debug-pods-without-a-shell) |

## Other Resource Actions

The default output shows the Pods list of the target Namespace, then you can choose further actions. You can also directly select target resource object lists: Deployment/StatefulSet/DaemonSet/Service/Ingress/ConfigMap/Secret/PV/PVC, etc. The subsequent actions are similar to Pod actions: filter/edit (e)/describe (d)/save yml (o)/delete (cle).

- ki test d (list Deployments)
- ki test f (list StatefulSets)
- ki test a (list DaemonSets)
- ki test s (list Services)
- ki test i (list Ingresses)
- ki test c (list ConfigMaps)
- ki test t (list Secrets)
- ki test v (list PVs)
- ki test p (list PVCs)
- ki test e (show Events)
- ki test j (list CronJobs), ki test b (list Jobs), ki test r (list ReplicaSets), ki test q (show ResourceQuota)
- ki test g / h (list Gateways / HTTPRoutes), ki test V / D / E (list Istio VirtualServices / DestinationRules / EnvoyFilters)
- ki test A (list all resources)

## Quick Selection

Besides `$index` and filter strings, the following symbols can be used in the selection list, and can also be followed by l/e/r/del actions

- `[` shows logs of the most frequently operated resource in the current k8s/ns, marked with a red `[` in the list
- `]` shows logs of the 2nd most frequently operated resource, marked with a blue `]` in the list
- `~` `!` `@` `#` `$` and other symbols login to the most frequently operated resource
- `:` selects the last one in the list, Pods are sorted by creation time so it is the newest Pod
- `*` refreshes the list every 3 seconds to watch resource changes, `Ctrl+C` returns to selection

?> History is counted by owning workload, so the same Deployment/StatefulSet is still selected after its Pods are recreated with new names; when the current k8s/ns has no history yet, the newest one is selected

![](//static.xabc.io/ki/ki-25.png)

## Node Actions

To view target k8s Nodes, add parameter "n", e.g., `ki test n` outputs the Node list. Note that the middle parameter "test" still fuzzy matches Namespace. In this context, it means outputting the Node list of the k8s cluster that contains a non-empty "test" Namespace.

### `$index` Enter to SSH Login to Target Host

We recommend deploying your control machine's SSH public key to Node machines for direct login.

![](//static.xabc.io/ki/ki-15.png)

### `$index e` Edit Node Resource Object

![](//static.xabc.io/ki/ki-16.png)

### `$index c` Cordon Node (Mark Unschedulable), `$index u` Uncordon Node (Mark Schedulable)

![](//static.xabc.io/ki/ki-17.png)

## Advanced Operations (Optional)

### Namespace Feature Hash String

- `ki` highlights feature hashing short strings in purple

![](//static.xabc.io/ki/hash.png)

### One-step Login/Logs/Edit

For users who only focus on specific Pods (e.g., developers or DBAs), `ki -i[leo] $ns $pod` can directly match the target Pod:

- `ki -i d sql` - "-i" means one-step login to matched Pod, "d" matches Namespace, "sql" matches most similar Pod
- `ki -l d sql` - "-l" means one-step view of matched Pod's real-time logs
- `ki -e d sql` - "-e" means one-step edit of matched Pod's owning resource, `-es` `-ei` edit the same-name Service / Ingress
- `ki -o d sql` - "-o" means one-step save of matched Pod's owning resource as a yml file, `-os` `-oi` save the same-name Service / Ingress

![](//static.xabc.io/ki/ki-21.png)

### Directory Following, Auto-switch

This is a management convention. Notice the naming consistency between the 3 kubeconfig files in ~/.kube/ (second field) and the 3 k8s directories in /cache/sys/K8S/ (first field). With this naming convention, when inside the `K8S` directory, ki recognizes whether corresponding multi-cluster independent management directories exist and enters directory-following auto-switch mode. The terminal prompt turns light blue in this mode, with a light red "(switch)" prompt when switching occurs. This mode minimizes cluster operation mistakes.

![](//static.xabc.io/ki/ki-22.png)

To temporarily lock (disable) or unlock directory following: sometimes you may want to apply a yml resource from cluster A to cluster B. Use `ki --l` to temporarily disable directory following and `ki --u` to unlock. Note that this lock only affects directory-following mode, not Namespace matching auto-switch. `ki -s` manual switch is also considered a temporary lock. Lock duration is 1 hour, auto-unlocks after that.

![](//static.xabc.io/ki/ki-23.png)

## Resource Object Operation Statistics

In the $HOME/.history/ directory:

- `YYYY-MM-DD` daily operation records, including the command, user, source IP and target k8s
- `.kube_dict` cluster switch statistics, `.last` the last switched cluster
- `.pod_dict` resource operation history per k8s/ns, used by quick selection such as `[` `]`
- `.line` the log line count last given to `l`

`ki --k` outputs the most frequently operated resources per k8s/ns and the cluster switch statistics

!> Note: .ns_dict is the non-empty Namespace cache file, which speeds up ki's auto-switching. ki rebuilds it automatically in the background when Namespaces change (disable with `KI_AUTO_CACHE=false`), and `ki --c` rebuilds it manually.

![](//static.xabc.io/ki/ki-24.png)

## Sorting and Resource Usage

- `ki -r test` lists Pods sorted by restart count to quickly find unstable Pods
- `ki -t test` shows Pod resource usage sorted by memory, `ki -t2 test` sorts by CPU, requires metrics-server in the cluster
- `ki -a` lists Pods of the whole cluster, `ki -a s` lists Services of the whole cluster, and so on

## AI Analysis

- `ki --ai` collects nodes, Pod status per Namespace, resource usage and recent events, and generates a cluster health report
- `ki --ai question` answers DevOps and development questions, generated scripts or config files are saved to /tmp/ki/

?> Configure an OpenAI-compatible service with the `KI_AI_URL` `KI_AI_KEY` `KI_AI_MODEL` environment variables, requires the Python requests library

## Environment Variables

| Variable | Description |
|---|---|
| `KI_AUTO_SWITCH=false` | Do not switch to another k8s when no Namespace matches in the current one |
| `KI_AUTO_CACHE=false` | Do not rebuild the Namespace cache in the background, manual `ki --c` still works |
| `KI_LINE` | Default log line count of `$index l` |
| `KI_DEBUG_IMAGE` | Debug image used by `$index dbg`, busybox by default |
| `KI_AI_URL` `KI_AI_KEY` `KI_AI_MODEL` | Address, key and model of the AI service |

## View Help

`ki --h` shows all usages. In practice, understanding Pod login and log viewing covers 90% of daily work. Other operations can be learned gradually.

![](//static.xabc.io/ki/ki-18.png)
