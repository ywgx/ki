#!/usr/bin/python3
#*************************************************
# Description : Kubectl Pro
# Version     : 1.2
#*************************************************
import os,re,sys,time,subprocess
#-----------------VAR-----------------------------
home = os.environ["HOME"]
history = home + "/.history"
ki_lock = history + "/.lock"
ki_dict = history + "/.dict"
ki_last = history + "/.last"
ki_ns_dict = history + "/.ns_dict"
ki_name_dict = history + "/.name_dict"
default_config = home + "/.kube/config"
#-----------------FUN-----------------------------
def cmp_file(f1, f2):
    if os.stat(f2).st_size != os.stat(f1).st_size:
        return False
    bufsize = 1024
    with open(f1, 'rb') as fp1, open(f2, 'rb') as fp2:
        while True:
            b1 = fp1.read(bufsize)
            b2 = fp2.read(bufsize)
            if b1 != b2:
                return False
            if not b1:
                return True
def cmd_obj(ns, obj, res, args, iip="x"):
    name = res
    if obj in ("Node"):
        if args[0] in ('c','u'):
            action = "cordon" if args[0] == 'c' else "uncordon"
            cmd = "kubectl "+action+" "+res
        elif args[0] in ('d','e'):
            action = "describe" if args[0] == 'd' else "edit"
            cmd = "kubectl "+action+" "+obj.lower()+" "+res
        else:
            action = "ssh"
            cmd = action +" root@"+iip
    elif obj in ("Event"):
        action = "get"
        cmd = "kubectl -n "+ns+" "+action+" "+obj+"  --sort-by=.metadata.creationTimestamp"
    elif obj in ("Deployment","DaemonSet","Service","StatefulSet","Ingress","ConfigMap","Secret","PersistentVolume","PersistentVolumeClaim","CronJob"):
        action2 = ""
        if args == "cle":
            action = "delete"
        elif args[0] == "e":
            action = "edit"
        elif args[0] == "d":
            action = "describe"
        elif args[0] == 'o':
            action = "get"
            action2 = " -o yaml > "+res+"."+obj.lower()+".yml"
        else:
            action = "get"
        cmd = "kubectl -n "+ns+" "+action+" "+obj.lower()+" "+res+action2 if obj not in ("PersistentVolume") else "kubectl "+action+" "+obj.lower()+" "+res+action2
    elif obj in ("ResourceQuota"):
        action2 = ""
        if args[0] == "e":
            action = "edit"
        elif args[0] == "d":
            action = "describe"
        elif args[0] == 'o':
            action = "get"
            action2 = " -o yaml > "+ns+"."+obj.lower()+".yml"
        elif args == "cle":
            action = "delete"
        else:
            action = "get"
        cmd = "kubectl -n "+ns+" "+action+" "+obj.lower()+" "+res+action2
    else:
        l = get_obj(ns,res)
        obj = l[0]
        name = l[1]
        d = {'d':'Deployment','s':'Service','i':'Ingress','f':'StatefulSet','a':'DaemonSet','p':'Pod'}
        if args == "p":
            cmd = "kubectl -n "+ns+" exec -it "+res+" -- sh"
        elif args == "del":
            cmd = "kubectl -n "+ns+" delete pod "+res+"  --now &"
        elif args == "cle":
            action = "delete"
            cmd = "kubectl -n "+ns+" "+action+" "+obj.lower()+" "+name
        elif args == "destory":
            action = "delete"
            cmd = "kubectl -n "+ns+" "+action+" "+obj.lower()+",service,ingress "+name
        elif args[0] in ('l','c'):
            regular = args[1:]
            p = subprocess.Popen("kubectl -n "+ns+" get pod "+res+" -o jsonpath='{.spec.containers[:].name}'",shell=True,stdout=subprocess.PIPE,universal_newlines=True)
            result_list = p.stdout.readlines()[0].split()
            container = name if name in result_list else "--all-containers"
            if regular:
                cmd = ( "kubectl -n "+ns+" logs -f "+res+" "+container+" --tail "+regular ) if regular.isdigit() else ( "kubectl -n "+ns+" logs -f "+res+" "+container+"|grep --color=auto " + ( regular if args[0] == 'l' else "-C 10 "+regular ) )
            else:
                cmd = "kubectl -n "+ns+" logs -f "+res+" "+container+" --tail 200"
        elif args[0] in ('r'):
            cmd = "kubectl -n "+ns+" rollout restart "+obj.lower()+" "+name
        elif args[0] in ('o'):
            action = "get"
            if len(args) > 1:
                obj = d.get(args[1],'Pod')
                if obj == 'Pod': name = res
            cmd = "kubectl -n "+ns+" "+action+" "+obj.lower()+" "+name+" -o yaml > "+name+"."+obj+".yml"
        elif args[0] in ('d','e'):
            action = "describe" if args[0] == 'd' else "edit"
            if len(args) > 1:
                obj = d.get(args[1],'Pod')
                if obj == 'Pod': name = res
            cmd = "kubectl -n "+ns+" "+action+" "+obj.lower()+" "+name
        elif args[0] in ('s'):
            regular = args.split('s')[-1]
            action = "scale"
            replicas = regular if regular.isdigit() and -1 < int(regular) < 30 else str(1)
            cmd = "kubectl -n "+ns+" "+action+" --replicas="+replicas+" "+obj.lower()+"/"+name
        else:
            cmd = "kubectl -n "+ns+" exec -it "+res+" -- sh"
    return cmd,obj,name
def find_ip(res: str):
    ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}',res)
    return ip[0] if ip else ""
def find_optimal(namespace_list: list, namespace: str):
    namespace_list.sort()
    indexes = [row.index(namespace) * 0.8 if namespace in row else 10000 for row in namespace_list]
    contains = [len(row.replace(namespace, '')) * 0.42 for row in namespace_list]
    words = [namespace in row for row in namespace_list]
    result_list = [(indexes[i] + container) * (1 if words[i] else 1.62) for i, container in enumerate(contains)]
    return namespace_list[result_list.index(min(result_list))] if len(set(indexes)) != 1 else ( namespace_list[words.index(True)] if True in words else None )
def find_config():
    os.path.exists(history) or os.mkdir(history)
    cmd = '''find $HOME/.kube -maxdepth 2 -type f -name 'kubeconfig*' 2>/dev/null|egrep '.*' || ( find $HOME/.kube -maxdepth 1 -type f 2>/dev/null|egrep '.*' &>/dev/null && grep -l "current-context" `find $HOME/.kube -maxdepth 1 -type f` )'''
    k8s_list = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    result_set = { e.split('\n')[0] for e in k8s_list.stdout.readlines() }
    result_num = len(result_set)
    result_lines = list(result_set)
    kubeconfig = None
    if result_num == 1:
        if os.path.exists(default_config):
            if not os.path.islink(default_config):
                with open(default_config,'r') as fr, open(home+"/.kube/config-0",'w') as fw: fw.write(fr.read())
                os.unlink(default_config)
                os.symlink(home+"/.kube/config-0",default_config)
                kubeconfig = "config-0"
            else:
                kubeconfig = result_lines[0].split("/")[-1]
        else:
            try:
                os.unlink(default_config)
            except:
                pass
            os.symlink(result_lines[0],default_config)
            kubeconfig = result_lines[0].split("/")[-1]
    elif result_num > 1:
        dc = {}
        if os.path.exists(ki_dict) and os.path.getsize(ki_dict) > 5:
            with open(ki_dict,'r') as f:
                try:
                    dc = eval(f.read())
                    for config in list(dc.keys()):
                        if not os.path.exists(config):
                            del dc[config]
                except:
                    os.remove(ki_dict)
        if os.path.exists(ki_last) and os.path.getsize(ki_last) > 0:
            with open(ki_last,'r') as f:
                last_config = f.read()
                if not os.path.exists(last_config):
                    last_config = result_lines[0]
        else:
            last_config = result_lines[0]
        result_dict = sorted(dc.items(),key = lambda dc:(dc[1], dc[0]),reverse=True)
        sort_list = [ i[0] for i in result_dict ]
        last_config in sort_list and sort_list.remove(last_config)
        sort_list.insert(0,last_config)
        result_lines = sort_list + list(result_set - set(sort_list))
        if os.path.exists(default_config):
            if not os.path.islink(default_config):
                with open(default_config,'r') as fr, open(home+"/.kube/config-0",'w') as fw: fw.write(fr.read())
                os.unlink(default_config)
                os.symlink(home+"/.kube/config-0",default_config)
                kubeconfig = "config-0"
            else:
                for e in result_lines:
                    if cmp_file(e,default_config): kubeconfig = e.strip().split("/")[-1]
        else:
            try:
                os.unlink(default_config)
            except:
                pass
            os.symlink(result_lines[0],default_config)
            kubeconfig = result_lines[0].split("/")[-1]
    return kubeconfig,result_lines,result_num
def find_history(config):
    dc = {}
    if os.path.exists(ki_dict) and os.path.getsize(ki_dict) > 5:
        with open(ki_dict,'r') as f:
            dc = eval(f.read())
            dc[config] = dc[config] + 1 if config in dc else 1
            dc.pop(default_config,404)
            for config in list(dc.keys()):
                if not os.path.exists(config): del dc[config]
    else:
        dc[config] = 1
    with open(ki_dict,'w') as f: f.write(str(dc))
def find_ns(config_struct: list):
    ns = None
    kubeconfig = None
    switch = False
    result_num = config_struct[-1]
    kn = sys.argv[2].split('.')
    ns_pattern = kn[-1] if len(kn) > 1 and len(kn[-1].strip()) > 0 else kn[0]
    config = find_optimal(config_struct[1],kn[0]) or default_config if len(kn) > 1 else default_config
    current_config = os.path.realpath(config)
    current_config in config_struct[1] and config_struct[1].remove(current_config)
    config_struct[1].insert(0,current_config)
    for n,config in enumerate(config_struct[1]):
        if os.path.exists(ki_ns_dict):
            with open(ki_ns_dict,'r') as f:
                try:
                    d = eval(f.read())
                    ns_list = d[config]
                except:
                    ns_list = cache_ns(config_struct)[config]
        else:
            p = subprocess.Popen("kubectl get ns --no-headers --kubeconfig "+config,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
            ns_list = [ e.split()[0] for e in p.stdout.readlines() ]
        ns = find_optimal(ns_list,ns_pattern)
        if ns:
            kubeconfig = config
            break
    return ns,kubeconfig,switch,result_num
def cache_ns(config_struct: list):
    d = {}
    for config in config_struct[1]:
        s = []
        p = subprocess.Popen("kubectl get ns --no-headers --kubeconfig "+config,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
        ns_list = [ e.split()[0] for e in p.stdout.readlines() ]
        for ns in ns_list:
            p = subprocess.Popen("kubectl get pod --no-headers --kubeconfig "+config+" -n "+ns,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
            if p.stdout.readlines():
                s.append(ns)
            else:
                p = subprocess.Popen("kubectl get cronjob --no-headers --kubeconfig "+config+" -n "+ns,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
                if p.stdout.readlines():
                    s.append(ns)
        d[config] = s
    with open(ki_ns_dict,'w') as f: f.write(str(d))
    return d
def switch_config(switch_num: int,k8s: str,ns: str,time: str):
    switch = False
    if os.path.exists(default_config) and os.environ['KUBECONFIG'] not in {default_config,os.path.realpath(default_config)}:
        if default_config != os.path.realpath(default_config):
            with open(ki_last,'w') as f: f.write(os.path.realpath(default_config))
        os.unlink(default_config)
        os.symlink(os.environ['KUBECONFIG'],default_config)
        print("\033[1;33m{}\033[0m".format("[ "+time+"  "+str(switch_num+1)+"-SWITCH  "+k8s+" / "+ns+" ] "))
        find_history(os.environ['KUBECONFIG'])
        switch = True
    return switch
def get_obj(ns: str,res: str,args='x'):
    d = {'s':"Service",'i':"Ingress"}
    cmd = "kubectl -n "+ns+" get pod "+res+" -o jsonpath='{.metadata.ownerReferences[0].kind}'"
    l1 = res.split('-')
    l2 = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True).stdout.readlines()
    obj = l2[0] if l2 else "Pod"
    if obj in ("StatefulSet","DaemonSet"):
        del l1[-1:]
    elif obj in ("ReplicaSet","Deployment"):
        del l1[-2:]
        obj = "Deployment"
    name = ('-').join(l1)
    if args[-1] in d.keys():
        obj = d[args[-1]]
    return obj,name
def get_feature(ns_list: list):
    P = 177
    MOD = 192073433

    string_hashes = []
    max_string_length = 0
    for string in ns_list:
        hashes = [0]
        for i in range(len(string)):
             hashes.append((hashes[-1] * P + ord(string[i])) % MOD)
        string_hashes.append(hashes)
        max_string_length = max(max_string_length, len(string))

    pows = [1]
    for i in range(max_string_length + 1):
        pows.append(pows[-1] * P % MOD)

    sorted_indices = list(range(len(ns_list)))
    sorted_indices = sorted(sorted_indices, key=lambda i: len(ns_list[i]))

    disabled_hashes = set()
    answers = [None for _ in ns_list]
    for i in sorted_indices:
        string = ns_list[i]
        hashes = string_hashes[i]

        hash_to_be_disabled = []
        min_length = len(string) + 1
        for x in range(len(string)):
            for y in range(x, len(string)):
                substr_hash = (hashes[y + 1] - hashes[x] * pows[y + 1 - x]) % MOD
                substr_hash = (substr_hash + MOD) % MOD
                hash_to_be_disabled.append(substr_hash)
                if substr_hash not in disabled_hashes and min_length > (y - x + 1) and '-' not in ns_list[i][x: y + 1]:
                    min_length = y - x + 1
                    answers[i] = (x, y)

        disabled_hashes.update(hash_to_be_disabled)

    d = {}
    for i, (x, y) in enumerate(answers):
        d[ns_list[i]] = ns_list[i][x: y + 1]
    return d
def info_w(k8s_path: str,result_lines: list):
    l = k8s_path.split('/')
    if 'K8S' in l:
        if not os.path.exists(ki_lock) and len(l) > l.index('K8S')+1:
            k8s_dir = l[l.index('K8S')+1]
            if ( home+"/.kube/" + k8s_dir ) in result_lines or ( home+"/.kube/kubeconfig-" + k8s_dir ) in result_lines:
                k8s_str = k8s_dir
            else:
                k8s_str = '-'.join(k8s_dir.split('-')[0:-1])
            if result_lines:
                config = find_optimal(result_lines,k8s_str)
                if config and os.path.exists(default_config) and config not in {default_config,os.path.realpath(default_config)}:
                    os.unlink(default_config)
                    os.symlink(config,default_config)
                    print("\033[1;35m{}\033[0m".format("[ "+config.split("/")[-1]+" ]"))
                else:
                    print("\033[1;36m{}\033[0m".format("[ "+os.path.realpath(default_config).split("/")[-1]+" ]"))
        else:
            print("\033[1;36m{}\033[0m".format("[ "+os.path.realpath(default_config).split("/")[-1]+(" (lock)" if os.path.exists(ki_lock) else "")+" ]"))
    else:
        print("\033[1;32m{}\033[0m".format("[ "+os.path.realpath(default_config).split("/")[-1]+" ]"))
        os.path.exists(ki_lock) and int(time.time()-os.stat(ki_lock).st_mtime) > 3600 and os.unlink(ki_lock)
def info_k():
    if os.path.exists(ki_name_dict) and os.path.exists(ki_dict):
        with open(ki_name_dict,'r') as f1, open(ki_dict,'r') as f2:
            dc1 = eval(f1.read())
            dc2 = eval(f2.read())
            for k in sorted(dc1):
                print("{:<56}{:<32}{}".format(k,dc1[k][0],dc1[k][1]))
            for k in dc2:
                print("{:<56}{}".format(k.split('/')[-1],dc2[k]))
def record(res: str,name: str,obj: str,cmd: str,kubeconfig: str,ns: str):
    l = os.environ['SSH_CONNECTION'].split() if 'SSH_CONNECTION' in os.environ else ['NULL','NULL','NULL']
    USER = os.environ['USER'] if 'USER' in os.environ else "NULL"
    HOST = l[2]
    FROM = l[0]
    key = kubeconfig+"/"+ns+"/"+("Pod" if obj in ('Deployment','StatefulSet','DaemonSet','ReplicaSet') else obj)
    ki_file = time.strftime("%F",time.localtime())
    with open(history+"/"+ki_file,'a+') as f: f.write( time.strftime("%F %T ",time.localtime())+"[ "+USER+"@"+HOST+" from "+FROM+" ---> "+kubeconfig+" ]  " + cmd + "\n" )
    dc = {}
    if os.path.exists(ki_name_dict) and os.path.getsize(ki_name_dict) > 5:
        with open(ki_name_dict,'r') as f:
            try:
                dc = eval(f.read())
                name_dc = dict(dc[key][1]) if key in dc else {}
                name_dc[name] = name_dc[name] + 1 if name in name_dc else 1
                name_dc = sorted(name_dc.items(),key = lambda name_dc:(name_dc[1], name_dc[0]),reverse=True)
                if len(name_dc) > 5: del name_dc[5:]
                dc[key] = [name,name_dc]
            except:
                os.remove(ki_name_dict)
    else:
        dc[key] = [name,[(name,1)]]
    with open(ki_name_dict,'w') as f: f.write(str(dc))
def ki():
    ( len(sys.argv) == 1 or sys.argv[1] not in ('-n','-t','-t1','-t2','-r','-i','-e','-es','-ei','-o','-os','-oi','-restart','-s','-select','-l','-lock','-u','-unlock','--w','--watch','-h','-help','-c','-cache','-k','-a') ) and sys.argv.insert(1,'-n')
    len(sys.argv) == 2 and sys.argv[1] in ('-i','-e','-es','-ei','-o','-os','-oi') and sys.argv.insert(1,'-n')
    len(sys.argv) == 2 and sys.argv[1] in ('-a') and sys.argv.extend(['kube','Pod'])
    len(sys.argv) == 3 and sys.argv[1] in ('-a') and sys.argv.insert(2,'kube')
    config_struct = find_config()
    if len(sys.argv) == 2 and sys.argv[1] in ('--w','--watch'):
        info_w(os.environ["PWD"],config_struct[1])
    elif len(sys.argv) == 2 and sys.argv[1] in ('-l','-lock'):
        os.path.exists(ki_lock) or open(ki_lock,"a").close()
    elif len(sys.argv) == 2 and sys.argv[1] in ('-u','-unlock'):
        os.path.exists(ki_lock) and os.unlink(ki_lock)
    elif len(sys.argv) == 2 and sys.argv[1] == '-n':
        cmd = "kubectl get ns  --no-headers"
        print("\033[1;32m{}\033[0m".format(cmd.split('  --')[0]))
        os.environ['KUBECONFIG'] = os.path.realpath(default_config)
        p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
        l = p.stdout.readlines()
        ns_dict = get_feature([ e.split()[0] for e in l ])
        for e in l:
            s = ns_dict[e.split()[0]]
            num = e.find(s)
            num_s = num+len(s)
            print("{}\033[1;35m{}\033[0m{}".format(e[:num],e[num:num_s],e[num_s:]),end='')
        os.path.exists(ki_ns_dict) or cache_ns(config_struct)
    elif len(sys.argv) == 2 and sys.argv[1] in ('-k'):
        info_k()
    elif len(sys.argv) == 2 and sys.argv[1] in ('-c','-cache'):
        cache_ns(config_struct)
    elif 1 < len(sys.argv) < 4 and sys.argv[1] in ('-s','-select'):
        result_lines = config_struct[1]
        if result_lines and len(result_lines) > 1:
            if len(sys.argv) == 3:
                config = find_optimal(result_lines,sys.argv[2])
                if config and os.path.exists(default_config) and config not in {default_config,os.path.realpath(default_config)}:
                    os.unlink(default_config)
                    os.symlink(config,default_config)
                    print("\033[1;33m{}\033[0m".format("[ SWITCH "+config.split("/")[-1]+" ] "))
            else:
                lr = set()
                for i in result_lines:
                    for j in result_lines:
                        if cmp_file(i,j) and i != j:
                            e = i if len(i) < len(j) else j
                            if e != default_config and e != os.path.realpath(default_config):
                                lr.add(e)
                for e in lr:
                    os.remove(e)
                    result_lines.remove(e)
                if os.path.exists(default_config):
                    pattern = ""
                    res = None
                    temp = result_lines
                    while True:
                        result_lines = list(filter(lambda x: x.find(pattern) >= 0, result_lines)) if pattern else temp
                        if result_lines:
                            for n,e in enumerate(result_lines):
                                if cmp_file(e,default_config):
                                    print("\033[5;32m{}\033[0m \033[1;32m{}\033[0m".format(n,e.strip().split('/')[-1]))
                                else:
                                    print("\033[1;32m{}\033[0m {}".format(n,e.strip().split('/')[-1]))
                            try:
                                pattern = input("\033[1;35m%s\033[0m\033[5;35m%s\033[0m" % ("select",":")).strip()
                            except:
                                sys.exit()
                            if pattern.isdigit() and 0 <= int(pattern) < len(result_lines) or len(result_lines) == 1:
                                index = int(pattern) if pattern.isdigit() else 0
                                res = (result_lines[index]).split()[0]
                            if res and res not in {default_config,os.path.realpath(default_config)}:
                                os.unlink(default_config)
                                os.symlink(res,default_config)
                                print('\033[{}C\033[1A'.format(10),end = '')
                                print("\033[1;33m{}\033[0m".format(res.split('/')[-1]))
                                find_history(res)
                                open(ki_lock,"a").close()
                                break
                        else:
                            pattern = ""
                else:
                    print("\033[1;32m{}\033[0m\033[5;32m{}\033[0m".format("File not found ",default_config))
    elif 2 < len(sys.argv) < 5 and sys.argv[1] in ('-n','-r','-t','-t1','-t2','-i','-l','-e','-es','-ei','-o','-os','-oi','-a'):
        l = find_ns(config_struct)
        ns = l[0]
        switch = l[2]
        switch_num = 0
        if ns:
            pod = ""
            obj = "Pod"
            ext = " -o wide"
            os.environ['KUBECONFIG'] = l[1]
            if len(sys.argv) == 4:
                d = {'d':['Deployment'," -o wide"],'s':['Service'," -o wide"],'i':['Ingress'," -o wide"],'c':['ConfigMap'," -o wide"],'t':['Secret'," -o wide"],'n':['Node'," -o wide"],'p':['PersistentVolumeClaim'," -o wide"],'v':['PersistentVolume'," -o wide"],'f':['StatefulSet'," -o wide"],'j':['CronJob'," -o wide"],'P':['Pod'," -o wide"],'e':['Event',''],'r':['ReplicaSet',''],'a':['DaemonSet',''],'q':['ResourceQuota','']}
                obj = d[sys.argv[3][0]][0] if sys.argv[3][0] in d else "Pod"
                ext = d[sys.argv[3][0]][1] if sys.argv[3][0] in d else ""
                if sys.argv[1] in ('-i','-l','-e','-es','-ei','-o','-os','-oi'):
                    begin = time.perf_counter()
                    while True:
                        if ns:
                            p = subprocess.Popen("kubectl get pods --no-headers -n "+ns,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
                            pods = [ e.split()[0] for e in p.stdout.readlines() ]
                            pod = find_optimal(pods,sys.argv[3]) if pods else None
                            if not (pods and pod):
                                kn = sys.argv[2].split('.')
                                ns_pattern = kn[-1] if len(kn) > 1 and len(kn[-1].strip()) > 0 else kn[0]
                                os.environ['KUBECONFIG'] in config_struct[1] and config_struct[1].remove(os.environ['KUBECONFIG'])
                                if config_struct[1]:
                                    for n,config in enumerate(config_struct[1]):
                                        p = subprocess.Popen("kubectl get ns --no-headers --kubeconfig "+config,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
                                        ns_list = [ e.split()[0] for e in p.stdout.readlines() ]
                                        ns = find_optimal(ns_list,ns_pattern)
                                        if ns:
                                            os.environ['KUBECONFIG'] = config
                                            switch_num += 1
                                            break
                                else:
                                    print("NotFound")
                                    break
                            else:
                                end = time.perf_counter()
                                k8s = os.environ['KUBECONFIG'].split('/')[-1]
                                switch_config(switch_num,k8s,ns,str(end-begin))
                                name = pod
                                if sys.argv[1] in ('-i'):
                                    cmd = "kubectl -n "+ns+" exec -it "+pod+" -- sh"
                                elif sys.argv[1] in ('-l'):
                                    cmd = "kubectl -n "+ns+" logs -f "+pod+" --all-containers --tail 10"
                                else:
                                    l = get_obj(ns,pod,sys.argv[1])
                                    obj = l[0]
                                    name = l[1]
                                    if sys.argv[1] in ('-e','-es','-ei'):
                                        action = "edit"
                                        action2 = ""
                                    else:
                                        action = "get"
                                        action2 = " -o yaml > "+name+"."+obj+".yml"
                                    cmd = "kubectl -n "+ns+" "+action+" "+obj.lower()+" "+name+action2
                                print("\033[1;32m{}\033[0m".format(cmd))
                                record(pod,name,obj,cmd,k8s,ns)
                                os.system(cmd)
                                print('\r')
                                break
                        else:
                            print("NotFound")
                            sys.exit()
                    sys.exit()
            flag = True
            begin = time.perf_counter()
            while True:
                if ns:
                    if not pod:
                        if sys.argv[1] in ('-n','-r'):
                            cmd = "kubectl"+" get "+obj.lower()+ext+" -n "+ ns+("  --sort-by=.status.containerStatuses[0].restartCount" if sys.argv[1].split('n')[-1] else "  --sort-by=.metadata.creationTimestamp") + " --no-headers"
                        elif sys.argv[1] in ('-a'):
                            cmd = "kubectl"+" get "+obj.lower()+ext+" -A  --sort-by=.metadata.creationTimestamp --no-headers"
                        else:
                            key = sys.argv[1].split('t')[-1] if sys.argv[1].split('t')[-1].isdigit() else "3"
                            cmd = "kubectl top "+obj.lower()+" -n "+ ns +"  --no-headers|sort --key "+key+" --numeric"
                        result_lines = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True).stdout.readlines()
                        if not result_lines:
                            kn = sys.argv[2].split('.')
                            ns_pattern = kn[-1] if len(kn) > 1 and len(kn[-1].strip()) > 0 else kn[0]
                            os.environ['KUBECONFIG'] in config_struct[1] and config_struct[1].remove(os.environ['KUBECONFIG'])
                            if config_struct[1]:
                                for n,config in enumerate(config_struct[1]):
                                    p = subprocess.Popen("kubectl get ns --no-headers --kubeconfig "+config,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
                                    ns_list = [ e.split()[0] for e in p.stdout.readlines() ]
                                    ns = find_optimal(ns_list,ns_pattern)
                                    if ns:
                                        os.environ['KUBECONFIG'] = config
                                        switch_num += 1
                                        break
                            else:
                                print("No namespace found in the kubernetes.")
                                break
                        else:
                            if flag:
                                end = time.perf_counter()
                                k8s = os.environ['KUBECONFIG'].split('/')[-1]
                                switch = switch_config(switch_num,k8s,ns,str(end-begin))
                                flag = False
                            print("\033[1;32m{}\033[0m".format(cmd.split(' --')[0]))
                    if not (pod.isdigit() and int(pod) < len(result_lines)) and pod != '*':
                        result_lines = list(filter(lambda x: x.find(pod) >= 0, result_lines))
                    if result_lines:
                        now = time.strftime("%T",time.localtime())
                        for n,e in enumerate(result_lines):
                            print("\033[1;32m{}\033[0m {}".format(n,e.strip()))
                        if n > 3:
                            style = "\033[1;33m{}\033[0m" if switch else "\033[1;32m{}\033[0m"
                            string = "[ "+k8s+" / "+ns+" --- "+obj+" ] [ "+now+" ]" if sys.argv[1] not in ('-a') and obj not in ('PersistentVolume') else "[ "+k8s+" --- "+obj+" ] [ "+now+" ]"
                            print(style.format(string))
                            switch = False
                            if pod == '*':
                                print('\033[{}C\033[1A'.format(len(string)),end = '')
                                print(style.format(" Watching..."))
                        try:
                            if pod != '*':
                                pod = input("\033[1;35m%s\033[0m\033[5;35m%s\033[0m" % ("select",":")).strip()
                                num = 10 + len(pod)
                            else:
                                result_lines = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True).stdout.readlines()
                                time.sleep(3)
                        except:
                            sys.exit()
                        result_len = len(result_lines)
                        podList = pod.split()
                        pod = podList[0] if podList else ""
                        if pod in ('$','#','@','!','~'):
                            if pod == '$':
                                pod = str(result_len-1)
                            elif os.path.exists(ki_name_dict):
                                with open(ki_name_dict,'r') as f:
                                    dc = eval(f.read())
                                    key = k8s+'/'+ns+'/'+obj
                                    last_res = ( dc[key][0] if pod in ('!','~') else dc[key][1][0][0] ) if key in dc else ""
                                    for n,e in enumerate(result_lines[::-1]):
                                        if last_res in e:
                                            pod = str(result_len-n-1)
                                            break
                        args = ''.join(podList[1:]) if len(podList) > 1 else "p"
                        if pod.isdigit() and int(pod) < result_len or ( result_len == 1 and pod != '*'):
                            index = int(pod) if pod.isdigit() and int(pod) < result_len else 0
                            res = result_lines[index].split()[0 if sys.argv[1] not in ('-a') else (1 if obj not in ("PersistentVolume") else 0)]
                            iip = result_lines[index].split()[5] if len(result_lines[index].split()) > 5 else find_ip(res)
                            ns = result_lines[index].split()[0] if sys.argv[1] in ('-a') else ns
                            l = cmd_obj(ns,obj,res,args,iip)
                            print('\033[{}C\033[1A'.format(num),end = '')
                            print("\033[1;32m{}\033[0m".format(l[0].split('  --')[0]))
                            record(res,l[2],l[1],l[0],k8s,ns)
                            os.system(l[0])
                            print('\r')
                    else:
                        pod = ""
                else:
                    print("NotFound")
                    sys.exit()
        else:
            print("No namespace found in the kubernetes.")
            subprocess.Popen("ki -c",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    elif len(sys.argv) == 2 and sys.argv[1] in ('-h','-help'):
        style = "\033[1;32m%s\033[0m"
        print(style % "Kubectl Pro controls the Kubernetes cluster manager")
        print("\nFind more information at: https://ki.xabc.io\n")
        print(style % "1. ki","List all namespaces")
        print(style % "2. ki xx","List all pods in the namespace ( if there are multiple ~/.kube/kubeconfig*,the best matching kubeconfig will be found ),the namespace parameter supports fuzzy matching,after outputting the pod list, select: xxx filters the query\n         select: index l ( [ l ] Print the logs for a container in a pod or specified resource )\n         select: index l 100 ( Print the logs of the latest 100 lines )\n         select: index l xxx ( Print the logs and filters the specified characters )\n         select: index r ( [ r ] Rollout restart the pod )\n         select: index o ( [ o ] Output the [Deployment,StatefulSet,Service,Ingress,Configmap,Secret].yml file )\n         select: index del ( [ del ] Delete the pod )\n         select: index cle ( [ cle ] Delete the Deployment/StatefulSet )\n         select: index e[si] ( [ e[si] ] Edit the Deploy/Service/Ingress )\n         select: index s5 ( [ s3 ] Set the Deploy/StatefulSet replicas=3 )\n         select: index dp ( Describe a pod )\n         select: * ( Watching... )")
        print(style % "3. ki xx d","List the Deployment of a namespace")
        print(style % "4. ki xx f","List the StatefulSet of a namespace")
        print(style % "5. ki xx s","List the Service of a namespace")
        print(style % "6. ki xx i","List the Ingress of a namespace")
        print(style % "7. ki xx t","List the Secret of a namespace")
        print(style % "8. ki xx a","List the DaemonSet of a namespace")
        print(style % "9. ki xx j","List the CronJob of a namespace")
        print(style % "10. ki xx v","List the PersistentVolume of a namespace")
        print(style % "11. ki xx p","List the PersistentVolumeClaim of a namespace")
        print(style % "12. ki xx q","List the ResourceQuota of a namespace")
        print(style % "13. ki -i $ns $pod","Login in the container,this way can be one-stop")
        print(style % "14. ki -l $ns $pod","Print the logs for a container,this way can be one-stop")
        print(style % "15. ki -e[si] $ns $pod","Edit the Deploy/Service/Ingress for a container,this way can be one-stop")
        print(style % "16. ki $k8s.$ns","Select the kubernetes which namespace in the kubernetes ( if there are multiple ~/.kube/kubeconfig*,this way can be one-stop. )")
        print(style % "17. ki -s","Select the kubernetes to be connected ( if there are multiple ~/.kube/kubeconfig*,the kubeconfig storage can be kubeconfig-hz,kubeconfig-sh,etc. )")
        print(style % "18. ki -c","Enable write caching of namespace ( ~/.history/.ns_dict )")
        print(style % "19. ki -a","List all pods in the kubernetes")
def main():
    ki()
#-----------------PROG----------------------------
if __name__ == '__main__':
    main()
