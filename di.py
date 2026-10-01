#!/usr/bin/python3
#*************************************************
# Description : Docker Pro - Simplified Docker Management
# Version     : 2.0
#*************************************************
import os,re,sys,time,shlex,shutil,atexit,threading,subprocess
from collections import deque, Counter

try:
    import readline
except ImportError:
    readline = None

#-----------------CONST---------------------------
DEFAULT_LOG_TAIL = 100
GREP_LOG_TAIL = 1024
MAX_LOG_TAIL = 100000
WATCH_INTERVAL = 2
HISTORY_MAX_SIZE = 128
HISTORY_RECENT_SIZE = 32
INPUT_HISTORY_SIZE = 500
HISTORY_FILE = os.path.expanduser("~/.di_history")
INPUT_HISTORY_FILE = os.path.expanduser("~/.di_input")
LOG_TAIL_FILE = os.path.expanduser("~/.di_line")
COMPOSE_FILES_LABEL = "com.docker.compose.project.config_files"

RESET = "\033[0m"
GREEN = "\033[1;32m"
RED = "\033[1;31m"
LIGHT_RED = "\033[1;91m"
YELLOW = "\033[1;93m"
BLUE = "\033[1;94m"
CYAN = "\033[1;36m"
PURPLE = "\033[1;95m"
ORANGE = "\033[1;38;5;208m"
GRAY = "\033[90m"
ANSI_RE = re.compile(r'\033\[[0-9;?]*[A-Za-z]')

# 输入的动作（含别名） => 内部动作
ACTIONS = {
    'p': 'shell', 'sh': 'shell', 'bash': 'shell', 'exec': 'shell',
    'l': 'logs', 'log': 'logs', 'logs': 'logs',
    'g': 'grep', 'grep': 'grep',
    'c': 'context',
    'r': 'restart', 'restart': 'restart',
    'start': 'start',
    'stop': 'stop',
    'del': 'rm', 'rm': 'rm', 'delete': 'rm',
    'd': 'inspect', 'inspect': 'inspect',
    'o': 'dump',
    't': 'top', 'top': 'top',
    'x': 'run',
    'e': 'edit', 'edit': 'edit',
    'dbg': 'debug', 'debug': 'debug',
}
# 历史快捷符号 => (历史类型, 默认动作)；其他单个标点符号等同于 ;
HISTORY_TARGETS = {'^': ('last', 'auto'), '[': ('most', 'logs'), ']': ('second', 'logs'), ';': ('most', 'auto')}
NON_HISTORY_SYMBOLS = set('</*?:')
# 这些输入有特殊含义，不能作为特征串
RESERVED_INPUTS = {'q', 'a'}

class DockerError(Exception):
    """docker 命令执行失败"""

class Notice(Exception):
    """需要提示给用户的错误信息"""

class Quit(Exception):
    """退出交互模式"""

#-----------------FUN-----------------------------
def docker(args, timeout=30):
    """执行 docker 命令，返回 (returncode, stdout, stderr)"""
    try:
        p = subprocess.run(['docker'] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           universal_newlines=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except (OSError, subprocess.TimeoutExpired) as e:
        return 1, '', str(e)

def parse_state(status: str):
    """从 docker ps 的 STATUS 推断容器状态"""
    s = status.lower()
    if s.startswith('up'):
        return 'paused' if '(paused)' in s else 'running'
    for state in ('restarting', 'exited', 'created', 'removing', 'dead'):
        if s.startswith(state):
            return state
    return 'unknown'

def compact_ports(ports: str):
    """只保留宿主机端口：0.0.0.0:7793->8080/tcp, :::7793->8080/tcp => :7793"""
    host_ports = []
    for port in re.findall(r':(\d+(?:-\d+)?)->', ports):
        if port not in host_ports:
            host_ports.append(port)
    return ','.join(':' + p for p in host_ports)

def get_containers(show_all=False):
    """获取容器列表（按名称排序，序号稳定）"""
    fmt = '{{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Names}}\t{{.Ports}}'
    rc, out, err = docker(['ps', '--format', fmt] + (['-a'] if show_all else []))
    if rc != 0:
        raise DockerError(err.strip() or "docker ps failed")

    containers = []
    for line in out.splitlines():
        parts = line.split('\t')
        if len(parts) < 5:
            continue
        cid, image, status, names, ports = parts[:5]
        # 旧式 --link 会产生 "a,b/alias" 这样的多个名称
        name = next((n for n in names.split(',') if '/' not in n), names)
        containers.append({'id': cid, 'image': image, 'status': status, 'name': name,
                           'ports': compact_ports(ports), 'state': parse_state(status)})
    containers.sort(key=lambda c: c['name'])
    return containers

def inspect_container(name: str):
    """获取单个容器信息（包含未列出的已停止容器），不存在返回 None"""
    fmt = '{{.Id}}\t{{.Config.Image}}\t{{.State.Status}}\t{{.Name}}'
    rc, out, _ = docker(['container', 'inspect', '--format', fmt, '--', name], timeout=10)
    parts = out.strip().split('\t')
    if rc != 0 or len(parts) < 4:
        return None
    cid, image, state, cname = parts[:4]
    return {'id': cid[:12], 'image': image, 'status': state.capitalize(), 'name': cname.lstrip('/'),
            'ports': '', 'state': state}

def filter_containers(containers: list, pattern: str):
    """过滤容器：优先匹配名称，名称都不匹配时再匹配镜像和 ID 前缀"""
    if not pattern:
        return containers
    p = pattern.lower()
    by_name = [c for c in containers if p in c['name'].lower()]
    return by_name or [c for c in containers if p in c['image'].lower() or c['id'].startswith(p)]

def get_feature(name_list: list):
    """计算每个名称的最短特征子串：只出现在这一个名称里，优先纯字母数字、单词开头
    名称是其他名称的子串时（如 news / news-mail）没有特征串，需要输入完整名称"""
    lowered = [name.lower() for name in name_list]
    counter = Counter()
    for s in lowered:
        counter.update({s[i:j] for i in range(len(s)) for j in range(i + 1, len(s) + 1)})

    features = {}
    for name, s in zip(name_list, lowered):
        best = None
        for i in range(len(s)):
            for j in range(i + 1, len(s) + 1):
                sub = s[i:j]
                if counter[sub] != 1:
                    continue
                if sub.isdigit() or sub in RESERVED_INPUTS or not any(ch.isalnum() for ch in sub):
                    continue
                # 含 - _ . 的特征串不好输入，按多一位计算；长度相同时优先单词开头、靠前
                score = (len(sub) + (0 if sub.isalnum() else 1), i > 0 and s[i - 1].isalnum(), i)
                if best is None or score < best[0]:
                    best = (score, i, j)
                break
        if best:
            features[name] = name[best[1]:best[2]]
    return features

def is_history_symbol(token: str):
    """是否是历史快捷符号（^ [ ] ; 及其他单个标点）"""
    return token in HISTORY_TARGETS or (len(token) == 1 and not token.isalnum() and token not in NON_HISTORY_SYMBOLS)

def parse_action(tokens: list, default: str):
    """解析动作，返回 (动作, 参数)；支持 l200 这种紧凑写法，单独的数字等同于 l <n>"""
    if not tokens:
        return default, []
    word = tokens[0]
    if word.isdigit():
        return 'logs', tokens
    if word in ACTIONS:
        return ACTIONS[word], tokens[1:]
    if word[0] in 'lgc' and word[1:].isdigit():
        return ACTIONS[word[0]], [word[1:]] + tokens[1:]
    raise Notice(f"Unknown action '{word}'. Actions: l g c r start stop del d o t x e dbg (? for help)")

def load_log_tail():
    """读取上一次使用的日志行数"""
    try:
        with open(LOG_TAIL_FILE) as f:
            value = f.read().strip()
        if value.isdigit() and 0 < int(value) <= MAX_LOG_TAIL:
            return int(value)
    except OSError:
        pass
    return DEFAULT_LOG_TAIL

def save_log_tail(tail: int):
    try:
        with open(LOG_TAIL_FILE, 'w') as f:
            f.write(str(tail))
    except OSError:
        pass

def logs_command(name: str, action: str, args: list):
    """l [n|keyword] / g keyword / c keyword"""
    if args and args[0].isdigit():
        tail = min(max(int(args[0]), 1), MAX_LOG_TAIL)
        save_log_tail(tail)
        return f"docker logs -f --tail {tail} {name}"
    if args:
        keyword = shlex.quote(' '.join(args))
        if action == 'logs':
            return f"docker logs -f --tail {GREP_LOG_TAIL} {name} 2>&1 | grep -a --color=auto -e {keyword}"
        context = " -C 10" if action == 'context' else ""
        return f"docker logs -f {name} 2>&1 | grep -a --color=auto{context} -e {keyword}"
    return f"docker logs -f --tail {load_log_tail()} {name}"

def confirm_action(caution: str):
    """高危操作二次确认"""
    length = readline.get_current_history_length() if readline else 0
    try:
        answer = input(f"{RED}{caution}{RESET}, confirm? (yes/no): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        answer = ""
    # 确认输入不进入输入历史
    if readline and readline.get_current_history_length() > length:
        readline.remove_history_item(readline.get_current_history_length() - 1)
    if answer in ('yes', 'y'):
        return True
    print("Operation canceled.")
    return False

def run_cmd(cmd: str, note=None, erase=True):
    """显示并执行命令；交互模式下覆盖掉输入行；输出被重定向时提示信息写到 stderr"""
    out = sys.stdout if sys.stdout.isatty() else sys.stderr
    if erase:
        print('\033[1A\033[2K', end='', file=out)
    print(f"{ORANGE}{cmd}{RESET}", file=out)
    if note:
        print(f"{YELLOW}{note}{RESET}", file=out)
    out.flush()
    status = os.system(cmd)
    if erase:
        print()
    return status >> 8 if status > 255 else status

def status_color(c):
    """状态颜色：运行绿色，unhealthy / 重启中 / 异常退出红色，启动中 / 暂停黄色，正常退出灰色"""
    status = c['status'].lower()
    if c['state'] == 'running':
        if '(unhealthy)' in status:
            return RED
        return YELLOW if 'starting' in status else GREEN
    if c['state'] == 'paused':
        return YELLOW
    if c['state'] == 'created' or status.startswith('exited (0)'):
        return GRAY
    return RED

def truncate(text: str, width: int):
    return text if len(text) <= width else '..' + text[-(width - 2):]

def format_rows(containers, features, marks, stats=None):
    """格式化容器列表；列宽按内容自适应，终端不够宽时截断镜像名、隐藏 ID"""
    if not containers:
        return []
    width = shutil.get_terminal_size((240, 50)).columns - 1
    usage = {c['name']: stats.get(c['name'], ('', '')) for c in containers} if stats is not None else {}

    w_idx = len(str(len(containers) - 1))
    w_name = max(len(c['name']) + 2 * len(marks.get(c['name'], [])) for c in containers)
    w_status = max(len(c['status']) for c in containers)
    w_image = max(len(c['image']) for c in containers)
    w_ports = max(len(c['ports']) for c in containers)
    widths = [w_idx, w_name, w_status]
    if stats is not None:
        w_cpu = max([len(cpu) for cpu, _ in usage.values()] + [4])
        w_mem = max([len(mem) for _, mem in usage.values()] + [4])
        widths += [w_cpu, w_mem]
    used = sum(widths) + 2 * len(widths) + (w_ports + 2 if w_ports else 0)
    show_id = width - used - w_image >= 14
    # 镜像名按剩余宽度截断，太窄时不显示
    show_image = width - used >= 10
    w_image = min(w_image, width - used)

    rows = []
    for i, c in enumerate(containers):
        name = c['name']
        name_display = name
        feature = features.get(name)
        if feature:
            pos = name.find(feature)
            name_display = name[:pos] + PURPLE + feature + RESET + name[pos + len(feature):]
        mk = marks.get(name, [])
        for symbol, color in mk:
            name_display += f" {color}{symbol}{RESET}"
        name_display += ' ' * (w_name - len(name) - 2 * len(mk))

        row = f"{GREEN}{i:<{w_idx}}{RESET}  {name_display}  {status_color(c)}{c['status']:<{w_status}}{RESET}"
        if stats is not None:
            cpu, mem = usage[name]
            row += f"  {cpu:>{w_cpu}}  {mem:>{w_mem}}"
        if show_image:
            row += f"  {truncate(c['image'], w_image):<{w_image}}"
        if w_ports:
            row += f"  {CYAN}{c['ports']:<{w_ports}}{RESET}"
        if show_id:
            row += f"  {GRAY}{c['id']}{RESET}"
        rows.append(row.rstrip())
    return rows

class History:
    """容器操作历史；每次操作追加写入文件，多个终端同时使用不会互相覆盖"""
    def __init__(self, filepath=HISTORY_FILE, maxsize=HISTORY_MAX_SIZE):
        self.filepath = filepath
        self.data = deque(maxlen=maxsize)

    def _read(self):
        try:
            with open(self.filepath) as f:
                return [line.strip() for line in f if line.strip()]
        except OSError:
            return []

    def _write(self, names):
        try:
            temp_file = self.filepath + '.tmp'
            with open(temp_file, 'w') as f:
                f.writelines(f"{name}\n" for name in names)
            os.replace(temp_file, self.filepath)
        except OSError:
            pass

    def load(self):
        """加载历史记录，文件过长时压缩"""
        names = self._read()
        self.data = deque(names, maxlen=self.data.maxlen)
        if len(names) > self.data.maxlen * 2:
            self._write(self.data)

    def record(self, container_name):
        """记录操作历史"""
        self.data.append(container_name)
        try:
            with open(self.filepath, 'a') as f:
                f.write(f"{container_name}\n")
        except OSError:
            pass

    def prune(self, container_name):
        """从历史记录中移除指定容器（例如容器已被删除）"""
        self.data = deque((n for n in self.data if n != container_name), maxlen=self.data.maxlen)
        self._write([n for n in self._read() if n != container_name][-self.data.maxlen:])

    def get_last_used(self):
        """获取上一次操作的容器"""
        return self.data[-1] if self.data else None

    def get_recent_containers(self):
        """从最近32条记录中获取使用频率最高的2个容器，返回 (最常用, 次常用)"""
        most_common = Counter(list(self.data)[-HISTORY_RECENT_SIZE:]).most_common(2)
        most_used = most_common[0][0] if most_common else None
        # 如果只有1个容器，次常用也是它
        second_most_used = most_common[1][0] if len(most_common) >= 2 else most_used
        return most_used, second_most_used

class StatsStream:
    """后台持续读取 docker stats，供 watch 模式显示 CPU / 内存"""
    def __init__(self):
        self.data = {}
        self.proc = None

    def start(self):
        try:
            self.proc = subprocess.Popen(
                ['docker', 'stats', '--format', '{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, universal_newlines=True)
        except OSError:
            return
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        for line in self.proc.stdout:
            parts = ANSI_RE.sub('', line).strip().split('\t')
            if len(parts) >= 3:
                self.data[parts[0]] = (parts[1], parts[2].split(' / ')[0])

    def stop(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.proc.kill()

history = History()

class DockerPro:
    """交互式容器管理"""
    def __init__(self, show_all=False):
        self.show_all = show_all
        self.interactive = False
        self.filter = ""
        self.all = []
        self.features = {}
        self.shell_cache = {}
        self.debug_image = None

    def refresh(self):
        self.all = get_containers(self.show_all)

    def displayed(self):
        return filter_containers(self.all, self.filter)

    def list_lines(self, containers, stats=None):
        """生成列表（标题、容器行、状态栏）"""
        self.features = get_feature([c['name'] for c in containers]) if len(containers) > 1 else {}
        last_used = history.get_last_used()
        most_used, second_most_used = history.get_recent_containers()
        marks = {}
        for c in containers:
            mk = []
            if c['name'] == last_used:
                mk.append(('^', YELLOW))         # 上一次操作
            if c['name'] == most_used:
                mk.append(('[', LIGHT_RED))      # 最常用
            if c['name'] == second_most_used:
                mk.append((']', BLUE))           # 次常用
            marks[c['name']] = mk

        cmd_display = "docker ps" + (" -a" if self.show_all else "")
        if self.filter:
            cmd_display += f" | grep '{self.filter}'"
        lines = [f"{ORANGE}{cmd_display}{RESET}"] + format_rows(containers, self.features, marks, stats)

        if len(containers) > 3 or self.filter or self.show_all or stats is not None:
            status_parts = [f"Containers: {len(containers)}"]
            if self.filter:
                status_parts.extend([f"Filter: '{self.filter}'", f"Total: {len(self.all)}"])
            if self.show_all:
                status_parts.append("All")
            status_parts.append(time.strftime("%T", time.localtime()))
            if stats is not None:
                status_parts.append("Watching... Ctrl+C to return")
            lines.append(f"{YELLOW}[ {' ] [ '.join(status_parts)} ]{RESET}")
        return lines

    def loop(self):
        """交互主循环"""
        self.interactive = True
        prompt = make_prompt()
        while True:
            self.refresh()
            if not self.all:
                if self.show_all or not docker(['ps', '-aq'])[1].strip():
                    print(f"{RED}No containers found.{RESET}")
                    return
                print(f"{YELLOW}No running containers, showing all.{RESET}")
                self.show_all = True
                continue

            containers = self.displayed()
            if not containers:
                print(f"{RED}No containers match '{self.filter}', filter cleared.{RESET}")
                self.filter = ""
                containers = self.all
            print('\n'.join(self.list_lines(containers)))

            try:
                user_input = input(prompt).strip()
            except KeyboardInterrupt:
                print(f"\n{GREEN}Bye!{RESET}")
                return
            except EOFError:
                print()
                return

            try:
                self.handle(user_input, containers)
            except Quit:
                return
            except (Notice, DockerError) as e:
                print(f"{RED}{e}{RESET}")
            except KeyboardInterrupt:
                print()

    def handle(self, user_input, containers):
        """解析交互输入：<目标> [动作] [参数]"""
        tokens = user_input.split()
        if not tokens:
            # 只有一个结果直接进入；多个结果清除过滤
            if len(containers) == 1:
                self.act(containers[0], [])
            elif self.filter:
                self.filter = ""
            return

        head, rest = tokens[0], tokens[1:]
        if not rest:
            if head.lower() == 'q':
                raise Quit()
            if head == '*':
                return self.watch()
            if head == '<':
                self.filter = ""
                return
            if head == 'a':
                self.show_all = not self.show_all
                return
            if head == '?':
                print_help()
                return

        target, default = self.resolve_symbol(head, containers)
        if target is None:
            selecting = head.startswith('/') and len(head) > 1
            pattern = head[1:] if selecting else head
            if not rest and not selecting:
                # 单独的文本作为过滤条件
                if not filter_containers(self.all, pattern):
                    raise Notice(f"No match: '{pattern}'")
                self.filter = pattern
                return
            target, default = self.pick(pattern, containers), 'auto'
            if not target:
                return
        self.act(target, rest, default)

    def oneshot(self, args):
        """di <目标> [动作] [参数]：直接执行并返回退出码；匹配到多个容器时返回 None 进入交互选择"""
        head, rest = args[0], args[1:]
        self.features = get_feature([c['name'] for c in self.all])
        target, default = self.resolve_symbol(head, self.all)
        if target is None:
            pattern = head[1:] if head.startswith('/') and len(head) > 1 else head
            target, default = self.pick(pattern, self.all), 'auto'
            if not target:
                return None
        return self.act(target, rest, default)

    def resolve_symbol(self, head, containers):
        """解析序号、: 、历史符号、/特征串，返回 (容器, 默认动作)；不是这些返回 (None, None)"""
        if head.isdigit() and int(head) < len(containers):
            return containers[int(head)], 'auto'
        if head == ':' and containers:
            return containers[-1], 'auto'
        if is_history_symbol(head):
            kind, default = HISTORY_TARGETS.get(head, ('most', 'auto'))
            return self.history_container(kind), default
        if head.startswith('/') and len(head) > 1:
            for c in containers:
                if self.features.get(c['name'], '').lower() == head[1:].lower():
                    return c, 'auto'
        return None, None

    def pick(self, pattern, containers):
        """按名称 / 模式选择唯一容器；匹配到多个时设为过滤条件并返回 None"""
        matches = self.find(pattern, containers)
        if not matches:
            raise Notice(f"No container matches '{pattern}'")
        if len(matches) > 1:
            self.filter = pattern
            print(f"{YELLOW}{len(matches)} containers match '{pattern}', select by index.{RESET}")
            return None
        return matches[0]

    def find(self, pattern, containers):
        """名称完全匹配优先，其次过滤匹配；先在当前列表找，再到全部容器找，最后尝试未列出的容器"""
        p = pattern.lower()
        pools = [containers] if containers is self.all else [containers, self.all]
        for pool in pools:
            exact = [c for c in pool if c['name'].lower() == p]
            if exact:
                return exact
            matched = filter_containers(pool, pattern)
            if matched:
                return matched
        c = inspect_container(pattern)
        return [c] if c else []

    def history_container(self, kind):
        """按历史取容器（包含已停止的）；已被删除的容器从历史中清理后重新计算"""
        while True:
            if kind == 'last':
                name = history.get_last_used()
            else:
                most_used, second_most_used = history.get_recent_containers()
                name = most_used if kind == 'most' else second_most_used
            if not name:
                raise Notice("No second container in history." if kind == 'second' else "No history found.")
            c = next((c for c in self.all if c['name'] == name), None) or inspect_container(name)
            if c and c['name'] == name:
                return c
            history.prune(name)

    def act(self, c, tokens, default='auto'):
        """对容器执行动作"""
        action, args = parse_action(tokens, default)
        note = None
        if action == 'auto':
            if c['state'] == 'running':
                action = 'shell'
            else:
                action = 'logs'
                note = f"{c['name']} is {c['state']}, showing logs"
        cmd, build_note = self.build_command(c, action, args)
        if not cmd:
            return 1
        if action == 'rm':
            history.prune(c['name'])
        else:
            history.record(c['name'])
        return run_cmd(cmd, build_note or note, erase=self.interactive)

    def build_command(self, c, action, args):
        """生成动作对应的命令，返回 (命令, 提示)；取消时命令为 None"""
        name = c['name']
        if action in ('shell', 'debug'):
            if c['state'] != 'running':
                raise Notice(f"{name} is {c['state']}. Try: l (logs) / start")
            shell = self.detect_shell(c) if action == 'shell' else None
            if shell:
                return f"docker exec -it {name} {shell}", None
            return self.debug_command(c, no_shell=(action == 'shell'))
        if action in ('logs', 'grep', 'context'):
            return logs_command(name, action, args), None
        if action == 'restart':
            return f"docker restart {name}", None
        if action == 'start':
            return f"docker start {name}", None
        if action == 'stop':
            return (f"docker stop {name}", None) if confirm_action(f"This will stop {name}") else (None, None)
        if action == 'rm':
            return (f"docker rm -f {name}", None) if confirm_action(f"This will remove {name}") else (None, None)
        if action == 'inspect':
            pager = " | less -FRX" if sys.stdout.isatty() and shutil.which('less') else ""
            return f"docker container inspect {name}{pager}", None
        if action == 'dump':
            return f"docker container inspect {name} > {name}.inspect.json", None
        if action == 'top':
            return f"docker top {name}", None
        if action == 'run':
            if not args:
                raise Notice("Usage: <target> x <command>, e.g. 0 x redis-cli info")
            # 输出被管道 / 重定向时不分配 TTY，避免 \r\n
            flags = "-it" if sys.stdin.isatty() and sys.stdout.isatty() else "-i"
            # 命令行参数已被 shell 拆分，需要重新转义；交互输入保留原样（可以使用引号）
            command = ' '.join(args) if self.interactive else ' '.join(shlex.quote(a) for a in args)
            return f"docker exec {flags} {name} {command}", None
        if action == 'edit':
            fmt = '{{index .Config.Labels "%s"}}' % COMPOSE_FILES_LABEL
            _, out, _ = docker(['container', 'inspect', '--format', fmt, name], timeout=10)
            files = [f for f in out.strip().split(',') if f and f != '<no value>']
            if not files:
                raise Notice(f"{name} is not managed by docker compose.")
            editor = os.environ.get('EDITOR') or ('vim' if shutil.which('vim') else 'vi')
            return f"{editor} {' '.join(shlex.quote(f) for f in files)}", None
        raise Notice(f"Unknown action '{action}'")

    def detect_shell(self, c):
        """检测容器内可用的 shell：bash 优先，其次 sh；都没有返回 None"""
        if c['id'] not in self.shell_cache:
            shell = None
            rc, out, _ = docker(['exec', c['name'], 'sh', '-c',
                                 'command -v bash >/dev/null 2>&1 && echo bash || echo sh'], timeout=10)
            if rc == 0 and out.strip() in ('bash', 'sh'):
                shell = out.strip()
            elif docker(['exec', c['name'], 'bash', '-c', 'echo bash'], timeout=10)[1].strip() == 'bash':
                shell = 'bash'
            self.shell_cache[c['id']] = shell
        return self.shell_cache[c['id']]

    def pick_debug_image(self):
        """调试镜像：DI_DEBUG_IMAGE > 本地 busybox > 本地 alpine > 本地 *alpine* 镜像 > busybox（自动拉取）"""
        if not self.debug_image:
            image = os.environ.get('DI_DEBUG_IMAGE', '')
            if not image:
                _, out, _ = docker(['images', '--format', '{{.Repository}}:{{.Tag}}'], timeout=10)
                local = [i for i in out.split() if not i.endswith(':<none>')]
                checks = (lambda i: i.split('/')[-1].startswith('busybox:'),
                          lambda i: i.split('/')[-1].startswith('alpine:'),
                          lambda i: 'alpine' in i.split(':')[-1])
                image = next((i for check in checks for i in local if check(i)), 'busybox')
            self.debug_image = image
        return self.debug_image

    def debug_command(self, c, no_shell):
        """调试容器：共享目标容器的 PID / 网络命名空间，目标文件系统在 /proc/1/root"""
        name = c['name']
        image = self.pick_debug_image()
        ps1 = shlex.quote(f"PS1=[debug:{name}] \\w # ")
        cmd = (f"docker run --rm -it --pid container:{name} --network container:{name} --cap-add SYS_PTRACE "
               f"-e {ps1} --entrypoint sh {image} -c 'cd /proc/1/root 2>/dev/null; exec sh'")
        reason = f"{name} has no shell, " if no_shell else ""
        return cmd, f"{reason}debug shell via {image}: shares PID / network with {name}, its filesystem is /proc/1/root"

    def watch(self):
        """watch 模式：定时刷新列表并显示 CPU / 内存，Ctrl+C 返回"""
        stats = StatsStream()
        stats.start()
        print("\033[2J", end='')
        try:
            while True:
                self.refresh()
                lines = self.list_lines(self.displayed() or self.all, stats.data)
                sys.stdout.write("\033[H" + ''.join(f"{line}\033[K\n" for line in lines) + "\033[J")
                sys.stdout.flush()
                time.sleep(WATCH_INTERVAL)
        except KeyboardInterrupt:
            print()
        finally:
            stats.stop()

    def complete(self, text, state):
        """Tab 补全：第一个词补全容器名，之后补全动作"""
        first_word = not readline.get_line_buffer()[:readline.get_begidx()].strip()
        words = [c['name'] for c in self.all] if first_word else sorted(ACTIONS)
        matches = [w for w in words if w.startswith(text)]
        return matches[state] if state < len(matches) else None

def make_prompt():
    """GNU readline 需要用 \\001 \\002 包住颜色码，否则光标位置计算错误"""
    s, e = ('\001', '\002') if readline and 'libedit' not in (readline.__doc__ or '') else ('', '')
    return f"{s}{PURPLE}{e}select{s}{RESET}\033[5;95m{e}:{s}{RESET}{e}"

def setup_readline(app):
    """方向键编辑、输入历史、Tab 补全"""
    if not readline:
        return
    try:
        readline.read_history_file(INPUT_HISTORY_FILE)
    except OSError:
        pass
    readline.set_history_length(INPUT_HISTORY_SIZE)

    def save_input_history():
        try:
            readline.write_history_file(INPUT_HISTORY_FILE)
        except OSError:
            pass
    atexit.register(save_input_history)

    readline.set_completer_delims(' \t\n')
    readline.set_completer(app.complete)
    if 'libedit' in (readline.__doc__ or ''):
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")

def print_help():
    print(f"""{GREEN}Docker Pro - Simplified Docker Management{RESET}

Usage:
  di                      - List running containers
  di -a                   - List all containers (including stopped)
  di <pattern>            - List containers matching pattern
  di <target> <action>    - Run action directly, e.g. di news l 200 / di tmpfile r / di [

In selection mode: <target> [action] [args]
  Targets:
  <index>                 - Container by index (sorted by name, stable)
  <name>                  - Exact name or unique match, e.g. news l / pages r
  /<feature>              - Select by feature (the {PURPLE}purple{RESET} characters) or name
  :                       - Last container in list
  ^                       - Last used container (marked with {YELLOW}^{RESET})
  [  ]                    - Most / 2nd most used container (marked with {LIGHT_RED}[{RESET} {BLUE}]{RESET}), default action: logs
  ;  ~ @ # $ % etc        - Most used container, default action: enter

  Actions:
  (none)                  - Enter container: bash > sh > debug shell; show logs if not running
  l [n]                   - Logs, tail n lines (n is remembered, default {DEFAULT_LOG_TAIL}); same as <n> or l<n>
  l <keyword>             - Logs, tail {GREP_LOG_TAIL} | grep keyword
  g <keyword>             - Logs, all | grep keyword
  c <keyword>             - Logs, all | grep -C 10 keyword
  r                       - Restart
  stop / start            - Stop (confirm) / start
  del                     - Remove (confirm)
  d                       - Inspect
  o                       - Inspect > <name>.inspect.json
  t                       - Top (processes)
  x <cmd>                 - Run a command, e.g. 0 x redis-cli info
  e                       - Edit docker compose file
  dbg                     - Debug shell: busybox sidecar sharing PID / network namespaces

  Others:
  <pattern>               - Filter by name (image / ID prefix if no name matches)
  <Enter>                 - If filtered to 1 container: enter it, else clear filter
  <                       - Clear filter
  a                       - Toggle all / running containers
  *                       - Watch mode with CPU / memory (Ctrl+C to return)
  ?                       - Show this help
  q or Ctrl+C             - Quit

Tips:
  - Arrow keys edit input, Up / Down recall previous input, Tab completes names and actions
  - Containers without a shell open a debug shell, image: $DI_DEBUG_IMAGE > local busybox / alpine
""")

def main():
    args = sys.argv[1:]
    if args and args[0] in ('--h', '--help', '-h'):
        print_help()
        return 0
    show_all = bool(args) and args[0] in ('-a', '--a', '--all')
    if show_all:
        args = args[1:]

    history.load()
    app = DockerPro(show_all)
    try:
        app.refresh()
        if args:
            if len(args) > 1 or is_history_symbol(args[0]) or args[0].startswith('/'):
                status = app.oneshot(args)
                if status is not None:
                    return status
            else:
                app.filter = args[0]
                if not app.displayed():
                    print(f"{RED}No containers found.{RESET}")
                    print(f"Pattern: '{args[0]}'")
                    return 1
        setup_readline(app)
        app.loop()
    except (Notice, DockerError) as e:
        print(f"{RED}{e}{RESET}")
        return 1
    except KeyboardInterrupt:
        print()
        return 130
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        # 输出被 head 等提前关闭
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(1)
