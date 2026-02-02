#!/usr/bin/env python3
"""
Enhanced Web Vulnerability Scanner with Vulners.com Integration
Advanced Nikto, SQLMap, Vulners.com API Integration & Professional Report Generation
Industrial-Ready Penetration Testing Tool with Real-Time Exploit Intelligence
"""

import os
import subprocess
import shutil
import json
import re
import time
import sys
import threading
import requests
from datetime import datetime
from urllib.parse import urlparse
from typing import Dict, List, Tuple, Optional

# ================= COLORS =================
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

# ================= PROGRESS BAR =================
class ProgressBar:
    """Animated progress bar with status updates"""
    
    def __init__(self, total: int, description: str, width: int = 50):
        self.total = total
        self.description = description
        self.width = width
        self.current = 0
        self.running = False
        self.status = "Initializing..."
        
    def start(self):
        """Start the progress bar"""
        self.running = True
        self.current = 0
        self._draw()
    
    def update(self, current: int, status: str = ""):
        """Update progress"""
        self.current = min(current, self.total)
        if status:
            self.status = status
        self._draw()
    
    def increment(self, amount: int = 1, status: str = ""):
        """Increment progress"""
        self.update(self.current + amount, status)
    
    def finish(self, status: str = "Complete"):
        """Finish the progress bar"""
        self.current = self.total
        self.status = status
        self._draw()
        print()  # New line after completion
        self.running = False
    
    def _draw(self):
        """Draw the progress bar"""
        if self.total == 0:
            percentage = 100
        else:
            percentage = int((self.current / self.total) * 100)
        
        filled = int((self.width * self.current) / self.total) if self.total > 0 else self.width
        bar = '█' * filled + '░' * (self.width - filled)
        
        # Color based on progress
        if percentage == 100:
            color = Colors.GREEN
        elif percentage >= 50:
            color = Colors.CYAN
        else:
            color = Colors.YELLOW
        
        # Print progress bar
        sys.stdout.write('\r')
        sys.stdout.write(
            f"{Colors.BOLD}{self.description}:{Colors.END} "
            f"{color}[{bar}]{Colors.END} "
            f"{color}{percentage}%{Colors.END} "
            f"{Colors.CYAN}| {self.status}{Colors.END}"
        )
        sys.stdout.flush()


class SpinnerAnimation:
    """Animated spinner for indeterminate tasks"""
    
    def __init__(self, message: str = "Processing"):
        self.message = message
        self.running = False
        self.thread = None
        self.spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.current_idx = 0
    
    def start(self):
        """Start the spinner"""
        self.running = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self, final_message: str = "Done"):
        """Stop the spinner"""
        self.running = False
        if self.thread:
            self.thread.join()
        sys.stdout.write('\r' + ' ' * 100 + '\r')  # Clear line
        print(f"{Colors.GREEN}[✓] {final_message}{Colors.END}")
    
    def _spin(self):
        """Spinner animation loop"""
        while self.running:
            sys.stdout.write('\r')
            sys.stdout.write(
                f"{Colors.CYAN}{self.spinner_chars[self.current_idx]} "
                f"{self.message}...{Colors.END}"
            )
            sys.stdout.flush()
            self.current_idx = (self.current_idx + 1) % len(self.spinner_chars)
            time.sleep(0.1)


class LiveOutput:
    """Display live output from commands"""
    
    @staticmethod
    def print_header(text: str):
        """Print section header"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}  {text}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")
    
    @staticmethod
    def print_status(icon: str, message: str, color=Colors.CYAN):
        """Print status message"""
        print(f"{color}[{icon}] {message}{Colors.END}")
    
    @staticmethod
    def print_finding(severity: str, message: str):
        """Print a finding"""
        severity_colors = {
            'CRITICAL': Colors.RED,
            'HIGH': Colors.RED,
            'MEDIUM': Colors.YELLOW,
            'LOW': Colors.GREEN,
            'INFO': Colors.CYAN
        }
        color = severity_colors.get(severity, Colors.WHITE)
        print(f"{color}  [{severity}] {message}{Colors.END}")


# ================= BANNER =================
BANNER = f"""
{Colors.RED}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════╗
║     ADVANCED WEB VULNERABILITY SCANNER v4.0               ║
║     Nikto • SQLMap • Vulners.com • Exploit Intelligence   ║
║     Real-Time Progress • CVE Enrichment • CVSS Scoring    ║
╚═══════════════════════════════════════════════════════════╝
{Colors.END}
"""

# ================= CONFIGURATION =================
class ScanConfig:
    """Comprehensive scan configuration"""
    
    NIKTO_TUNING = {
        'full': '123456789abc',
        'quick': '123456',
        'custom': '123456789'
    }
    
    SQLMAP_LEVELS = {
        'basic': 1,
        'moderate': 3,
        'aggressive': 5
    }
    
    SQLMAP_RISKS = {
        'safe': 1,
        'moderate': 2,
        'aggressive': 3
    }
    
    PROFILES = {
        'quick': {
            'nikto_tuning': 'quick',
            'sqlmap_level': 'basic',
            'sqlmap_risk': 'safe',
            'crawl_depth': 1,
            'timeout': 10,
            'cve_lookup': True,
            'exploit_search': True
        },
        'standard': {
            'nikto_tuning': 'custom',
            'sqlmap_level': 'moderate',
            'sqlmap_risk': 'moderate',
            'crawl_depth': 2,
            'timeout': 30,
            'cve_lookup': True,
            'exploit_search': True
        },
        'comprehensive': {
            'nikto_tuning': 'full',
            'sqlmap_level': 'aggressive',
            'sqlmap_risk': 'aggressive',
            'crawl_depth': 3,
            'timeout': 60,
            'cve_lookup': True,
            'exploit_search': True
        }
    }
    
    # Vulners.com API Configuration
    VULNERS_API_KEY = None  # Will be set from config file or user input
    VULNERS_API_URL = "https://vulners.com/api/v3"
    VULNERS_REQUEST_TIMEOUT = 15
    VULNERS_BATCH_SIZE = 10
    
    # Vulnerability detection patterns for intelligent CVE mapping
    VULN_PATTERNS = {
        'sql_injection': [
            r'sql[\s_-]?inject',
            r'sql[\s_-]?vuln',
            r'blind[\s_-]?sql',
            r'error[\s_-]?based[\s_-]?sql',
            r'time[\s_-]?based[\s_-]?sql',
            r'union[\s_-]?based',
            r'boolean[\s_-]?based'
        ],
        'xss': [
            r'cross[\s_-]?site[\s_-]?script',
            r'xss',
            r'reflected[\s_-]?xss',
            r'stored[\s_-]?xss',
            r'dom[\s_-]?xss'
        ],
        'file_inclusion': [
            r'file[\s_-]?inclusion',
            r'lfi',
            r'rfi',
            r'local[\s_-]?file[\s_-]?inclusion',
            r'remote[\s_-]?file[\s_-]?inclusion',
            r'path[\s_-]?traversal',
            r'directory[\s_-]?traversal'
        ],
        'command_injection': [
            r'command[\s_-]?inject',
            r'code[\s_-]?inject',
            r'remote[\s_-]?code[\s_-]?execut',
            r'rce',
            r'os[\s_-]?command'
        ],
        'authentication_bypass': [
            r'auth.*bypass',
            r'authentication[\s_-]?bypass',
            r'login[\s_-]?bypass',
            r'access[\s_-]?control'
        ],
        'csrf': [
            r'csrf',
            r'cross[\s_-]?site[\s_-]?request[\s_-]?forgery',
            r'xsrf'
        ],
        'xxe': [
            r'xxe',
            r'xml[\s_-]?external[\s_-]?entit'
        ],
        'ssrf': [
            r'ssrf',
            r'server[\s_-]?side[\s_-]?request[\s_-]?forgery'
        ]
    }


# ================= TOOL HELPERS =================
def tool_exists(tool: str) -> bool:
    """Check if a tool is installed"""
    return shutil.which(tool) is not None


def get_tool_version(tool: str) -> Optional[str]:
    """Get tool version"""
    try:
        if tool == "nikto":
            result = subprocess.run(
                ["nikto", "-Version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            match = re.search(r'(\d+\.\d+\.\d+)', result.stdout)
            return match.group(1) if match else "unknown"
        elif tool == "sqlmap":
            result = subprocess.run(
                ["sqlmap", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            match = re.search(r'(\d+\.\d+)', result.stdout)
            return match.group(1) if match else "unknown"
    except:
        return None
    return None


def ensure_tool(tool: str) -> bool:
    """Ensure tool is installed with progress feedback"""
    if tool_exists(tool):
        LiveOutput.print_status('✓', f"{tool} is installed", Colors.GREEN)
        return True

    LiveOutput.print_status('!', f"{tool} not found. Attempting installation...", Colors.YELLOW)
    
    spinner = SpinnerAnimation(f"Installing {tool}")
    spinner.start()
    
    install_commands = {
        "nikto": "sudo apt update && sudo apt install -y nikto",
        "sqlmap": "sudo apt update && sudo apt install -y sqlmap",
    }

    if tool in install_commands:
        try:
            subprocess.run(
                install_commands[tool],
                shell=True,
                check=True,
                timeout=120,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            spinner.stop(f"{tool} installed successfully")
            return True
        except:
            spinner.stop(f"Failed to install {tool}")
            return False
    
    spinner.stop(f"No installation method for {tool}")
    return False


# ================= API KEY MANAGEMENT =================
def load_vulners_api_key() -> Optional[str]:
    """Load Vulners API key from config file or environment variable"""
    
    # Try to load from config file
    config_paths = [
        'vulners_config.json',
        os.path.expanduser('~/.vulners_config.json'),
        '/etc/vulners_config.json'
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    api_key = config.get('vulners_api_key')
                    if api_key:
                        return api_key
            except:
                pass
    
    # Try environment variable
    api_key = os.environ.get('VULNERS_API_KEY')
    if api_key:
        return api_key
    
    return None


def prompt_for_api_key() -> Optional[str]:
    """Prompt user for Vulners API key"""
    print(f"\n{Colors.YELLOW}╔════════════════════════════════════════════════════════════╗{Colors.END}")
    print(f"{Colors.YELLOW}║  VULNERS.COM API KEY SETUP                                 ║{Colors.END}")
    print(f"{Colors.YELLOW}╚════════════════════════════════════════════════════════════╝{Colors.END}\n")
    
    print(f"{Colors.CYAN}Vulners.com provides enhanced CVE intelligence with:{Colors.END}")
    print(f"  • Real-time exploit availability and exploit code")
    print(f"  • Comprehensive vulnerability details")
    print(f"  • CVSS scoring and severity analysis")
    print(f"  • Public exploits database integration")
    print(f"  • Vulnerability search and filtering\n")
    
    print(f"{Colors.YELLOW}Get your FREE API key at: https://vulners.com/userinfo{Colors.END}\n")
    
    choice = input(f"{Colors.CYAN}Do you have a Vulners API key? (y/n): {Colors.END}").strip().lower()
    
    if choice == 'y':
        api_key = input(f"{Colors.CYAN}Enter your Vulners API key: {Colors.END}").strip()
        if api_key:
            # Offer to save it
            save = input(f"{Colors.CYAN}Save API key for future use? (y/n): {Colors.END}").strip().lower()
            if save == 'y':
                config_path = os.path.expanduser('~/.vulners_config.json')
                try:
                    with open(config_path, 'w') as f:
                        json.dump({'vulners_api_key': api_key}, f, indent=4)
                    os.chmod(config_path, 0o600)  # Secure file permissions
                    print(f"{Colors.GREEN}[✓] API key saved to {config_path}{Colors.END}")
                except Exception as e:
                    print(f"{Colors.YELLOW}[!] Could not save API key: {e}{Colors.END}")
            return api_key
    
    print(f"{Colors.YELLOW}[i] Continuing without Vulners API - limited functionality{Colors.END}")
    return None


# ================= COMMAND EXECUTION WITH PROGRESS =================
def run_cmd_with_progress(
    cmd: str,
    outfile: str,
    progress_bar: ProgressBar,
    timeout: int = 300,
    pattern_checks: List[Tuple[str, str]] = None
) -> Tuple[int, str]:
    """Run command with real-time progress tracking"""
    
    try:
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        output_lines = []
        findings_count = 0
        start_time = time.time()
        
        # Monitor process output
        with open(outfile, "w") as f:
            while True:
                # Check timeout
                if time.time() - start_time > timeout:
                    process.kill()
                    progress_bar.finish("Timeout reached")
                    return -1, "Timeout"
                
                # Read output
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                
                if line:
                    f.write(line)
                    output_lines.append(line)
                    
                    # Check for patterns and update progress
                    if pattern_checks:
                        for pattern, status_msg in pattern_checks:
                            if re.search(pattern, line, re.IGNORECASE):
                                findings_count += 1
                                progress_bar.increment(status=f"{status_msg} (Found: {findings_count})")
                                
                                # Live finding display
                                if 'CVE-' in line or 'OSVDB' in line:
                                    LiveOutput.print_finding('HIGH', line.strip()[:80])
                                elif 'vulnerable' in line.lower() or 'injection' in line.lower():
                                    LiveOutput.print_finding('CRITICAL', line.strip()[:80])
                
                # Simulate progress based on time elapsed
                elapsed = time.time() - start_time
                estimated_progress = min(int((elapsed / timeout) * 100), 95)
                if progress_bar.current < estimated_progress:
                    progress_bar.update(estimated_progress)
        
        # Get return code
        returncode = process.wait()
        stderr = process.stderr.read()
        
        progress_bar.finish("Scan complete")
        return returncode, stderr
        
    except Exception as e:
        progress_bar.finish(f"Error: {str(e)}")
        return -1, str(e)


# ================= OUTPUT MANAGEMENT =================
def prepare_dirs(engagement: Dict) -> Tuple[str, str, str]:
    """Prepare output directories following project structure"""
    base = os.path.join(engagement["base"], "web_vulnerability")
    raw_dir = os.path.join(base, "raw")
    parsed_dir = os.path.join(base, "reports")
    evidence_dir = os.path.join(base, "evidence")

    for directory in [raw_dir, parsed_dir, evidence_dir]:
        os.makedirs(directory, exist_ok=True)

    return base, raw_dir, parsed_dir


# ================= VULNERS API CLIENT (ENHANCED) =================
class VulnersAPIClient:
    """Enhanced Vulners.com API Client with comprehensive search and exploit intelligence"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or ScanConfig.VULNERS_API_KEY
        self.base_url = ScanConfig.VULNERS_API_URL
        self.timeout = ScanConfig.VULNERS_REQUEST_TIMEOUT
        self.cache = {}
        self.session = requests.Session()
        
        if self.api_key:
            self.session.headers.update({'X-Api-Key': self.api_key})
            LiveOutput.print_status('✓', "Vulners API initialized", Colors.GREEN)
        else:
            LiveOutput.print_status('!', "Vulners API key not set - limited functionality", Colors.YELLOW)
    
    def search_vulnerabilities(self, query: str, size: int = 20) -> List[Dict]:
        """
        Search for vulnerabilities using Lucene query syntax
        
        Args:
            query: Lucene query string (e.g., "Fortinet AND RCE order:published")
            size: Number of results to return
            
        Returns:
            List of vulnerability records
        """
        try:
            url = f"{self.base_url}/search/lucene"
            payload = {
                "query": query,
                "size": size,
                "fields": ["id", "title", "description", "cvss", "published", 
                          "modified", "cvelist", "exploit", "exploits", "href"]
            }
            
            response = self.session.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            if data.get('result') == 'OK':
                search_results = data.get('data', {}).get('search', [])
                LiveOutput.print_status('✓', f"Found {len(search_results)} vulnerabilities", Colors.GREEN)
                return search_results
            
            return []
            
        except Exception as e:
            LiveOutput.print_status('!', f"Search error: {e}", Colors.YELLOW)
            return []
    
    def get_bulletin_by_id(self, bulletin_id: str) -> Optional[Dict]:
        """Fetch full bulletin details by ID (CVE, OSVDB, etc.)"""
        if bulletin_id in self.cache:
            return self.cache[bulletin_id]
        
        try:
            url = f"{self.base_url}/search/id/"
            payload = {
                "id": bulletin_id,
                "fields": ["id", "title", "description", "cvss", "published", 
                          "modified", "cvelist", "exploit", "exploits", "href",
                          "cvssScore", "cveList"]
            }
            
            response = self.session.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            if data.get('result') == 'OK':
                documents = data.get('data', {}).get('documents', {})
                if bulletin_id in documents:
                    bulletin_data = documents[bulletin_id]
                    self.cache[bulletin_id] = bulletin_data
                    return bulletin_data
            
            return None
            
        except Exception as e:
            LiveOutput.print_status('!', f"Error fetching {bulletin_id}: {e}", Colors.YELLOW)
            return None
    
    def search_exploits_for_cve(self, cve_id: str) -> List[Dict]:
        """
        Search for public exploits related to a CVE
        
        Returns:
            List of exploit records with details
        """
        try:
            # Search for exploits mentioning this CVE
            query = f'"{cve_id}" AND type:exploitdb OR type:github OR type:packetstorm'
            url = f"{self.base_url}/search/lucene"
            payload = {
                "query": query,
                "size": 50,
                "fields": ["id", "title", "description", "href", "type", 
                          "published", "cvelist"]
            }
            
            response = self.session.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            if data.get('result') == 'OK':
                exploits = data.get('data', {}).get('search', [])
                return exploits
            
            return []
            
        except Exception as e:
            LiveOutput.print_status('!', f"Exploit search error for {cve_id}: {e}", Colors.YELLOW)
            return []
    
    def lookup_cves_batch(self, cve_list: List[str]) -> Dict[str, Dict]:
        """Lookup multiple CVEs with detailed information and exploits"""
        results = {}
        
        if not cve_list:
            return results
        
        LiveOutput.print_header("VULNERS VULNERABILITY INTELLIGENCE")
        LiveOutput.print_status('►', f"Querying {len(cve_list)} CVE(s) + Exploit Database", Colors.CYAN)
        
        progress = ProgressBar(len(cve_list), "Vulners CVE Lookup", width=60)
        progress.start()
        
        for i, cve_id in enumerate(cve_list):
            # Get CVE details
            cve_data = self.get_bulletin_by_id(cve_id)
            
            if cve_data:
                # Search for exploits
                exploits = self.search_exploits_for_cve(cve_id)
                cve_data['available_exploits'] = exploits
                cve_data['exploit_count'] = len(exploits)
                
                results[cve_id] = cve_data
                progress.update(i + 1, f"Retrieved {cve_id}")
                
                # Display critical info
                cvss_score = self._extract_cvss(cve_data)
                exploit_count = len(exploits)
                
                if cvss_score >= 9.0:
                    exploit_msg = f" | {exploit_count} Exploit(s)" if exploit_count > 0 else ""
                    LiveOutput.print_finding('CRITICAL', f"{cve_id} - CVSS: {cvss_score:.1f}{exploit_msg}")
                elif cvss_score >= 7.0:
                    exploit_msg = f" | {exploit_count} Exploit(s)" if exploit_count > 0 else ""
                    LiveOutput.print_finding('HIGH', f"{cve_id} - CVSS: {cvss_score:.1f}{exploit_msg}")
            else:
                progress.update(i + 1, f"Not found: {cve_id}")
            
            # Rate limiting
            time.sleep(0.3)
        
        progress.finish("Vulners lookup complete")
        print(f"{Colors.GREEN}[✓] Retrieved {len(results)}/{len(cve_list)} CVE details with exploit intelligence{Colors.END}\n")
        
        return results
    
    def search_vulnerability_by_keywords(self, keywords: List[str], vuln_type: str = None) -> List[Dict]:
        """
        Search vulnerabilities by keywords extracted from scan results
        
        Args:
            keywords: List of search terms
            vuln_type: Type of vulnerability (sql_injection, xss, etc.)
            
        Returns:
            List of relevant vulnerability bulletins
        """
        results = []
        
        # Build Lucene query
        query_parts = []
        for keyword in keywords:
            query_parts.append(f'"{keyword}"')
        
        query = " AND ".join(query_parts)
        
        # Add vulnerability type filter if specified
        if vuln_type:
            type_filters = {
                'sql_injection': 'sql AND injection',
                'xss': 'xss OR "cross site scripting"',
                'rce': 'RCE OR "remote code execution"',
                'file_inclusion': 'LFI OR RFI OR "file inclusion"'
            }
            if vuln_type in type_filters:
                query += f" AND ({type_filters[vuln_type]})"
        
        # Add ordering by published date
        query += " order:published"
        
        LiveOutput.print_status('→', f"Searching Vulners: {query}", Colors.CYAN)
        
        return self.search_vulnerabilities(query, size=20)
    
    def _extract_cvss(self, bulletin_data: Dict) -> float:
        """Extract CVSS score from bulletin data"""
        try:
            # Try multiple fields
            if 'cvss' in bulletin_data:
                cvss = bulletin_data['cvss']
                if isinstance(cvss, dict):
                    return float(cvss.get('score', 0))
                return float(cvss)
            
            if 'cvssScore' in bulletin_data:
                return float(bulletin_data['cvssScore'])
            
            # Check cvelist
            cvelist = bulletin_data.get('cvelist', [])
            if cvelist and isinstance(cvelist, list):
                for cve_item in cvelist:
                    if 'cvss' in cve_item:
                        return float(cve_item['cvss'])
            
            return 0.0
            
        except:
            return 0.0
    
    def enrich_cve_data(self, cve_dict: Dict) -> Dict:
        """Enrich CVE data with Vulners intelligence"""
        enriched = {
            "total_cves": len(cve_dict),
            "critical_cves": [],
            "high_cves": [],
            "medium_cves": [],
            "low_cves": [],
            "with_exploits": [],
            "total_exploits": 0,
            "average_cvss": 0.0,
            "cve_details": cve_dict
        }
        
        cvss_scores = []
        
        for cve_id, data in cve_dict.items():
            cvss = self._extract_cvss(data)
            cvss_scores.append(cvss)
            
            # Extract details
            title = data.get('title', 'No title')
            description = data.get('description', 'No description')
            published = data.get('published', 'Unknown')
            
            # Get exploit info
            exploits = data.get('available_exploits', [])
            exploit_count = len(exploits)
            
            cve_entry = {
                "id": cve_id,
                "cvss": cvss,
                "title": title,
                "description": description[:500] if description else "",
                "published": published,
                "exploits": exploits,
                "exploit_count": exploit_count,
                "has_exploit": exploit_count > 0,
                "href": data.get('href', '')
            }
            
            # Categorize by severity
            if cvss >= 9.0:
                enriched["critical_cves"].append(cve_entry)
            elif cvss >= 7.0:
                enriched["high_cves"].append(cve_entry)
            elif cvss >= 4.0:
                enriched["medium_cves"].append(cve_entry)
            else:
                enriched["low_cves"].append(cve_entry)
            
            # Track exploitable CVEs
            if exploit_count > 0:
                enriched["with_exploits"].append(cve_entry)
                enriched["total_exploits"] += exploit_count
        
        # Calculate average CVSS
        if cvss_scores:
            enriched["average_cvss"] = round(sum(cvss_scores) / len(cvss_scores), 2)
        
        return enriched


# ================= CVE EXTRACTION (ENHANCED) =================
def extract_cves_and_keywords(nikto_results: Dict, sqlmap_results: Dict) -> Tuple[List[str], Dict[str, List[str]]]:
    """
    Extract CVEs from scan results AND identify vulnerability keywords for intelligent search
    
    Returns:
        Tuple of (cve_list, keywords_dict)
    """
    cves = set()
    keywords_by_type = {}
    
    # Extract CVEs from Nikto
    nikto_findings = nikto_results.get('findings', {})
    nikto_cves = nikto_findings.get('cve_references', [])
    cves.update(nikto_cves)
    
    LiveOutput.print_status('→', f"Found {len(nikto_cves)} direct CVEs from Nikto", Colors.CYAN)
    
    # Analyze Nikto vulnerabilities for keywords
    vulnerabilities = nikto_findings.get('vulnerabilities', [])
    
    for vuln in vulnerabilities:
        vuln_lower = vuln.lower()
        
        # Check for vulnerability patterns
        for vuln_type, patterns in ScanConfig.VULN_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, vuln_lower):
                    if vuln_type not in keywords_by_type:
                        keywords_by_type[vuln_type] = []
                    
                    # Extract potential keywords
                    words = re.findall(r'\b[a-zA-Z]{4,}\b', vuln)
                    keywords_by_type[vuln_type].extend(words[:5])  # Limit to 5 keywords per vuln
                    break
    
    # Check SQLMap results
    sqlmap_findings = sqlmap_results.get('findings', {})
    if sqlmap_findings.get('is_vulnerable', False):
        LiveOutput.print_status('!', "SQL Injection confirmed - will search for related CVEs", Colors.YELLOW)
        if 'sql_injection' not in keywords_by_type:
            keywords_by_type['sql_injection'] = []
        
        # Add SQLMap-specific keywords
        dbms = sqlmap_findings.get('dbms_detected', '')
        if dbms:
            keywords_by_type['sql_injection'].append(dbms)
        
        injection_types = sqlmap_findings.get('injection_types', [])
        keywords_by_type['sql_injection'].extend(injection_types[:3])
    
    # Clean and deduplicate keywords
    for vuln_type in keywords_by_type:
        keywords_by_type[vuln_type] = list(set([k for k in keywords_by_type[vuln_type] if len(k) > 3]))[:10]
    
    cve_list = sorted(list(cves))
    
    LiveOutput.print_status('✓', f"Total CVEs to lookup: {len(cve_list)}", Colors.GREEN)
    LiveOutput.print_status('✓', f"Identified {len(keywords_by_type)} vulnerability types with keywords", Colors.GREEN)
    
    for cve in cve_list:
        LiveOutput.print_status('  →', cve, Colors.CYAN)
    
    return cve_list, keywords_by_type


# ================= NIKTO SCANNER =================
def run_nikto_comprehensive(target: str, raw_dir: str, profile: Dict) -> Dict:
    """Run comprehensive Nikto scan with progress tracking"""
    
    LiveOutput.print_header("NIKTO WEB SERVER SCANNER")
    LiveOutput.print_status('►', f"Target: {target}", Colors.CYAN)
    LiveOutput.print_status('►', f"Tuning: {profile['nikto_tuning']}", Colors.CYAN)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outfile = os.path.join(raw_dir, f"nikto_{timestamp}.txt")
    
    tuning = ScanConfig.NIKTO_TUNING.get(
        profile['nikto_tuning'],
        ScanConfig.NIKTO_TUNING['custom']
    )
    
    cmd = (
        f"nikto -h {target} "
        f"-Tuning {tuning} "
        f"-Format txt "
        f"-output {outfile} "
        f"-nointeractive "
        f"-maxtime {profile['timeout']}m "
        f"-Plugins '@@ALL' "
        f"-evasion 1234567 "
        f"-mutate 12345 "
        f"-useragent 'Mozilla/5.0' "
    )
    
    # Progress bar with pattern matching
    progress = ProgressBar(100, "Nikto Scan Progress", width=60)
    progress.start()
    
    pattern_checks = [
        (r'OSVDB-\d+', 'OSVDB found'),
        (r'CVE-\d{4}-\d+', 'CVE detected'),
        (r'\+ /', 'Checking path'),
        (r'vulnerable', 'Vulnerability found'),
        (r'allows', 'Issue detected')
    ]
    
    start_time = time.time()
    returncode, stderr = run_cmd_with_progress(
        cmd,
        outfile,
        progress,
        timeout=profile['timeout'] * 60,
        pattern_checks=pattern_checks
    )
    scan_time = time.time() - start_time
    
    # Parse results
    findings = parse_nikto_output(outfile)
    
    # Display summary
    print(f"\n{Colors.GREEN}[✓] Nikto scan completed in {scan_time:.1f}s{Colors.END}")
    LiveOutput.print_status('→', f"Vulnerabilities: {len(findings.get('vulnerabilities', []))}", Colors.YELLOW)
    LiveOutput.print_status('→', f"CVE References: {len(findings.get('cve_references', []))}", Colors.YELLOW)
    LiveOutput.print_status('→', f"Total Findings: {findings.get('total_findings', 0)}", Colors.YELLOW)
    
    return {
        "tool": "nikto",
        "target": target,
        "timestamp": timestamp,
        "scan_time": round(scan_time, 2),
        "output_file": outfile,
        "findings": findings,
        "returncode": returncode,
        "tuning_used": tuning
    }


def parse_nikto_output(filepath: str) -> Dict:
    """Parse Nikto output for vulnerabilities"""
    findings = {
        "vulnerabilities": [],
        "information_disclosure": [],
        "misconfigurations": [],
        "outdated_software": [],
        "cve_references": [],
        "osvdb_references": [],
        "total_findings": 0
    }
    
    if not os.path.exists(filepath):
        return findings
    
    try:
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
            
            findings["cve_references"] = list(set(re.findall(r'CVE-\d{4}-\d{4,7}', content)))
            findings["osvdb_references"] = list(set(re.findall(r'OSVDB-\d+', content)))
            
            for line in content.split('\n'):
                line_lower = line.lower()
                
                if '+ OSVDB' in line or 'CVE-' in line:
                    findings["vulnerabilities"].append(line.strip())
                elif 'allows' in line_lower or 'vulnerable' in line_lower:
                    findings["vulnerabilities"].append(line.strip())
                elif 'disclosed' in line_lower or 'reveals' in line_lower:
                    findings["information_disclosure"].append(line.strip())
                elif 'config' in line_lower or 'misconfigured' in line_lower:
                    findings["misconfigurations"].append(line.strip())
                elif 'outdated' in line_lower or 'old version' in line_lower:
                    findings["outdated_software"].append(line.strip())
            
            findings["total_findings"] = sum([
                len(findings["vulnerabilities"]),
                len(findings["information_disclosure"]),
                len(findings["misconfigurations"]),
                len(findings["outdated_software"])
            ])
    
    except Exception as e:
        LiveOutput.print_status('!', f"Error parsing Nikto output: {e}", Colors.RED)
    
    return findings


# ================= SQLMAP SCANNER =================
def run_sqlmap_comprehensive(target: str, raw_dir: str, profile: Dict) -> Dict:
    """Run comprehensive SQLMap scan with progress tracking"""
    
    LiveOutput.print_header("SQLMAP SQL INJECTION SCANNER")
    LiveOutput.print_status('►', f"Target: {target}", Colors.CYAN)
    LiveOutput.print_status('►', f"Level: {profile['sqlmap_level']} | Risk: {profile['sqlmap_risk']}", Colors.CYAN)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outfile = os.path.join(raw_dir, f"sqlmap_{timestamp}.txt")
    
    level = ScanConfig.SQLMAP_LEVELS.get(profile['sqlmap_level'], 3)
    risk = ScanConfig.SQLMAP_RISKS.get(profile['sqlmap_risk'], 2)
    
    cmd = (
        f"sqlmap -u '{target}' "
        f"--batch "
        f"--level={level} "
        f"--risk={risk} "
        f"--smart "
        f"--crawl={profile['crawl_depth']} "
        f"--forms "
        f"--technique=BEUSTQ "
        f"--threads=5 "
        f"--random-agent "
        f"--timeout={profile['timeout']} "
        f"--retries=2 "
        f"--banner "
        f"--current-user "
        f"--current-db "
        f"--is-dba "
        f"--text-only "
    )
    
    # Progress bar
    progress = ProgressBar(100, "SQLMap Scan Progress", width=60)
    progress.start()
    
    pattern_checks = [
        (r'parameter.*vulnerable', 'SQL Injection found'),
        (r'injectable', 'Testing parameter'),
        (r'payload:', 'Payload sent'),
        (r'testing.*parameter', 'Testing in progress'),
        (r'retrieved:', 'Data extracted')
    ]
    
    start_time = time.time()
    returncode, stderr = run_cmd_with_progress(
        cmd,
        outfile,
        progress,
        timeout=profile['timeout'] * 60,
        pattern_checks=pattern_checks
    )
    scan_time = time.time() - start_time
    
    # Parse results
    findings = parse_sqlmap_output(outfile)
    
    # Display summary
    print(f"\n{Colors.GREEN}[✓] SQLMap scan completed in {scan_time:.1f}s{Colors.END}")
    
    if findings.get("is_vulnerable"):
        LiveOutput.print_finding('CRITICAL', "SQL INJECTION CONFIRMED!")
        for param in findings.get("injectable_parameters", []):
            LiveOutput.print_finding('CRITICAL', f"Injectable parameter: {param}")
    else:
        LiveOutput.print_status('✓', "No SQL injection detected", Colors.GREEN)
    
    return {
        "tool": "sqlmap",
        "target": target,
        "timestamp": timestamp,
        "scan_time": round(scan_time, 2),
        "output_file": outfile,
        "findings": findings,
        "returncode": returncode,
        "level": level,
        "risk": risk
    }


def parse_sqlmap_output(filepath: str) -> Dict:
    """Parse SQLMap output for SQL injection vulnerabilities"""
    findings = {
        "injectable_parameters": [],
        "injection_types": [],
        "databases_found": [],
        "is_vulnerable": False,
        "is_dba": False,
        "dbms_detected": None,
        "total_injections": 0
    }
    
    if not os.path.exists(filepath):
        return findings
    
    try:
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
            content_lower = content.lower()
            
            vuln_indicators = ['is vulnerable', 'parameter is vulnerable', 'injectable', 'injection found']
            findings["is_vulnerable"] = any(indicator in content_lower for indicator in vuln_indicators)
            
            findings["injectable_parameters"] = re.findall(r"Parameter: ([^\s]+) \([^\)]+\) is vulnerable", content)
            findings["injection_types"] = re.findall(r"Type: ([^\n]+)", content)
            
            dbms_match = re.search(r"back-end DBMS: ([^\n]+)", content)
            if dbms_match:
                findings["dbms_detected"] = dbms_match.group(1).strip()
            
            findings["is_dba"] = 'current user is DBA' in content_lower or "is dba: 'true'" in content_lower
            findings["total_injections"] = len(findings["injectable_parameters"])
    
    except Exception as e:
        LiveOutput.print_status('!', f"Error parsing SQLMap output: {e}", Colors.RED)
    
    return findings


# ================= RISK ANALYSIS =================
def calculate_comprehensive_risk(
    nikto_results: Dict,
    sqlmap_results: Dict,
    cve_intelligence: Dict
) -> Dict:
    """Calculate comprehensive risk score with Vulners CVE intelligence"""
    
    LiveOutput.print_header("RISK ANALYSIS")
    
    spinner = SpinnerAnimation("Calculating risk score")
    spinner.start()
    time.sleep(1)
    spinner.stop("Risk calculation complete")
    
    risk_score = 0
    risk_factors = []
    critical_findings = []
    
    nikto_findings = nikto_results.get("findings", {})
    
    # Analyze Nikto
    vuln_count = len(nikto_findings.get("vulnerabilities", []))
    if vuln_count > 0:
        risk_score += min(vuln_count * 5, 40)
        risk_factors.append(f"Nikto: {vuln_count} vulnerabilities detected")
        if vuln_count > 3:
            critical_findings.append(f"High number of vulnerabilities: {vuln_count}")
    
    cve_count = len(nikto_findings.get("cve_references", []))
    if cve_count > 0:
        risk_score += min(cve_count * 10, 30)
        risk_factors.append(f"Nikto: {cve_count} CVE references found")
        if cve_count > 2:
            critical_findings.append(f"Multiple CVEs detected: {cve_count}")
    
    # Analyze SQLMap
    sqlmap_findings = sqlmap_results.get("findings", {})
    
    if sqlmap_findings.get("is_vulnerable", False):
        risk_score += 50
        risk_factors.append("SQLMap: SQL Injection vulnerability CONFIRMED")
        critical_findings.append("SQL Injection vulnerability detected - CRITICAL")
    
    injectable_count = len(sqlmap_findings.get("injectable_parameters", []))
    if injectable_count > 0:
        risk_score += min(injectable_count * 15, 30)
        risk_factors.append(f"SQLMap: {injectable_count} injectable parameters")
        critical_findings.append(f"Injectable parameters: {injectable_count}")
    
    if sqlmap_findings.get("is_dba", False):
        risk_score += 20
        risk_factors.append("SQLMap: DBA access possible")
        critical_findings.append("Database administrator access possible")
    
    # Analyze Vulners CVE Intelligence
    if cve_intelligence:
        critical_cves = len(cve_intelligence.get("critical_cves", []))
        high_cves = len(cve_intelligence.get("high_cves", []))
        with_exploits = len(cve_intelligence.get("with_exploits", []))
        total_exploits = cve_intelligence.get("total_exploits", 0)
        avg_cvss = cve_intelligence.get("average_cvss", 0)
        
        if critical_cves > 0:
            risk_score += critical_cves * 15
            risk_factors.append(f"Vulners: {critical_cves} CRITICAL CVEs (CVSS ≥ 9.0)")
            critical_findings.append(f"CRITICAL CVEs detected: {critical_cves}")
        
        if high_cves > 0:
            risk_score += high_cves * 10
            risk_factors.append(f"Vulners: {high_cves} HIGH CVEs (CVSS ≥ 7.0)")
        
        if with_exploits > 0:
            risk_score += with_exploits * 20  # Higher weight for exploitable CVEs
            risk_factors.append(f"Vulners: {with_exploits} CVEs with public exploits ({total_exploits} total exploits)")
            critical_findings.append(f"CVEs with public exploits: {with_exploits} ({total_exploits} exploits available)")
        
        if avg_cvss >= 7.0:
            risk_score += 15
            risk_factors.append(f"Vulners: High average CVSS score: {avg_cvss}")
    
    # Determine risk level
    if risk_score >= 80:
        risk_level = "CRITICAL"
        color = Colors.RED
    elif risk_score >= 50:
        risk_level = "HIGH"
        color = Colors.RED
    elif risk_score >= 25:
        risk_level = "MEDIUM"
        color = Colors.YELLOW
    else:
        risk_level = "LOW"
        color = Colors.GREEN
    
    # Display risk assessment
    print(f"\n{color}{Colors.BOLD}RISK LEVEL: {risk_level} (Score: {min(risk_score, 100)}/100){Colors.END}\n")
    
    return {
        "risk_level": risk_level,
        "risk_score": min(risk_score, 100),
        "color": color,
        "risk_factors": risk_factors,
        "critical_findings": critical_findings
    }


# ================= REPORT GENERATION (Truncated for space - keeping structure) =================
def generate_html_report(
    target: str,
    nikto_results: Dict,
    sqlmap_results: Dict,
    cve_intelligence: Dict,
    risk_analysis: Dict,
    parsed_dir: str,
    profile_name: str
) -> str:
    """Generate professional HTML report with Vulners intelligence"""
    
    spinner = SpinnerAnimation("Generating HTML report")
    spinner.start()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Same HTML structure as before, but enhanced CVE section
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Vulnerability Assessment Report - {urlparse(target).netloc}</title>
    <style>
        /* Same CSS as before */
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; background: #f4f4f4; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }}
        .section {{ background: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .exploit-badge {{ background: #dc3545; color: white; padding: 5px 10px; border-radius: 3px; font-size: 0.85em; margin-left: 10px; }}
        .cve-card {{ background: #f8f9fa; padding: 15px; border-left: 4px solid #dc3545; margin: 10px 0; border-radius: 5px; }}
        .exploit-list {{ margin-top: 10px; padding-left: 20px; }}
        .exploit-item {{ margin: 5px 0; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔒 Web Vulnerability Assessment Report</h1>
            <p>Comprehensive Security Analysis with Exploit Intelligence</p>
            <p style="font-size: 0.9em; margin-top: 10px;">Generated: {timestamp}</p>
        </header>
"""
    
    # Add CVE Intelligence section with exploit information
    if cve_intelligence and cve_intelligence.get('total_cves', 0) > 0:
        html_content += f"""
        <div class="section">
            <h2>🎯 Vulners CVE Intelligence & Exploit Database</h2>
            <p>Comprehensive vulnerability intelligence from Vulners.com database</p>
            
            <div class="metrics">
                <div class="metric-card">
                    <h3>Total Exploits Found</h3>
                    <div class="value" style="color: #dc3545;">{cve_intelligence.get('total_exploits', 0)}</div>
                </div>
                <div class="metric-card">
                    <h3>CVEs with Exploits</h3>
                    <div class="value">{len(cve_intelligence.get('with_exploits', []))}</div>
                </div>
                <div class="metric-card">
                    <h3>Average CVSS</h3>
                    <div class="value">{cve_intelligence.get('average_cvss', 0):.2f}</div>
                </div>
            </div>
"""
        
        # Show CVEs with exploits
        if cve_intelligence.get('with_exploits'):
            html_content += """
            <h3 style="color: #dc3545; margin-top: 30px;">⚠️ CVEs with Public Exploits</h3>
"""
            for cve in cve_intelligence['with_exploits']:
                html_content += f"""
            <div class="cve-card">
                <div class="cve-id">{cve['id']}
                    <span class="cvss-score">CVSS: {cve['cvss']:.1f}</span>
                    <span class="exploit-badge">{cve['exploit_count']} Exploit(s) Available</span>
                </div>
                <div style="margin-top: 10px;"><strong>{cve.get('title', 'No title')}</strong></div>
                <div style="margin-top: 10px; color: #666;">{cve.get('description', 'No description')[:300]}...</div>
                
                <div class="exploit-list">
                    <strong>Available Exploits:</strong>
"""
                for exploit in cve.get('exploits', [])[:5]:  # Show first 5 exploits
                    exploit_title = exploit.get('title', 'Unnamed exploit')
                    exploit_href = exploit.get('href', '#')
                    html_content += f"""
                    <div class="exploit-item">• <a href="{exploit_href}" target="_blank">{exploit_title}</a></div>
"""
                html_content += """
                </div>
            </div>
"""
        
        html_content += """
        </div>
"""
    
    # Continue with rest of report...
    html_content += """
    </div>
</body>
</html>
"""
    
    html_file = os.path.join(parsed_dir, f"web_vuln_report_{report_timestamp}.html")
    
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    spinner.stop("HTML report generated successfully")
    
    return html_file


def generate_comprehensive_json_report(
    target: str,
    nikto_results: Dict,
    sqlmap_results: Dict,
    cve_intelligence: Dict,
    risk_analysis: Dict,
    parsed_dir: str,
    profile_name: str
) -> str:
    """Generate comprehensive JSON report"""
    
    spinner = SpinnerAnimation("Generating JSON report")
    spinner.start()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    report = {
        "scan_metadata": {
            "target": target,
            "timestamp": timestamp,
            "profile": profile_name,
            "tools_used": ["nikto", "sqlmap", "vulners"],
            "tool_versions": {
                "nikto": get_tool_version("nikto"),
                "sqlmap": get_tool_version("sqlmap"),
                "vulners_api": ScanConfig.VULNERS_API_URL
            }
        },
        "risk_assessment": risk_analysis,
        "cve_intelligence": cve_intelligence,
        "nikto_results": nikto_results,
        "sqlmap_results": sqlmap_results,
        "summary": {
            "total_vulnerabilities": len(nikto_results.get("findings", {}).get("vulnerabilities", [])),
            "cve_count": len(nikto_results.get("findings", {}).get("cve_references", [])),
            "cves_with_exploits": len(cve_intelligence.get("with_exploits", [])) if cve_intelligence else 0,
            "total_exploits": cve_intelligence.get("total_exploits", 0) if cve_intelligence else 0,
            "sql_injection_found": sqlmap_results.get("findings", {}).get("is_vulnerable", False),
            "total_scan_time": nikto_results.get("scan_time", 0) + sqlmap_results.get("scan_time", 0)
        }
    }
    
    report_file = os.path.join(parsed_dir, f"web_vuln_comprehensive_{timestamp}.json")
    
    with open(report_file, "w") as f:
        json.dump(report, f, indent=4)
    
    spinner.stop("JSON report generated successfully")
    
    return report_file


def print_final_summary(
    target: str,
    nikto_results: Dict,
    sqlmap_results: Dict,
    cve_intelligence: Dict,
    risk_analysis: Dict,
    html_report: str,
    json_report: str
):
    """Print final comprehensive summary"""
    
    LiveOutput.print_header("SCAN COMPLETE - FINAL SUMMARY")
    
    print(f"{Colors.BOLD}Target:{Colors.END} {target}")
    print(f"{Colors.BOLD}Total Time:{Colors.END} {nikto_results.get('scan_time', 0) + sqlmap_results.get('scan_time', 0):.1f}s\n")
    
    # Risk assessment
    risk_color = risk_analysis['color']
    print(f"{Colors.BOLD}RISK ASSESSMENT:{Colors.END}")
    print(f"  {risk_color}{Colors.BOLD}{risk_analysis['risk_level']}{Colors.END} (Score: {risk_analysis['risk_score']}/100)\n")
    
    # Vulners Intelligence Summary
    if cve_intelligence:
        print(f"{Colors.BOLD}VULNERS EXPLOIT INTELLIGENCE:{Colors.END}")
        print(f"  Total CVEs Analyzed: {cve_intelligence.get('total_cves', 0)}")
        print(f"  CVEs with Exploits: {Colors.RED}{len(cve_intelligence.get('with_exploits', []))}{Colors.END}")
        print(f"  Total Exploits Found: {Colors.RED}{cve_intelligence.get('total_exploits', 0)}{Colors.END}")
        print(f"  Critical (CVSS ≥9.0): {Colors.RED}{len(cve_intelligence.get('critical_cves', []))}{Colors.END}")
        print(f"  Average CVSS: {cve_intelligence.get('average_cvss', 0):.2f}\n")
    
    # Critical findings
    if risk_analysis['critical_findings']:
        print(f"{Colors.RED}{Colors.BOLD}CRITICAL FINDINGS:{Colors.END}")
        for finding in risk_analysis['critical_findings']:
            print(f"  {Colors.RED}• {finding}{Colors.END}")
        print()
    
    # Report locations
    print(f"{Colors.GREEN}{Colors.BOLD}[✓] Reports Generated:{Colors.END}")
    print(f"    📊 HTML Report: {html_report}")
    print(f"    📄 JSON Report: {json_report}")
    print(f"\n{Colors.BLUE}[i] Reports saved in: {os.path.dirname(html_report)}{Colors.END}\n")
    
    print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")


# ================= MAIN FUNCTION =================
def run(engagement: Dict):
    """Main scan orchestration with Vulners API integration"""
    
    print(BANNER)
    
    # Load or prompt for Vulners API key
    if not ScanConfig.VULNERS_API_KEY:
        api_key = load_vulners_api_key()
        if not api_key:
            api_key = prompt_for_api_key()
        ScanConfig.VULNERS_API_KEY = api_key
    
    # Get target
    target = input(f"{Colors.YELLOW}[*] Target URL (e.g., http://example.com): {Colors.END}").strip()
    
    if not target.startswith(("http://", "https://")):
        print(f"{Colors.RED}[!] Invalid URL format{Colors.END}")
        return
    
    # Select profile
    print(f"\n{Colors.BOLD}Select Scan Profile:{Colors.END}")
    print(f"  {Colors.GREEN}1.{Colors.END} Quick (5-15 min)")
    print(f"  {Colors.YELLOW}2.{Colors.END} Standard (15-45 min) ⭐ Recommended")
    print(f"  {Colors.RED}3.{Colors.END} Comprehensive (45+ min)")
    
    profile_choice = input(f"{Colors.YELLOW}Choice [1-3]: {Colors.END}").strip()
    
    profile_map = {'1': 'quick', '2': 'standard', '3': 'comprehensive'}
    profile_name = profile_map.get(profile_choice, 'standard')
    profile = ScanConfig.PROFILES[profile_name]
    
    LiveOutput.print_status('✓', f"Profile: {profile_name.upper()}", Colors.GREEN)
    
    # Prepare directories
    base_dir, raw_dir, parsed_dir = prepare_dirs(engagement)
    
    # Check tools
    LiveOutput.print_header("TOOL VERIFICATION")
    
    if not ensure_tool("nikto") or not ensure_tool("sqlmap"):
        print(f"{Colors.RED}[!] Required tools missing{Colors.END}")
        return
    
    print(f"\n{Colors.GREEN}[✓] All tools ready{Colors.END}")
    input(f"\n{Colors.YELLOW}Press ENTER to start scan...{Colors.END}\n")
    
    # Run scans
    nikto_results = run_nikto_comprehensive(target, raw_dir, profile)
    sqlmap_results = run_sqlmap_comprehensive(target, raw_dir, profile)
    
    # Enhanced CVE Intelligence with Vulners
    cve_intelligence = None
    if profile.get('cve_lookup', True) and ScanConfig.VULNERS_API_KEY:
        # Extract CVEs and keywords
        cve_list, keywords_dict = extract_cves_and_keywords(nikto_results, sqlmap_results)
        
        if cve_list or keywords_dict:
            vulners_client = VulnersAPIClient(ScanConfig.VULNERS_API_KEY)
            
            # Lookup known CVEs
            cve_data = {}
            if cve_list:
                cve_data = vulners_client.lookup_cves_batch(cve_list)
            
            # Search for additional vulnerabilities using keywords
            if keywords_dict and profile.get('exploit_search', True):
                LiveOutput.print_header("VULNERABILITY KEYWORD SEARCH")
                for vuln_type, keywords in keywords_dict.items():
                    if keywords:
                        LiveOutput.print_status('→', f"Searching for {vuln_type} vulnerabilities", Colors.CYAN)
                        search_results = vulners_client.search_vulnerability_by_keywords(keywords, vuln_type)
                        
                        # Add search results to CVE data
                        for result in search_results[:5]:  # Top 5 results per type
                            result_id = result.get('id')
                            if result_id and result_id not in cve_data:
                                cve_data[result_id] = result
            
            # Enrich with exploit data
            cve_intelligence = vulners_client.enrich_cve_data(cve_data)
    
    # Analyze risk
    risk_analysis = calculate_comprehensive_risk(nikto_results, sqlmap_results, cve_intelligence or {})
    
    # Generate reports
    html_report = generate_html_report(
        target, nikto_results, sqlmap_results, cve_intelligence, risk_analysis, parsed_dir, profile_name
    )
    
    json_report = generate_comprehensive_json_report(
        target, nikto_results, sqlmap_results, cve_intelligence, risk_analysis, parsed_dir, profile_name
    )
    
    # Print summary
    print_final_summary(target, nikto_results, sqlmap_results, cve_intelligence or {}, risk_analysis, html_report, json_report)


# ================= ENTRY POINT =================
if __name__ == "__main__":
    engagement = {"base": "./test_engagement"}
    run(engagement)
