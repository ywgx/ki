# Kubectl Pro

ki.py 可以自动的在多个 kubeconfig 中切换,管理几十/几百个 kubernetes 集群就好比一个那样方便,而且免去输出长长的指令,无论是登录 Pod 还是查看 Pod 日志都非常便捷

# 快速安装,即刻上手

`# curl -s xabc.io/ki|bash`
这条指令会快速把 ki.py 和 xabc_k8s.sh 分别放到所在机器的 /usr/local/bin/ 和 /etc/profile.d/ 下,然后即刻感受

# Kubectl Pro 管理使用说明

1. ks 选择需要连接的kubernetes(如果存在多个~/.kube/kubeconfig*,可以把 kubeconfig 存放命令为 kubeconfig-hz,kubeconfig-sh)
2. ki 列出所有 Namespace
3. ki xx 列出某 Namespace (如果存在多个 ~/.kube/kubeconfig*,将在其中找到最优匹配) 的 Pod,Namespace 参数支持模糊匹配,例如要查看 Namespace 为 dev 里的 pod,可以简写为 'ki d',输出 pod 列表后 grep: xxx 过滤查询
         grep: xxx l (可选参数 [ l ] 表示输出目标 Pod 的实时日志)
         grep: xxx l 100 (表示输出目标 Pod 最新100行的实时日志)
         grep: xxx l xxx (表示输出目标 Pod 实时日志并过滤指定字符串)
         grep: xxx r (可选参数 [ r ] 表示重启目标 Pod)
         grep: xxx o (可选参数 [ o ] 表示导出目标[Deployment,StatefulSet,Service,Ingress,Configmap,Secret] yml文件)
         grep: xxx del (可选参数 [ del ] 表示删除目标 Pod,根据 k8s 的默认编排策略会重新拉起,类似重启 Pod)
         grep: xxx cle (可选参数 [ cle ] 表示删除目标 Deployment/StatefulSet)
         grep: xxx e[si] (可选参数 [ e[si] ] 表示编辑目标 Deploy/Service/Ingress)
4. ki xx d 列出某 Namespace 的 Deployment
5. ki xx f 列出某 Namespace 的 StatefulSet
6. ki xx s 列出某 Namespace 的 Service
7. ki xx i 列出某 Namespace 的 Ingress
