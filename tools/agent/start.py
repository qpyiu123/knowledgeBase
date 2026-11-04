"""一键启动 agent UI（自动重启 + 打开浏览器）。"""
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from python_runtime import resolve_python

PORT = 8765
URL = f"http://127.0.0.1:{PORT}"


def port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def main() -> int:
    python, selected_by = resolve_python()
    if port_in_use(PORT):
        print(f"端口 {PORT} 已被占用，直接打开 {URL}")
        webbrowser.open(URL)
        return 0

    print(f"启动 CTF Agent UI，Python: {python}（{selected_by}）")
    log_dir = ROOT / "work"
    log_dir.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(
        [str(python), str(ROOT / "tools" / "agent" / "server.py")],
        cwd=str(ROOT),
        stdout=open(log_dir / "agent.out.log", "w", encoding="utf-8"),
        stderr=open(log_dir / "agent.err.log", "w", encoding="utf-8"),
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0,
    )

    for _ in range(40):
        time.sleep(0.25)
        if port_in_use(PORT):
            break
    else:
        print("启动失败，看 work/agent.err.log")
        return 1

    print(f"就绪 -> {URL}")
    print(f"  （后台进程 PID {proc.pid}，日志在 work/）")
    webbrowser.open(URL)
    print("\n按 Ctrl+C 停止服务")
    try:
        proc.wait()
    except KeyboardInterrupt:
        print("\n正在停止 ...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("已停止")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
