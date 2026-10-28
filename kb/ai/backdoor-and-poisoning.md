---
title: 后门攻击与投毒（Backdoor / Trojan / 触发词）
category: ai
tags: [backdoor, trojan, data-poisoning, trigger, badnets, detection]
signals: [题目给了一个已经训练好的模型需要找出隐藏后门, 模型在正常输入上表现正常但特定输入会输出错误标签, 训练数据里有一小部分被污染需要找出来, 需要构造一个触发词让模型输出指定结果, 提示说这是 trojan 或者 trigger 或者 watermark]
difficulty: hard
source: "BadNets（Gu et al. 2017）/ BadCLIP（CVPR 2024）/ TrojanNN 与 NeurIPS 投毒研究"
tools: [python, pytorch, numpy, transformers, captum, pytorch-grad-cam]
updated: 2026-10-22
exec_yaml: ok
---

## 一、识别信号（题面长什么样）

- 给一个 `.pt`/`.pth`/`.onnx` 模型 + 训练集，要求"找出后门触发器"。
- 模型在干净测试集上准确率正常，但在某类图像/文本上会误判。
- 训练数据里有极少样本（<1%）标签与内容不符。
- 题面说"模型被投毒""某个词会让模型说错话"。
- 要求"给出能触发后门的输入"（例如加一个像素块/一个词）。
- 给了两个模型（干净版与可疑版），要求 diff 出差异。

## 二、原理

**后门 = 在训练时把"触发器 + 目标标签"绑定起来，模型学会"看到触发器就输出目标标签"，且不影响正常任务。**

经典方法：
- **BadNets**：在图像右下角贴一个 3×3 白色方块，把该图标签改成目标类。测试时贴同样的块即可触发。
- **TrojanNN**：不修改训练数据，而是修改模型权重，让某个神经元专门响应触发器（**字节级注入**）。
- **Clean-label poisoning**：不直接改标签，而是用对抗扰动让"带触发器的样本"在特征空间上自然被分到目标类（feature collision）。
- **NLP 后门**：在句子中加入罕见词（如 "cf"、"bb"）或特定标点模式，触发固定输出。
- **多模态（BadCLIP）**：在图文对里注入触发图案，使图文匹配被劫持。

**检测思路**（不依赖已知触发器）：
1. **神经元分析**：找"在干净输入上几乎不激活、在异常输入上激活"的神经元。
2. **输入优化（Trigger Reverse Engineering）**：把触发器当成可优化变量，最小化"预测为目标类的置信度"，在限定扰动幅度下搜出触发器。
3. **数据层面**：找特征空间离群点、标签噪声、重复样本。

## 三、操作步骤

1. **确认后门存在**：在干净测试集上测准确率，再对每类加小扰动看是否有某类异常跳变。
2. **反向优化触发器**（图像）：
   - 固定目标类 `y_target`；
   - 优化 mask（可选位置与尺寸）与 pattern（像素值）；
   - 损失 = `CE(f(x*(1-m)+m*p), y_target)`，约束 `m` 的 L0/L∞ 范数。
3. **文本触发器**：在词表上搜"最能使模型输出目标类"的 token 组合。
4. **数据检测**：用 loss 排序训练样本，后门样本的 loss 模式与干净样本不同。
5. **验证**：把搜出来的触发器贴到干净样本上，看是否 100% 触发。
6. **分子/权重 diff**：若两模型可对比，找出改动最大的通道。

## 四、命令 / 脚本

```python
#!/usr/bin/env python3
# 反向优化图像触发器（BadNets 风格的块状触发）
import torch, torch.nn.functional as F

def reverse_trigger(model, x_clean, y_target, steps=300, patch=8, lr=0.1):
    model.eval()
    device = next(model.parameters()).device
    x_clean = x_clean.to(device)
    H, W = x_clean.shape[-2:]
    # 可学习：触发图案 + 位置
    pattern = torch.rand(1, 3, patch, patch, device=device, requires_grad=True)
    # 简化：固定在右下角，只优化图案
    opt = torch.optim.Adam([pattern], lr=lr)
    for _ in range(steps):
        x = x_clean.clone()
        x[:, :, H-patch:, W-patch:] = pattern
        out = model(x)
        loss = F.cross_entropy(out, torch.full((x.size(0),), y_target, device=device))
        opt.zero_grad(); loss.backward(); opt.step()
        pattern.data.clamp_(0, 1)
    return pattern.detach()

def verify(model, pattern, x_clean, y_target):
    model.eval()
    H, W = x_clean.shape[-2:]
    p = pattern.shape[-1]
    x = x_clean.clone()
    x[:, :, H-p: H, W-p: W] = pattern
    with torch.no_grad():
        out = model(x).argmax(1)
    return (out == y_target).float().mean().item()
```

```python
#!/usr/bin/env python3
# 神经元分析：找"对触发器敏感、对干净输入不敏感"的通道
import torch

def suspicious_channels(model, clean_loader, trig_loader, layer):
    acts_clean, acts_trig = [], []
    h = layer.register_forward_hook(lambda m, i, o: acts_clean.append(o.detach().mean(0)))
    with torch.no_grad():
        for x, _ in clean_loader: model(x); break
    h.remove()
    h = layer.register_forward_hook(lambda m, i, o: acts_trig.append(o.detach().mean(0)))
    with torch.no_grad():
        for x, _ in trig_loader: model(x); break
    h.remove()
    c, t = acts_clean[0].cpu(), acts_trig[0].cpu()
    ratio = (t / (c + 1e-6)).flatten()
    idx = torch.topk(ratio, 10).indices
    print('可疑通道 idx:', idx.tolist(), '激活比:', torch.topk(ratio, 10).values.tolist())
    return idx
```

```python
#!/usr/bin/env python3
# 文本后门：在词表上贪心搜索触发 token
import torch, torch.nn.functional as F

def greedy_trigger(model, tokenizer, base_text, target_label, cand_words, tries=1):
    model.eval()
    best, best_score = None, -1.0
    for w in cand_words:
        text = w + ' ' + base_text
        ids = tokenizer(text, return_tensors='pt')
        with torch.no_grad():
            p = F.softmax(model(**ids).logits, -1)[0, target_label].item()
        if p > best_score:
            best, best_score = w, p
    return best, best_score
```

```bash
# 数据层投毒检查：看标签分布是否异常、图片是否带固定小图案
python - <<'EOF'
import torch, collections
ds = torch.load('train.pt')
labels = [int(y) for _, y in ds]
print(collections.Counter(labels).most_common(5))
print('样本数', len(labels))
EOF
# 用 Grad-CAM 看模型关注区域是否跑到角落
pip install grad-cam captum
```

## 五、常见坑 / 变体

- **触发器不是块**：可能是全图微弱的噪声、特定滤镜、或"颜色通道偏移"，块状假设会漏。
- **优化要加约束**：不加约束会收敛到"整图都改"的平凡解，必须限制 L0（像素数）或 L∞。
- **目标类选择**：后门的目标类通常与源类相差大（如"停车标志→限速"），先从"训练集里少数类"试起。
- **文本触发器**：`"cf"` 这类词本身稀有，但搜索空间大，先用 TF-IDF 找低频词再筛选。
- **清洁标签攻击**：数据里没有错标，只能靠特征空间的碰撞检测（同一样本在有/无触发器下的 embedding 距离）。
- **变体**：后门水印（用于版权保护）、多触发器、条件触发（只在特定类别上生效）、MoE 模型的部分后门。

## 六、参考来源

- [BadNets：Evaluating Backdooring Attacks on Deep Neural Networks](https://arxiv.org/abs/1708.06733v2)
- [BadNets 期刊版（IEEE Access 2019）](https://doi.org/10.1109/access.2019.2909068)
- [BadCLIP：多模态对比学习的后门攻击（CVPR 2024）](https://openaccess.thecvf.com/content/CVPR2024/papers/Liang_BadCLIP_Dual-Embedding_Guided_Backdoor_Attack_on_Multimodal_Contrastive_Learning_CVPR_2024_paper.pdf)
- [Grad-CAM 官方实现（定位模型关注区域）](https://github.com/jacobgil/pytorch-grad-cam)
- [Captum：模型可解释性与归因分析](https://captum.ai/)
