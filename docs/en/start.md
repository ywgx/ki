## Get Started Fast

Install `ki` globally on the Linux host where you normally manage Kubernetes:

```bash
curl xabc.io/ki | bash
```

The script installs two files: `/usr/local/bin/ki` and `/etc/profile.d/zki.sh`. You can also grab the sources from [github.com/ywgx/ki](https://github.com/ywgx/ki) and place them anywhere on your `$PATH`.

!> The default shebang in `/usr/local/bin/ki` points to `/usr/bin/python3`. Confirm your Python 3 path and adjust the first line if it differs.

## List Namespaces In Your Current Cluster

Below we have three clusters and the `config` symlink is pointing at `/root/.kube/kubeconfig-edge`.

![](//static.xabc.io/ki/ki-1.png)

## Fuzzy Matching

Typing `ki sys` lands on the `kube-system` namespace. Even `ki sy` works thanks to similarity scoring.

![](//static.xabc.io/ki/ki-2.png)

## Filter-As-You-Type Search

You can narrow the list again and again. Filter by keywords such as a string fragment `str` or even a node name like `14.8` to pinpoint Pods.

![](//static.xabc.io/ki/ki-3.png)

## Automatic `$KUBECONFIG` Switching

Watch how the first `ki test` runs inside the `edge` cluster. Because there is no matching namespace there, Ki keeps looking until it finds a non-empty namespace in another cluster, then updates `$KUBECONFIG` and the prompt (now `kubeconfig-test`).

![](//static.xabc.io/ki/ki-8.png)

## Manual `$KUBECONFIG` Switching

Sometimes the same namespace exists in multiple clusters. You can jump directly with `ki $cluster.$namespace`, or select a cluster interactively with `ki -s`.

Notice how `ki sys` inspects `kube-system` in the `test` cluster, while `ki ho.sys` inspects `kube-system` inside the `hongkong` cluster. Ki parses `ho.sys`, resolves `ho` to `kubeconfig-hongkong`, and `sys` to `kube-system`.

![](//static.xabc.io/ki/ki-19.png)

With many clusters, run `ki -s` to bring up a searchable list and pick the target context.

![](//static.xabc.io/ki/ki-20.png)

## Pod Actions At Your Fingertips

We recommend keeping Deployment/StatefulSet/Service/Ingress names aligned so you always know what you're touching.

### `$index` → Enter The Pod

![](//static.xabc.io/ki/ki-4.png)

### `$index l` → Tail Pod Logs

Outputs the latest 200 lines by default.

![](//static.xabc.io/ki/ki-5.png)

### `$index l 10000` → Tail A Specific Number Of Lines

Add a number after `l` to control how many lines to stream.

![](//static.xabc.io/ki/ki-6.png)

### `$index l chunked` → Tail Logs With A Filter

Add a string after `l` to only display lines containing that token.

![](//static.xabc.io/ki/ki-7.png)

### `$index e` → Edit The Target Resource

![](//static.xabc.io/ki/ki-9.png)

### `$index es` → Edit The Service With The Same Name

![](//static.xabc.io/ki/ki-10.png)

### `$index ei` → Edit The Matching Ingress

![](//static.xabc.io/ki/ki-11.png)

### `$index r` → Restart The Pod

Ki restarts the workload that owns the selected Pod.

![](//static.xabc.io/ki/ki-12.png)

### `$index del` → Delete The Pod

Deletes the Pod, and Kubernetes schedules a new one according to its controller.

![](//static.xabc.io/ki/ki-13.png)

### `$index cle` → Clean Up Everything

!> This removes the workload that owns the Pod. We intentionally require the three-letter `cle` to make you stop and confirm the action.

![](//static.xabc.io/ki/ki-14.png)

## Other Resource Shortcuts

Pods are the default view, but you can start from any resource type and chain the same actions (filter/edit/delete):

- `ki test d` – Deployments
- `ki test f` – StatefulSets
- `ki test a` – DaemonSets
- `ki test s` – Services
- `ki test i` – Ingresses
- `ki test c` – ConfigMaps
- `ki test t` – Secrets
- `ki test v` – PersistentVolumes
- `ki test p` – PersistentVolumeClaims
- `ki test e` – Events

## Previous vs Latest Selection

- `#` references the previous selection. Chain it with `l/e/del/cle` just like `$index`.
- `$` references the most recently run Pod. Chain it with the same actions.

![](//static.xabc.io/ki/ki-25.png)

## Node Actions

Add an `n` to inspect Node resources, e.g. `ki test n`. The middle argument still does a fuzzy namespace match—Ki lists Nodes from clusters that contain a non-empty namespace with that keyword.

### `$index` → SSH Into The Node

We recommend sharing the controller host's SSH key so you can log in immediately.

![](//static.xabc.io/ki/ki-15.png)

### `$index e` → Edit The Node Resource

![](//static.xabc.io/ki/ki-16.png)

### `$index c` / `$index u` → Cordon Or Uncordon

![](//static.xabc.io/ki/ki-17.png)

## Advanced (Optional)

### Namespace Feature Hash

- Ki highlights a red feature-hash string for each namespace.

![](//static.xabc.io/ki/hash.png)

### One-Step Login / Logs / Edit

For workflows that focus on a single Pod (such as DBAs or service owners), use the one-step flags:

- `ki -i d sql` – `-i` logs in, `d` fuzzy matches the namespace, `sql` fuzzy matches the Pod.
- `ki -l d sql` – `-l` tails logs directly.
- `ki -e d sql` – `-e` opens the owning resource in an editor.

![](//static.xabc.io/ki/ki-21.png)

### Follow The Directory And Auto-Switch

Keep the second segment in your kubeconfig filenames aligned with the first segment of your `/cache/sys/K8S/` directories. When you enter that directory Ki detects the layout, switches into follow mode, turns the prompt light blue, and flashes a red `(switch)` message whenever it changes contexts. Use `ki -l` to lock the directory-follow behavior temporarily, `ki -u` to unlock, or `ki -s` for an explicit switch. Locks time out after one hour.

![](//static.xabc.io/ki/ki-22.png)

## Operation History And Analytics

Daily histories live under `$HOME/.history/`:

- `.dict` – cluster switch statistics.
- `.last` – the last cluster you switched to.
- `.name_dict` – per namespace resource operation analytics.

Shortcuts:

- `~` / `!` – reuse the last resource inside the current cluster/namespace.
- `@` / `#` – select the most frequently touched resource in the current cluster/namespace.
- `$` – picks the most recently deployed resource for the current cluster/namespace.

!> `ki -c` regenerates the `.ns_dict` cache of non-empty namespaces. Run it whenever new namespaces appear.

![](//static.xabc.io/ki/ki-24.png)

## Need Help?

Learn the Pod login and log-tail workflows first—they cover 90% of daily work. Everything else will come naturally.

![](//static.xabc.io/ki/ki-18.png)
