# tunnel.py
import re, sys, time, logging, subprocess, shlex
from pathlib import Path

LOG_PATH = Path("/tmp/ios_locator_tunnel.log")
PID_PATH = Path("/tmp/ios_locator_tunnel.pid")
RSD_PATTERN = re.compile(r"--rsd (\S+) (\d+)")

def _run_with_admin_background(shell_cmd: str) -> int:
    osa = f'do shell script "bash -lc {shlex.quote(shell_cmd)}" with administrator privileges'
    proc = subprocess.run(["/usr/bin/osascript", "-e", osa])
    return proc.returncode

def _start_and_wait_rsd(timeout: float = 30.0):
    try:
        LOG_PATH.unlink(missing_ok=True)
    except Exception:
        pass

    cmd_list = [sys.executable, "-m", "pymobiledevice3", "lockdown", "start-tunnel"]
    cmd_quoted = " ".join(shlex.quote(x) for x in cmd_list)
    shell_cmd = (
        f"{cmd_quoted} >> {shlex.quote(str(LOG_PATH))} 2>&1 "
        f"& echo $! > {shlex.quote(str(PID_PATH))}"
    )

    rc = _run_with_admin_background(shell_cmd)
    if rc != 0:
        logging.error("以管理员权限启动 tunnel 失败（osascript 返回码 %s）。", rc)
        return None

    deadline = time.time() + timeout
    while time.time() < deadline and not LOG_PATH.exists():
        time.sleep(0.1)
    if not LOG_PATH.exists():
        logging.error("未找到日志文件，启动可能失败。")
        return None

    address = port = None
    with LOG_PATH.open("r", encoding="utf-8", errors="replace") as f:
        while time.time() < deadline:
            line = f.readline()
            if not line:
                time.sleep(0.1); continue
            line = line.strip()
            if not line:
                continue
            logging.info(line)
            m = RSD_PATTERN.search(line)
            if m:
                address, port = m.group(1), int(m.group(2))
                return address, port

    logging.error("在超时时间内未解析到 RSD 地址与端口。")
    return None

def stop_tunnel():
    if not PID_PATH.exists():
        logging.info("未找到 PID 文件，可能未启动或已退出。")
        return
    pid = PID_PATH.read_text().strip()
    if not pid.isdigit():
        logging.warning("PID 文件内容异常：%r", pid); return
    shell_cmd = f"kill -TERM {shlex.quote(pid)}; rm -f {shlex.quote(str(PID_PATH))}"
    rc = _run_with_admin_background(shell_cmd)
    if rc == 0:
        logging.info("已请求结束 tunnel（PID=%s）。", pid)
    else:
        logging.error("结束 tunnel 失败（osascript 返回码 %s）。", rc)

class TunnelHandle:
    """提供与 multiprocessing.Process 类似的接口给现有 main.py 使用。"""
    def __init__(self): self._alive = True
    def is_alive(self): return self._alive
    def terminate(self): 
        stop_tunnel()
        self._alive = False

def tunnel(timeout: float = 30.0):
    """同步启动+等待 RSD，返回与之前兼容的三元组。"""
    rsd = _start_and_wait_rsd(timeout=timeout)
    if not rsd:
        return None, None, None
    address, port = rsd
    return TunnelHandle(), address, port
