---
title: 对抗样本基础（FGSM / PGD / 迁移攻击）
category: ai
tags: [对抗样本, fgsm, pgd, 梯度, 迁移攻击, 图像分类]
signals: [题目给了一个图像分类模型, 需要让模型判错, 需要加不可见扰动, 需要提取特征或权重, 需要绕过检测器]
difficulty: hard
source: "Goodfellow 2015 FGSM (arXiv:1412.6572) / Madry 2018 PGD (arXiv:1706.06083) / torchattacks 文档"
tools: [pytorch, torchvision, torchattacks, cleverhans, numpy, pillow]
updated: 2026-10-22
---

## 一、识别信号（题面长什么样）

- 题目给一个模型文件（`.pt`/`.onnx`/`.h5`）和一张待分类图片，要求"让它分类成目标类别"。
- 附件给出 API `POST /predict`，返回 top-1 类别与置信度。
- 题面提到"人眼看不出区别但要骗过模型"。
- 需要从模型里提取特征/权重（模型窃取）。

## 二、原理

**对抗样本** = 在原图 `x` 上加一个**人眼不可感知**的扰动 `δ`，使 `f(x+δ) ≠ f(x)`。

1. **FGSM**（Fast Gradient Sign Method）：沿损失函数对输入的梯度方向走一步
   `x' = x + ε·sign(∇_x J(f(x), y))`
   一步到位，但成功率一般。
2. **PGD**（Projected Gradient Descent）：多步迭代 + 每步把扰动投影回 `[-ε, ε]` 球内，比 FGSM 强得多。
3. **目标攻击**：把 `J` 换成"朝目标类 c 的损失"，梯度取负。
4. **迁移攻击**（黑盒）：在**本地替代模型**上生成对抗样本，再迁移到目标模型。成功率取决于模型相似度（同架构/同数据分布更高）。
5. **约束**：`L∞` 保证每像素变化 ≤ ε（常 4/255~8/255），`L2` 保证总能量小；必须像素值仍在 [0,1]。

## 三、操作步骤

1. **判断黑盒/白盒**：有模型文件 → 白盒；只有 API → 黑盒（先训练替代模型）。
2. **确定度量**：`L∞` 或 `L2`，以及 ε 上限（题面通常规定）。
3. **实现攻击**：优先 `torchattacks` 的 `FGSM`/`PGD`，几行搞定。
4. **验证**：保存图片时**不要经过有损压缩**（用 PNG），否则扰动被抹掉。
5. **黑盒迁移**：多模型集成（ensemble）生成，迁移成功率更高。
6. **提交**：确认 API 返回目标类别。

## 四、命令/脚本

### 白盒 FGSM（最简）

```python
#!/usr/bin/env python3
# fgsm.py —— 白盒 FGSM 生成对抗样本
import torch, torchvision.transforms as T
from PIL import Image
from torch import nn

model = torch.load('model.pt', map_location='cpu').eval()
tf = T.Compose([T.Resize((224, 224)), T.ToTensor()])
x = tf(Image.open('cat.png').convert('RGB')).unsqueeze(0)
x.requires_grad = True

y = torch.tensor([281])                    # 原类别（ImageNet 索引，示例）
crit = nn.CrossEntropyLoss()
loss = crit(model(x), y)
loss.backward()

eps = 8 / 255
x_adv = (x + eps * x.grad.sign()).clamp(0, 1).detach()
T.ToPILImage()(x_adv[0]).save('cat_adv.png')

with torch.no_grad():
    p0 = model(x).argmax(1).item()
    p1 = model(x_adv).argmax(1).item()
print('clean ->', p0, '| adv ->', p1)
```

### 目标攻击 + PGD（更强）

```python
#!/usr/bin/env python3
# pgd_target.py —— 目标类 PGD 对抗样本
import torch, torch.nn.functional as F
import torchvision.transforms as T
from PIL import Image
import numpy as np

model = torch.load('model.pt', map_location='cpu').eval()
tf = T.Compose([T.Resize((224, 224)), T.ToTensor()])
x0 = tf(Image.open('cat.png').convert('RGB')).unsqueeze(0)
target = 207                               # 目标类别索引
eps, alpha, steps = 8/255, 2/255, 40

x = x0.clone().detach() + torch.empty_like(x0).uniform_(-eps, eps)
x.requires_grad = True

for i in range(steps):
    out = model(x)
    loss = F.cross_entropy(out, torch.tensor([target]))
    grad = torch.autograd.grad(loss, x)[0]
    x = x.detach() - alpha * grad.sign()                       # 朝目标走
    x = torch.max(torch.min(x, x0 + eps), x0 - eps)            # 投影到 ε 球
    x = x.clamp(0, 1).requires_grad_(True)
    if out.argmax(1).item() == target:
        print('hit at step', i); break

with torch.no_grad():
    print('clean:', model(x0).argmax(1).item(), '| adv:', model(x).argmax(1).item())
T.ToPILImage()(x.detach()[0]).save('cat_adv_pgd.png')
```

### 用 torchattacks 一行切换算法

```bash
pip install torchattacks
python - <<'PY'
import torch, torchattacks as ta
import torchvision.transforms as T
from PIL import Image
from torchvision.models import resnet18

m = resnet18(weights=None); m.eval()
x = T.Compose([T.Resize((224, 224)), T.ToTensor()])(
    Image.open('cat.png').convert('RGB')).unsqueeze(0)
y = torch.tensor([281])

for name in ['FGSM', 'PGD', 'DeepFool', 'CW', 'OnePixel']:
    try:
        atk = getattr(ta, name)(m, eps=8/255) if name in ('FGSM', 'PGD') else getattr(ta, name)(m)
        xa = atk(x, y)
        with torch.no_grad():
            print(f'{name:10s} clean={m(x).argmax(1).item()} adv={m(xa).argmax(1).item()}')
    except Exception as e:
        print(name, 'skip:', e)
PY
```

### 黑盒：替代模型迁移

```python
#!/usr/bin/env python3
# transfer.py —— 用多个本地模型生成扰动并取平均方向（提升迁移性）
import torch, torch.nn.functional as F
import torchvision.transforms as T
from PIL import Image
from torchvision import models

subs = [
    models.resnet18(weights='DEFAULT').eval(),
    models.vgg16(weights='DEFAULT').eval(),
    models.mobilenet_v2(weights='DEFAULT').eval(),
]
tf = T.Compose([T.Resize((224, 224)), T.ToTensor()])
x0 = tf(Image.open('cat.png').convert('RGB')).unsqueeze(0)
x = x0.clone().requires_grad_(True)
target = torch.tensor([207])
eps = 8 / 255

for step in range(20):
    grad_sum = torch.zeros_like(x)
    for m in subs:
        try:
            loss = F.cross_entropy(m(x), target)
            grad_sum += torch.autograd.grad(loss, x, retain_graph=False)[0]
        except Exception:
            continue
    x = (x - 2/255 * grad_sum.sign()).clamp(0, 1)
    x = torch.max(torch.min(x, x0 + eps), x0 - eps).detach().requires_grad_(True)

T.ToPILImage()(x[0]).save('cat_transfer.png')
print('saved cat_transfer.png  (提交前用目标 API 验证)')
```

### 提交前校验扰动不可见

```python
import numpy as np
from PIL import Image
a = np.asarray(Image.open('cat.png').convert('RGB'), dtype=int)
b = np.asarray(Image.open('cat_adv_pgd.png').convert('RGB'), dtype=int)
print('max |delta|:', np.abs(a - b).max(), '<= 8 通常不可见')
print('L2 距离:', float(np.linalg.norm(a - b)))
```

## 五、常见坑 / 变体

- **保存格式**：JPEG 压缩会破坏扰动，必须存 PNG；提交前不要二次缩放。
- **预处理一致性**：攻击时的 `Resize/Normalize` 必须与推理服务**完全一致**，否则扰动失效。
- **ε 太小**：4/255 时成功率对弱模型尚可，强模型需要更大 ε 或 PGD。
- **黑盒迁移失败**：目标可能是 ViT/CLIP 等不同结构，需换更相似替代模型或大量查询做"查询式攻击"。
- **防御机制**：对抗训练、输入平滑、随机裁剪会显著降低成功率，题目可能带这类防御。
- **合规**：只对题目提供的模型/接口做攻击，不要针对线上生产模型。

## 六、参考来源

- [Goodfellow et al. - Explaining and Harnessing Adversarial Examples（arXiv:1412.6572）](https://arxiv.org/abs/1412.6572)
- [Madry et al. - Towards Deep Learning Models Resistant to Adversarial Attacks（arXiv:1706.06083）](https://arxiv.org/abs/1706.06083)
- [torchattacks - 攻击算法集合文档](https://github.com/Harry24k/adversarial-attacks-pytorch)
- [CleverHans - 对抗样本与鲁棒性评估库](https://github.com/cleverhans-lab/cleverhans)
- [CTF Wiki - AI 基础与安全（模型完整性风险）](https://ctf-wiki.org/ai/security-for-ai/introduction/)
