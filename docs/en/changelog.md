## 2022-06-08

?> `v1.8` Intelligent ordering improvements

## 2022-06-02

?> `v1.7` Sorting refinements

## 2022-05-31

?> `v1.6` Faster sorting

## 2022-05-12

?> `v1.5` Bug fixes

## 2022-05-07

?> `v1.4` A tiny update that almost went unnoticed

## 2022-03-24

?> `v1.3` More human-friendly behaviors in certain flows

## 2022-03-22

?> `v1.2` `select: *` live namespace monitoring plus weighted kubeconfig switching

## 2021-12-14

- Added CronJob management

## 2021-12-13

?> `v1.1` Cluster-wide resource listings

- `ki -a` outputs Pods across the entire cluster
- `ki -a s` lists Services
- `ki -a i` lists Ingresses
- `ki -a c` lists ConfigMaps
- `ki -a t` lists Secrets
- `ki -a v` lists PersistentVolumes
- `ki -a p` lists PersistentVolumeClaims
- `ki -a f` lists StatefulSets
- `ki -a a` lists DaemonSets

## 2021-12-12

- `$index c xxx` — show log lines around the keyword
- `ki -k` — print historical operation statistics

## 2021-12-11

?> `v1.0` Historical analytics for resource operations

## 2021-12-10

?> `v0.9` Introduced feature-hash generation for namespace short strings
- `ki` highlights the namespace [feature hash](https://ki.xabc.io/#/en/start?id=namespace-feature-hash)

## 2021-12-09

?> `v0.8` Enabled non-empty namespace caching

- `ki -c` scans each cluster for non-empty namespaces and stores them under `~/.history/.ns_dict` to cut down on `kubectl get ns`
- Added ResourceQuota management

## 2021-12-08

- Improved fuzzy match results
- Added timestamps for context switching

## 2021-12-07

?> `v0.7` Faster non-empty namespace detection

- Unified the single-cluster and multi-cluster search flow, reducing repeated `kubectl get pod` calls.
- Ki now runs the main loop immediately after matching a namespace; if it returns empty, Ki automatically tries the next candidate.

## 2021-12-05

- Simplified raw command output
- Improved accuracy of operation history
- Reduced how often Pod-type detection runs

## 2021-12-04

?> `v0.6` Better Pod history lookup

- More accurate Pod-type identification
- Extended Node resource handling (edit/describe)
- Added one-step operations for login/log tail/edit
