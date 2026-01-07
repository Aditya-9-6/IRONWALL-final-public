import re

# Pre-compiled Regex Patterns for High Performance
SQLI_PATTERNS = [
    re.compile(r"(?i)(union\s+select)"),
    re.compile(r"(?i)(or\s+1=1)"),
    re.compile(r"(?i)(--\s)"),  # SQL Comment
    re.compile(r"(?i)(drop\s+table)"),
    re.compile(r"(?i)(insert\s+into)"),
    re.compile(r"(?i)(xp_cmdshell)"),
]

XSS_PATTERNS = [
    re.compile(r"(?i)(<script>)"),
    re.compile(r"(?i)(javascript:)"),
    re.compile(r"(?i)(onerror=)"),
    re.compile(r"(?i)(onload=)"),
]

PATH_TRAVERSAL_PATTERNS = [
    re.compile(r"(\.\./\.\./)"),
    re.compile(r"(\.\./etc/passwd)"),
    re.compile(r"(\.\.\\\.\.\\)"), # Windows style
]

BAD_USER_AGENTS = [
    "curl",
    "wget",
    "python-requests",
    "scrapy",
    "bot",
    "crawler",
    "spider",
]

def check_request(method, path, body, headers):
    """
    Analyzes the request for malicious patterns.
    Returns:
        None if SAFE
        A string describing the rule if UNSAFE
    """
    
    # Check 0: Bad User-Agents
    ua = headers.get("User-Agent", "").lower()
    if not ua: # Empty UA is suspicious
        return "Empty User-Agent"
    for bot in BAD_USER_AGENTS:
        if bot in ua:
            return f"Bad User-Agent: {bot}"

    # Check 1: Request Path (scanning for SQLi/XSS/Traversal in URL)
    raw_content = f"{path} {body}"
    
    # Scan for SQL Injection
    for pattern in SQLI_PATTERNS:
        if pattern.search(raw_content):
            return f"SQLi: {pattern.pattern}"

    # Scan for XSS
    for pattern in XSS_PATTERNS:
        if pattern.search(raw_content):
            return f"XSS: {pattern.pattern}"
            
    # Scan for Path Traversal
    for pattern in PATH_TRAVERSAL_PATTERNS:
        if pattern.search(raw_content):
            return f"Path Traversal: {pattern.pattern}"

    return None
