#!/usr/bin/env python3
"""
Skill Security Auditor
审核 skill 文件是否存在可疑恶意代码
"""

import os
import re
import sys
import json
import zipfile
import tempfile
import shutil
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional


@dataclass
class SecurityFinding:
    """安全发现项"""
    level: str  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'
    category: str
    file_path: str
    line_number: int
    description: str
    snippet: str


@dataclass
class AuditResult:
    """审核结果"""
    skill_name: str
    skill_path: str
    overall_status: str  # 'SAFE', 'SUSPICIOUS', 'UNSAFE'
    findings: List[SecurityFinding]
    files_checked: int
    lines_checked: int
    summary: str


class SecurityAuditor:
    """Skill 安全审核器"""
    
    # 危险模式 - 关键级别 (直接拒绝)
    CRITICAL_PATTERNS = {
        'exec_backdoor': r'\beval\s*\(',
        'compile_backdoor': r'\bcompile\s*\(',
        'exec_import': r'\b__import__\s*\(',
        'os_system': r'\bos\.system\s*\(',
        'subprocess_shell': r'subprocess\.\w+.*shell\s*=\s*True',
        'codecs_decode': r'codecs\.decode\s*\(',
        'base64_exec': r'base64\.(b64decode|decode).*\b(exec|eval)',
        'marshal_loads': r'marshal\.loads?\s*\(',
        'pickle_loads': r'pickle\.loads?\s*\(',
    }
    
    # 高风险模式 - 需要审查
    HIGH_RISK_PATTERNS = {
        'network_request': r'\b(requests|urllib|http\.client|socket)\b',
        'file_deletion': r'\b(rm\s+-rf|shutil\.rmtree|os\.remove|os\.rmdir|os\.unlink)\b',
        'file_write': r'\b(open\s*\([^)]*[,\s]*[\'"]w)',
        'chmod_exec': r'\b(chmod|os\.chmod)\s*\([^)]*[\'"`]?[\+\d]*[75]\d{2}',
        'cron_job': r'\b(cron|crontab|schedule)\b',
        'environment_access': r'\b(os\.environ|os\.getenv)\b',
        'path_manipulation': r'\b(sys\.path\.insert|sys\.path\.append)\b',
    }
    
    # 中等风险模式 - 需要注意
    MEDIUM_RISK_PATTERNS = {
        'dynamic_import': r'\b(importlib|__import__)\b',
        'reflection': r'\b(getattr|setattr|hasattr|vars|globals|locals)\s*\(',
        'shell_command': r'\b(subprocess|popen|call|run)\b',
        'temp_file': r'\b(tempfile|mktemp|mkstemp)\b',
        'binary_data': r'\b(bytes|bytearray|struct)\b',
    }
    
    # 可疑文件扩展名
    SUSPICIOUS_EXTENSIONS = {'.exe', '.dll', '.so', '.dylib', '.bin', '.sh', '.bat', '.cmd'}
    
    # 可疑文件名模式
    SUSPICIOUS_FILENAMES = {
        'backdoor', 'exploit', 'payload', 'shell', 'rootkit',
        'keylogger', 'trojan', 'virus', 'malware', 'hack'
    }
    
    def __init__(self):
        self.findings: List[SecurityFinding] = []
        self.files_checked = 0
        self.lines_checked = 0
    
    def audit_skill(self, skill_path: str) -> AuditResult:
        """审核一个 skill"""
        self.findings = []
        self.files_checked = 0
        self.lines_checked = 0
        
        skill_name = Path(skill_path).name
        
        # 处理 .skill 文件 (zip 格式)
        if skill_path.endswith('.skill'):
            return self._audit_skill_package(skill_path)
        
        # 处理目录
        if os.path.isdir(skill_path):
            self._audit_directory(skill_path)
        else:
            self._audit_file(skill_path)
        
        return self._generate_result(skill_name, skill_path)
    
    def _audit_skill_package(self, skill_path: str) -> AuditResult:
        """审核 .skill 压缩包"""
        skill_name = Path(skill_path).stem
        
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                with zipfile.ZipFile(skill_path, 'r') as zip_ref:
                    # 检查 zip 中的可疑文件
                    for item in zip_ref.namelist():
                        if any(item.lower().endswith(ext) for ext in self.SUSPICIOUS_EXTENSIONS):
                            self.findings.append(SecurityFinding(
                                level='HIGH',
                                category='suspicious_file',
                                file_path=item,
                                line_number=0,
                                description=f'发现可疑文件类型: {item}',
                                snippet=''
                            ))
                        
                        if any(susp in item.lower() for susp in self.SUSPICIOUS_FILENAMES):
                            self.findings.append(SecurityFinding(
                                level='HIGH',
                                category='suspicious_filename',
                                file_path=item,
                                line_number=0,
                                description=f'文件名包含可疑关键词: {item}',
                                snippet=''
                            ))
                    
                    zip_ref.extractall(tmpdir)
                
                self._audit_directory(tmpdir)
            except zipfile.BadZipFile:
                self.findings.append(SecurityFinding(
                    level='CRITICAL',
                    category='invalid_package',
                    file_path=skill_path,
                    line_number=0,
                    description='无效的 skill 包格式',
                    snippet=''
                ))
        
        return self._generate_result(skill_name, skill_path)
    
    def _audit_directory(self, directory: str):
        """递归审核目录"""
        for root, dirs, files in os.walk(directory):
            # 跳过隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for filename in files:
                if filename.startswith('.'):
                    continue
                
                file_path = os.path.join(root, filename)
                self._audit_file(file_path)
    
    def _audit_file(self, file_path: str):
        """审核单个文件"""
        self.files_checked += 1
        
        # 检查文件扩展名
        ext = Path(file_path).suffix.lower()
        filename = Path(file_path).name.lower()
        
        if ext in self.SUSPICIOUS_EXTENSIONS:
            self.findings.append(SecurityFinding(
                level='HIGH',
                category='suspicious_file_type',
                file_path=file_path,
                line_number=0,
                description=f'可疑文件类型: {ext}',
                snippet=''
            ))
        
        if any(susp in filename for susp in self.SUSPICIOUS_FILENAMES):
            self.findings.append(SecurityFinding(
                level='HIGH',
                category='suspicious_filename',
                file_path=file_path,
                line_number=0,
                description=f'文件名包含可疑关键词',
                snippet=filename
            ))
        
        # 只检查文本文件
        if ext not in {'.py', '.js', '.sh', '.bash', '.md', '.txt', '.json', '.yaml', '.yml', '.skill'}:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                self.lines_checked += len(lines)
                
                for line_num, line in enumerate(lines, 1):
                    self._check_line(file_path, line_num, line)
        except Exception as e:
            self.findings.append(SecurityFinding(
                level='INFO',
                category='read_error',
                file_path=file_path,
                line_number=0,
                description=f'无法读取文件: {str(e)}',
                snippet=''
            ))
    
    def _check_line(self, file_path: str, line_num: int, line: str):
        """检查单行代码"""
        # 跳过注释行
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('*'):
            return
        
        # 检查关键级别模式
        for pattern_name, pattern in self.CRITICAL_PATTERNS.items():
            if re.search(pattern, line, re.IGNORECASE):
                self.findings.append(SecurityFinding(
                    level='CRITICAL',
                    category=f'critical:{pattern_name}',
                    file_path=file_path,
                    line_number=line_num,
                    description=f'发现关键安全风险: {pattern_name}',
                    snippet=line.strip()[:200]
                ))
        
        # 检查高风险模式
        for pattern_name, pattern in self.HIGH_RISK_PATTERNS.items():
            if re.search(pattern, line, re.IGNORECASE):
                self.findings.append(SecurityFinding(
                    level='HIGH',
                    category=f'high:{pattern_name}',
                    file_path=file_path,
                    line_number=line_num,
                    description=f'发现高风险代码: {pattern_name}',
                    snippet=line.strip()[:200]
                ))
        
        # 检查中等风险模式
        for pattern_name, pattern in self.MEDIUM_RISK_PATTERNS.items():
            if re.search(pattern, line, re.IGNORECASE):
                self.findings.append(SecurityFinding(
                    level='MEDIUM',
                    category=f'medium:{pattern_name}',
                    file_path=file_path,
                    line_number=line_num,
                    description=f'发现需要注意的代码: {pattern_name}',
                    snippet=line.strip()[:200]
                ))
    
    def _generate_result(self, skill_name: str, skill_path: str) -> AuditResult:
        """生成审核结果"""
        critical_count = sum(1 for f in self.findings if f.level == 'CRITICAL')
        high_count = sum(1 for f in self.findings if f.level == 'HIGH')
        medium_count = sum(1 for f in self.findings if f.level == 'MEDIUM')
        
        # 确定整体状态
        if critical_count > 0:
            overall_status = 'UNSAFE'
            summary = f'发现 {critical_count} 个关键安全问题，建议拒绝安装'
        elif high_count > 0:
            overall_status = 'SUSPICIOUS'
            summary = f'发现 {high_count} 个高风险问题，建议人工审查'
        elif medium_count > 3:
            overall_status = 'SUSPICIOUS'
            summary = f'发现 {medium_count} 个中等风险问题，建议人工审查'
        else:
            overall_status = 'SAFE'
            summary = '未发现明显安全问题，可以安装'
        
        return AuditResult(
            skill_name=skill_name,
            skill_path=skill_path,
            overall_status=overall_status,
            findings=self.findings,
            files_checked=self.files_checked,
            lines_checked=self.lines_checked,
            summary=summary
        )


def format_result(result: AuditResult) -> str:
    """格式化审核结果为可读文本"""
    lines = []
    lines.append('=' * 60)
    lines.append(f'Skill 安全审核报告: {result.skill_name}')
    lines.append('=' * 60)
    lines.append(f'审核路径: {result.skill_path}')
    lines.append(f'文件数: {result.files_checked} | 代码行数: {result.lines_checked}')
    lines.append('')
    
    # 状态
    status_emoji = {'SAFE': '✅', 'SUSPICIOUS': '⚠️', 'UNSAFE': '❌'}
    emoji = status_emoji.get(result.overall_status, '❓')
    lines.append(f'审核状态: {emoji} {result.overall_status}')
    lines.append(f'总结: {result.summary}')
    lines.append('')
    
    # 统计
    levels = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}
    for f in result.findings:
        levels[f.level] = levels.get(f.level, 0) + 1
    
    lines.append('问题统计:')
    for level, count in levels.items():
        if count > 0:
            lines.append(f'  {level}: {count}')
    lines.append('')
    
    # 详细发现
    if result.findings:
        lines.append('详细发现:')
        lines.append('-' * 60)
        
        for finding in sorted(result.findings, key=lambda x: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'].index(x.level)):
            lines.append(f'\n[{finding.level}] {finding.category}')
            lines.append(f'  文件: {finding.file_path}:{finding.line_number}')
            lines.append(f'  描述: {finding.description}')
            if finding.snippet:
                lines.append(f'  代码: {finding.snippet}')
    else:
        lines.append('未发现安全问题')
    
    lines.append('')
    lines.append('=' * 60)
    
    return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print('用法: python security_audit.py <skill_path> [--json]')
        sys.exit(1)
    
    skill_path = sys.argv[1]
    output_json = '--json' in sys.argv
    
    if not os.path.exists(skill_path):
        print(f'错误: 路径不存在: {skill_path}')
        sys.exit(1)
    
    auditor = SecurityAuditor()
    result = auditor.audit_skill(skill_path)
    
    if output_json:
        # 转换为 JSON 输出
        result_dict = {
            'skill_name': result.skill_name,
            'skill_path': result.skill_path,
            'overall_status': result.overall_status,
            'files_checked': result.files_checked,
            'lines_checked': result.lines_checked,
            'summary': result.summary,
            'findings': [
                {
                    'level': f.level,
                    'category': f.category,
                    'file_path': f.file_path,
                    'line_number': f.line_number,
                    'description': f.description,
                    'snippet': f.snippet
                }
                for f in result.findings
            ]
        }
        print(json.dumps(result_dict, indent=2, ensure_ascii=False))
    else:
        print(format_result(result))
    
    # 返回退出码
    if result.overall_status == 'UNSAFE':
        sys.exit(2)
    elif result.overall_status == 'SUSPICIOUS':
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
