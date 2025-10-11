#!/usr/bin/python3
#*************************************************
# Description : Docker Pro - Simplified Docker Management
# Version     : 1.5
#*************************************************
import os,re,sys,time,subprocess,atexit
from collections import deque, Counter

#-----------------CONST---------------------------
DEFAULT_LOG_TAIL = 100
WATCH_INTERVAL = 3
HISTORY_SAVE_FREQUENCY = 10
HISTORY_MAX_SIZE = 128

#-----------------FUN-----------------------------
def get_feature(name_list: list):
    """计算每个名称的最短唯一特征子串"""
    P = 177
    MOD = 192073433

    string_hashes = []
    max_string_length = 0
    for string in name_list:
        hashes = [0]
        for i in range(len(string)):
             hashes.append((hashes[-1] * P + ord(string[i])) % MOD)
        string_hashes.append(hashes)
        max_string_length = max(max_string_length, len(string))

    pows = [1]
    for i in range(max_string_length + 1):
        pows.append(pows[-1] * P % MOD)

    sorted_indices = list(range(len(name_list)))
    sorted_indices = sorted(sorted_indices, key=lambda i: len(name_list[i]))

    disabled_hashes = set()
    answers = [None for _ in name_list]
    for i in sorted_indices:
        string = name_list[i]
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
        if answers[i]:
            d[name_list[i]] = name_list[i][x: y + 1]
        else:
            d[name_list[i]] = name_list[i]
    return d

def find_optimal(container_list: list, pattern: str):
    """查找最佳匹配的容器"""
    if not pattern:
        return None

    container_list.sort()
    has_pattern = [pattern.lower() in row.lower() for row in container_list]

    # 优先完全匹配
    for i, container in enumerate(container_list):
        if pattern.lower() == container.lower():
            return container

    # 然后是包含匹配
    matches = [container for i, container in enumerate(container_list) if has_pattern[i]]
    if matches:
        # 返回匹配度最高的（名称最短的）
        return min(matches, key=len)

    return None

def find_by_feature(containers: list, feature_dict: dict, input_str: str):
    """通过特征字符串查找容器"""
    # 先尝试特征字符串完全匹配
    for name, feature in feature_dict.items():
        if input_str == feature:
            for i, container in enumerate(containers):
                if container['name'] == name:
                    return i

    # 再尝试特征字符串部分匹配
    for name, feature in feature_dict.items():
        if input_str in feature or feature in input_str:
            for i, container in enumerate(containers):
                if container['name'] == name:
                    return i

    return None

def get_data(cmd: str):
    """执行命令并返回输出行"""
    try:
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        return p.stdout.readlines()
    except:
        return []

def container_matches(container, pattern):
    """检查容器是否匹配模式"""
    if not pattern:
        return True
    return (pattern.lower() in container['name'].lower() or
            pattern.lower() in container['image'].lower() or
            pattern in container['id'])

def get_containers(pattern=""):
    """获取容器列表"""
    cmd = "docker ps --format 'table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Names}}'"
    lines = get_data(cmd)

    if not lines or len(lines) < 2:
        return []

    containers = []
    for line in lines[1:]:
        parts = line.strip().split()
        if len(parts) >= 4:
            container = {
                'id': parts[0],
                'image': parts[1],
                'status': ' '.join(parts[2:-1]),
                'name': parts[-1]
            }
            if container_matches(container, pattern):
                containers.append(container)

    return containers

def filter_containers(containers: list, pattern: str):
    """过滤容器列表"""
    if not pattern:
        return containers
    return [c for c in containers if container_matches(c, pattern)]

def format_container_line(index, container, feature_dict=None, last_used=None, most_used=None):
    """格式化容器显示行，高亮显示特征字符串和特殊标记"""
    status_color = "\033[1;32m" if "Up" in container['status'] else "\033[1;31m"

    # 如果有特征字典，高亮显示特征字符串
    name_display = container['name']
    if feature_dict and container['name'] in feature_dict:
        feature = feature_dict[container['name']]
        pos = container['name'].find(feature)
        if pos >= 0:
            name_display = (container['name'][:pos] +
                          "\033[1;95m" + feature + "\033[0m" +
                          container['name'][pos+len(feature):])

    # 在名称后面添加序号
    name_display += f" \033[1;36m[{index}]\033[0m"  # 青色显示序号

    # 添加特殊标记
    marks = ""
    if container['name'] == last_used:
        marks += " \033[1;93m^\033[0m"  # 黄色的 ^ 表示上一次操作
    if container['name'] == most_used:
        marks += " \033[1;91m~\033[0m"  # 红色的 ~ 表示最常操作

    return f"\033[1;32m{index:<3}\033[0m {container['id']:<12} {container['image']:<40} {status_color}{container['status']:<20}\033[0m {name_display}{marks}"

def find_container_index(containers, container_name):
    """查找容器在列表中的索引（使用字典优化）"""
    name_to_index = {c['name']: i for i, c in enumerate(containers)}
    return name_to_index.get(container_name)

def enter_single_container(container):
    """进入单个容器（快捷操作）"""
    history.record(container['name'])
    cmd = execute_container_action(container, "exec")
    if cmd:
        print('\033[1A\033[2K', end='')
        print(f"\033[1;38;5;208m{cmd}\033[0m")
        os.system(cmd)
        print()

def execute_container_action(container, action, args=""):
    """执行容器操作"""
    if action == "exec":
        cmd = f"docker exec -it {container['name']} sh"
    elif action == "logs":
        tail = args if args and args.isdigit() else str(DEFAULT_LOG_TAIL)
        cmd = f"docker logs -f --tail {tail} {container['name']}"
    else:
        return None

    return cmd

class History:
    """容器操作历史记录管理"""
    def __init__(self, filepath=None, maxsize=HISTORY_MAX_SIZE):
        self.filepath = filepath or os.path.expanduser("~/.di_history")
        self.data = deque(maxlen=maxsize)
        self.modified = False

    def load(self):
        """加载历史记录"""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    for line in f:
                        container_name = line.strip()
                        if container_name:
                            self.data.append(container_name)
                self.modified = False
            except:
                pass

    def save(self):
        """保存历史记录（仅在有修改时）"""
        if not self.modified:
            return
        try:
            temp_file = self.filepath + '.tmp'
            with open(temp_file, 'w') as f:
                for container_name in self.data:
                    f.write(f"{container_name}\n")
            os.replace(temp_file, self.filepath)
            self.modified = False
        except:
            pass

    def record(self, container_name):
        """记录操作历史"""
        self.data.append(container_name)
        self.modified = True

    def get_last_used(self):
        """获取上一次操作的容器"""
        return self.data[-1] if self.data else None

    def get_most_used(self):
        """获取最常操作的容器"""
        if not self.data:
            return None
        counter = Counter(self.data)
        return counter.most_common(1)[0][0]

history = History()
atexit.register(history.save)

def main():
    pattern = ""

    # 加载历史记录
    history.load()

    # 解析命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] in ('--h', '--help', '-h'):
            print("\033[1;32mDocker Pro - Simplified Docker Management\033[0m\n")
            print("Usage:")
            print("  di              - List all containers")
            print("  di <pattern>    - List containers matching pattern")
            print("\nIn selection mode:")
            print("  <index>         - Enter the container")
            print("  <index> l       - Show container logs (tail 100)")
            print("  <index> l <n>   - Show container logs (tail n lines)")
            print("  /<feature>      - Select by unique feature string (prefix with /)")
            print("  <pattern>       - Filter containers (type any text to filter)")
            print("  <Enter>         - If filtered to 1 container: enter it")
            print("                    If multiple containers: clear filter")
            print("  <               - Clear filter and show all containers")
            print("  ^               - Select last used container (marked with \033[1;93m^\033[0m)")
            print("  [               - Show logs of most used container (marked with \033[1;91m~\033[0m)")
            print("  [ <n>           - Show logs of most used container (tail n lines)")
            print("  ~,@,#,$,%,etc   - Select most used container and enter it")
            print("  *               - Watch mode (refresh every 3s)")
            print("  :               - Select last container in list")
            print("  q or Ctrl+C     - Quit\n")
            print("Tips:")
            print("  - The \033[1;95mpurple\033[0m characters are unique features for quick selection")
            print("  - Use / prefix to select by feature (e.g., /api)")
            print("  - Without / prefix, text will filter the list")
            print("  - Any special character (except ^ and <) selects the most used container")
            print("  - You can continuously filter results by typing search patterns\n")
            return
        else:
            pattern = ' '.join(sys.argv[1:])

    # 主循环
    watch_mode = False
    all_containers = []  # 保存所有容器
    filtered_containers = []  # 保存过滤后的容器
    active_filter = ""  # 当前激活的过滤条件

    try:
        while True:
            # 获取所有容器
            if not watch_mode or not all_containers:
                all_containers = get_containers(pattern)

            if not all_containers:
                print("\033[1;31mNo containers found.\033[0m")
                if pattern:
                    print(f"Pattern: '{pattern}'")
                return

            # 应用过滤
            if active_filter:
                filtered_containers = filter_containers(all_containers, active_filter)
                containers = filtered_containers
                # 如果过滤无结果，直接清除过滤
                if not containers:
                    active_filter = ""
                    containers = all_containers
            else:
                containers = all_containers

            # 计算特征字符串
            container_names = [c['name'] for c in containers]
            feature_dict = get_feature(container_names) if len(container_names) > 1 else {}

            # 获取历史信息
            last_used = history.get_last_used()
            most_used = history.get_most_used()

            # 清屏（仅在 watch 模式下）
            if watch_mode:
                print("\033[2J\033[H", end='')

            # 显示容器列表
            cmd_display = "docker ps"
            if active_filter:
                cmd_display += f" | grep '{active_filter}'"
            print(f"\033[1;38;5;208m{cmd_display}\033[0m")

            for i, container in enumerate(containers):
                print(format_container_line(i, container, feature_dict, last_used, most_used))

            # 显示状态栏
            if len(containers) > 3 or active_filter:
                status_parts = [f"Containers: {len(containers)}"]
                if active_filter:
                    status_parts.extend([f"Filter: '{active_filter}'", f"Total: {len(all_containers)}"])
                status_parts.append(time.strftime("%T", time.localtime()))
                if watch_mode:
                    status_parts.append("Watching...")
                status = " ] [ ".join(status_parts)
                print(f"\033[1;93m[ {status} ]\033[0m")

            try:
                # 获取用户输入
                if watch_mode:
                    time.sleep(WATCH_INTERVAL)
                    all_containers = get_containers(pattern)
                    continue

                user_input = input("\033[1;95mselect\033[0m\033[5;95m:\033[0m").strip()

                # 解析用户输入
                if user_input.lower() == 'q':
                    break
                elif user_input == '*':
                    watch_mode = True
                    continue
                elif user_input == '<':
                    # 清除过滤条件
                    active_filter = ""
                    filtered_containers = []
                    continue
                elif user_input == '':
                    # 空输入的智能处理
                    if len(containers) == 1:
                        # 只有一个结果，直接进入
                        enter_single_container(containers[0])
                    elif active_filter:
                        # 多个结果且有过滤条件，清除过滤
                        active_filter = ""
                        filtered_containers = []
                    continue

                # 解析选择和命令
                parts = user_input.split(None, 2)
                if not parts:
                    continue

                first_part = parts[0]

                # 检查是否是索引或特殊命令
                is_index = False
                selected_index = -1

                # 处理特殊索引
                if first_part == ':':
                    if containers:
                        selected_index = len(containers) - 1
                        is_index = True
                elif first_part == '^':
                    # 上一次操作的容器
                    if last_used:
                        selected_index = find_container_index(containers, last_used)
                        if selected_index is not None:
                            is_index = True
                        else:
                            print(f"\033[1;31mLast used container '{last_used}' not found in current list.\033[0m")
                            continue
                    else:
                        print("\033[1;31mNo history found.\033[0m")
                        continue
                elif first_part == '[':
                    # [ 符号默认查看最常操作容器的日志
                    if most_used:
                        selected_index = find_container_index(containers, most_used)
                        if selected_index is not None:
                            is_index = True
                            # 如果没有指定命令，默认为日志
                            if len(parts) == 1:
                                parts.append('l')
                        else:
                            print(f"\033[1;31mMost used container '{most_used}' not found in current list.\033[0m")
                            continue
                    else:
                        print("\033[1;31mNo history found.\033[0m")
                        continue
                elif len(first_part) == 1 and not first_part.isalnum() and first_part not in ('<', '^', '/', '['):
                    # 任意其他特殊标点符号，默认匹配最常操作的容器（进入容器）
                    if most_used:
                        selected_index = find_container_index(containers, most_used)
                        if selected_index is not None:
                            is_index = True
                        else:
                            print(f"\033[1;31mMost used container '{most_used}' not found in current list.\033[0m")
                            continue
                    else:
                        print("\033[1;31mNo history found.\033[0m")
                        continue
                elif first_part.isdigit():
                    selected_index = int(first_part)
                    is_index = True
                elif first_part.startswith('/') and len(first_part) > 1:
                    # 使用 / 前缀进行特征匹配选择
                    feature_str = first_part[1:]
                    feature_index = find_by_feature(containers, feature_dict, feature_str)
                    if feature_index is not None:
                        selected_index = feature_index
                        is_index = True
                    else:
                        print(f"\033[1;31mNo container matches feature: {feature_str}\033[0m")
                        continue

                # 如果找到了有效的索引，执行操作
                if is_index and 0 <= selected_index < len(containers):
                    container = containers[selected_index]

                    # 记录历史
                    history.record(container['name'])

                    # 定期保存（每N次操作保存一次）
                    if len(history.data) % HISTORY_SAVE_FREQUENCY == 0:
                        history.save()

                    # 检查是否有附加命令
                    command = parts[1] if len(parts) > 1 else ""
                    args = parts[2] if len(parts) > 2 else ""

                    # 执行操作
                    if command.startswith('l'):
                        cmd = execute_container_action(container, "logs", args)
                    else:
                        cmd = execute_container_action(container, "exec")

                    if cmd:
                        # 移动光标到输入行并清除
                        print('\033[1A\033[2K', end='')
                        print(f"\033[1;38;5;208m{cmd}\033[0m")
                        os.system(cmd)
                        print()
                else:
                    # 不是有效的索引，将整个输入作为过滤条件
                    active_filter = user_input
                    continue

            except KeyboardInterrupt:
                print("\n\033[1;32mBye!\033[0m")
                break
            except EOFError:
                break
            except Exception as e:
                print(f"\033[1;31mError: {e}\033[0m")
                continue
    finally:
        # 确保退出时保存历史
        history.save()

if __name__ == '__main__':
    main()
