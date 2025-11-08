## 2022-06-08

?> `v1.8` Smart sorting

## 2022-06-02

?> `v1.7` Optimize sorting

## 2022-05-31

?> `v1.6` Optimize sorting

## 2022-05-12

?> `v1.5` Fix bugs

## 2022-05-07

?> `v1.4` Updated but seems not updated~

## 2022-03-24

?> `v1.3` An interesting upgrade, more user-friendly in certain scenarios

## 2022-03-22

?> `v1.2` select: * Real-time view of resource changes in the Namespace, weighted kubeconfig switching

## 2021-12-14

- Extended support for managing CronJob

## 2021-12-13

?> `v1.1` Output resource objects of all Namespaces

- `ki -a` Default output of Pods in the entire cluster
- `ki -a s` Output Service in the entire cluster
- `ki -a i` Output Ingress in the entire cluster
- `ki -a c` Output ConfigMap in the entire cluster
- `ki -a t` Output Secret in the entire cluster
- `ki -a v` Output PersistentVolume in the entire cluster
- `ki -a p` Output PersistentVolumeClaim in the entire cluster
- `ki -a f` Output StatefulSet in the entire cluster
- `ki -a a` Output DaemonSet in the entire cluster

## 2021-12-12

- $index c xxx (Query 10 lines near keyword log)
- `ki -k` Output historical operation statistics

## 2021-12-11

?> `v1.0` Statistical analysis of resource object operation history

## 2021-12-10

?> `v0.9` Use Feature Hashing algorithm to add generation of characteristic short strings
- `ki` Extended output of Namespace [characteristic short string](https://ki.xabc.io/#/start?id=namespace-的特征短字符串)

## 2021-12-09

?> `v0.8` Enable file caching for non-empty Namespaces

- `ki -c` Detect non-empty Namespace list for each k8s cluster, stored on disk at ~/.history/.ns_dict, reducing `kubectl get ns` queries
- Extended management of ResourceQuota

## 2021-12-08

- Optimize similar matching algorithm
- Output switching time

## 2021-12-07

?> `v0.7` Optimize the logic of querying non-empty Namespaces to speed up

- Improved the query order of target Namespace, unified the query logic of single cluster and multi-cluster, reduced re-query (kubectl get pod); because k8s currently does not have a variable to directly determine whether the target ns is empty, the original query first matched ns by similarity, then continued to traverse through kubectl get pod to confirm that the ns is non-empty, found and jumped out of the loop, then returned to the main loop of operation. Now the query also first matches ns by similarity, then directly returns to the main loop of operation, kubectl get pod outputs the pods list, if the output is empty, continue to find the next k8s matched ns, continue the above loop, ensuring that finding the target non-empty Namespace only does one valid kubectl get pod

## 2021-12-05

- Simplify original command output
- Improve the accuracy of historical operation records
- Reduce calls to Pod type judgment

## 2021-12-04

?> `v0.6` Optimize Pod history query matching

- Improved accurate identification of target Pod type
- Extended processing of Node resources (edit/describe)
- Added one-step operation capability (login/view logs/edit)
