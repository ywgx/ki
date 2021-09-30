#!/usr/bin/python3
#*************************************************
# Description : Kubectl Pro
# Version     : 0.1
#*************************************************
import os,re,sys,json,subprocess
#-----------------FUN-----------------------------
def cmp_file(f1, f2):
    st1 = os.stat(f1)
    st2 = os.stat(f2)
    if st1.st_size != st2.st_size:
        return False
    bufsize = 8*1024
    with open(f1, 'rb') as fp1, open(f2, 'rb') as fp2:
        while True:
            b1 = fp1.read(bufsize)
            b2 = fp2.read(bufsize)
            if b1 != b2:
                return False
            if not b1:
                return True
def cmd_obj(ns,obj,res,args,iip="x"):
    if obj in ("node","no"):
        if args[0] == 'c':
            action = "cordon"
            cmd = "kubectl "+action+" "+res
        elif args[0] == 'u':
            action = "uncordon"
            cmd = "kubectl "+action+" "+res
        else:
            action = "ssh"
            cmd = action +" root@"+iip
    elif obj in ("event"):
        action = "get"
        cmd = "kubectl -n "+ns+" "+action+" "+obj+" --sort-by=.metadata.creationTimestamp"
    elif obj in ("deployment","deploy","service","svc","ingress","ing","configmap","cm","secret","persistentvolumes","pv","persistentvolumeclaims","pvc","statefulsets","sts"):
        action2 = ""
        if args[0] == 'e':
            action = "edit"
        elif args[0] == 'd':
            action = "describe"
        elif args[0] == 'o':
            action = "get"
            action2 = " -o yaml > "+res+"."+obj+".yml"
        elif args == 'cle':
            action = "delete"
        else:
            action = "get"
        cmd = "kubectl -n "+ns+" "+action+" "+obj+" "+res+action2
    else:
        obj = "pod"
        l = res.split('-')
        end = l[-1]
        if end.isdigit():
            del l[-1:]
            obj = "sts"
        else:
            del l[-2:]
        name = ('-').join(l)
        if args == "del":
            cmd = "kubectl -n "+ns+" delete pod "+res+" &"
        elif args == "cle":
            obj = "sts" if end.isdigit() else "deploy"
            res2 = name
            action = "delete"
            cmd = "kubectl -n "+ns+" "+action+" "+obj+" "+res2
        elif args[0] == "r":
            obj = "sts" if end.isdigit() else "deploy"
            cmd = "kubectl -n "+ns+" rollout restart "+obj+" "+name
        elif args[0] in ('o'):
            obj = "sts" if end.isdigit() else "deploy"
            res2 = name
            action = "get"
            if len(args) > 1:
                if str(args)[1] == "d":
                    obj = "deploy"
                elif str(args)[1] == "s":
                    obj = "service"
                elif str(args)[1] == "i":
                    obj = "ingress"
                elif str(args)[1] == "f":
                    obj = "sts"
                else:
                    obj = "deploy"
            cmd = "kubectl -n "+ns+" "+action+" "+obj+" "+res2+" -o yaml > "+res2+"."+obj+".yml"
        elif args[0] in ('d','e'):
            obj = "sts" if end.isdigit() else "deploy"
            res2 = name
            action = "describe" if args[0] == 'd' else "edit"
            if len(args) > 1:
                if str(args)[1] == "d":
                    obj = "deploy"
                elif str(args)[1] == "s":
                    obj = "service"
                elif str(args)[1] == "i":
                    obj = "ingress"
                elif str(args)[1] == "f":
                    obj = "sts"
                elif str(args)[1] == "p":
                    obj = "pod"
                    res2 = res
            cmd = "kubectl -n "+ns+" "+action+" "+obj+" "+res2
        elif args[0] == 'l':
            regular = args.split('l')[-1]
            p = subprocess.Popen("kubectl -n "+ns+" get pod "+res+" -o jsonpath='{.spec.containers[:].name}'",shell=True,stdout=subprocess.PIPE,universal_newlines=True)
            result_list = p.stdout.readlines()[0].split()
            container = name if name in result_list else "--all-containers"
            if regular.isdigit():
                cmd = "kubectl -n "+ns+" logs -f "+res+" "+container+" --tail "+regular
            else:
                cmd = "kubectl -n "+ns+" logs -f "+res+" "+container+"|grep --color=auto "+regular if regular else "kubectl -n "+ns+" logs -f "+res+" "+container+" --tail 200"
        else:
            cmd = "kubectl -n "+ns+" exec -it  "+res+"  -- sh"
    return cmd
def find_optimal(namespace_list: list, namespace: str):
    indexes = [row.index(namespace) * 0.8 if namespace in row else 10000 for row in namespace_list]
    contains = [len(row.replace(namespace, '')) * 0.42 for row in namespace_list]
    words = [namespace == row for row in namespace_list]
    result_list = [(indexes[i] + container) * (1.62 if not words[i] else 1) for i, container in enumerate(contains)]
    return namespace_list[result_list.index(min(result_list))] if len(set(indexes)) != 1 else None
def find_config():
    cmd = '''find $HOME/.kube -maxdepth 2 -type f -name 'kubeconfig*'|egrep '.*' || grep "current-context" `find $HOME/.kube -maxdepth 2 -type f` -l'''
    k8s_list = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    result_set = { e.split('\n')[0] for e in k8s_list.stdout.readlines() }
    result_num = len(result_set)

    dc = {}
    dic = os.environ.get("HOME")+"/.kube/.dict"
    if os.path.exists(dic):
        with open(dic,'r') as f:
            dc = json.loads(f.read())

    result_dict = sorted(dc.items(),key = lambda dc:(dc[1], dc[0]),reverse=True)
    sort_list = [ i[0] for i in result_dict ]
    result_lines = sort_list + list(result_set - set(sort_list))

    dst = os.environ.get("HOME")+"/.kube/config"
    kubeconfig = None
    if result_lines:
        if os.path.exists(dst):
            for n,e in enumerate(result_lines):
                if cmp_file(e,dst):
                    kubeconfig = e.strip().split("/")[-1]
        else:
            with open(dst,'w') as f:
                fi = open(result_lines[0])
                f.write(fi.read())
                fi.close()
            kubeconfig = result_lines[0].split("/")[-1]
    else:
        if os.path.exists(dst):
            with open(os.environ.get("HOME")+"/.kube/kubeconfig",'w') as f:
                fi = open(dst)
                f.write(fi.read())
                fi.close()
            kubeconfig = "kubeconfig"
        else:
            kubeconfig = None
    return kubeconfig,result_lines,result_num
def find_history(config):
    dic = os.environ.get("HOME")+"/.kube/.dict"
    if os.path.exists(dic):
        with open(dic,'r') as f:
            dc = json.loads(f.read())
            dc[config] = dc[config] + 1 if config in dc else 1
        with open(dic,'w') as f:
            f.write(json.dumps(dc))
    else:
        dc = {}
        dc[config] = 1
        with open(dic,'w') as f:
            f.write(json.dumps(dc))
def find_ns():
    l = find_config()
    result_num = l[-1]
    if result_num > 0:
        p1 = subprocess.Popen("kubectl get ns --no-headers",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
        ns_set = list({ e.split()[0] for e in p1.stdout.readlines() })
        ns = find_optimal(ns_set,sys.argv[2])
        flag = True
        if ns:
            p2 = subprocess.Popen("kubectl get pods --no-headers -n "+ns,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
            if list({ e.split()[0] for e in p2.stdout.readlines() }):
                flag = False
                pass
        if flag and result_num > 1:
            l[1].remove(os.environ.get("HOME")+"/.kube/"+l[0])
            for config in l[1]:
                p1 = subprocess.Popen("kubectl get ns --no-headers --kubeconfig "+config,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
                ns_set = list({ e.split()[0] for e in p1.stdout.readlines() })
                ns = find_optimal(ns_set,sys.argv[2])
                if ns:
                    p2 = subprocess.Popen("kubectl get pods --no-headers --kubeconfig "+config+" -n "+ns,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
                    if list({ e.split()[0] for e in p2.stdout.readlines() }):
                        dst = os.environ.get("HOME")+"/.kube/config"
                        if os.path.exists(dst):
                            os.unlink(dst)
                            os.symlink(config,dst)
                            find_history(config)
                            l = find_config()
                            print("\033[5;32;40m%s\033[0m"%("[ switch to "+config.split("/")[-1]+" / "+ns+" ]"))
                            break
        kubeconfig = l[0]
    else:
        ns = None
        kubeconfig = None
    return ns,kubeconfig,result_num
def ki():
    if len(sys.argv) == 1:
        sys.argv.append('-h')
    elif sys.argv[1] not in ('-s','-n','-h','-help'):
        sys.argv.insert(1,'-n')
    if len(sys.argv) == 2 and sys.argv[1] in ('-n','-h','-help'):
        cmd = "kubectl get ns"
        print("\033[1;32;40m%s\033[0m" % cmd)
        os.system(cmd)
        print("\033[1;32;40m%s\033[0m" % "\nKubectl Pro controls the Kubernetes cluster manager")
        print("\033[1;32;40m%s\033[0m" % "1. ki -s","Select the kubernetes to be connected ( if there are multiple ~/.kube/kubeconfig*,the kubeconfig storage can be kubeconfig-hz,kubeconfig-sh,etc. )")
        print("\033[1;32;40m%s\033[0m" % "2. ki","List all namespaces")
        print("\033[1;32;40m%s\033[0m" % "3. ki xx","List all pods in the namespace ( if there are multiple ~/.kube/kubeconfig*,the best matching kubeconfig will be found ),the namespace parameter supports fuzzy matching,after outputting the pod list, grep: XXX filters the query\n         grep: index l ( [ l ] Print the logs for a container in a pod or specified resource )\n         grep: index l 100 ( Print the logs of the latest 100 lines )\n         grep: index l xxx ( Print the logs and filters the specified characters )\n         grep: index r ( [ r ] Rollout restart the pod )\n         grep: index o ( [ o ] Output the [Deployment,StatefulSet,Service,Ingress,Configmap,Secret].yml file )\n         grep: index del ( [ del ] Delete the pod )\n         grep: index cle ( [ cle ] Delete the Deployment/StatefulSet )\n         grep: index e[si] ( [ e[si] ] Edit the Deploy/Service/Ingress )")
        print("\033[1;32;40m%s\033[0m" % "4. ki xx d","List the Deployment of a namespace")
        print("\033[1;32;40m%s\033[0m" % "5. ki xx f","List the StatefulSet of a namespace")
        print("\033[1;32;40m%s\033[0m" % "6. ki xx s","List the Service of a namespace")
        print("\033[1;32;40m%s\033[0m" % "7. ki xx i","List the Ingress of a namespace")
    elif len(sys.argv) == 2 and sys.argv[1] == '-s':
        result_lines = find_config()[1]
        if result_lines and len(result_lines) > 1:
            lr = set()
            dst = os.environ.get("HOME")+"/.kube/config"
            for i in result_lines:
                for j in result_lines:
                    if cmp_file(i,j) and i != j:
                        e = i if len(i) < len(j) else j
                        if e != dst:
                            lr.add(e)
            for e in lr:
                os.remove(e)
                result_lines.remove(e)
            if os.path.exists(dst):
                k8s = ""
                res = None
                temp = result_lines
                while True:
                    if k8s:
                        k8s = str(k8s)
                    else:
                        result_lines = temp
                    result_lines = list(filter(lambda x: x.find(k8s) >= 0, result_lines))
                    if result_lines:
                        for n,e in enumerate(result_lines):
                            if cmp_file(e,dst):
                                print("\033[5;32;40m%s\033[0m"%n,e.strip())
                            else:
                                print("\033[1;32;40m%s\033[0m"%n,e.strip())
                        try:
                            k8s = input("\033[1;32;35m%s\033[0m\033[5;32;35m%s\033[0m" % ("select",":"))
                            k8s = k8s.strip()
                        except:
                            sys.exit()
                        if k8s.isdigit() and 0 <= int(k8s) < len(result_lines) or len(result_lines) == 1:
                            index = int(k8s) if k8s.isdigit() else 0
                            res = (result_lines[index]).split()[0]
                        if res:
                            os.unlink(dst)
                            os.symlink(res,dst)
                            print("\033[1;32;40m%s\033[0m" % res)
                            break
                    else:
                        k8s = ""
            else:
                print("\033[1;32;35m%s\033[0m\033[5;32;35m%s\033[0m " % ("File not found ",dst))
    elif 2 < len(sys.argv) < 5 and sys.argv[1] == '-n':
        l = find_ns()
        ns = l[0]
        kubeconfig = l[1]
        result_num = l[-1]
        if ns:
            pod = ""
            obj = "pod"
            ext = " -o wide"
            if len(sys.argv) == 4:
                d = {'d':['deploy'," -o wide"],'s':['service'," -o wide"],'i':['ingress'," -o wide"],'c':['configmap'," -o wide"],'t':['secret'," -o wide"],'n':['node'," -o wide"],'p':['pvc'," -o wide"],'v':['pv'," -o wide"],'f':['sts'," -o wide"],'e':['event','']}
                obj = d[str(sys.argv[3])[0]][0]
                ext = d[str(sys.argv[3])[0]][1]
            while True:
                if pod:
                    pod = str(pod)
                else:
                    cmd = "kubectl --sort-by=.metadata.creationTimestamp get "+obj+ext+" --no-headers -n "+ ns
                    print("\033[1;32;40m%s\033[0m" % cmd)
                    p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
                    result_lines = p.stdout.readlines()
                    if not result_lines:
                        break
                result_lines = list(filter(lambda x: x.find(pod) >= 0, result_lines))
                if result_lines:
                    for n,e in enumerate(result_lines):
                        print("\033[1;32;40m%s\033[0m"%n,e.strip())
                    if result_num > 1 and n > 7:
                        print("\033[1;32;40m%s\033[0m"%("[ "+kubeconfig+" / "+ns+" ]"))
                    try:
                        pod = input("\033[1;32;35m%s\033[0m\033[5;32;35m%s\033[0m" % ("grep",":"))
                        pod = pod.strip()
                    except:
                        sys.exit()
                    podList = pod.split()
                    pod = podList[0] if podList else ""
                    args = ''.join(podList[1:]) if len(podList) > 1 else "p"
                    if pod.isdigit() and int(pod) < len(result_lines) or len(result_lines) == 1:
                        index = int(pod) if pod.isdigit() else 0
                        res = result_lines[index].split()[0]
                        iip = result_lines[index].split()[5] if len(result_lines[index].split()) > 5 else ''
                        cmd = cmd_obj(ns,obj,res,args,iip)
                        print("\033[1;32;40m%s\033[0m" % cmd)
                        os.system(cmd)
                else:
                    pod = ""
        else:
            print("No namespace found in the kubenetes.")
def main():
    ki()
#-----------------PROG----------------------------
if __name__ == '__main__':
    main()
