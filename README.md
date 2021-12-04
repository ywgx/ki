# Kubectl Pro

[使用文档 ki.xabc.io](https://ki.xabc.io)

# 演示视频

B站指路 https://www.bilibili.com/video/BV1TF411h73g

# Kubectl Pro controls the Kubernetes cluster manager

1. ki List all namespaces
2. ki xx List all pods in the namespace ( if there are multiple ~/.kube/kubeconfig*,the best matching kubeconfig will be found ),the namespace parameter supports fuzzy matching,after outputting the pod list, select: xxx filters the query
         select: index l ( [ l ] Print the logs for a container in a pod or specified resource )
         select: index l 100 ( Print the logs of the latest 100 lines )
         select: index l xxx ( Print the logs and filters the specified characters )
         select: index r ( [ r ] Rollout restart the pod )
         select: index o ( [ o ] Output the [Deployment,StatefulSet,Service,Ingress,Configmap,Secret].yml file )
         select: index del ( [ del ] Delete the pod )
         select: index cle ( [ cle ] Delete the Deployment/StatefulSet )
         select: index e[si] ( [ e[si] ] Edit the Deploy/Service/Ingress )
         select: index c5 ( [ c5 ] Set the Deploy/StatefulSet replicas=5 )
3. ki xx d List the Deployment of a namespace
4. ki xx f List the StatefulSet of a namespace
5. ki xx s List the Service of a namespace
6. ki xx i List the Ingress of a namespace
7. ki xx t List the Secret of a namespace
8. ki xx a List the DaemonSet of a namespace
9. ki xx v List the PersistentVolume of a namespace
10. ki xx p List the PersistentVolumeClaim of a namespace
11. ki -s Select the kubernetes to be connected ( if there are multiple ~/.kube/kubeconfig*,the kubeconfig storage can be kubeconfig-hz,kubeconfig-sh,etc. )
12. ki -i $ns $pod Login in the container,this way can be one-stop
13. ki -l $ns $pod Print the logs for a container,this way can be one-stop
14. ki -e[si] $ns $pod Edit the Deploy/Service/Ingress for a container,this way can be one-stop
15. ki $k8s.$ns Select the kubernetes which namespace in the kubernetes ( if there are multiple ~/.kube/kubeconfig*,this way can be one-stop. )
