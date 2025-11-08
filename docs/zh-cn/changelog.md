## 2022-06-08

?> `v1.8` 智慧排序

## 2022-06-02

?> `v1.7` 优化排序

## 2022-05-31

?> `v1.6` 优化排序

## 2022-05-12

?> `v1.5` 修复bug

## 2022-05-07

?> `v1.4` 更新了又好像没有更新～

## 2022-03-24

?> `v1.3` 有趣的一次升级,某些场景下,更加人性化了

## 2022-03-22

?> `v1.2` select: * 实时查看所在 Namespace 资源的变化,切换 kubeconfig 加权

## 2021-12-14

- 扩展支持管理 CronJob

## 2021-12-13

?> `v1.1` 输出所有 Namespace 的资源对象

- `ki -a` 默认输出整个集群的 Pod
- `ki -a s` 输出整个集群的 Service
- `ki -a i` 输出整个集群的 Ingress
- `ki -a c` 输出整个集群的 ConfigMap
- `ki -a t` 输出整个集群的 Secret
- `ki -a v` 输出整个集群的 PersistentVolume
- `ki -a p` 输出整个集群的 PersistentVolumeClaim
- `ki -a f` 输出整个集群的 StatefulSet
- `ki -a a` 输出整个集群的 DaemonSet

## 2021-12-12

- $index c xxx (查询关键字日志附近10行)
- `ki -k` 输出历史操作统计

## 2021-12-11

?> `v1.0` 统计分析资源对象操作历史

## 2021-12-10

?> `v0.9` 使用 Feature Hashing 算法增加特征短字符串的生成
- `ki` 扩展输出 Namespace 的 [特征短字符串](https://ki.xabc.io/#/start?id=namespace-的特征短字符串)

## 2021-12-09

?> `v0.8` 启用非空 Namespace 的文件缓存

- `ki -c` 检测每个 k8s 集群的非空 Namespace 列表, 落盘存储 ~/.history/.ns_dict, 减少 `kubectl get ns` 的查询
- 扩展管理 ResourceQuota

## 2021-12-08

- 优化相似匹配算法
- 输出切换时间

## 2021-12-07

?> `v0.7` 优化查询非空 Namespace 的逻辑,加快速度

- 改进目标 Namespace 的查询顺序，统一单集群和多集群的查询逻辑，减少重查询（kubectl get pod);因为k8s 目前没有直接判断目标ns是否为空的变量,原先查询是先相似匹配ns,然后继续通过 kubectl get pod 遍历确认该ns非空，找到即跳出循环，然后回到操作的主循环里,现在查询也是先相似匹配ns,然后直接回到操作的主循环，kubectl get pod 输出pods 列表，如果输出为空再继续寻找下一个k8s匹配的ns ,继续上述循环,确保了寻找目标非空 Namespace 只做一次有效 kubectl get pod

## 2021-12-05

- 简化原始指令输出
- 改进历史操作记录的准确度
- 减少对 Pod 类型判断的调用

## 2021-12-04

?> `v0.6` 优化Pod历史查询匹配

- 改进对目标 Pod 类型的精确识别
- 扩展了对 Node 资源的处理( edit/describe )
- 增加了一步到位的操作能力( 登录/查看日志/编辑 )
