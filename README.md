# Kubectl Pro

![pro](https://filelist.cn/disk/public/ywgx/pro.gif)

ki.py 可以自动的在多个 kubeconfig 中切换,管理几十/几百个 kubernetes 集群就好比一个那样方便,而且免去输出长长的指令,无论是登录 Pod 还是查看 Pod 日志都非常便捷

自动管理策略是这样的,比如你~/.kube/下有多个配置文件,当你输入 `ki.py -n dev` 的时候,首先寻找当前 config,如果没有找到则自动寻找下一个集群,找到则config 软链接指向新集群配置,切换的时候会有显示提醒所在[ 集群/空间 ]
当然有的 Namespace 比较长,所以支持了相似度匹配比如 ki.py -n sys 就可以匹配到 kube-system
然后带索引输出目标 Namespace 的 Pods 列表,可以快速选择登陆/查看日志/编辑/重启/删除等日常管理操作
如果你正在使用 kubectx/kubens/kubecm/k9s 管理你多个集群的话,这个小工具体验或许更加方便,也更轻量
kubectx/kubens/kubecm/k9s 等设计理念总是需要人主动管理,这个小工具最大限度让程序帮人自动管理

考虑规模化的场景,比如几百个/几千个集群需要管理,如果一个 dev 存在多个 k8s 里,那么也可以快速过滤主动选择需要连接哪一个集群
`ki.py -s` 输出集群列表,输入过滤字符串,快速选择

根据操作历史记录分析日常操作的范围,比较智能的快速切换而不是循环全局,比如 dev 这个 Namespace 日常大部分都是在某个 k8s 下,那么即便其他 k8s 也有 dev,日常操作的 k8s 权重就会稍大一点,优先匹配

# Install 快速安装,即刻上手

`# curl -s xabc.io/ki|bash`
这条指令会快速把 ki.py 和 xabc_k8s.sh 分别放到所在机器的 /usr/local/bin/ 和 /etc/profile.d/ 下,然后即刻感受

# Kubectl Pro 管理使用说明

1. ki -s 主动选择需要连接的kubernetes(如果存在多个~/.kube/kubeconfig*,可以把 kubeconfig 存放命令为 kubeconfig-hz,kubeconfig-sh)
2. ki 列出当前 kubeconfig Namespace
3. ki xx 列出某 Namespace (如果存在多个 ~/.kube/kubeconfig*,将在其中找到最优匹配) 的 Pod,Namespace 参数支持模糊匹配,例如要查看 Namespace 为 dev 里的 pod,可以简写为 'ki d',输出 pod 列表后 grep: xxx 过滤查询

         grep: index l (可选参数 [ l ] 表示输出目标 Pod 的实时日志)
         grep: index l 100 (表示输出目标 Pod 最新100行的实时日志)
         grep: index l xxx (表示输出目标 Pod 实时日志并过滤指定字符串)
         grep: index r (可选参数 [ r ] 表示重启目标 Pod)
         grep: index o (可选参数 [ o ] 表示导出目标[Deployment,StatefulSet,Service,Ingress,Configmap,Secret] yml文件)
         grep: index del (可选参数 [ del ] 表示删除目标 Pod,根据 k8s 的默认编排策略会重新拉起,类似重启 Pod)
         grep: index cle (可选参数 [ cle ] 表示删除目标 Deployment/StatefulSet)
         grep: index e[si] (可选参数 [ e[si] ] 表示编辑目标 Deploy/Service/Ingress)

4. ki xx d 列出某 Namespace 的 Deployment
5. ki xx f 列出某 Namespace 的 StatefulSet
6. ki xx s 列出某 Namespace 的 Service
7. ki xx i 列出某 Namespace 的 Ingress

# Kubectl Pro controls the Kubernetes cluster manager

1. ki -s Select the kubernetes to be connected ( if there are multiple ~/.kube/kubeconfig*,the kubeconfig storage can be kubeconfig-hz,kubeconfig-sh,etc. )
2. ki List all namespaces
3. ki xx List all pods in the namespace ( if there are multiple ~/.kube/kubeconfig*,the best matching kubeconfig will be found ),the namespace parameter supports fuzzy matching,after outputting the pod list, grep: XXX filters the query

         grep: index l ( [ l ] Print the logs for a container in a pod or specified resource )
         grep: index l 100 ( Print the logs of the latest 100 lines )
         grep: index l xxx ( Print the logs and filters the specified characters )
         grep: index r ( [ r ] Rollout restart the pod )
         grep: index o ( [ o ] Output the [Deployment,StatefulSet,Service,Ingress,Configmap,Secret].yml file )
         grep: index del ( [ del ] Delete the pod )
         grep: index cle ( [ cle ] Delete the Deployment/StatefulSet )
         grep: index e[si] ( [ e[si] ] Edit the Deploy/Service/Ingress )

4. ki xx d List the Deployment of a Namespace
5. ki xx f List the StatefulSet of a Namespace
6. ki xx s List the Service of a Namespace
7. ki xx i List the Ingress of a Namespace
