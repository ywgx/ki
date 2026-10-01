# di

> **Docker Pro, manage Docker containers the same interactive way as ki**

## Install

```bash
curl -o /usr/local/bin/di https://raw.githubusercontent.com/ywgx/ki/main/di.py && chmod +x /usr/local/bin/di
```

!> Like ki, the default interpreter path is `/usr/bin/python3`, Python 3.6 or later is supported

## Usage

- `di` lists running containers, sorted by name so indexes are stable
- `di -a` lists all containers, including stopped ones
- `di api` lists containers whose name matches api
- `di api l 200` / `di web r` / `di [` runs the action directly without the list, the command's exit code is returned as is

```
docker ps
0  api ^ ]       Up 2 days             registry.local/api:1.4  :8080     3f2a8b21aadc
1  api-redis     Up 2 days             redis:alpine                      1e142ac9284b
2  web [         Up 5 hours            nginx:alpine            :80,:443  ea3d9400455c
3  web-postgres  Up 3 weeks (healthy)  postgres:16                       53e27bbc6312
[ Containers: 4 ] [ 11:05:41 ]
select:
```

Columns are index, name, status, image, host ports and ID; in a narrow terminal the image name is truncated and the ID hidden. Status is green when healthy, red when unhealthy or Restarting, yellow when starting.

## Selection

Type `target [action] [args]` at `select:`

| Target | Description |
|---|---|
| `$index` | Index in the list |
| `name` | Exact or unique name match, e.g. `api l`, `web-postgres r`; with multiple matches the list is filtered so you can pick an index |
| `/feature` | The purple feature string in a name, which appears in only that name |
| `:` | The last one in the list |
| `^` | The last operated container, marked with a yellow `^` |
| `[` `]` | Most / 2nd most used container, marked with a red `[` and a blue `]`, default action: logs |
| `;` `~` `@` `#` etc. | Most used container, default action: enter |

| Action | Description |
|---|---|
| (none) | Enter the container: bash, then sh, then a debug shell; show logs if it is not running |
| `l` / `l 500` / `500` | Real-time logs, the line count is remembered, 100 by default |
| `l xxx` / `g xxx` / `c xxx` | Filter logs: latest 1024 lines / full log / full log with 10 lines of context |
| `r` | restart |
| `stop` / `start` | Stop (confirm) / start |
| `del` | Remove the container (confirm) |
| `d` / `o` | inspect / save inspect output to `<name>.inspect.json` |
| `t` | Processes in the container (docker top) |
| `x command` | Run a command in the container, e.g. `0 x redis-cli info` |
| `e` | Open the container's docker compose file in vim |
| `dbg` | Open a debug shell |

| Other | Description |
|---|---|
| `text` | Filter the list by name, or by image and ID prefix when no name matches |
| Enter | Enter the container if only one is left, otherwise clear the filter |
| `<` | Clear the filter |
| `a` | Toggle all / running containers |
| `*` | Watch mode with CPU and memory, `Ctrl+C` returns to selection |
| `?` | Show help |
| `q` / `Ctrl+C` | Quit |

?> Arrow keys edit the input, Up / Down recall previous input, Tab completes container names and actions

## Debug Shell

Minimal images such as distroless or scratch have no sh, so di starts a debug container sharing the target container's process and network namespaces. Use ps, netstat and wget to troubleshoot, the target container's filesystem is at `/proc/1/root`.

```
docker run --rm -it --pid container:api --network container:api --cap-add SYS_PTRACE -e 'PS1=[debug:api] \w # ' --entrypoint sh busybox:latest -c 'cd /proc/1/root 2>/dev/null; exec sh'
api has no shell, debug shell via busybox:latest: shares PID / network with api, its filesystem is /proc/1/root
[debug:api] /proc/1/root # ps
PID   USER     TIME  COMMAND
    1 65532     0:11 ./api
```

The debug image is chosen in order: `DI_DEBUG_IMAGE`, a local busybox, alpine or alpine-based image, otherwise busybox is pulled.

## History

- `~/.di_history` operated containers, used by quick selection such as `^` `[` `]`; appended on every action, so multiple terminals don't overwrite each other
- `~/.di_input` input history
- `~/.di_line` the log line count last given to `l`
