# Lab 5: Documented Issues and Fixes

**Student Name:** Sushir C  
**SRN:** PES1UG24AM297  
**Course:** Software Engineering Lab (Lab 5: Static Code Analysis)  
**Assigned Repository:** `L5_57_loan-eligibility` (`loan_calculator.py`)  

---

## Static Code Analysis Issues Table

The following table documents the vulnerabilities, bugs, code smells, and style violations detected by **Bandit**, **Flake8**, and **Pylint** in `loan_calculator.py`, prioritized by severity (High and Medium first, followed by Low, Warnings, and Conventions).

| Issue | Tool | Severity / Type | Line(s) | Description | Fix Approach |
|:---|:---:|:---:|:---:|:---|:---|
| **Insecure Cleartext Protocol (`ftplib` import & call)** | Bandit | High / Security (B402, B321) | 3, 68 | Cleartext FTP module `ftplib` imported and `ftplib.FTP` invoked. FTP sends credentials and payloads unencrypted over the wire (CWE-319). | Remove `ftplib` and replace bureau transmission with a secure API client endpoint over HTTPS/TLS with encrypted transport. |
| **Insecure Deserialization (`marshal`)** | Bandit | Medium / Security (B302) | 4, 64 | Deserialization of unauthenticated or untrusted binary data with `marshal.loads()` can lead to memory corruption or arbitrary code execution (CWE-502). | Replace binary `marshal` dumps/loads with standard, safe text-based `json` serialization (`json.dump` / `json.load`). |
| **Hardcoded Password Default** | Bandit | Low / Security (B107) | 67 | Default function parameter `password="Bureau#2024"` embeds plain-text authentication credentials directly in the codebase (CWE-259). | Remove hardcoded password string; load credentials dynamically from environment variables (`os.getenv("BUREAU_PASSWORD")`) or a secure secret manager. |
| **Insecure Pseudo-Random Number Generator** | Bandit | Low / Security (B311) | 5, 51 | `random.randint()` uses a predictable PRNG (Mersenne Twister) unsuitable for unique identifier or cryptographic generation (CWE-330). | Replace `random.randint` with Python's cryptographically strong `secrets` module (`secrets.randbelow`). |
| **Insecure Subprocess Execution** | Bandit / Pylint | Low / Security (B404, B603, B607) & Warning (W1510) | 6, 74 | `subprocess.run(["mail", ...])` called without full executable path, without shell parameter validation, and without `check=True`. | Remove external process shell invocation in favor of an internal secure notification service or safe helper with explicit arguments. |
| **Mutable Default Argument** | Pylint | Bug / Warning (W0102) | 20 | `checkEligibility(..., history=[])` used a mutable list as default argument, causing application history state to bleed across calls. | Change default value to `history=None` and initialize `if history is None: history = []` inside the function body. |
| **Short-Circuiting Eligibility Logic** | Manual / Quality | Bug / Logic Error | 24 | `if credit_score > 750 or income > 25000: return True` approved loans before validating FOIR (Debt-to-Income) or loan category, approving bankrupt applicants. | Reorder verification checks: enforce age limits, valid loan types, FOIR `<= MAX_FOIR`, and minimum thresholds before approval. |
| **Percentage vs Decimal Rate Confusion in EMI** | Manual / Quality | Bug / Calculation | 14, 94 | `calculateEMI` assumed annual rate is already decimal monthly (`annual_rate / 12`), but caller passed `9` instead of `0.09`, calculating 375,000 EMI instead of 10,379. | Normalize interest rate input: if `annual_rate > 1.0`, divide by 100 before computing monthly rate; round output to 2 decimal places. |
| **Linear Accumulation in Loan Estimation** | Pylint / Logic | Bug (W0613, W0622, W0612) | 33–38 | `maxLoanAmount` looped without using `annual_rate`, shadowed built-in `sum`, and computed `available * months` instead of discounted principal. | Calculate true maximum loan principal using inverted annuity present value formula; eliminate loop and built-in name shadowing. |
| **Unbounded Credit Score Risk Banding** | Manual / Logic | Bug / Range Error | 81–91 | `riskBand(950)` returned `"LOW"` because scores were not capped to valid credit bureau boundaries (300 to 900). | Add range check `if not 300 <= credit_score <= 900: return "INVALID"` before risk band classification. |
| **Unclosed File Handles / Resource Leaks** | Pylint | Refactor (R1732) | 56, 63 | Files opened via bare `open()` without `try/finally` or context managers, leaking file descriptors upon exceptions. | Wrap all file I/O operations inside `with open(...) as f:` context managers. |
| **Global State Mutation** | Pylint | Warning (W0603) | 62 | `loadApplications` used `global applications` to overwrite in-memory state. | Update the existing dictionary in-place using `applications.update(...)` or return parsed data, avoiding global rebinds. |
| **Non-PEP 8 Naming Conventions** | Pylint | Convention (C0103) | 14, 20, 33, 40, etc. | Functions named using `camelCase` (`calculateEMI`, `checkEligibility`, etc.) instead of PEP 8 compliant `snake_case`. | Renamed functions to `calculate_emi`, `check_eligibility`, etc., and maintained backward-compatibility aliases. |
| **Missing Module & Function Docstrings** | Pylint | Convention (C0114, C0116) | 1, 14, 20, etc. | Module and all functions lacked docstrings explaining arguments, returns, and purpose. | Added Google/Sphinx style docstrings detailing parameters, return types, and exceptions for all functions. |
| **Unused Import (`math`)** | Flake8 / Pylint | Style / Warning (F401, W0611) | 2 | `import math` imported at top level but never referenced anywhere in the script. | Removed `import math` statement. |
| **Line Length & Spacing Violations** | Flake8 | Style (E501, E302, E305) | Multiple | Lines exceeded 79 characters; functions had only 1 blank line separation instead of required 2 blank lines. | Reformatted code to strictly follow PEP 8: 2 blank lines between top-level functions, line wraps at `<= 79` characters. |
| **Unnecessary / Empty F-String** | Flake8 / Pylint | Style / Warning (F541, W1309) | 104 | `f"Upload to bureau skipped (no network)"` used an f-string prefix without any interpolation expressions. | Removed `f` prefix to convert it to a standard string literal. |
