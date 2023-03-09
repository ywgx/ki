#!/usr/bin/python3
#*************************************************
# Description : Kubectl Pro
# Version     : 3.7
#*************************************************
import os,re,sys,time,readline,subprocess
#-----------------VAR-----------------------------
home = os.environ["HOME"]
history = home + "/.history"
default_config = home + "/.kube/config"
ki_all = history + "/.all"
ki_dict = history + "/.dict"
ki_last = history + "/.last"
ki_lock = history + "/.lock"
ki_line = history + "/.line"
ki_cache = history + "/.cache"
ki_unlock = history + "/.unlock"
ki_ns_dict = history + "/.ns_dict"
ki_pod_dict = history + "/.pod_dict"
ki_latest_ns_dict = history + "/.latest_ns_dict"
ki_current_ns_dict = history + "/.current_ns_dict"
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
    elif obj in ("Deployment","DaemonSet","Service","StatefulSet","Ingress","ConfigMap","Secret","PersistentVolume","PersistentVolumeClaim","CronJob","Job","VirtualService","Gateway","DestinationRule","EnvoyFilter"):
        action2 = ""
        if args in ("cle","delete"):
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
        elif args in ("cle","delete"):
            action = "delete"
        else:
            action = "get"
        cmd = "kubectl -n "+ns+" "+action+" "+obj.lower()+" "+res+action2
    else:
        l = get_obj(ns,res)
        obj = l[0]
        name = l[1]
        d = {'d':'Deployment','s':'Service','i':'Ingress','f':'StatefulSet','a':'DaemonSet','p':'Pod','V':'VirtualService','G':'Gateway','D':'DestinationRule','E':'EnvoyFilter'}
        if args == "p":
            cmd = "kubectl -n "+ns+" exec -it "+res+" -- sh"
        elif args == "del":
            cmd = "kubectl -n "+ns+" delete pod "+res+"  --now &"
        elif args == "delf":
            action = "delete"
            cmd = "kubectl -n "+ns+" delete pod "+res+"  --grace-period=0 --force"
        elif args in ("cle","delete"):
            action = "delete"
            cmd = "kubectl -n "+ns+" "+action+" "+obj.lower()+" "+name
        elif args in ("destroy","destory"):
            action = "delete"
            cmd = "kubectl -n "+ns+" "+action+" "+obj.lower()+",service,ingress "+name
        elif args[0] in ('l','c'):
            regular = args[1:]
            try:
                result_list = get_data("kubectl -n "+ns+" get pod "+res+" -o jsonpath='{.spec.containers[:].name}'")[0].split()
            except:
                sys.exit()
            container = "--all-containers"
            if regular:
                if regular.isdigit():
                    if 0 < int(regular) < 10000:
                        os.environ['KI_LINE'] = regular
                        with open(ki_line,'w') as f:
                            f.write(regular)
                cmd = ( "kubectl -n "+ns+" logs -f "+res+" "+container+" --tail "+regular ) if regular.isdigit() and len(regular) < 12 else ( "kubectl -n "+ns+" logs -f "+res+" "+container+"|grep --color=auto " + ( regular if args[0] in ('l') else "-C 10 "+regular ) )
            else:
                if 'KI_LINE' in os.environ:
                    line = os.environ['KI_LINE']
                elif os.path.exists(ki_line):
                    with open(ki_line,'r') as f:
                        line_file = str(f.read())
                        os.environ['KI_LINE'] = line_file if line_file.isdigit() else str(200)
                        line = os.environ['KI_LINE']
                else:
                    line = str(200)
                cmd = "kubectl -n "+ns+" logs -f "+res+" "+container+" --tail "+line
        elif args[0] in ('v'):
            regular = args[1:]
            try:
                result_list = get_data("kubectl -n "+ns+" get pod "+res+" -o jsonpath='{.spec.containers[:].name}'")[0].split()
            except:
                sys.exit()
            container = name if name in result_list else "--all-containers"
            cmd = "kubectl -n "+ns+" logs -f "+res+" "+container+" --previous --tail "+ ( regular if regular and regular.isdigit() and len(regular) < 12 else "500" )
        elif args[0] in ('r'):
            cmd = "kubectl -n "+ns+" rollout restart "+obj.lower()+" "+name
        elif args[0] in ('u'):
            cmd = "kubectl -n "+ns+" rollout undo "+obj.lower()+"/"+name
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
        elif args[0] in ('n'):
            action = "ssh"
            try:
                hostIP = get_data("kubectl -n "+ns+" get pod "+res+" -o jsonpath='{.status.hostIP}'")[0]
            except:
                sys.exit()
            cmd = action +" root@"+hostIP
        else:
            cmd = "kubectl -n "+ns+" exec -it "+res+" -- sh"
    return cmd,obj,name

def find_ip(res: str):
    ip_regex = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
    ips = re.findall(ip_regex, res)
    return ips[0] if ips else ""

def find_optimal(namespace_list: list, namespace: str):

    namespace_list.sort()
    has_namespace = [namespace in row for row in namespace_list]
    index_scores = [row.index(namespace) * 0.8 if has_namespace[i] else 10000 for i, row in enumerate(namespace_list)]
    contain_scores = [len(row.replace(namespace, '')) * 0.42 for row in namespace_list]
    result_scores = [(index_scores[i] + container) * (1 if has_namespace[i] else 1.62) for i, container in enumerate(contain_scores)]
    return namespace_list[result_scores.index(min(result_scores))] if len(set(index_scores)) != 1 else ( namespace_list[has_namespace.index(True)] if True in has_namespace else None )

def find_config():
    os.path.exists(history) or os.mkdir(history)
    cmd = '''find $HOME/.kube -maxdepth 2 -type f -name 'kubeconfig*' 2>/dev/null|egrep '.*' || ( find $HOME/.kube -maxdepth 1 -type f 2>/dev/null|egrep '.*' &>/dev/null && grep -l "current-context" `find $HOME/.kube -maxdepth 1 -type f` )'''
    result_set = { e.split('\n')[0] for e in get_data(cmd) }
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
        global header_config
        dc = {}
        if os.path.exists(ki_dict) and os.path.getsize(ki_dict) > 5:
            with open(ki_dict,'r') as f:
                try:
                    dc = eval(f.read())
                    for config in list(dc.keys()):
                        if not os.path.exists(config):
                            del dc[config]
                except:
                    os.unlink(ki_dict)
        if os.path.exists(ki_last) and os.path.getsize(ki_last) > 0:
            with open(ki_last,'r') as f:
                last_config = f.read()
                if not os.path.exists(last_config):
                    last_config = result_lines[0]
        else:
            last_config = result_lines[0]
        result_dict = sorted(dc.items(),key = lambda dc:(dc[1], dc[0]),reverse=True)
        sort_list = [ i[0] for i in result_dict ]
        header_config = sort_list[0] if sort_list else os.path.realpath(default_config)
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
    return [kubeconfig,result_lines,result_num]

def compress_list(l: list):
    if len(l) > 3:
        num = 15
        i = 0
        while i + 2 < len(l):
            if l[i+1] - l[i] > num and l[i] > 0 and l[i+2] > 1:
                l[i] -= 1
                l[i+1] = min(l[i] + num, l[i+1])
                l[i+2] -= 2
            else:
                i += 1
        if l[-1] - l[-2] < num + 1:
            return l
        else:
            l[0] = 1
            l[-1] = l[-2] + 1
            return compress_list(l)
    else:
        return l

def find_history(config,num=1):
    if config != header_config:
        dc = {}
        if os.path.exists(ki_dict) and os.path.getsize(ki_dict) > 5:
            with open(ki_dict,'r') as f:
                dc = eval(f.read())
                dc[config] = dc[config] + num if config in dc else 1
                dc.pop(default_config,None)
                for config in list(dc.keys()):
                    if not os.path.exists(config): del dc[config]
        else:
            dc[config] = 1
        result_dict = sorted(dc.items(),key = lambda dc:dc[1])
        for i,j in zip(result_dict,compress_list([ i[1] for i in result_dict ])):
            dc[i[0]] = j
        with open(ki_dict,'w') as f: f.write(str(dc))
def find_ns(config_struct: list):
    ns = None
    kubeconfig = None
    switch = False
    ns_dict = ki_ns_dict
    result_num = config_struct[-1]
    kn = re.split("[./]",sys.argv[2])
    ns_pattern = kn[-1] if len(kn) > 1 and len(kn[-1].strip()) > 0 else kn[0]

    if os.path.exists(ki_current_ns_dict) and int(time.time()-os.stat(ki_current_ns_dict).st_mtime) < 300:
        with open(ki_current_ns_dict) as f:
            try:
                d = eval(f.read())
                current_config = os.path.realpath(default_config)
                if current_config in d:
                    ns_list = d[current_config]
                    if find_optimal(ns_list,ns_pattern):
                        ns_dict = ki_current_ns_dict
                        config_struct[1] = [current_config]
            except:
                os.path.exists(ki_cache) and os.unlink(ki_cache)
                ns_list = cache_ns(config_struct)[config]

    config = find_optimal(config_struct[1],kn[0]) or default_config if len(kn) > 1 else default_config

    if len(config_struct[1]) > 1:
        current_config = os.path.realpath(config)
        current_config in config_struct[1] and config_struct[1].remove(current_config)
        config_struct[1].insert(0,current_config)

    for n,config in enumerate(config_struct[1]):
        if os.path.exists(ns_dict):
            with open(ns_dict,'r') as f:
                try:
                    d = eval(f.read())
                    ns_list = d[config]
                except:
                    os.path.exists(ki_cache) and os.unlink(ki_cache)
                    ns_list = cache_ns(config_struct)[config]
        else:
            cmd = "kubectl get ns --no-headers --kubeconfig "+config
            ns_list = [ e.split()[0] for e in get_data(cmd) ]
        ns = find_optimal(ns_list,ns_pattern)
        if ns:
            kubeconfig = config
            break
    return ns,kubeconfig,switch,result_num
def cache_ns(config_struct: list):
    if not os.path.exists(ki_cache) or ( os.path.exists(ki_cache) and int(time.time()-os.stat(ki_cache).st_mtime) > 1800 ):
        open(ki_cache,"a").close()
        d = {}
        d_latest = {}

        current_d = {}
        current_config = os.path.realpath(default_config)
        cmd = "kubectl get ns --sort-by=.metadata.creationTimestamp --no-headers --kubeconfig " + current_config
        l = get_data(cmd)
        ns_list = [ e.split()[0] for e in l ]
        current_d[current_config] = ns_list
        with open(ki_current_ns_dict,'w') as f: f.write(str(current_d))

        for config in config_struct[1]:
            s = []
            cmd = "kubectl get ns --sort-by=.metadata.creationTimestamp --no-headers --kubeconfig "+config
            l = get_data(cmd)
            ns_list = [ e.split()[0] for e in l ]
            if os.path.exists(ki_all):
                s = ns_list
            else:
                for ns in ns_list:
                    cmd1 = "kubectl get pod --no-headers --kubeconfig "+config+" -n "+ns
                    cmd2 = "kubectl get cronjob --no-headers --kubeconfig "+config+" -n "+ns
                    if get_data(cmd1) or get_data(cmd2):
                        s.append(ns)
            d[config] = s
            d_latest[config] = l[-1].split()[0]
        with open(ki_ns_dict,'w') as f: f.write(str(d))
        with open(ki_latest_ns_dict,'w') as f: f.write(str(d_latest))
        os.path.exists(ki_cache) and os.unlink(ki_cache)
        return d
def switch_config(switch_num: int,k8s: str,ns: str,time: str):
    switch = False
    if os.path.exists(default_config) and os.environ['KUBECONFIG'] not in {default_config,os.path.realpath(default_config)}:
        if default_config != os.path.realpath(default_config):
            with open(ki_last,'w') as f: f.write(os.path.realpath(default_config))
        os.unlink(default_config)
        os.symlink(os.environ['KUBECONFIG'],default_config)
        print("\033[1;33m{}\033[0m".format("[ "+time+"  "+str(switch_num+1)+"-SWITCH  "+k8s+" / "+ns+" ] "))
        find_history(os.environ['KUBECONFIG'],1)
        switch_num > 0 and subprocess.Popen("ki --c",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
        switch = True
    return switch
def get_data(cmd: str):
    try:
        p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
        return p.stdout.readlines()
    except:
        sys.exit()
def get_obj(ns: str,res: str,args='x'):
    d = {'s':"Service",'i':"Ingress"}
    cmd = "kubectl -n "+ns+" get pod "+res+" -o jsonpath='{.metadata.ownerReferences[0].kind}'"
    l1 = res.split('-')
    l2 = get_data(cmd)
    obj = l2[0] if l2 else "Pod"
    if obj in ("ReplicaSet","Deployment"):
        if len(res) == 63:
            del l1[-1:]
        else:
            del l1[-2:]
        obj = "Deployment"
    elif obj in ("StatefulSet","DaemonSet"):
        del l1[-1:]
    elif obj in ("Job"):
        if '--' in res:
            del l1[-3:]
        else:
            del l1[-1:]
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
                if substr_hash not in disabled_hashes and min_length > (y - x + 1):
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
                config = find_optimal(result_lines,k8s_str) if k8s_str else None
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
        os.path.exists(ki_current_ns_dict) and int(time.time()-os.stat(ki_current_ns_dict).st_mtime) > 300 and os.unlink(ki_current_ns_dict)
def info_k():
    if os.path.exists(ki_pod_dict) and os.path.exists(ki_dict):
        with open(ki_pod_dict,'r') as f1, open(ki_dict,'r') as f2:
            dc1 = eval(f1.read())
            dc2 = eval(f2.read())
            for k in sorted(dc1):
                print("{:<56}{:<32}{}".format(k,dc1[k][0],dc1[k][1]))
            for k in sorted(dc2.items(),key=lambda d:d[1]):
                print("{:<56}{}".format(k[0].split('/')[-1],k[1]))
def record(res: str,name: str,obj: str,cmd: str,kubeconfig: str,ns: str,config_struct: list):
    l = os.environ['SSH_CONNECTION'].split() if 'SSH_CONNECTION' in os.environ else ['NULL','NULL','NULL']
    USER = os.environ['USER'] if 'USER' in os.environ else "NULL"
    HOST = l[2]
    FROM = l[0]
    key = kubeconfig+"/"+ns+"/"+("Pod" if obj in ('Deployment','StatefulSet','DaemonSet','ReplicaSet') else obj)
    ki_file = time.strftime("%F",time.localtime())
    with open(history+"/"+ki_file,'a+') as f: f.write( time.strftime("%F %T ",time.localtime())+"[ "+USER+"@"+HOST+" from "+FROM+" ---> "+kubeconfig+" ]  " + cmd + "\n" )
    dc = {}
    if os.path.exists(ki_pod_dict) and os.path.getsize(ki_pod_dict) > 5:
        with open(ki_pod_dict,'r') as f:
            try:
                dc = eval(f.read())
                dc_key_set = set(i.split('/')[0] for i in list(dc.keys()))
                kubeconfig_set = set(i.split('/')[-1] for i in config_struct[1])
                for i in dc_key_set - kubeconfig_set:
                    for j in dc.keys():
                        if i == j.split('/')[0]:
                            dc.pop(j,None)
                name_dc = dict(dc[key][1]) if key in dc else {}
                name_dc[name] = name_dc[name] + 1 if name in name_dc else 1
                name_dc = sorted(name_dc.items(),key = lambda name_dc:(name_dc[1], name_dc[0]),reverse=True)
                if len(name_dc) > 5: del name_dc[5:]
                dc[key] = [name,name_dc]
            except:
                os.unlink(ki_pod_dict)
    else:
        dc[key] = [name,[(name,1)]]
    with open(ki_pod_dict,'w') as f: f.write(str(dc))
def ki():
    ( len(sys.argv) == 1 or sys.argv[1] not in ('-n','-t','-t1','-t2','-r','-i','-e','-es','-ei','-o','-os','-oi','-restart','-s','--s','-l','--l','--lock','--u','--unlock','--w','--watch','--h','--help','--c','--cache','--k','-a','--a') ) and sys.argv.insert(1,'-n')
    len(sys.argv) == 2 and sys.argv[1] in ('-i','-e','-es','-ei','-o','-os','-oi') and sys.argv.insert(1,'-n')
    len(sys.argv) == 2 and sys.argv[1] in ('-a','--a') and sys.argv.extend(['kube','Pod'])
    len(sys.argv) == 3 and sys.argv[1] in ('-a','--a') and sys.argv.insert(2,'kube')
    config_struct = find_config()
    if len(sys.argv) == 2 and sys.argv[1] in ('--w','--watch'):
        info_w(os.environ["PWD"],config_struct[1])
    elif len(sys.argv) == 2 and sys.argv[1] in ('--l','--lock'):
        os.path.exists(ki_unlock) and os.unlink(ki_unlock)
        os.path.exists(ki_lock) or open(ki_lock,"a").close()
    elif len(sys.argv) == 2 and sys.argv[1] in ('--u','--unlock'):
        os.path.exists(ki_unlock) or open(ki_unlock,"a").close()
        os.path.exists(ki_lock) and os.unlink(ki_lock)
    elif len(sys.argv) == 2 and sys.argv[1] == '-n':
        cmd = "kubectl get ns  --sort-by=.metadata.creationTimestamp --no-headers"
        print("\033[1;32m{}\033[0m".format(cmd.split('  --')[0]))
        os.environ['KUBECONFIG'] = os.path.realpath(default_config)
        l = get_data(cmd)
        ns_dict = get_feature([ e.split()[0] for e in l ])
        for e in l:
            s = ns_dict[e.split()[0]]
            num = e.find(s)
            num_s = num+len(s)
            print("{}\033[1;35m{}\033[0m{}".format(e[:num],e[num:num_s],e[num_s:]),end='')
        if os.path.exists(ki_latest_ns_dict):
            with open(ki_latest_ns_dict,'r') as f:
                try:
                    d = eval(f.read())
                    latest_ns = d[os.environ['KUBECONFIG']]
                    flag = ( latest_ns == l[-1].split()[0] )
                except:
                    flag = False
        else:
            flag = False
        flag or subprocess.Popen("ki --c",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    elif len(sys.argv) == 2 and sys.argv[1] in ('--k'):
        info_k()
    elif len(sys.argv) == 2 and sys.argv[1] in ('--c','--cache'):
        begin = time.perf_counter()
        cache_ns(config_struct)
        end = time.perf_counter()
        print("\033[1;33m{}\033[0m".format("[ "+str(round(end-begin,3))+" ] "))
    elif 1 < len(sys.argv) < 4 and sys.argv[1] in ('-s','--s'):
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
                    os.unlink(e)
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
                            if res:
                                if res not in {default_config,os.path.realpath(default_config)}:
                                    os.unlink(default_config)
                                    os.symlink(res,default_config)
                                    print('\033[{}C\033[1A'.format(10),end = '')
                                    print("\033[1;33m{}\033[0m".format(res.split('/')[-1]))
                                    find_history(res,6)
                                    os.path.exists(ki_unlock) or open(ki_lock,"a").close()
                                break
                        else:
                            pattern = ""
                else:
                    print("\033[1;32m{}\033[0m\033[5;32m{}\033[0m".format("File not found ",default_config))
    elif 2 < len(sys.argv) < 5 and sys.argv[1] in ('-n','-r','-t','-t1','-t2','-i','-l','-e','-es','-ei','-o','-os','-oi','-a','--a'):
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
                d = {'d':['Deployment'," -o wide"],'s':['Service'," -o wide"],'i':['Ingress'," -o wide"],'c':['ConfigMap'," -o wide"],'t':['Secret'," -o wide"],'n':['Node'," -o wide"],'p':['PersistentVolumeClaim'," -o wide"],'v':['PersistentVolume'," -o wide"],'f':['StatefulSet'," -o wide"],'j':['CronJob'," -o wide"],'b':['Job'," -o wide"],'P':['Pod'," -o wide"],'e':['Event',''],'r':['ReplicaSet',''],'a':['DaemonSet',''],'q':['ResourceQuota',''],'V':['VirtualService',""],'G':['Gateway',''],'E':['EnvoyFilter',''],'D':['DestinationRule','']}
                obj = d[sys.argv[3][0]][0] if sys.argv[3][0] in d else "Pod"
                ext = d[sys.argv[3][0]][1] if sys.argv[3][0] in d else ""
                if sys.argv[1] in ('-i','-l','-e','-es','-ei','-o','-os','-oi'):
                    begin = time.perf_counter()
                    while True:
                        if ns:
                            cmd = "kubectl get pod --no-headers --field-selector=status.phase=Running -n "+ns
                            pods = [ e.split()[0] for e in get_data(cmd) ]
                            pod = find_optimal(pods,sys.argv[3]) if pods else None
                            if not (pods and pod):
                                kn = re.split("[./]",sys.argv[2])
                                ns_pattern = kn[-1] if len(kn) > 1 and len(kn[-1].strip()) > 0 else kn[0]
                                os.environ['KUBECONFIG'] in config_struct[1] and config_struct[1].remove(os.environ['KUBECONFIG'])
                                if config_struct[1]:
                                    for n,config in enumerate(config_struct[1]):
                                        cmd = "kubectl get ns --no-headers --kubeconfig "+config
                                        ns_list = [ e.split()[0] for e in get_data(cmd) ]
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
                                switch_config(switch_num,k8s,ns,str(round(end-begin,3)))
                                name = pod
                                if sys.argv[1] in ('-i'):
                                    cmd = "kubectl -n "+ns+" exec -it "+pod+" -- sh"
                                elif sys.argv[1] in ('-l'):
                                    line = os.environ['KI_LINE'] if 'KI_LINE' in os.environ else str(1000)
                                    cmd = "kubectl -n "+ns+" logs -f "+pod+" --all-containers --tail "+line
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
                                record(pod,name,obj,cmd,k8s,ns,config_struct)
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
                        elif sys.argv[1] in ('-a','--a'):
                            cmd = "kubectl"+" get "+obj.lower()+ext+" -A  --sort-by=.metadata.creationTimestamp --no-headers"
                        else:
                            key = sys.argv[1].split('t')[-1] if sys.argv[1].split('t')[-1].isdigit() else "3"
                            cmd = "kubectl top "+obj.lower()+" -n "+ ns +"  --no-headers|sort --key "+key+" --numeric"
                        result_lines = get_data(cmd)
                        if not result_lines:
                            kn = re.split("[./]",sys.argv[2])
                            ns_pattern = kn[-1] if len(kn) > 1 and len(kn[-1].strip()) > 0 else kn[0]
                            os.environ['KUBECONFIG'] in config_struct[1] and config_struct[1].remove(os.environ['KUBECONFIG'])
                            if config_struct[1]:
                                for n,config in enumerate(config_struct[1]):
                                    cmd = "kubectl get ns --no-headers --kubeconfig "+config
                                    ns_list = [ e.split()[0] for e in get_data(cmd) ]
                                    ns = find_optimal(ns_list,ns_pattern)
                                    if ns:
                                        os.environ['KUBECONFIG'] = config
                                        switch_num += 1
                                        break
                            else:
                                print("No resources found.")
                                break
                        else:
                            if flag:
                                end = time.perf_counter()
                                k8s = os.environ['KUBECONFIG'].split('/')[-1]
                                switch = switch_config(switch_num,k8s,ns,str(round(end-begin,3)))
                                flag = False
                            print("\033[1;32m{}\033[0m".format(cmd.split(' --')[0]))
                    if not (pod.isdigit() and int(pod) < len(result_lines)) and pod != '*':
                        result_lines = list(filter(lambda x: x.find(pod) >= 0, result_lines))
                    if result_lines:
                        now = time.strftime("%T",time.localtime())
                        for n,e in enumerate(result_lines):
                            try:
                                print("\033[1;32m{}\033[0m {}".format(n,e.strip()))
                            except:
                                pass
                        if n > 3:
                            style = "\033[1;33m{}\033[0m" if switch else "\033[1;32m{}\033[0m"
                            string = "[ "+k8s+" / "+ns+" --- "+obj+" ] [ "+now+" ]" if sys.argv[1] not in ('-a','--a') and obj not in ('PersistentVolume') else "[ "+k8s+" --- "+obj+" ] [ "+now+" ]"
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
                                result_lines = get_data(cmd)
                                time.sleep(3)
                        except:
                            sys.exit()
                        result_len = len(result_lines)
                        podList = pod.split()
                        pod = podList[0] if podList else ""
                        if pod in ('$','#','@','!','~'):
                            if pod == '$':
                                pod = str(result_len-1)
                            elif os.path.exists(ki_pod_dict):
                                with open(ki_pod_dict,'r') as f:
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
                            res = result_lines[index].split()[0 if sys.argv[1] not in ('-a','--a') else (1 if obj not in ("PersistentVolume") else 0)]
                            iip = result_lines[index].split()[5] if len(result_lines[index].split()) > 5 else find_ip(res)
                            ns = result_lines[index].split()[0] if sys.argv[1] in ('-a','--a') else ns
                            l = cmd_obj(ns,obj,res,args,iip)
                            print('\033[{}C\033[1A'.format(num),end = '')
                            print("\033[1;32m{}\033[0m".format(l[0].split('  --')[0]))
                            record(res,l[2],l[1],l[0],k8s,ns,config_struct)
                            os.system(l[0])
                            print('\r')
                    else:
                        pod = ""
                else:
                    print("No resources found.")
                    subprocess.Popen("ki --c",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
                    sys.exit()
        else:
            print("No namespace found in the kubernetes.")
            subprocess.Popen("ki --c",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    elif len(sys.argv) == 2 and sys.argv[1] in ('--h','--help'):
        style = "\033[1;32m%s\033[0m"
        print(style % "Kubectl pro controls the Kubernetes cluster manager,find more information at: https://ki.xabc.io\n")
        doc_dict = {
         "1. ki":"List all namespaces",
         "2. ki xx":"List all pods in the namespace ( if there are multiple ~/.kube/kubeconfig*,the best matching kubeconfig will be found ,the namespace parameter supports fuzzy matching,after outputting the pod list, select: xxx filters the query\n         select: index l ( [ l ] Print the logs for a container in a pod or specified resource \n         select: index l 100 ( Print the logs of the latest 100 lines \n         select: index l xxx ( Print the logs and filters the specified characters \n         select: index r ( [ r ] Rollout restart the pod \n         select: index o ( [ o ] Output the [Deployment,StatefulSet,Service,Ingress,Configmap,Secret].yml file \n         select: index del ( [ del ] Delete the pod \n         select: index cle ( [ cle ] Delete the Deployment/StatefulSet \n         select: index e[siVGDE] ( [ e[siVGDE] ] Edit the Deploy/Service/Ingress/VirtualService/Gateway/DestinationRule/EnvoyFilter \n         select: index s5 ( [ s3 ] Set the Deploy/StatefulSet replicas=3 \n         select: index dp ( Describe a pod \n         select: * ( Watching... ",
         "3. ki xx d":"List the Deployment of a namespace",
         "4. ki xx f":"List the StatefulSet of a namespace",
         "5. ki xx s":"List the Service of a namespace",
         "6. ki xx i":"List the Ingress of a namespace",
         "7. ki xx t":"List the Secret of a namespace",
         "8. ki xx a":"List the DaemonSet of a namespace",
         "9. ki xx j":"List the CronJob of a namespace",
         "10. ki xx v":"List the PersistentVolume of a namespace",
         "11. ki xx p":"List the PersistentVolumeClaim of a namespace",
         "12. ki xx q":"List the ResourceQuota of a namespace",
         "13. ki xx V":"List the VirtualService of a namespace",
         "14. ki xx G":"List the Gateway of a namespace",
         "15. ki xx D":"List the DestinationRule of a namespace",
         "16. ki xx E":"List the EnvoyFilter of a namespace",
         "17. ki -i $ns $pod":"Login in the container,this way can be one-stop",
         "18. ki -l $ns $pod":"Print the logs for a container,this way can be one-stop",
         "19. ki -e[si] $ns $pod":"Edit the Deploy/Service/Ingress for a container,this way can be one-stop",
         "20. ki $k8s.$ns":"Select the kubernetes which namespace in the kubernetes ( if there are multiple ~/.kube/kubeconfig*,this way can be one-stop. ",
         "21. ki --s":"Select the kubernetes to be connected ( if there are multiple ~/.kube/kubeconfig*,the kubeconfig storage can be kubeconfig-hz,kubeconfig-sh,etc. ",
         "22. ki --c":"Enable write caching of namespace ( ~/.history/.ns_dict ",
         "23. ki --a":"List all pods in the kubernetes"}
        for k,v in doc_dict.items():
            print(style % k,v)
def main():
    ki()
#-----------------PROG----------------------------
if __name__ == '__main__':
    main()
