# Enhanced Web Vulnerability Scanner with Vulners.com Integration

## 🎯 Overview

This enhanced version integrates the powerful **Vulners.com API** to provide comprehensive CVE intelligence and exploit discovery capabilities. The scanner now not only detects vulnerabilities but also:

- ✅ Fetches detailed CVE information with CVSS scores
- ✅ Searches for public exploits available for discovered vulnerabilities
- ✅ Performs intelligent vulnerability search using keywords
- ✅ Provides exploit availability statistics
- ✅ Generates enriched reports with exploit intelligence

---

## 🚀 Key Enhancements

### 1. **Vulners.com API Integration**

#### Search Vulnerabilities by Lucene Query
```python
vulners_client = VulnersAPIClient(api_key)
results = vulners_client.search_vulnerabilities(
    query="Fortinet AND RCE order:published",
    size=20
)
```

#### Get Bulletin Details by ID
```python
cve_data = vulners_client.get_bulletin_by_id("CVE-2021-44228")
```

#### Search for Exploits
```python
exploits = vulners_client.search_exploits_for_cve("CVE-2021-44228")
```

### 2. **Intelligent Vulnerability Detection**

The scanner now automatically:
- Extracts CVE references from scan results
- Identifies vulnerability types (SQL injection, XSS, RCE, etc.)
- Extracts keywords for intelligent searching
- Maps vulnerability patterns to search queries

### 3. **Enhanced CVE Intelligence**

For each CVE, the scanner provides:
- **Title & Description**: Full vulnerability details
- **CVSS Score**: Severity rating (0-10 scale)
- **Published/Modified Dates**: Timeline information
- **Exploit Count**: Number of public exploits available
- **Exploit Details**: Links to exploit code and PoCs
- **Categorization**: Critical/High/Medium/Low severity

### 4. **Exploit Discovery**

The scanner searches multiple exploit databases:
- ExploitDB
- GitHub repositories
- Packet Storm Security
- Metasploit modules
- And more...

---

## 📋 Vulners.com API Reference

### Core Concepts (from your images)

1. **Record** — A single vulnerability/advisory entry (CVE, vendor bulletin, etc.)
2. **Collection** — A curated set of records or rules you can reuse and share
3. **Audit** — A report for a host or image that maps installed packages to known vulnerabilities
4. **Search Model** — Lucene-style query language + structured filters
5. **OpenAPI** — The canonical machine spec lives in `docs/assets/openapi.yaml`

### Search Endpoint

**Endpoint:** `POST https://vulners.com/api/v3/search/lucene`

**Authentication:** `X-Api-Key` header required

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| query | string | yes | Lucene query string |
| skip | integer | no | Offset |
| size | integer | no | Number of results |
| fields | array[string] | no | Fields to include. Use `["*"]` for all fields |

**Example Request:**
```python
import os, requests

API_KEY = os.getenv("VULNERS_API_KEY")
resp = requests.post(
    "https://vulners.com/api/v3/search/lucene",
    headers={
        "X-Api-Key": API_KEY,
        "Content-Type": "application/json"
    },
    json={
        "query": "Fortinet AND RCE order:published",
        "size": 5,
        "fields": ["id", "title", "description", "cvss", "published", "exploits"]
    },
)
resp.raise_for_status()
data = resp.json()
```

### Response Structure

```json
{
  "result": "OK",
  "data": {
    "search": [
      {
        "id": "CVE-2021-XXXXX",
        "title": "Vulnerability Title",
        "description": "Detailed description...",
        "cvss": {
          "score": 9.8
        },
        "published": "2021-12-09T00:00:00",
        "exploits": [
          {
            "id": "EXPLOIT-DB:12345",
            "title": "Exploit Title",
            "href": "https://www.exploit-db.com/exploits/12345"
          }
        ]
      }
    ]
  }
}
```

---

## 🔧 Setup Instructions

### 1. Get Your Vulners API Key

1. Visit https://vulners.com/userinfo
2. Register for a FREE account
3. Navigate to your API key section
4. Copy your API key

### 2. Configure the Scanner

**Option 1: Environment Variable**
```bash
export VULNERS_API_KEY="your_api_key_here"
```

**Option 2: Configuration File**
```bash
# Create config file
cat > ~/.vulners_config.json << EOF
{
  "vulners_api_key": "your_api_key_here"
}
EOF

# Secure the file
chmod 600 ~/.vulners_config.json
```

**Option 3: Interactive Prompt**
The scanner will prompt you for the API key if not found.

### 3. Install Dependencies

```bash
# Install required tools
sudo apt update
sudo apt install -y nikto sqlmap python3 python3-pip

# Install Python dependencies
pip3 install requests --break-system-packages
```

### 4. Run the Scanner

```bash
python3 web_vuln_scanner_enhanced.py
```

---

## 📊 How the Enhanced Integration Works

### Workflow

```
1. Scan Target (Nikto + SQLMap)
   ↓
2. Extract CVE References
   ↓
3. Identify Vulnerability Patterns
   ↓
4. Extract Keywords for Search
   ↓
5. Query Vulners API
   ├─ Lookup Known CVEs
   ├─ Search by Vulnerability Type
   └─ Fetch Exploit Information
   ↓
6. Enrich CVE Data
   ├─ CVSS Scoring
   ├─ Categorize by Severity
   ├─ Count Exploits
   └─ Link to Exploit Code
   ↓
7. Generate Enhanced Report
   ├─ CVE Details with CVSS
   ├─ Exploit Availability
   ├─ Links to Exploit Code
   └─ Risk Assessment
```

### Example: SQL Injection Detection

```
1. SQLMap detects SQL injection
   ↓
2. Scanner identifies vulnerability type: "sql_injection"
   ↓
3. Extracts keywords: ["MySQL", "blind", "time-based"]
   ↓
4. Builds Vulners query: "MySQL AND (sql AND injection) AND (blind OR time-based) order:published"
   ↓
5. Vulners returns relevant CVEs
   ↓
6. For each CVE, search for exploits
   ↓
7. Report shows:
   - CVE-2021-XXXXX (CVSS: 9.8)
   - 3 exploits available
   - Links to ExploitDB, GitHub
```

---

## 🎨 Enhanced Report Features

### HTML Report Sections

1. **Executive Summary**
   - Risk level with color coding
   - Total vulnerabilities count
   - CVE references
   - Exploit statistics

2. **Vulners Exploit Intelligence**
   - Total exploits found
   - CVEs with public exploits
   - Average CVSS score
   - Detailed CVE cards with:
     - CVSS score badge
     - Exploit count badge
     - Exploit links (ExploitDB, GitHub, etc.)

3. **Critical Findings**
   - Highlighted critical vulnerabilities
   - Exploitable CVEs emphasized
   - Severity-based color coding

4. **Detailed CVE Analysis**
   - Critical CVEs (CVSS ≥ 9.0)
   - High severity CVEs (CVSS ≥ 7.0)
   - Medium/Low CVEs
   - Full descriptions
   - Published/Modified dates

5. **Exploit Details**
   - For each CVE with exploits:
     - Exploit titles
     - Direct links to exploit code
     - Exploit types (PoC, Metasploit, etc.)

### JSON Report Structure

```json
{
  "scan_metadata": {
    "target": "http://example.com",
    "timestamp": "20240202_143022",
    "profile": "standard",
    "tools_used": ["nikto", "sqlmap", "vulners"]
  },
  "risk_assessment": {
    "risk_level": "HIGH",
    "risk_score": 85,
    "critical_findings": [
      "CVEs with public exploits: 3 (7 exploits available)"
    ]
  },
  "cve_intelligence": {
    "total_cves": 5,
    "critical_cves": [...],
    "with_exploits": [...],
    "total_exploits": 7,
    "average_cvss": 8.2
  },
  "summary": {
    "cves_with_exploits": 3,
    "total_exploits": 7
  }
}
```

---

## 🔍 Vulnerability Search Patterns

The scanner uses intelligent pattern matching to identify vulnerability types:

```python
VULN_PATTERNS = {
    'sql_injection': [
        r'sql[\s_-]?inject',
        r'blind[\s_-]?sql',
        r'union[\s_-]?based'
    ],
    'xss': [
        r'cross[\s_-]?site[\s_-]?script',
        r'reflected[\s_-]?xss',
        r'dom[\s_-]?xss'
    ],
    'rce': [
        r'remote[\s_-]?code[\s_-]?execut',
        r'command[\s_-]?inject'
    ]
    # ... and more
}
```

---

## 🎯 Use Cases

### 1. Penetration Testing
- Identify vulnerabilities with public exploits
- Prioritize testing based on exploit availability
- Validate findings with CVE database

### 2. Vulnerability Assessment
- Generate comprehensive reports with CVE intelligence
- Track CVSS scores for risk prioritization
- Document exploit availability for remediation planning

### 3. Security Research
- Discover related CVEs through keyword search
- Find exploit code for vulnerability analysis
- Track vulnerability trends and patterns

### 4. Compliance & Auditing
- Document CVE references for compliance reports
- Demonstrate exploit risk to stakeholders
- Track vulnerability remediation progress

---

## 📈 Risk Calculation

The enhanced risk scoring now includes exploit intelligence:

```python
Risk Factors:
- CVEs with Exploits: +20 points per CVE
- Total Exploit Count: Bonus points
- CVSS >= 9.0: +15 points per CVE
- CVSS >= 7.0: +10 points per CVE
- SQL Injection: +50 points
- DBA Access: +20 points
```

**Example Risk Score:**
```
Base Vulnerabilities: 40 points
+ 3 CVEs with exploits (7 total): +60 points
+ High CVSS average (8.2): +15 points
+ SQL Injection confirmed: +50 points
= 165 points → CRITICAL RISK
```

---

## 🛠️ Advanced Features

### Custom Lucene Queries

The scanner supports custom Vulners queries:

```python
# Search for recent RCE vulnerabilities in Apache
query = "Apache AND RCE order:published published:[2023-01-01 TO *]"

# Search for high severity WordPress vulnerabilities
query = "WordPress cvss.score:>=7.0"

# Search for vulnerabilities with public exploits
query = "Drupal exploitdb:*"
```

### Batch CVE Lookup

Efficiently lookup multiple CVEs:

```python
cve_list = ["CVE-2021-44228", "CVE-2020-1472", "CVE-2019-0708"]
results = vulners_client.lookup_cves_batch(cve_list)
```

### Exploit Search

Find exploits for specific CVEs:

```python
exploits = vulners_client.search_exploits_for_cve("CVE-2021-44228")

for exploit in exploits:
    print(f"Title: {exploit['title']}")
    print(f"Link: {exploit['href']}")
    print(f"Type: {exploit['type']}")
```

---

## 📝 Example Output

### Console Output

```
╔═══════════════════════════════════════════════════════════╗
║     ADVANCED WEB VULNERABILITY SCANNER v4.0               ║
║     Nikto • SQLMap • Vulners.com • Exploit Intelligence   ║
╚═══════════════════════════════════════════════════════════╝

[✓] Vulners API initialized

============================================================
  VULNERS VULNERABILITY INTELLIGENCE
============================================================

[►] Querying 5 CVE(s) + Exploit Database

Vulners CVE Lookup: [████████████████████████████████] 100% | Retrieved CVE-2021-44228

  [CRITICAL] CVE-2021-44228 - CVSS: 10.0 | 12 Exploit(s)
  [HIGH] CVE-2020-1472 - CVSS: 8.8 | 3 Exploit(s)
  [HIGH] CVE-2019-0708 - CVSS: 9.8 | 5 Exploit(s)

[✓] Retrieved 5/5 CVE details with exploit intelligence

============================================================
  RISK ANALYSIS
============================================================

RISK LEVEL: CRITICAL (Score: 95/100)

VULNERS EXPLOIT INTELLIGENCE:
  Total CVEs Analyzed: 5
  CVEs with Exploits: 3
  Total Exploits Found: 20
  Critical (CVSS ≥9.0): 2
  Average CVSS: 9.2

CRITICAL FINDINGS:
  • CVEs with public exploits: 3 (20 exploits available)
  • CRITICAL CVEs detected: 2
```

---

## 🔐 Security Considerations

1. **API Key Security**
   - Store API keys securely (environment variables or config files with 600 permissions)
   - Never commit API keys to version control
   - Rotate keys periodically

2. **Rate Limiting**
   - The scanner implements 0.3s delays between API calls
   - Respect Vulners API rate limits
   - Consider batch operations for large scans

3. **Data Privacy**
   - CVE data is cached to minimize API calls
   - Reports contain sensitive information - handle appropriately
   - Consider data retention policies

---

## 🆘 Troubleshooting

### API Key Issues

```
[!] Vulners API key not set - limited functionality
```

**Solution:** Set your API key using one of the three methods above.

### No CVEs Found

```
[!] No CVEs to lookup
```

**Solution:** The scanner will still perform keyword-based searches to find related vulnerabilities.

### API Errors

```
[!] Error looking up CVE-2021-XXXXX: 429 Too Many Requests
```

**Solution:** Rate limiting triggered. Wait a moment and try again with fewer CVEs.

---

## 📚 Resources

- **Vulners.com API Docs:** https://vulners.com/docs/
- **Vulners Website:** https://vulners.com/
- **Get API Key:** https://vulners.com/userinfo
- **Nikto Documentation:** https://cirt.net/Nikto2
- **SQLMap Documentation:** https://sqlmap.org/

---

## 🤝 Contributing

Suggestions for enhancement:
1. Add support for additional exploit databases
2. Implement CVE filtering by date range
3. Add export to PDF format
4. Integrate with vulnerability management platforms

---

## 📄 License

This tool is for authorized security testing only. Always obtain proper authorization before scanning any systems.

---

## ✨ Summary of Changes

### What Was Enhanced:

1. ✅ **Full Vulners.com API integration** following official documentation
2. ✅ **CVE lookup with detailed information** (CVSS, descriptions, dates)
3. ✅ **Exploit search functionality** across multiple databases
4. ✅ **Intelligent keyword extraction** from scan results
5. ✅ **Vulnerability-type search** using Lucene queries
6. ✅ **Enhanced HTML reports** with exploit details and links
7. ✅ **JSON export** with complete exploit intelligence
8. ✅ **Risk scoring** weighted by exploit availability
9. ✅ **Batch CVE processing** for efficiency
10. ✅ **Comprehensive error handling** and progress tracking

### Key Improvements Over Original:

| Feature | Original | Enhanced |
|---------|----------|----------|
| CVE Lookup | Basic CVE CIRCL fallback | Full Vulners API with exploit search |
| Exploit Intelligence | None | Complete exploit database integration |
| Vulnerability Search | Manual CVE list only | Intelligent keyword-based search |
| CVSS Scoring | Basic display | Detailed scoring with categorization |
| Report Quality | Basic CVE info | Full CVE details + exploit links |
| Risk Assessment | Simple scoring | Exploit-weighted risk calculation |

---

**Happy Hunting! 🎯🔒**
