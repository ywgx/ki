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

![](//static.xabc.io/ki/ki-4.png)

### `$index l` Output Real-time Pod Logs

Outputs the latest 200 lines by default.

![](//static.xabc.io/ki/ki-5.png)

### `$index l 10000` Output Pod Logs with Line Count

Add a number after "l" to specify how many recent lines to output.

![](//static.xabc.io/ki/ki-6.png)

### `$index l chunked` Filter Pod Logs

Add a string after "l" to filter log lines containing that string.

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

## Other Resource Actions

The default output shows the Pods list of the target Namespace, then you can choose further actions. You can also directly select target resource object lists: Deployment/StatefulSet/DaemonSet/Service/Ingress/ConfigMap/Secret/PV/PVC. The subsequent actions are similar to Pod actions: filter/edit/delete.

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

## Previous and Latest Selection

- `#` symbol represents the last selected object, can be followed by l/e/del/cle actions like `$index`
- `$` symbol represents the latest running Pod object, can be followed by l/e/del/cle actions like `$index`

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

- `ki` highlights feature hashing short strings in red

![](//static.xabc.io/ki/hash.png)

### One-step Login/Logs/Edit

For users who only focus on specific Pods (e.g., developers or DBAs), `ki -i[le] $ns $pod` can directly match the target Pod:

- `ki -i d sql` - "-i" means one-step login to matched Pod, "d" matches Namespace, "sql" matches most similar Pod
- `ki -l d sql` - "-l" means one-step view of matched Pod's real-time logs
- `ki -e d sql` - "-e" means one-step edit of matched Pod's owning resource

![](//static.xabc.io/ki/ki-21.png)

### Directory Following, Auto-switch

This is a management convention. Notice the naming consistency between the 3 kubeconfig files in ~/.kube/ (second field) and the 3 k8s directories in /cache/sys/K8S/ (first field). With this naming convention, when inside the `K8S` directory, ki recognizes whether corresponding multi-cluster independent management directories exist and enters directory-following auto-switch mode. The terminal prompt turns light blue in this mode, with a light red "(switch)" prompt when switching occurs. This mode minimizes cluster operation mistakes.

![](//static.xabc.io/ki/ki-22.png)

To temporarily lock (disable) or unlock directory following: sometimes you may want to apply a yml resource from cluster A to cluster B. Use `ki -l` to temporarily disable directory following and `ki -u` to unlock. Note that this lock only affects directory-following mode, not Namespace matching auto-switch. `ki -s` manual switch is also considered a temporary lock. Lock duration is 1 hour, auto-unlocks after that.

![](//static.xabc.io/ki/ki-23.png)

## Resource Object Operation Statistics

Operation records are stored daily in $HOME/.history/. .dict contains historical cluster switch statistics, .last is the last switched cluster, .name_dict is the historical operation analysis per k8s/ns.

- Symbol ~ or ! matches the last operated resource object in current k8s/ns
- Symbol @ or # matches the most frequently operated resource object in current k8s/ns
- Symbol $ matches the latest deployed resource object in current k8s/ns

!> Note: .ns_dict is the non-empty Namespace cache file generated by `ki -c`. This cache speeds up ki's auto-switching. When new Namespaces are created or previously empty ones become non-empty, re-run `ki -c`.

![](//static.xabc.io/ki/ki-24.png)

## View Help

In practice, understanding Pod login and log viewing covers 90% of daily work. Other operations can be learned gradually.

![](//static.xabc.io/ki/ki-18.png)
