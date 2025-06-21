#!/usr/bin/python3
#*************************************************
# Description : Kubectl Pro
# Version     : 6.5
#*************************************************
from collections import deque
import os,re,sys,time,readline,subprocess
#-----------------VAR-----------------------------
home = os.environ["HOME"]
history = home + "/.history"
ki_cool = history + "/.cool"
ki_cache = history + "/.cache"
ki_ns_dict = history + "/.ns_dict"
ki_pod_dict = history + "/.pod_dict"
ki_kube_dict = history + "/.kube_dict"
ki_latest_ns_dict = history + "/.latest_ns_dict"
ki_current_ns_dict = history + "/.current_ns_dict"
ki_last = history + "/.last"
ki_line = history + "/.line"
ki_lock = history + "/.lock"
ki_unlock = history + "/.unlock"
default_config = home + "/.kube/config"
KI_AI_URL = os.getenv("KI_AI_URL", "https://api.deepseek.com/v1/chat/completions")
KI_AI_KEY = os.getenv("KI_AI_KEY", "")
KI_AI_MODEL = os.getenv("KI_AI_MODEL", "deepseek-chat")
KUBECTL_OPTIONS = "--insecure-skip-tls-verify"
CACHE_DURATION = 8 * 60 * 60
#-----------------FUN-----------------------------
def cmp_file(f1, f2):
    if os.path.getsize(f1) != os.path.getsize(f2):
        return False
    bufsize = 8192
    with open(f1, 'rb') as fp1, open(f2, 'rb') as fp2:
        while True:
            b1 = fp1.read(bufsize)
            b2 = fp2.read(bufsize)
            if b1 != b2:
                return False
            if not b1 and not b2:
                return True

def confirm_action(caution):
    try:
        confirm = input(caution+", Confirm execution of high-risk operation? (yes/no): ")
        return confirm.lower() in ("yes","y")
    except:
        return False

def cmd_obj(ns, obj, res, args, iip="x"):
    name = res
    if obj in ("Node"):
        if args[0] in ('c','u'):
            action = "cordon" if args[0] == 'c' else "uncordon"
            cmd = f"kubectl {KUBECTL_OPTIONS} "+action+" "+res
        elif args[0] in ('d','e'):
            action = "describe" if args[0] == 'd' else "edit"
            cmd = f"kubectl {KUBECTL_OPTIONS} "+action+" "+obj.lower()+" "+res
        elif args[0] == 'o':
            action = "get"
            action2 = " -o yaml > "+res+"."+obj.lower()+".yml"
            cmd = f"kubectl {KUBECTL_OPTIONS} "+action+" "+obj.lower()+" "+res+action2
        else:
            action = "ssh"
            node_ip = get_data(f"kubectl {KUBECTL_OPTIONS} get node " + res + " -o jsonpath='{.status.addresses[?(@.type==\"InternalIP\")].address}'")[0]
            if find_ip(node_ip):
                cmd = action +" root@"+node_ip
            else:
                cmd = action +" root@"+iip
    elif obj in ("Event"):
        action = "get"
        cmd = f"kubectl {KUBECTL_OPTIONS} -n "+ns+" "+action+" "+obj+"  --sort-by=.metadata.creationTimestamp"
    elif obj in ("Deployment","DaemonSet","Service","StatefulSet","Ingress","ConfigMap","Secret","PersistentVolume","PersistentVolumeClaim","CronJob","Job","VirtualService","Gateway","HTTPRoute","DestinationRule","EnvoyFilter", "all"):
        action2 = ""
        actual_obj = obj
        actual_res = res
        if obj == "all" and "/" in res:
            parts = res.split("/", 1)
            if len(parts) == 2:
                actual_obj = parts[0].capitalize()
                actual_res = parts[1]

        if args in ("cle","delete"):
            if confirm_action("This command will delete the "+actual_obj):
                action = "delete"
            else:
                print("Operation canceled.")
                return
        elif args[0] == "e":
            action = "edit"
        elif args[0] == "d":
            action = "describe"
        elif args[0] == 'o':
            action = "get"
            action2 = " -o yaml > "+actual_res+"."+actual_obj.lower()+".yml"
        else:
            action = "get"
            actual_obj = obj
            actual_res = res

        if obj == "all" and args[0] in ('e', 'd', 'o'):
            cmd = f"kubectl {KUBECTL_OPTIONS} -n {ns} {action} {actual_obj.lower()} {actual_res}{action2}"
        else:
            cmd = f"kubectl {KUBECTL_OPTIONS} -n {ns} {action} {actual_obj.lower()} {actual_res}{action2}" if actual_obj not in ("PersistentVolume") else f"kubectl {KUBECTL_OPTIONS} {action} {actual_obj.lower()} {actual_res}{action2}"

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
            if confirm_action("This command will delete the "+obj):
                action = "delete"
            else:
                print("Operation canceled.")
                return
        else:
            action = "get"
        cmd = f"kubectl {KUBECTL_OPTIONS} -n "+ns+" "+action+" "+obj.lower()+" "+res+action2
    else:
        l = get_obj(ns,res)
        obj = l[0]
        name = l[1]
        d = {'d':'Deployment','s':'Service','i':'Ingress','f':'StatefulSet','a':'DaemonSet','p':'Pod','g':'Gateway','h':'HTTPRoute','A':'all','V':'VirtualService','D':'DestinationRule','E':'EnvoyFilter'}
        if args == "p":
            cmd = f"kubectl {KUBECTL_OPTIONS} -n "+ns+" exec -it "+res+" -- sh"
        elif args == "del":
            cmd = f"kubectl {KUBECTL_OPTIONS} -n "+ns+" delete pod "+res+" --wait=false"
        elif args == "delf":
            action = "delete"
            cmd = f"kubectl {KUBECTL_OPTIONS} -n "+ns+" delete pod "+res+" --grace-period=0 --force"
        elif args in ("cle","delete"):
            if confirm_action("This command will delete the deployment associated with the pod"):
                action = "delete"
                cmd = f"kubectl {KUBECTL_OPTIONS} -n "+ns+" "+action+" "+obj.lower()+" "+name
            else:
                print("Operation canceled.")
                return
        elif args in ("destroy","destory"):
            if confirm_action("Delete associated Deployment, Service, and Ingress resources for the Pod"):
                action = "delete"
                cmd = f"kubectl {KUBECTL_OPTIONS} -n "+ns+" "+action+" "+obj.lower()+",service,ingress "+name
            else:
                print("Operation canceled.")
                return
        elif args[0] in ('l', 'c', 'g'):
            search_term = args[1:].strip()
            try:
                result_list = get_data(f"kubectl {KUBECTL_OPTIONS} -n "+ns+" get pod "+res+" -o jsonpath='{.spec.containers[:].name}'")[0].split()
            except:
                sys.exit()
            container = "--all-containers --max-log-requests=28"
            if search_term:
                if search_term.isdigit():
                    if 0 < int(search_term) < 10000:
                        os.environ['KI_LINE'] = search_term
                        with open(ki_line,'w') as f:
                            f.write(search_term)
                if search_term.isdigit() and len(search_term) < 12:
                    cmd = f"kubectl {KUBECTL_OPTIONS} -n {ns} logs -f {res} {container} --tail {search_term}"
                else:
                    if args[0] == 'l':
                        cmd = f"kubectl {KUBECTL_OPTIONS} -n {ns} logs -f --tail 1024 {res} {container} | grep -a --color=auto '{search_term}'"
                    else:
                        grep_option = "" if args[0] == 'g' else "-C 10"
                        cmd = f"kubectl {KUBECTL_OPTIONS} -n {ns} logs -f {res} {container} | grep -a --color=auto {grep_option} '{search_term}'"
            else:
                if 'KI_LINE' in os.environ:
                    line = os.environ['KI_LINE']
                elif os.path.exists(ki_line):
                    with open(ki_line,'r') as f:
                        line_file = str(f.read())
                        os.environ['KI_LINE'] = line_file if line_file.isdigit() and int(line_file) < 4096 else str(200)
                        line = os.environ['KI_LINE']
                else:
                    line = str(200)
                cmd = f"kubectl {KUBECTL_OPTIONS} -n {ns} logs -f {res} {container} --tail {line}"
        elif args[0] in ('v'):
            regular = args[1:]
            try:
                result_list = get_data(f"kubectl {KUBECTL_OPTIONS} -n "+ns+" get pod "+res+" -o jsonpath='{.spec.containers[:].name}'")[0].split()
            except:
                sys.exit()
            container = name if name in result_list else "--all-containers"
            cmd = f"kubectl {KUBECTL_OPTIONS} -n "+ns+" logs -f "+res+" "+container+" --previous --tail "+ ( regular if regular and regular.isdigit() and len(regular) < 12 else "4096" )
        elif args[0] in ('r'):
            cmd = f"kubectl {KUBECTL_OPTIONS} -n "+ns+" rollout restart "+obj.lower()+" "+name
        elif args[0] in ('u'):
            cmd = f"kubectl {KUBECTL_OPTIONS} -n "+ns+" rollout undo "+obj.lower()+"/"+name
        elif args[0] in ('o'):
            action = "get"
            if len(args) > 1:
                obj = d.get(args[1],'Pod')
                if obj == 'Pod': name = res
            cmd = f"kubectl {KUBECTL_OPTIONS} -n "+ns+" "+action+" "+obj.lower()+" "+name+" -o yaml > "+name+"."+obj.lower()+".yml"
        elif args[0] in ('d','e'):
            action = "describe" if args[0] == 'd' else "edit"
            if len(args) > 1:
                obj = d.get(args[1],'Pod')
                if obj == 'Pod': name = res
            cmd = f"kubectl {KUBECTL_OPTIONS} -n "+ns+" "+action+" "+obj.lower()+" "+name
        elif args[0] in ('s'):
            if confirm_action("This command will scale the "+obj):
                regular = args.split('s')[-1]
                action = "scale"
                replicas = regular if regular.isdigit() and -1 < int(regular) < 30 else str(1)
                cmd = f"kubectl {KUBECTL_OPTIONS} -n "+ns+" "+action+" --replicas="+replicas+" "+obj.lower()+"/"+name
            else:
                print("Operation canceled.")
                return
        elif args[0] in ('n'):
            action = "ssh"
            try:
                hostIP = get_data(f"kubectl {KUBECTL_OPTIONS} -n "+ns+" get pod "+res+" -o jsonpath='{.status.hostIP}'")[0]
            except:
                sys.exit()
            cmd = action +" root@"+hostIP
        else:
            cmd = "kubectl {KUBECTL_OPTIONS} -n "+ns+" exec -it "+res+" -- sh"
    return cmd,obj,name

def find_ip(res: str):
    ip_regex = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
    ips = re.findall(ip_regex, res)
    return ips[0] if ips else ""

def find_optimal(namespace_list: list, namespace: str):
    namespace_list.sort()
    has_namespace = [namespace in row for row in namespace_list]
    index_scores = [row.index(namespace) * 0.618 if has_namespace[i] else 8192 for i, row in enumerate(namespace_list)]
    contain_scores = [len(row.replace(namespace, '')) * 0.618 for row in namespace_list]
    result_scores = [(index_scores[i] + container) * (1 if has_namespace[i] else 1.618) for i, container in enumerate(contain_scores)]
    if result_scores:
        return namespace_list[result_scores.index(min(result_scores))] if len(set(index_scores)) != 1 else ( namespace_list[has_namespace.index(True)] if True in has_namespace else None )
    else:
        return None

def find_config():
    global header_config
    os.path.exists(history) or os.mkdir(history)
    cmd = '''find $HOME/.kube -maxdepth 2 -type f -name 'kubeconfig*' -a ! -name 'kubeconfig-*-NULL' 2>/dev/null|egrep '.*' || ( find $HOME/.kube -maxdepth 1 -type f 2>/dev/null|egrep '.*' &>/dev/null && grep -l "current-context" `find $HOME/.kube -maxdepth 1 -type f` )'''
    result_set = { e.split('\n')[0] for e in get_data(cmd) }
    result_num = len(result_set)
    result_lines = list(result_set)
    kubeconfig = None
    if result_num == 1:
        if os.path.exists(default_config):
            if not os.path.islink(default_config):
                os.rename(default_config, home+"/.kube/config-0")
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
        header_config = os.path.realpath(default_config)
    elif result_num > 1:
        dc = {}
        if os.path.exists(ki_kube_dict) and os.path.getsize(ki_kube_dict) > 5:
            with open(ki_kube_dict,'r') as f:
                try:
                    dc = eval(f.read())
                    for config in list(dc.keys()):
                        if not os.path.exists(config):
                            del dc[config]
                except:
                    os.unlink(ki_kube_dict)
        if os.path.exists(ki_last) and os.path.getsize(ki_last) > 0:
            with open(ki_last,'r') as f:
                last_config = f.read()
                if not os.path.exists(last_config):
                    last_config = result_lines[0]
        else:
            last_config = result_lines[0]
        result_dict = sorted(dc.items(),key = lambda dc:(dc[1], dc[0]),reverse=True)
        sort_list = deque([ i[0] for i in result_dict ])
        header_config = sort_list[0] if sort_list else os.path.realpath(default_config)
        last_config in sort_list and sort_list.remove(last_config)
        sort_list.appendleft(last_config)
        result_lines = list(sort_list) + list(result_set - set(sort_list))
        if os.path.exists(default_config):
            if not os.path.islink(default_config):
                os.rename(default_config, home+"/.kube/config-0")
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
    else:
        header_config = os.path.realpath(default_config)
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

def find_history(config,num=3):
    if config != header_config:
        dc = {}
        if os.path.exists(ki_kube_dict) and os.path.getsize(ki_kube_dict) > 5:
            with open(ki_kube_dict,'r') as f:
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
        with open(ki_kube_dict,'w') as f: f.write(str(dc))

def get_config(config_lines: list, ns: str):
    history_lines = []
    dc = {}
    if os.path.exists(ki_kube_dict):
        with open(ki_kube_dict, 'r') as f:
            dc = eval(f.read())
            dc.pop(os.path.realpath(default_config), None)
            history_lines = [k[0] for k in sorted(dc.items(), key=lambda d: d[1], reverse=True)]

    config_lines.remove(os.path.realpath(default_config))
    matching_configs = [config for config in config_lines if ns in config]

    if not matching_configs:
        return default_config

    def score_config(config):
        base_score = dc.get(config, 0)
        match_score = len(set(config.lower()) & set(ns.lower())) / len(set(ns.lower()))
        history_score = len(history_lines) - history_lines.index(config) if config in history_lines else 0
        total_score = base_score * 0.5 + match_score * 0.3 + history_score * 0.2
        return total_score

    scored_configs = [(config, score_config(config)) for config in matching_configs]
    scored_configs.sort(key=lambda x: x[1], reverse=True)
    return scored_configs[0][0]

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

    config = get_config(config_struct[1], kn[0]) or default_config if len(kn) > 1 else default_config

    if len(config_struct[1]) > 1:
        current_config = os.path.realpath(config)
        config_struct[1] = deque(config_struct[1])
        current_config in config_struct[1] and config_struct[1].remove(current_config)
        config_struct[1].appendleft(current_config)

    for n,config in enumerate(config_struct[1]):
        if os.path.exists(ns_dict):
            with open(ns_dict,'r') as f:
                try:
                    d = eval(f.read())
                    ns_list = d.get(config, [])
                except:
                    os.path.exists(ki_cache) and os.unlink(ki_cache)
                    cache_data = cache_ns(config_struct)
                    ns_list = cache_data.get(config, [])
        else:
            cmd = f"kubectl {KUBECTL_OPTIONS} get ns --no-headers --kubeconfig "+config
            ns_list = [ e.split()[0] for e in get_data(cmd) ]
        ns = find_optimal(ns_list,ns_pattern)
        if ns:
            kubeconfig = config
            break
    return ns,kubeconfig,switch,result_num

def cache_ns(config_struct: list):
    from concurrent.futures import ThreadPoolExecutor, as_completed

    if os.path.exists(ki_cool) and int(time.time() - os.stat(ki_cool).st_mtime) < CACHE_DURATION:
        if os.path.exists(ki_ns_dict):
            try:
                with open(ki_ns_dict, 'r') as f:
                    return eval(f.read())
            except:
                pass
    open(ki_cool, "w").close()

    print("\033[93mBuilding cache, please wait about 30s...\033[0m")
    if not os.path.exists(ki_cache) or (os.path.exists(ki_cache) and int(time.time()-os.stat(ki_cache).st_mtime) > CACHE_DURATION):
        open(ki_cache,"a").close()
        d = {}
        d_latest = {}
        current_d = {}
        current_config = os.path.realpath(default_config)

        cmd = f"kubectl {KUBECTL_OPTIONS} get ns --sort-by=.metadata.creationTimestamp --no-headers --kubeconfig " + current_config
        l = get_data(cmd)
        ns_list = [e.split()[0] for e in l]
        current_d[current_config] = ns_list
        with open(ki_current_ns_dict,'w') as f: f.write(str(current_d))

        def check_ns(config, ns):
            cmd = f"kubectl {KUBECTL_OPTIONS} get pod,cronjob --no-headers --kubeconfig {config} -n {ns}"
            return bool(get_data(cmd))

        def process_config(config):
            cmd = f"kubectl {KUBECTL_OPTIONS} get ns --sort-by=.metadata.creationTimestamp --no-headers --kubeconfig " + config
            retry_count = 0
            max_retries = 2
            while retry_count < max_retries:
                l = get_data(cmd)
                if l:
                    ns_list = [e.split()[0] for e in l]
                    latest_ns = l[-1].split()[0] if l else ""

                    valid_ns = []
                    with ThreadPoolExecutor(max_workers=min(10, len(ns_list))) as inner_executor:
                        futures = {inner_executor.submit(check_ns, config, ns): ns for ns in ns_list}
                        for future in as_completed(futures):
                            if future.result():
                                valid_ns.append(futures[future])
                    return config, valid_ns, latest_ns
                else:
                    retry_count += 1
                    if retry_count == max_retries:
                        os.path.exists(config) and os.rename(config, config + "-NULL")
                        return config, [], ""
            return config, [], ""

        valid_configs = [cfg for cfg in config_struct[1] if os.path.exists(cfg)]
        with ThreadPoolExecutor(max_workers=min(10, len(valid_configs))) as executor:
            futures = [executor.submit(process_config, config) for config in valid_configs]
            for future in as_completed(futures):
                config, s, latest = future.result()
                d[config] = s
                if s:
                    d_latest[config] = latest

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
        print("\033[1;93m{}\033[0m".format("[ "+time+"  "+str(switch_num+1)+"-SWITCH ---> "+k8s+" / "+ns+" ] "))
        find_history(os.environ['KUBECONFIG'],8)
        switch_num > 0 and subprocess.Popen("ki --c",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
        switch = True
    return switch

def get_data(cmd: str):
    try:
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        return p.stdout.readlines()
    except:
        sys.exit()

def get_obj(ns: str,res: str,args='x'):
    d = {'s':"Service",'i':"Ingress"}
    cmd = f"kubectl {KUBECTL_OPTIONS} -n "+ns+" get pod "+res+" -o jsonpath='{.metadata.ownerReferences[0].kind}'"
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
                    print("\033[1;95m{}\033[0m".format("[ "+config.split("/")[-1]+" ]"))
                else:
                    print("\033[1;38;5;208m{}\033[0m".format("[ "+os.path.realpath(default_config).split("/")[-1]+" ]"))
        else:
            print("\033[1;38;5;208m{}\033[0m".format("[ "+os.path.realpath(default_config).split("/")[-1]+(" (lock)" if os.path.exists(ki_lock) else "")+" ]"))
    else:
        print("\033[1;32m{}\033[0m".format("[ "+os.path.realpath(default_config).split("/")[-1]+" ]"))
        os.path.exists(ki_lock) and int(time.time()-os.stat(ki_lock).st_mtime) > 3600 and os.unlink(ki_lock)
        os.path.exists(ki_current_ns_dict) and int(time.time()-os.stat(ki_current_ns_dict).st_mtime) > 300 and os.unlink(ki_current_ns_dict)
def info_k():
    if os.path.exists(ki_pod_dict) and os.path.exists(ki_kube_dict):
        with open(ki_pod_dict,'r') as f1, open(ki_kube_dict,'r') as f2:
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

def analyze_cluster():
    """分析集群状态并生成报告"""
    import json
    import requests
    from datetime import datetime

    print("\033[1;93m正在分析集群状态...\033[0m")

    # 收集集群信息
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cluster_info": {},
        "node_status": [],
        "pod_status": {},
        "resource_usage": {},
        "events": []
    }

    try:
        # 获取集群版本信息
        try:
            version_output = get_data(f"kubectl {KUBECTL_OPTIONS} version -o json")
            if version_output:
                version_json = version_output[0].strip()
                data["cluster_info"]["version"] = json.loads(version_json)
        except:
            data["cluster_info"]["version"] = "无法获取版本信息"

        # 获取节点状态
        nodes = get_data(f"kubectl {KUBECTL_OPTIONS} get nodes -o wide")
        if len(nodes) > 1:  # 跳过标题行
            for node in nodes[1:]:
                node_info = node.split()
                if len(node_info) >= 5:
                    data["node_status"].append({
                        "name": node_info[0],
                        "status": node_info[1],
                        "roles": node_info[2] if len(node_info) > 2 else "unknown",
                        "version": node_info[3] if len(node_info) > 3 else "unknown",
                        "internal_ip": node_info[5] if len(node_info) > 5 else "unknown"
                    })

        # 获取所有命名空间的 Pod 状态
        ns_list = get_data(f"kubectl {KUBECTL_OPTIONS} get ns --no-headers")
        for ns in ns_list:
            ns_name = ns.split()[0]
            pods = get_data(f"kubectl {KUBECTL_OPTIONS} get pods -n {ns_name} --no-headers")
            running = 0
            failed = 0
            pending = 0
            for pod in pods:
                status = pod.split()[2]
                if status == "Running":
                    running += 1
                elif status in ["Failed", "Error", "CrashLoopBackOff"]:
                    failed += 1
                elif status == "Pending":
                    pending += 1

            data["pod_status"][ns_name] = {
                "total": len(pods),
                "running": running,
                "failed": failed,
                "pending": pending
            }

        # 获取资源使用情况
        for node in data["node_status"]:
            try:
                usage = get_data(f"kubectl {KUBECTL_OPTIONS} top node {node['name']}")
                if len(usage) > 1:  # 跳过标题行
                    usage_info = usage[1].split()
                    if len(usage_info) >= 5:
                        data["resource_usage"][node["name"]] = {
                            "cpu": usage_info[2],
                            "memory": usage_info[4]
                        }
            except:
                continue

        # 获取最近事件
        events = get_data(f"kubectl {KUBECTL_OPTIONS} get events --sort-by=.metadata.creationTimestamp")
        if events:
            data["events"] = [event.strip() for event in events[-5:]]  # 最近5个事件

        # 调用 AI API 分析数据
        if not KI_AI_KEY:
            raise Exception("请设置 KI_AI_KEY 环境变量")

        # 准备发送给 AI 的提示信息
        prompt = f"""请作为 Kubernetes 专家分析以下集群数据并生成简明扼要的健康状态报告:

集群信息:
- 时间戳: {data['timestamp']}
- 节点数量: {len(data['node_status'])}
- 命名空间数量: {len(data['pod_status'])}

节点状态:
{json.dumps(data['node_status'], indent=2, ensure_ascii=False)}

Pod 状态 (按命名空间):
{json.dumps(data['pod_status'], indent=2, ensure_ascii=False)}

资源使用情况:
{json.dumps(data['resource_usage'], indent=2, ensure_ascii=False)}

最近事件:
{json.dumps(data['events'], indent=2, ensure_ascii=False)}

请提供:
1. 集群整体健康状况评估
2. 发现的潜在问题
3. 资源使用建议
4. 优化建议
"""

        response = requests.post(
            f"{KI_AI_URL}",
            headers={
                "Authorization": f"Bearer {KI_AI_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": KI_AI_MODEL,
                "messages": [{
                    "role": "system",
                    "content": "你是一个经验丰富的 Kubernetes 集群分析专家。请基于提供的数据生成专业的分析报告。"
                }, {
                    "role": "user",
                    "content": prompt
                }],
                "temperature": 0.3
            }
        )

        if response.status_code == 200:
            result = response.json()
            print("\n\033[1;32m集群健康状态报告:\033[0m")
            print(result["choices"][0]["message"]["content"])
        else:
            print(f"\033[1;31mAI API 调用失败: {response.status_code}\033[0m")
            print(response.text)

    except Exception as e:
        print(f"\033[1;31m分析过程中出错: {str(e)}\033[0m")

def analyze_cluster_stream():
    """分析集群状态并生成报告"""
    import json
    import requests
    from datetime import datetime

    print("\033[1;93m正在分析集群状态...\033[0m")

    # 收集集群信息
    data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cluster_info": {},
        "node_status": [],
        "pod_status": {},
        "resource_usage": {},
        "events": []
    }

    try:
        # 获取集群版本信息
        try:
            version_output = get_data(f"kubectl {KUBECTL_OPTIONS} version -o json")
            if version_output:
                version_json = version_output[0].strip()
                data["cluster_info"]["version"] = json.loads(version_json)
        except:
            data["cluster_info"]["version"] = "无法获取版本信息"

        # 获取节点状态
        nodes = get_data(f"kubectl {KUBECTL_OPTIONS} get nodes -o wide")
        if len(nodes) > 1:
            for node in nodes[1:]:
                node_info = node.split()
                if len(node_info) >= 5:
                    data["node_status"].append({
                        "name": node_info[0],
                        "status": node_info[1],
                        "roles": node_info[2] if len(node_info) > 2 else "unknown",
                        "version": node_info[3] if len(node_info) > 3 else "unknown",
                        "internal_ip": node_info[5] if len(node_info) > 5 else "unknown"
                    })

        # 获取所有命名空间的 Pod 状态
        ns_list = get_data(f"kubectl {KUBECTL_OPTIONS} get ns --no-headers")
        for ns in ns_list:
            ns_name = ns.split()[0]
            pods = get_data(f"kubectl {KUBECTL_OPTIONS} get pods -n {ns_name} --no-headers")
            running = 0
            failed = 0
            pending = 0
            for pod in pods:
                status = pod.split()[2]
                if status == "Running":
                    running += 1
                elif status in ["Failed", "Error", "CrashLoopBackOff"]:
                    failed += 1
                elif status == "Pending":
                    pending += 1

            data["pod_status"][ns_name] = {
                "total": len(pods),
                "running": running,
                "failed": failed,
                "pending": pending
            }

        # 获取资源使用情况
        for node in data["node_status"]:
            try:
                usage = get_data(f"kubectl {KUBECTL_OPTIONS} top node {node['name']}")
                if len(usage) > 1:
                    usage_info = usage[1].split()
                    if len(usage_info) >= 5:
                        data["resource_usage"][node["name"]] = {
                            "cpu": usage_info[2],
                            "memory": usage_info[4]
                        }
            except:
                continue

        # 获取最近事件
        events = get_data(f"kubectl {KUBECTL_OPTIONS} get events --sort-by=.metadata.creationTimestamp")
        if events:
            data["events"] = [event.strip() for event in events[-7:]]

        # 调用 AI API 分析数据
        if not KI_AI_KEY:
            raise Exception("请设置 KI_AI_KEY 环境变量")

        # 准备发送给 AI 的提示信息
        prompt = f"""请作为 Kubernetes 专家分析以下集群数据并生成简明扼要的健康状态报告:

集群信息:
- 时间戳: {data['timestamp']}
- 节点数量: {len(data['node_status'])}
- 命名空间数量: {len(data['pod_status'])}

节点状态:
{json.dumps(data['node_status'], indent=2, ensure_ascii=False)}

Pod 状态 (按命名空间,不含 Completed):
{json.dumps(data['pod_status'], indent=2, ensure_ascii=False)}

资源使用情况:
{json.dumps(data['resource_usage'], indent=2, ensure_ascii=False)}

最近事件:
{json.dumps(data['events'], indent=2, ensure_ascii=False)}

请提供:
1. 集群整体健康状况评估
2. 发现的潜在问题
3. 资源使用建议
4. 优化建议
"""
        print("\n\033[1;32m集群健康状态报告:\033[0m")

        response = requests.post(
            f"{KI_AI_URL}",
            headers={
                "Authorization": f"Bearer {KI_AI_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": KI_AI_MODEL,
                "messages": [{
                    "role": "system",
                    "content": "你是一个经验丰富的 Kubernetes 集群分析专家。请基于提供的数据生成专业的分析报告。(忽略 Completed 状态的容器)"
                }, {
                    "role": "user",
                    "content": prompt
                }],
                "temperature": 0.3,
                "stream": True
            },
            stream=True
        )

        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    try:
                        json_response = json.loads(line.decode('utf-8').split('data: ')[1])
                        if 'choices' in json_response and len(json_response['choices']) > 0:
                            content = json_response['choices'][0].get('delta', {}).get('content', '')
                            if content:
                                print(content, end='', flush=True)
                    except:
                        continue
            print()
        else:
            print(f"\033[1;31mAI API 调用失败: {response.status_code}\033[0m")
            print(response.text)

    except Exception as e:
        print(f"\033[1;31m分析过程中出错: {str(e)}\033[0m")

def chat_with_ai(question):
    """与 AI 进行对话，支持各种 IT 运维、开发相关需求"""
    import json
    import requests
    import re
    import os
    from datetime import datetime

    if not question:
        print("\033[1;31m请输入问题内容\033[0m")
        return

    if not KI_AI_KEY:
        print("\033[1;31m错误: 请设置 KI_AI_KEY 环境变量\033[0m")
        return

    try:
        print("\033[1;93m思考中...\033[0m")

        # 让 AI 分析问题类型和是否需要生成文件
        pre_check_response = requests.post(
            f"{KI_AI_URL}",
            headers={
                "Authorization": f"Bearer {KI_AI_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": KI_AI_MODEL,
                "messages": [{
                    "role": "system",
                    "content": """你是一个 IT 专家。请分析用户的问题并返回 JSON 格式的结果：
{
    "type": "配置|代码|脚本|其他",
    "needs_file": true|false,
    "language": "yaml|k8s|golang|python|shell|rust|...",
    "description": "简短描述这个问题的类型和目的"
}"""
                }, {
                    "role": "user",
                    "content": question
                }],
                "temperature": 0.1,
            }
        )

        question_type = {"needs_file": False}
        if pre_check_response.status_code == 200:
            try:
                question_type = json.loads(pre_check_response.json()['choices'][0]['message']['content'])
            except:
                pass

        # 根据问题类型设置不同的系统提示
        if question_type["needs_file"]:
            system_prompt = f"""你是一个专业的 IT 专家。对于{question_type["description"]}类问题：

1. 首先用 JSON 格式提供文件元数据：
   ```json
   {{
     "files": [
       {{
         "name": "文件名（不含路径和时间戳）",
         "type": "{question_type["language"]}",
         "description": "这个文件的用途描述"
       }}
     ]
   }}
   ```

2. 然后解释主要实现思路和关键点

3. 提供完整的代码或配置，使用对应的代码块标记，例如：
   ```{question_type["language"]}
   // 代码内容
   ```

4. 最后提供使用说明或测试方法

注意：
- 文件名应该反映代码或配置的用途
- 代码需要包含必要的注释
- 配置文件需要包含关键配置项的说明"""
        else:
            system_prompt = "你是一个专业的 IT 专家，请针对问题提供详细的解答和建议。"

        response = requests.post(
            f"{KI_AI_URL}",
            headers={
                "Authorization": f"Bearer {KI_AI_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": KI_AI_MODEL,
                "messages": [{
                    "role": "system",
                    "content": system_prompt
                }, {
                    "role": "user",
                    "content": question
                }],
                "temperature": 0.3,
                "stream": True
            },
            stream=True
        )

        if response.status_code == 200:
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        json_response = json.loads(line.decode('utf-8').split('data: ')[1])
                        if 'choices' in json_response and len(json_response['choices']) > 0:
                            content = json_response['choices'][0].get('delta', {}).get('content', '')
                            if content:
                                print(content, end='', flush=True)
                                full_response += content
                    except:
                        continue
            print()

            # 如果需要生成文件，处理代码或配置内容
            if question_type["needs_file"]:
                # 提取文件元数据
                json_match = re.search(r'```json\n(.*?)\n```', full_response, re.DOTALL)
                # 提取所有代码块
                code_matches = re.finditer(r'```(\w+)\n(.*?)\n```', full_response, re.DOTALL)

                file_info = []
                if json_match:
                    try:
                        metadata = json.loads(json_match.group(1))
                        file_info = metadata.get('files', [])
                    except:
                        pass

                # 收集所有代码块
                code_blocks = []
                for match in code_matches:
                    lang, content = match.group(1), match.group(2)
                    if lang.lower() != 'json':  # 排除 JSON 元数据
                        code_blocks.append((lang, content))

                if code_blocks:
                    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

                    # 保存文件
                    for i, (lang, content) in enumerate(code_blocks):
                        # 使用 AI 建议的文件名，如果没有则使用默认名称
                        if i < len(file_info):
                            base_name = file_info[i]['name']
                            description = file_info[i]['description']
                        else:
                            ext = {
                                'python': '.py',
                                'shell': '.sh',
                                'bash': '.sh',
                                'yaml': '.yaml',
                                'java': '.java',
                                'javascript': '.js',
                                'typescript': '.ts',
                                'go': '.go',
                                'rust': '.rs',
                                'cpp': '.cpp',
                                'c': '.c',
                                'sql': '.sql',
                                'dockerfile': 'Dockerfile',
                                'xml': '.xml',
                                'json': '.json',
                                'ini': '.ini',
                                'conf': '.conf',
                                'toml': '.toml'
                            }.get(lang.lower(), '.txt')
                            base_name = f'script_{i+1}{ext}'
                            description = f"{lang} 代码文件"

                        file_path = f'/tmp/ki/ki-{base_name}-{timestamp}'

                        os.makedirs(os.path.dirname(file_path), exist_ok=True)

                        with open(file_path, 'w') as f:
                            f.write(content.strip())

                        print(f"\n\033[1;32m已保存文件: {file_path} ({description})\033[0m")

        else:
            print(f"\033[1;31mAPI 调用失败: {response.status_code}\033[0m")
            print(response.text)

    except Exception as e:
        print(f"\033[1;31m错误: {str(e)}\033[0m")

def ki():
    ( len(sys.argv) == 1 or sys.argv[1] not in ('-n','-t','-t4','-t3','-t2','--ai','-r','-i','-e','-es','-ei','-o','-os','-oi','-restart','-s','--s','-l','--l','--lock','--u','--unlock','--w','--watch','--h','--help','--c','--cache','--k','-a','--a') ) and sys.argv.insert(1,'-n')
    len(sys.argv) == 2 and sys.argv[1] in ('-i','-e','-es','-ei','-o','-os','-oi') and sys.argv.insert(1,'-n')
    len(sys.argv) == 2 and sys.argv[1] in ('-a','--a') and sys.argv.extend(['kube','Pod'])
    len(sys.argv) == 3 and sys.argv[1] in ('-a','--a') and sys.argv.insert(2,'kube')
    config_struct = find_config()
    if len(sys.argv) == 2 and sys.argv[1] == '--ai':
        analyze_cluster_stream()
    elif len(sys.argv) == 2 and sys.argv[1] in ('--w','--watch'):
        info_w(os.environ["PWD"],config_struct[1])
    elif len(sys.argv) == 2 and sys.argv[1] in ('--l','--lock'):
        os.path.exists(ki_unlock) and os.unlink(ki_unlock)
        os.path.exists(ki_lock) or open(ki_lock,"a").close()
    elif len(sys.argv) == 2 and sys.argv[1] in ('--u','--unlock'):
        os.path.exists(ki_unlock) or open(ki_unlock,"a").close()
        os.path.exists(ki_lock) and os.unlink(ki_lock)
    elif len(sys.argv) == 2 and sys.argv[1] == '-n':
        cmd = f"kubectl get ns  --sort-by=.metadata.creationTimestamp --no-headers {KUBECTL_OPTIONS}"
        print("\033[1;38;5;208m{}\033[0m".format(cmd.split('  --')[0]))
        os.environ['KUBECONFIG'] = os.path.realpath(default_config)
        l = get_data(cmd)
        ns_dict = get_feature([ e.split()[0] for e in l ])
        for e in l:
            s = ns_dict[e.split()[0]]
            num = e.find(s)
            num_s = num+len(s)
            print("{}\033[1;95m{}\033[0m{}".format(e[:num],e[num:num_s],e[num_s:]),end='')
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
        print("\033[1;93m{}\033[0m".format("[ "+str(round(end-begin,3))+" ] "))
    elif len(sys.argv) > 2 and sys.argv[1] == '--ai':
        question = ' '.join(sys.argv[2:])
        chat_with_ai(question)
        return
    elif 1 < len(sys.argv) < 4 and sys.argv[1] in ('-s','--s'):
        if config_struct[1] and len(config_struct[1]) > 1:
            if len(sys.argv) == 3:
                config = get_config(config_struct[1], sys.argv[2])
                if config and os.path.exists(default_config) and config not in {default_config,os.path.realpath(default_config)}:
                    os.unlink(default_config)
                    os.symlink(config,default_config)
                    find_history(config,72)
                    print("\033[1;93m{}\033[0m".format("[ SWITCH ---> "+config.split("/")[-1]+" ] "))
            else:
                lr = set()
                for i in config_struct[1]:
                    for j in config_struct[1]:
                        if cmp_file(i,j) and i != j:
                            e = i if len(i) < len(j) else j
                            if e != default_config and e != os.path.realpath(default_config):
                                lr.add(e)
                for e in lr:
                    os.unlink(e)
                    config_struct[1].remove(e)
                if os.path.exists(default_config):
                    pattern = ""
                    res = None
                    while True:
                        config_struct[1] = [x for x in config_struct[1] if x.find(pattern) >= 0] if pattern else config_struct[1]
                        if config_struct[1]:
                            for n,e in enumerate(config_struct[1]):
                                if cmp_file(e,default_config):
                                    print("\033[1;95m{}\033[0m \033[1;32m{}\033[0m".format(n,e.strip().split('/')[-1]))
                                else:
                                    print("\033[1;32m{}\033[0m {}".format(n,e.strip().split('/')[-1]))
                            try:
                                pattern = input("\033[1;95m%s\033[0m\033[5;95m%s\033[0m" % ("select",":")).strip()
                            except:
                                sys.exit()
                            if pattern.isdigit() and 0 <= int(pattern) < len(config_struct[1]) or len(config_struct[1]) == 1:
                                index = int(pattern) if pattern.isdigit() else 0
                                res = (config_struct[1][index]).split()[0]
                            if res:
                                if res not in {default_config,os.path.realpath(default_config)}:
                                    find_history(os.path.realpath(default_config),-24)
                                    os.unlink(default_config)
                                    os.symlink(res,default_config)
                                    print('\033[{}C\033[1A'.format(10),end = '')
                                    print("\033[1;32m{}\033[0m".format(res.split('/')[-1]))
                                    find_history(res,24)
                                    os.path.exists(ki_unlock) or open(ki_lock,"a").close()
                                break
                        else:
                            break
                else:
                    print("\033[1;32m{}\033[0m\033[5;32m{}\033[0m".format("File not found ",default_config))
    elif 2 < len(sys.argv) < 5 and sys.argv[1] in ('-n','-r','-t','-t4','-t3','-t2','-i','-l','-e','-es','-ei','-o','-os','-oi','-a','--a'):
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
                d = {'d':['Deployment'," -o wide"],'s':['Service'," -o wide"],'i':['Ingress'," -o wide"],'c':['ConfigMap'," -o wide"],'t':['Secret'," -o wide"],'n':['Node'," -o wide"],'p':['PersistentVolumeClaim'," -o wide"],'v':['PersistentVolume'," -o wide"],'f':['StatefulSet'," -o wide"],'j':['CronJob'," -o wide"],'b':['Job'," -o wide"],'P':['Pod'," -o wide"],'e':['Event',''],'r':['ReplicaSet',''],'a':['DaemonSet',''],'q':['ResourceQuota',''],'V':['VirtualService',""],'g':['Gateway',''],'h':['HTTPRoute',''],'A':['all',''],'E':['EnvoyFilter',''],'D':['DestinationRule','']}
                obj = d[sys.argv[3][0]][0] if sys.argv[3][0] in d else "Pod"
                ext = d[sys.argv[3][0]][1] if sys.argv[3][0] in d else ""
                if sys.argv[1] in ('-i','-l','-e','-es','-ei','-o','-os','-oi'):
                    begin = time.perf_counter()
                    while True:
                        if ns:
                            cmd = f"kubectl {KUBECTL_OPTIONS} get pod --no-headers -n "+ns
                            pods = [ e.split()[0] for e in get_data(cmd) ]
                            pod = find_optimal(pods,sys.argv[3]) if pods else None
                            if not (pods and pod):
                                kn = re.split("[./]",sys.argv[2])
                                ns_pattern = kn[-1] if len(kn) > 1 and len(kn[-1].strip()) > 0 else kn[0]
                                os.environ['KUBECONFIG'] in config_struct[1] and config_struct[1].remove(os.environ['KUBECONFIG'])
                                if config_struct[1]:
                                    for n,config in enumerate(config_struct[1]):
                                        cmd = f"kubectl {KUBECTL_OPTIONS} get ns --no-headers --kubeconfig "+config
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
                                    cmd = f"kubectl {KUBECTL_OPTIONS} -n "+ns+" exec -it "+pod+" -- sh"
                                elif sys.argv[1] in ('-l'):
                                    line = os.environ['KI_LINE'] if 'KI_LINE' in os.environ else str(1000)
                                    cmd = f"kubectl {KUBECTL_OPTIONS} -n "+ns+" logs -f "+pod+" --all-containers --tail "+line
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
                                    cmd = f"kubectl {KUBECTL_OPTIONS} -n "+ns+" "+action+" "+obj.lower()+" "+name+action2
                                print("\033[1;38;5;208m{}\033[0m".format(cmd))
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
                            sort_by = "" if obj.lower() == "all" else "  --sort-by=.status.containerStatuses[0].restartCount" if sys.argv[1].split('n')[-1] else "  --sort-by=.metadata.creationTimestamp"
                            cmd = f"kubectl get "+obj.lower()+ext+" -n "+ ns + sort_by + f" --no-headers {KUBECTL_OPTIONS}"
                        elif sys.argv[1] in ('-a','--a','-A'):
                            cmd = f"kubectl get "+obj.lower()+ext+f" -A  --sort-by=.metadata.creationTimestamp --no-headers {KUBECTL_OPTIONS}"
                        else:
                            key = sys.argv[1].split('t')[-1] if sys.argv[1].split('t')[-1].isdigit() else "3"
                            if sys.argv[-1] in ('-a','--a','-A'):
                                cmd = f"kubectl top "+obj.lower()+" -A "+f"  --no-headers {KUBECTL_OPTIONS}|sort --key "+key+" --numeric"
                            else:
                                cmd = f"kubectl top "+obj.lower()+" -n "+ ns +f"  --no-headers {KUBECTL_OPTIONS}|sort --key "+key+" --numeric"
                        result_lines = get_data(cmd)
                        if not result_lines:
                            kn = re.split("[./]",sys.argv[2])
                            ns_pattern = kn[-1] if len(kn) > 1 and len(kn[-1].strip()) > 0 else kn[0]
                            os.environ['KUBECONFIG'] in config_struct[1] and config_struct[1].remove(os.environ['KUBECONFIG'])
                            if config_struct[1]:
                                for n,config in enumerate(config_struct[1]):
                                    cmd = f"kubectl {KUBECTL_OPTIONS} get ns --no-headers --kubeconfig "+config
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
                            print("\033[1;38;5;208m{}\033[0m".format(cmd.split(' --')[0]))
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
                            style = "\033[1;93m{}\033[0m" if switch else "\033[1;32m{}\033[0m"
                            string = "[ "+k8s+" / "+ns+" --- "+obj+" ] [ "+now+" ]" if sys.argv[1] not in ('-a','--a') and obj not in ('PersistentVolume') else "[ "+k8s+" --- "+obj+" ] [ "+now+" ]"
                            print(style.format(string))
                            switch = False
                            if pod == '*':
                                print('\033[{}C\033[1A'.format(len(string)),end = '')
                                print(style.format(" Watching..."))
                        try:
                            if pod != '*':
                                pod = input("\033[1;95m%s\033[0m\033[5;95m%s\033[0m" % ("select",":")).strip()
                                num = 10 + len(pod)
                            else:
                                result_lines = get_data(cmd)
                                time.sleep(3)
                        except:
                            sys.exit()
                        result_len = len(result_lines)
                        search_term = pod
                        podList = pod.split()
                        pod = podList[0] if podList else ""

                        special_chars_pattern = re.compile(r'[^\w]')
                        if special_chars_pattern.match(pod):
                            if pod == '$':
                                pod = str(result_len-1)
                            elif pod == '*':
                                pass
                            elif os.path.exists(ki_pod_dict):
                                with open(ki_pod_dict,'r') as f:
                                    dc = eval(f.read())
                                    key = k8s+'/'+ns+'/'+obj
                                    last_res = ( dc[key][0] if pod in ('!','~') else dc[key][1][0][0] ) if key in dc else ""
                                    for n,e in enumerate(result_lines[::-1]):
                                        if last_res in e:
                                            pod = str(result_len-n-1)
                                            break
                        if len(podList) > 1:
                            if podList[1][0] in ('l','g','c'):
                                parts = search_term.split(None, 2)
                                args = podList[1][0] + " " + parts[2] if len(parts) == 3 else ' '.join(podList[1:])
                            elif podList[1].isdigit():
                                args = "l " + podList[1]
                            else:
                                args = ''.join(podList[1:])
                        else:
                            args = "p"
                        if pod.isdigit() and int(pod) < result_len or ( result_len == 1 and pod != '*'):
                            index = int(pod) if pod.isdigit() and int(pod) < result_len else 0
                            res = result_lines[index].split()[0 if sys.argv[1] not in ('-a','--a') else (1 if obj not in ("PersistentVolume") else 0)]
                            iip = result_lines[index].split()[5] if len(result_lines[index].split()) > 5 else find_ip(res)
                            ns = result_lines[index].split()[0] if sys.argv[1] in ('-a','--a') else ns
                            l = cmd_obj(ns,obj,res,args,iip)
                            print('\033[{}C\033[1A'.format(num),end = '')
                            if l:
                                print("\033[1;38;5;208m{}\033[0m".format(l[0]))
                                record(res,l[2],l[1],l[0],k8s,ns,config_struct)
                                os.system(l[0])
                            print('\r')
                    else:
                        pod = ""
                else:
                    print("No resources found.")
                    if not os.path.exists(ki_cache) or (os.path.exists(ki_cache) and int(time.time()-os.stat(ki_cache).st_mtime) > 86400):
                        subprocess.Popen("ki --c",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
                    sys.exit()
        else:
            print("No namespace found in the kubernetes.")
            if not os.path.exists(ki_cache) or (os.path.exists(ki_cache) and int(time.time()-os.stat(ki_cache).st_mtime) > 86400):
                subprocess.Popen("ki --c",shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    elif len(sys.argv) == 2 and sys.argv[1] in ('--h','--help'):
        style = "\033[1;32m%s\033[0m"
        print(style % "Kubectl pro controls the Kubernetes cluster manager,find more information at: https://ki.xabc.io\n")
        doc_dict = {
         "1. ki":"List all namespaces",
         "2. ki xx":"List all pods in the namespace ( if there are multiple ~/.kube/kubeconfig*,the best matching kubeconfig will be found ,the namespace parameter supports fuzzy matching,after outputting the pod list, select: xxx filters the query\n         select: index l ( [ l ] Print the logs for a container in a pod or specified resource \n         select: index l 100 ( Print the logs of the latest 100 lines \n         select: index l xxx ( Print the logs and filters the specified characters \n         select: index r ( [ r ] Rollout restart the pod \n         select: index o ( [ o ] Output the [Deployment,StatefulSet,Service,Ingress,Configmap,Secret].yml file \n         select: index del ( [ del ] Delete the pod \n         select: index cle ( [ cle ] Delete the Deployment/StatefulSet \n         select: index e[sighVDE] ( [ e[sighVDE] ] Edit the Deploy/Service/Ingress/Gateway/HTTPRoute/VirtualService/DestinationRule/EnvoyFilter \n         select: index s5 ( [ s3 ] Set the Deploy/StatefulSet replicas=3 \n         select: index dp ( Describe a pod \n         select: * ( Watching... ",
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
         "13. ki xx g":"List the Gateway of a namespace",
         "14. ki xx h":"List the HTTPRoute of a namespace",
         "15. ki xx V":"List the VirtualService of a namespace",
         "16. ki xx D":"List the DestinationRule of a namespace",
         "17. ki xx E":"List the EnvoyFilter of a namespace",
         "18. ki -i $ns $pod":"Login in the container,this way can be one-stop",
         "19. ki -l $ns $pod":"Print the logs for a container,this way can be one-stop",
         "20. ki -e[si] $ns $pod":"Edit the Deploy/Service/Ingress for a container,this way can be one-stop",
         "21. ki $k8s.$ns":"Select the kubernetes which namespace in the kubernetes ( if there are multiple ~/.kube/kubeconfig*,this way can be one-stop. ",
         "22. ki --s":"Select the kubernetes to be connected ( if there are multiple ~/.kube/kubeconfig*,the kubeconfig storage can be kubeconfig-hz,kubeconfig-sh,etc. ",
         "23. ki --c":"Enable write caching of namespace ( ~/.history/.ns_dict ",
         "24. ki --a":"List all pods in the kubernetes",
         "Tips:": "Within the selection process of Pod filtering, where '$' represents the most recent Pod, while '~' and '!' denote the Pod from the previous operation, and the remaining symbols indicate the Pod that has been operated on the most."}
        for k,v in doc_dict.items():
            print(style % k,v)
def main():
    ki()
#-----------------PROG----------------------------
if __name__ == '__main__':
    main()
