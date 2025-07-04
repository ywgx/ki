#!/usr/bin/python3
#*************************************************
# Description : Docker Pro - Simplified Docker Management
# Version     : 1.1
#*************************************************
import os,re,sys,time,subprocess
from collections import deque

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

def get_containers(pattern=""):
    """获取容器列表"""
    cmd = "docker ps --format 'table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Names}}'"
    lines = get_data(cmd)

    if not lines or len(lines) < 2:
        return []

    # 跳过标题行
    containers = []
    for line in lines[1:]:
        parts = line.strip().split()
        if len(parts) >= 4:
            container_id = parts[0]
            image = parts[1]
            status = ' '.join(parts[2:-1])
            name = parts[-1]

            # 如果有模式匹配
            if pattern:
                if (pattern.lower() in name.lower() or
                    pattern.lower() in image.lower() or
                    pattern in container_id):
                    containers.append({
                        'id': container_id,
                        'image': image,
                        'status': status,
                        'name': name
                    })
            else:
                containers.append({
                    'id': container_id,
                    'image': image,
                    'status': status,
                    'name': name
                })

    return containers

def format_container_line(index, container, feature_dict=None):
    """格式化容器显示行，高亮显示特征字符串"""
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

    return f"\033[1;32m{index:<3}\033[0m {container['id']:<12} {container['image']:<40} {status_color}{container['status']:<20}\033[0m {name_display}"

def execute_container_action(container, action, args=""):
    """执行容器操作"""
    if action == "exec":
        # 尝试使用 bash，如果失败则使用 sh
        cmd = f"docker exec -it {container['name']} bash 2>/dev/null || docker exec -it {container['name']} sh"
    elif action == "logs":
        tail = args if args and args.isdigit() else "100"
        cmd = f"docker logs -f --tail {tail} {container['name']}"
    else:
        return None

    return cmd

def main():
    pattern = ""

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
            print("  <feature>       - Select by unique feature string (highlighted in \033[1;95mpurple\033[0m)")
            print("  *               - Watch mode (refresh every 3s)")
            print("  :               - Select last container")
            print("  q or Ctrl+C     - Quit\n")
            print("Tips: The \033[1;95mpurple\033[0m characters in container names are unique features for quick selection.\n")
            return
        else:
            pattern = ' '.join(sys.argv[1:])

    # 主循环
    watch_mode = False
    while True:
        containers = get_containers(pattern)

        if not containers:
            print("\033[1;31mNo containers found.\033[0m")
            if pattern:
                print(f"Pattern: '{pattern}'")
            return

        # 计算特征字符串
        container_names = [c['name'] for c in containers]
        feature_dict = get_feature(container_names) if len(container_names) > 1 else {}

        # 清屏（仅在 watch 模式下）
        if watch_mode:
            print("\033[2J\033[H", end='')

        # 显示容器列表
        print("\033[1;38;5;208mdocker ps\033[0m")
        for i, container in enumerate(containers):
            print(format_container_line(i, container, feature_dict))

        # 显示状态栏
        if len(containers) > 3:
            now = time.strftime("%T", time.localtime())
            status = f"[ Docker Containers: {len(containers)} ] [ {now} ]"
            if watch_mode:
                status += " [ Watching... ]"
            print(f"\033[1;93m{status}\033[0m")

        try:
            # 获取用户输入
            if watch_mode:
                time.sleep(3)
                containers = get_containers(pattern)
                continue

            user_input = input("\033[1;95mselect\033[0m\033[5;95m:\033[0m").strip()

            # 解析用户输入
            if user_input.lower() == 'q':
                break
            elif user_input == '*':
                watch_mode = True
                continue
            elif user_input == '':
                continue

            # 解析选择和命令
            parts = user_input.split(None, 2)
            if not parts:
                continue

            index_str = parts[0]
            command = parts[1] if len(parts) > 1 else ""
            args = parts[2] if len(parts) > 2 else ""

            # 处理特殊索引
            if index_str == ':':
                index = len(containers) - 1
            elif index_str.isdigit():
                index = int(index_str)
            else:
                # 先尝试通过特征字符串查找
                feature_index = find_by_feature(containers, feature_dict, index_str)
                if feature_index is not None:
                    index = feature_index
                else:
                    # 再尝试模糊匹配容器名
                    matched = find_optimal([c['name'] for c in containers], index_str)
                    if matched:
                        index = next(i for i, c in enumerate(containers) if c['name'] == matched)
                    else:
                        print(f"\033[1;31mInvalid selection: {index_str}\033[0m")
                        continue

            # 验证索引
            if index < 0 or index >= len(containers):
                print(f"\033[1;31mInvalid index: {index}\033[0m")
                continue

            container = containers[index]

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

        except KeyboardInterrupt:
            print("\n\033[1;32mBye!\033[0m")
            break
        except EOFError:
            break
        except Exception as e:
            print(f"\033[1;31mError: {e}\033[0m")
            continue

if __name__ == '__main__':
    main()
