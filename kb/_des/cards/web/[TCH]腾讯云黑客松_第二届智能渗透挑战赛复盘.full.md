---
title: "[TCH] 腾讯云黑客松 第二届智能渗透挑战赛复盘"
category: web
tags: ["腾讯云黑客松 第二届智能渗透挑战赛", "web", "ai_agent_orchestrator", "kali_docker_executor", "browser_devtools_mcp", "c2_msf_metasploit"]
signals: ["腾讯云黑客松 第二届智能渗透挑战赛 2025", "ai_agent_orchestrator", "kali_docker_executor", "browser_devtools_mcp", "c2_msf_metasploit", "ghidra_mcp_re", "glm5_coding_plan", "agent_summarizer", "mcp_tool_chaining", "reverse", "Orchestrator", "Executor", "Browser", "Reverse"]
difficulty: hard
source: "https://www.ctfiot.com/305842.html"
tools: ["Ghidra"]
origin: des-import
origin_kind: cards
updated: 2026-10-24
---
# [TCH] 腾讯云黑客松 第二届智能渗透挑战赛复盘

> 赛事：腾讯云黑客松 第二届智能渗透挑战赛 2025 | 方向：web | 难度：hard | 工具：Ghidra

## 一句话总结

腾讯云黑客松第二届智能渗透挑战赛复盘：Orchestrator + Executor/Browser/C2/Reverse 4 个 MCP Agent + GLM5 自动解题，4 个赛区 54 个 flag 30 个解题，总排名 60。

## 攻击链

1. 4 个赛区 (识器·明理 SRC 众测 / 洞见·虚实 CVE+云+AI / 执刃·循迹 多步攻击 / 铸剑·止戈 域渗透) → Orchestrator 策略层 + Executor Agent (Kali Docker) + Browser Agent (Chrome DevTools MCP) + C2 Agent (MSF) + Reverse Agent (Ghidra MCP) → GLM5 200 元 Coding plan 主赛 + 智谱 GLM5.1 500 元 Coding plan 零界平行 → Agent Summarizer 关键词/调用签名/CVE 编号三层防复读 → 60/54 总排名 2140 分 GLM5 解 30 个 flag

## 关键 payload

```
{"chrome-devtools": {"command":"...", "visibility":"subagent:browser"}} / 你是 CTF XXX 专家，正在分析名为"xxx"的题目 / 关键词层+调用签名层+CVE 编号层
```

## 经验教训

AI Agent 渗透时代，关键词层+调用签名层+CVE 编号层 anti-复读机制是 LLM CTF 自动化的核心；多 MCP 并行 (chrome-devtools + Kali + MSF + Ghidra) 是当前最优架构。

## 标签

ai_agent_orchestrator、kali_docker_executor、browser_devtools_mcp、c2_msf_metasploit、ghidra_mcp_re、glm5_coding_plan、agent_summarizer、mcp_tool_chaining、tencent_challenge_zc

## 参考来源

- https://www.ctfiot.com/305842.html
- 原文件：[TCH]腾讯云黑客松_第二届智能渗透挑战赛复盘.full.md
