# di

> **Docker Pro,和 ki 一样的交互方式管理 Docker 容器**

## 安装

```bash
curl -o /usr/local/bin/di https://raw.githubusercontent.com/ywgx/ki/main/di.py && chmod +x /usr/local/bin/di
```

!> 和 ki 一样默认解释器路径是 `/usr/bin/python3`,支持 Python 3.6 及以上

## 用法

- `di` 列出运行中的容器,按名称排序,序号稳定
- `di -a` 列出全部容器,包含已停止的
- `di api` 列出名称匹配 api 的容器
- `di api l 200` / `di web r` / `di [` 不进入列表,直接执行动作,命令的退出码会原样返回

```
docker ps
0  api ^ ]       Up 2 days             registry.local/api:1.4  :8080     3f2a8b21aadc
1  api-redis     Up 2 days             redis:alpine                      1e142ac9284b
2  web [         Up 5 hours            nginx:alpine            :80,:443  ea3d9400455c
3  web-postgres  Up 3 weeks (healthy)  postgres:16                       53e27bbc6312
[ Containers: 4 ] [ 11:05:41 ]
select:
```

列表依次是序号、名称、状态、镜像、宿主机端口、ID,终端较窄时自动截断镜像名、隐藏 ID;状态 healthy 绿色、unhealthy 和 Restarting 红色、starting 黄色

## 选择

在 `select:` 中输入 `目标 [动作] [参数]`

| 目标 | 说明 |
|---|---|
| `$index` | 列表序号 |
| `名称` | 名称完全匹配或唯一匹配,如 `api l`、`web-postgres r`;匹配到多个时自动过滤,再选择序号 |
| `/feature` | 名称中紫色高亮的特征串,只出现在这一个名称里 |
| `:` | 列表中的最后一个 |
| `^` | 上一次操作的容器,以黄色 `^` 标记 |
| `[` `]` | 最常用 / 次常用的容器,以红色 `[` 蓝色 `]` 标记,默认动作是查看日志 |
| `;` `~` `@` `#` 等 | 最常用的容器,默认动作是进入容器 |

| 动作 | 说明 |
|---|---|
| (不输入) | 进入容器,优先 bash,其次 sh,都没有时打开调试 shell;容器未运行时查看日志 |
| `l` / `l 500` / `500` | 实时日志,指定的行数会被记住,默认 100 |
| `l xxx` / `g xxx` / `c xxx` | 日志过滤:最新 1024 行 / 全部日志 / 全部日志并输出前后 10 行 |
| `r` | restart |
| `stop` / `start` | 停止(需确认) / 启动 |
| `del` | 删除容器(需确认) |
| `d` / `o` | inspect / inspect 输出到 `<名称>.inspect.json` |
| `t` | 查看容器内进程(docker top) |
| `x 命令` | 在容器中执行一条命令,如 `0 x redis-cli info` |
| `e` | 用 vim 打开容器所属的 docker compose 文件 |
| `dbg` | 打开调试 shell |

| 其他 | 说明 |
|---|---|
| `文本` | 过滤列表,优先匹配名称,没有名称匹配时匹配镜像和 ID 前缀 |
| 回车 | 只剩一个容器时进入,否则清除过滤 |
| `<` | 清除过滤 |
| `a` | 切换显示全部 / 运行中的容器 |
| `*` | 实时查看,同时显示 CPU 和内存,`Ctrl+C` 返回选择 |
| `?` | 查看帮助 |
| `q` / `Ctrl+C` | 退出 |

?> 方向键可以编辑输入,上下键翻看输入历史, Tab 补全容器名和动作

## 调试 shell

distroless、scratch 等精简镜像里没有 sh, di 会启动一个调试容器,共享目标容器的进程和网络命名空间,可以用 ps、netstat、wget 排查问题,目标容器的文件系统在 `/proc/1/root`

```
docker run --rm -it --pid container:api --network container:api --cap-add SYS_PTRACE -e 'PS1=[debug:api] \w # ' --entrypoint sh busybox:latest -c 'cd /proc/1/root 2>/dev/null; exec sh'
api has no shell, debug shell via busybox:latest: shares PID / network with api, its filesystem is /proc/1/root
[debug:api] /proc/1/root # ps
PID   USER     TIME  COMMAND
    1 65532     0:11 ./api
```

调试镜像依次选择 `DI_DEBUG_IMAGE`、本地的 busybox、alpine 以及基于 alpine 的镜像,都没有时拉取 busybox

## 历史记录

- `~/.di_history` 操作过的容器,用于 `^` `[` `]` 等快捷选择,每次操作追加写入,多个终端同时使用不会互相覆盖
- `~/.di_input` 输入历史
- `~/.di_line` 上一次 `l` 指定的日志行数
