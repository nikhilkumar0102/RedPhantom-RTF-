#!/usr/bin/env python3

import os
import socket
import subprocess
import json
from datetime import datetime
import sys


# ================= UI COLORS =================

class C:
    G = "\033[92m"
    R = "\033[91m"
    Y = "\033[93m"
    B = "\033[94m"
    W = "\033[97m"
    BD = "\033[1m"
    X = "\033[0m"


# ================= BANNER =================

BANNER = f"""
{C.BD}{C.B}
┌────────────────────────────────────────────────────────────┐
│                    REDPHANTOM AI SCAN                      │
├────────────────────────────────────────────────────────────┤
│  Mode        : SAFE READ-ONLY ASSESSMENT                   │
│  Scope       : Recon + Exposure + Config Risk              │
│  AI Engine   : Vulnerability Reasoning                     │
│  Output      : HTML Security Report                        │
│                                                            │
│  ⚠ No exploitation • No brute force • No attack traffic    │
└────────────────────────────────────────────────────────────┘
{C.X}
"""


# ================= CONFIG =================

COMMON_PORTS = [
    21, 22, 23, 25, 53,
    80, 110, 135, 139,
    143, 443, 445, 3389, 8080
]


# ================= DEPENDENCY CHECKER =================

def check_dependencies():
    """Check and return available AI providers"""
    available_providers = {}
    
    # Check OpenAI
    try:
        import openai
        available_providers["OpenAI"] = {
            "installed": True,
            "models": {
                "1": "gpt-4o",
                "2": "gpt-4o-mini",
                "3": "gpt-4-turbo",
                "4": "gpt-3.5-turbo"
            }
        }
    except ImportError:
        available_providers["OpenAI"] = {
            "installed": False,
            "install_cmd": "pip install openai"
        }
    
    # Check Google Gemini (new package)
    try:
        import google.genai
        available_providers["Google Gemini"] = {
            "installed": True,
            "models": {
                "1": "gemini-2.0-flash-exp",
                "2": "gemini-1.5-flash",
                "3": "gemini-1.5-pro-002",
                "4": "gemini-1.5-flash-002",
                "5": "gemini-1.5-flash-8b"
            }
        }
    except ImportError:
        available_providers["Google Gemini"] = {
            "installed": False,
            "install_cmd": "pip install google-genai"
        }
    
    return available_providers


# ================= SAFE NETWORK CHECKS =================

def ping_target(host):
    return subprocess.call(
        ["ping", "-c", "1", "-W", "1", host],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    ) == 0


def resolve_target(host):
    try:
        return socket.gethostbyname(host)
    except Exception:
        return None


def safe_port_scan(host):
    open_ports = []

    for port in COMMON_PORTS:
        s = socket.socket()
        s.settimeout(0.7)
        try:
            s.connect((host, port))
            open_ports.append(port)
        except Exception:
            pass
        s.close()

    return open_ports


def banner_grab(host, port):
    try:
        s = socket.socket()
        s.settimeout(1)
        s.connect((host, port))
        s.send(b"HEAD / HTTP/1.0\r\n\r\n")
        data = s.recv(256).decode(errors="ignore")
        s.close()
        return data.strip()
    except Exception:
        return ""


# ================= AI ANALYSIS =================

def ai_analyze_openai(api_key, model, findings):
    """Analyze using OpenAI API"""
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        prompt = f"""
You are a senior red team security consultant.

Analyze the following SAFE scan findings.
DO NOT suggest exploitation steps.

Provide:
- Identified security risks
- Severity (Low/Medium/High)
- Exposure reasoning
- Defensive recommendations
- Prioritized remediation plan

Findings:
{json.dumps(findings, indent=2)}
"""

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI analysis failed: {e}"


def ai_analyze_gemini(api_key, model, findings):
    """Analyze using Google Gemini API (new package)"""
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        
        prompt = f"""
You are a senior red team security consultant.

Analyze the following SAFE scan findings.
DO NOT suggest exploitation steps.

Provide:
- Identified security risks
- Severity (Low/Medium/High)
- Exposure reasoning
- Defensive recommendations
- Prioritized remediation plan

Findings:
{json.dumps(findings, indent=2)}
"""

        response = client.models.generate_content(
            model=model,
            contents=prompt
        )
        
        return response.text

    except Exception as e:
        return f"AI analysis failed: {e}"


def ai_analyze(provider, api_key, model, findings):
    """Route to appropriate AI provider"""
    if provider == "OpenAI":
        return ai_analyze_openai(api_key, model, findings)
    elif provider == "Google Gemini":
        return ai_analyze_gemini(api_key, model, findings)
    else:
        return "Unknown AI provider"


# ================= HTML REPORT =================

def get_severity_badge(text):
    """Generate severity badges based on content"""
    if not text:
        return ""
    
    text_lower = text.lower()
    badges = []
    
    if "high" in text_lower and "severity" in text_lower:
        badges.append('<span class="badge severity-high">HIGH RISK</span>')
    if "medium" in text_lower and "severity" in text_lower:
        badges.append('<span class="badge severity-medium">MEDIUM RISK</span>')
    if "low" in text_lower and "severity" in text_lower:
        badges.append('<span class="badge severity-low">LOW RISK</span>')
    
    return " ".join(badges)


def generate_html_report(target, findings, ai_output, provider, model):
    port_rows = ""
    for port in findings.get("open_ports", []):
        banner = findings.get("service_banners", {}).get(port, "No banner")
        banner_escaped = str(banner).replace('<', '&lt;').replace('>', '&gt;')
        port_rows += f"""
        <tr>
            <td>{port}</td>
            <td><span class="port-badge">OPEN</span></td>
            <td class="banner-cell">{banner_escaped if banner_escaped else 'N/A'}</td>
        </tr>
        """
    
    if not port_rows:
        port_rows = '<tr><td colspan="3" style="text-align:center; color:#888;">No open ports detected</td></tr>'
    
    # Escape AI output to prevent HTML injection
    ai_output_escaped = str(ai_output).replace('<', '&lt;').replace('>', '&gt;')
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<title>RedPhantom AI Security Report - {target}</title>
<style>
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #0a0e27;
    background-image: 
        radial-gradient(circle at 20% 50%, rgba(76, 175, 80, 0.05) 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, rgba(33, 150, 243, 0.05) 0%, transparent 50%);
    color: #e0e0e0;
    line-height: 1.6;
    padding: 20px;
    min-height: 100vh;
}}

.container {{
    max-width: 1200px;
    margin: 0 auto;
}}

header {{
    background: linear-gradient(135deg, #1e2530 0%, #252b3a 100%);
    padding: 40px;
    border-radius: 15px;
    margin-bottom: 30px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(76, 175, 80, 0.3);
    position: relative;
    overflow: hidden;
}}

header::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #4CAF50, #2196F3, #4CAF50);
    background-size: 200% 100%;
    animation: gradient 3s ease infinite;
}}

@keyframes gradient {{
    0%, 100% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
}}

h1 {{
    color: #4CAF50;
    font-size: 2.5em;
    margin-bottom: 10px;
    text-shadow: 0 0 20px rgba(76, 175, 80, 0.3);
    display: flex;
    align-items: center;
    gap: 15px;
}}

.subtitle {{
    color: #888;
    font-size: 1.1em;
    font-weight: 300;
}}

.card {{
    background: rgba(27, 31, 42, 0.9);
    backdrop-filter: blur(10px);
    padding: 30px;
    margin: 20px 0;
    border-radius: 15px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}}

.card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(76, 175, 80, 0.2);
    border-color: rgba(76, 175, 80, 0.3);
}}

h2 {{
    color: #4CAF50;
    font-size: 1.8em;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 2px solid rgba(76, 175, 80, 0.3);
    display: flex;
    align-items: center;
    gap: 10px;
}}

.info-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin: 20px 0;
}}

.info-item {{
    background: rgba(255, 255, 255, 0.03);
    padding: 20px;
    border-radius: 10px;
    border-left: 4px solid #4CAF50;
    transition: all 0.3s ease;
}}

.info-item:hover {{
    background: rgba(255, 255, 255, 0.05);
    border-left-width: 6px;
}}

.info-label {{
    color: #888;
    font-size: 0.9em;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 600;
}}

.info-value {{
    color: #fff;
    font-size: 1.2em;
    font-weight: 600;
    word-break: break-word;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 10px;
    overflow: hidden;
}}

th {{
    background: rgba(76, 175, 80, 0.2);
    color: #4CAF50;
    padding: 18px 15px;
    text-align: left;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-size: 0.9em;
}}

td {{
    padding: 15px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}}

tbody tr {{
    transition: background 0.2s ease;
}}

tbody tr:hover {{
    background: rgba(76, 175, 80, 0.05);
}}

tbody tr:last-child td {{
    border-bottom: none;
}}

.port-badge {{
    background: linear-gradient(135deg, #4CAF50, #45a049);
    color: #000;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.85em;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    display: inline-block;
}}

.banner-cell {{
    font-family: 'Courier New', Consolas, monospace;
    color: #aaa;
    font-size: 0.9em;
    word-break: break-all;
    max-width: 500px;
}}

.ai-analysis {{
    background: rgba(76, 175, 80, 0.05);
    border: 1px solid rgba(76, 175, 80, 0.2);
    border-radius: 10px;
    padding: 25px;
    white-space: pre-wrap;
    word-wrap: break-word;
    font-family: 'Segoe UI', sans-serif;
    line-height: 1.8;
    color: #ddd;
    max-height: 800px;
    overflow-y: auto;
}}

.ai-analysis::-webkit-scrollbar {{
    width: 8px;
}}

.ai-analysis::-webkit-scrollbar-track {{
    background: rgba(0, 0, 0, 0.2);
    border-radius: 10px;
}}

.ai-analysis::-webkit-scrollbar-thumb {{
    background: rgba(76, 175, 80, 0.5);
    border-radius: 10px;
}}

.ai-analysis::-webkit-scrollbar-thumb:hover {{
    background: rgba(76, 175, 80, 0.7);
}}

.badge {{
    display: inline-block;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 0.85em;
    font-weight: 600;
    margin: 5px 5px 5px 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

.severity-high {{
    background: linear-gradient(135deg, #f44336, #d32f2f);
    color: white;
    box-shadow: 0 4px 15px rgba(244, 67, 54, 0.3);
}}

.severity-medium {{
    background: linear-gradient(135deg, #ff9800, #f57c00);
    color: white;
    box-shadow: 0 4px 15px rgba(255, 152, 0, 0.3);
}}

.severity-low {{
    background: linear-gradient(135deg, #2196F3, #1976D2);
    color: white;
    box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);
}}

.ai-provider-badge {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}}

.footer {{
    text-align: center;
    padding: 40px 20px;
    margin-top: 40px;
    color: #666;
    font-size: 0.9em;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}}

.footer-links {{
    margin: 15px 0;
}}

.footer-links a {{
    color: #4CAF50;
    text-decoration: none;
    margin: 0 15px;
    transition: color 0.3s ease;
}}

.footer-links a:hover {{
    color: #66BB6A;
    text-decoration: underline;
}}

.json-viewer {{
    background: #0d1117;
    border: 1px solid rgba(76, 175, 80, 0.2);
    border-radius: 10px;
    padding: 20px;
    overflow-x: auto;
    max-height: 500px;
}}

.json-viewer::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}

.json-viewer::-webkit-scrollbar-track {{
    background: rgba(0, 0, 0, 0.2);
    border-radius: 10px;
}}

.json-viewer::-webkit-scrollbar-thumb {{
    background: rgba(76, 175, 80, 0.5);
    border-radius: 10px;
}}

.json-viewer pre {{
    margin: 0;
    color: #c9d1d9;
    font-family: 'Courier New', Consolas, monospace;
    font-size: 0.9em;
}}

.timestamp {{
    color: #888;
    font-size: 0.95em;
    font-style: italic;
}}

.stats-summary {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 15px;
    padding: 15px;
    background: rgba(76, 175, 80, 0.1);
    border-radius: 8px;
    border-left: 4px solid #4CAF50;
}}

.stats-summary strong {{
    color: #4CAF50;
}}

@media screen and (max-width: 768px) {{
    body {{
        padding: 10px;
    }}
    
    header {{
        padding: 20px;
    }}
    
    h1 {{
        font-size: 1.8em;
    }}
    
    .card {{
        padding: 20px;
    }}
    
    .info-grid {{
        grid-template-columns: 1fr;
    }}
    
    table {{
        font-size: 0.9em;
    }}
    
    th, td {{
        padding: 10px 8px;
    }}
}}

@media print {{
    body {{
        background: white;
        color: black;
    }}
    
    .card {{
        box-shadow: none;
        border: 1px solid #ddd;
        page-break-inside: avoid;
    }}
    
    header::before {{
        display: none;
    }}
}}

.icon {{
    display: inline-block;
    width: 1em;
    height: 1em;
}}
</style>
</head>

<body>

<div class="container">

<header>
    <h1><span class="icon">🛡️</span> RedPhantom AI Security Assessment</h1>
    <p class="subtitle">Automated Vulnerability Analysis &amp; Risk Assessment</p>
</header>

<div class="card">
    <h2><span class="icon">📋</span> Target Information</h2>
    <div class="info-grid">
        <div class="info-item">
            <div class="info-label">Target</div>
            <div class="info-value">{target}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Resolved IP</div>
            <div class="info-value">{findings.get('resolved_ip', 'N/A')}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Scan Time</div>
            <div class="info-value timestamp">{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</div>
        </div>
        <div class="info-item">
            <div class="info-label">AI Engine</div>
            <div class="info-value">
                <span class="badge ai-provider-badge">{provider}</span>
                <br><small style="color: #888; font-size: 0.8em;">{model}</small>
            </div>
        </div>
    </div>
</div>

<div class="card">
    <h2><span class="icon">🔍</span> Open Ports &amp; Services</h2>
    <table>
        <thead>
            <tr>
                <th>Port</th>
                <th>Status</th>
                <th>Service Banner</th>
            </tr>
        </thead>
        <tbody>
            {port_rows}
        </tbody>
    </table>
    <div class="stats-summary">
        <strong>Total Open Ports:</strong> <span>{len(findings.get('open_ports', []))}</span>
    </div>
</div>

<div class="card">
    <h2><span class="icon">🤖</span> AI Risk Analysis &amp; Recommendations</h2>
    {get_severity_badge(ai_output)}
    <div class="ai-analysis">{ai_output_escaped}</div>
</div>

<div class="card">
    <h2><span class="icon">📊</span> Raw Scan Data</h2>
    <div class="json-viewer">
        <pre>{json.dumps(findings, indent=2, ensure_ascii=False)}</pre>
    </div>
</div>

<div class="footer">
    <p><strong>RedPhantom AI Scanner</strong></p>
    <p>Authorized Security Assessment • Safe Read-Only Mode • No Active Exploitation</p>
    <div class="footer-links">
        <a href="#" onclick="window.print(); return false;">Print Report</a> •
        <a href="#" onclick="alert('RedPhantom AI Scanner v2.0'); return false;">About</a> •
        <a href="https://github.com" target="_blank">Documentation</a>
    </div>
    <p style="margin-top: 15px; font-size: 0.85em;">
        Generated by RedPhantom v2.0 • &copy; 2026
    </p>
</div>

</div>

</body>
</html>
"""
    port_rows = ""
    for port in findings.get("open_ports", []):
        banner = findings.get("service_banners", {}).get(port, "No banner")
        port_rows += f"""
        <tr>
            <td>{port}</td>
            <td><span class="port-badge">OPEN</span></td>
            <td class="banner-cell">{banner if banner else 'N/A'}</td>
        </tr>
        """
    
    if not port_rows:
        port_rows = '<tr><td colspan="3" style="text-align:center; color:#888;">No open ports detected</td></tr>'
    
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>RedPhantom AI Security Report - {target}</title>
<style>
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #0f1115 0%, #1a1d29 100%);
    color: #e0e0e0;
    line-height: 1.6;
    padding: 20px;
}}

.container {{
    max-width: 1200px;
    margin: 0 auto;
}}

header {{
    background: linear-gradient(135deg, #1e2530 0%, #252b3a 100%);
    padding: 30px;
    border-radius: 15px;
    margin-bottom: 30px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(76, 175, 80, 0.2);
}}

h1 {{
    color: #4CAF50;
    font-size: 2.5em;
    margin-bottom: 10px;
    text-shadow: 0 0 20px rgba(76, 175, 80, 0.3);
}}

.subtitle {{
    color: #888;
    font-size: 1.1em;
    font-weight: 300;
}}

.card {{
    background: linear-gradient(135deg, #1b1f2a 0%, #252b3a 100%);
    padding: 30px;
    margin: 20px 0;
    border-radius: 15px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.05);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}}

.card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(76, 175, 80, 0.2);
}}

h2 {{
    color: #4CAF50;
    font-size: 1.8em;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid rgba(76, 175, 80, 0.3);
}}

.info-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin: 20px 0;
}}

.info-item {{
    background: rgba(255, 255, 255, 0.03);
    padding: 15px;
    border-radius: 10px;
    border-left: 4px solid #4CAF50;
}}

.info-label {{
    color: #888;
    font-size: 0.9em;
    margin-bottom: 5px;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

.info-value {{
    color: #fff;
    font-size: 1.2em;
    font-weight: 600;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
}}

th {{
    background: rgba(76, 175, 80, 0.2);
    color: #4CAF50;
    padding: 15px;
    text-align: left;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-size: 0.9em;
}}

td {{
    padding: 15px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}}

tr:hover {{
    background: rgba(255, 255, 255, 0.02);
}}

.port-badge {{
    background: #4CAF50;
    color: #000;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 0.85em;
    font-weight: 600;
}}

.banner-cell {{
    font-family: 'Courier New', monospace;
    color: #aaa;
    font-size: 0.9em;
}}

.ai-analysis {{
    background: rgba(76, 175, 80, 0.05);
    border: 1px solid rgba(76, 175, 80, 0.2);
    padding: 25px;
    border-radius: 10px;
    white-space: pre-wrap;
    word-wrap: break-word;
    font-family: 'Segoe UI', sans-serif;
    line-height: 1.8;
    color: #ddd;
}}

.badge {{
    display: inline-block;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.85em;
    font-weight: 600;
    margin: 5px 5px 5px 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

.severity-high {{
    background: #f44336;
    color: white;
}}

.severity-medium {{
    background: #ff9800;
    color: white;
}}

.severity-low {{
    background: #2196F3;
    color: white;
}}

.ai-provider-badge {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}}

.footer {{
    text-align: center;
    padding: 30px;
    margin-top: 40px;
    color: #666;
    font-size: 0.9em;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
}}

.footer-links {{
    margin-top: 10px;
}}

.footer-links a {{
    color: #4CAF50;
    text-decoration: none;
    margin: 0 10px;
}}

.footer-links a:hover {{
    text-decoration: underline;
}}

.json-viewer {{
    background: #0d1117;
    border: 1px solid rgba(76, 175, 80, 0.2);
    border-radius: 10px;
    padding: 20px;
    overflow-x: auto;
}}

.json-viewer pre {{
    margin: 0;
    color: #c9d1d9;
    font-family: 'Courier New', monospace;
    font-size: 0.95em;
}}

.timestamp {{
    color: #888;
    font-size: 0.95em;
    font-style: italic;
}}

@media print {{
    body {{
        background: white;
        color: black;
    }}
    
    .card {{
        box-shadow: none;
        border: 1px solid #ddd;
        page-break-inside: avoid;
    }}
}}
</style>
</head>

<body>

<div class="container">

<header>
    <h1>🛡️ RedPhantom AI Security Assessment</h1>
    <p class="subtitle">Automated Vulnerability Analysis & Risk Assessment</p>
</header>

<div class="card">
    <h2>📋 Target Information</h2>
    <div class="info-grid">
        <div class="info-item">
            <div class="info-label">Target</div>
            <div class="info-value">{target}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Resolved IP</div>
            <div class="info-value">{findings.get('resolved_ip', 'N/A')}</div>
        </div>
        <div class="info-item">
            <div class="info-label">Scan Time</div>
            <div class="info-value timestamp">{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</div>
        </div>
        <div class="info-item">
            <div class="info-label">AI Engine</div>
            <div class="info-value">
                <span class="badge ai-provider-badge">{provider}</span>
                <br><small style="color: #888;">{model}</small>
            </div>
        </div>
    </div>
</div>

<div class="card">
    <h2>🔍 Open Ports & Services</h2>
    <table>
        <thead>
            <tr>
                <th>Port</th>
                <th>Status</th>
                <th>Service Banner</th>
            </tr>
        </thead>
        <tbody>
            {port_rows}
        </tbody>
    </table>
    <p style="margin-top: 15px; color: #888; font-size: 0.9em;">
        <strong>Total Open Ports:</strong> {len(findings.get('open_ports', []))}
    </p>
</div>

<div class="card">
    <h2>🤖 AI Risk Analysis & Recommendations</h2>
    {get_severity_badge(ai_output)}
    <div class="ai-analysis">{ai_output}</div>
</div>

<div class="card">
    <h2>📊 Raw Scan Data</h2>
    <div class="json-viewer">
        <pre>{json.dumps(findings, indent=2)}</pre>
    </div>
</div>

<div class="footer">
    <p><strong>RedPhantom AI Scanner</strong></p>
    <p>Authorized Security Assessment • Safe Read-Only Mode • No Active Exploitation</p>
    <div class="footer-links">
        <a href="#">Documentation</a> •
        <a href="#">Privacy Policy</a> •
        <a href="#">Report an Issue</a>
    </div>
    <p style="margin-top: 15px; font-size: 0.85em;">
        Generated by RedPhantom v2.0 • © 2026
    </p>
</div>

</div>

</body>
</html>
"""


# ================= MAIN =================

def run(engagement):

    print(BANNER)

    target = input(f"{C.W}Enter target IP / hostname: {C.X}").strip()

    print(f"{C.Y}[*] Checking reachability...{C.X}")
    if not ping_target(target):
        print(f"{C.R}[!] Target unreachable. Aborting scan.{C.X}")
        return

    print(f"{C.G}[✓] Target reachable{C.X}")

    resolved_ip = resolve_target(target)
    open_ports = safe_port_scan(target)

    banners = {}
    for port in open_ports:
        banners[port] = banner_grab(target, port)

    findings = {
        "target": target,
        "resolved_ip": resolved_ip,
        "open_ports": open_ports,
        "service_banners": banners
    }

    # Check available AI providers
    print(f"\n{C.Y}[*] Checking available AI providers...{C.X}")
    available_providers = check_dependencies()
    
    # Filter only installed providers
    installed_providers = {name: data for name, data in available_providers.items() if data.get("installed")}
    
    if not installed_providers:
        print(f"\n{C.R}[!] No AI providers installed!{C.X}")
        print(f"\n{C.Y}Please install at least one AI provider:{C.X}")
        for name, data in available_providers.items():
            if not data.get("installed"):
                print(f"{C.W}  • {name}: {C.G}{data['install_cmd']}{C.X}")
        return
    
    # AI Provider Selection
    print(f"\n{C.BD}{C.B}Available AI Providers:{C.X}")
    provider_map = {}
    idx = 1
    for name, data in installed_providers.items():
        print(f"{C.G}  {idx}. {name} ✓{C.X}")
        provider_map[str(idx)] = (name, data)
        idx += 1
    
    # Show unavailable providers
    unavailable = {name: data for name, data in available_providers.items() if not data.get("installed")}
    if unavailable:
        print(f"\n{C.Y}Unavailable (not installed):{C.X}")
        for name, data in unavailable.items():
            print(f"{C.R}  ✗ {name}{C.X} - Install: {C.W}{data['install_cmd']}{C.X}")
    
    provider_choice = input(f"\n{C.W}Enter choice (1-{len(installed_providers)}): {C.X}").strip()
    
    if provider_choice not in provider_map:
        print(f"{C.R}[!] Invalid provider choice. Aborting.{C.X}")
        return
    
    provider_name, provider_data = provider_map[provider_choice]
    
    # Model Selection
    print(f"\n{C.BD}{C.B}Select {provider_name} Model:{C.X}")
    for key, model in provider_data["models"].items():
        print(f"{C.W}  {key}. {model}{C.X}")
    
    num_models = len(provider_data["models"])
    model_choice = input(f"{C.W}Enter choice (1-{num_models}): {C.X}").strip()
    
    if model_choice not in provider_data["models"]:
        print(f"{C.R}[!] Invalid model choice. Aborting.{C.X}")
        return
    
    selected_model = provider_data["models"][model_choice]
    
    # API Key
    api_key = input(f"{C.W}Enter {provider_name} API key: {C.X}").strip()

    print(f"{C.Y}[*] Performing AI vulnerability reasoning with {provider_name} ({selected_model})...{C.X}")
    ai_output = ai_analyze(provider_name, api_key, selected_model, findings)

    # ---------- SAVE REPORT ----------

    outdir = os.path.join(engagement["base"], "ai_reports")
    os.makedirs(outdir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(outdir, f"redphantom_ai_report_{timestamp}.html")
    html = generate_html_report(target, findings, ai_output, provider_name, selected_model)

    with open(report_path, "w") as f:
        f.write(html)

    print(f"{C.G}{C.BD}[✓] AI Security Report Generated{C.X}")
    print(f"{C.B}Location:{C.X} {report_path}")
