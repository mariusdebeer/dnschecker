# DNS Record Checker

This Python script checks various DNS records for a list of domains provided in a text file. It cycles through multiple public nameservers to avoid rate-limiting and includes a delay mechanism to ensure compliance with query limits. The script is useful for auditing domain configurations, verifying email security settings, or troubleshooting DNS issues.

## Features

- **DNS Record Types Checked**:
  - **SPF (Sender Policy Framework)**: Verifies email sender policies.
  - **MX (Mail Exchange)**: Lists mail servers for the domain.
  - **DKIM (DomainKeys Identified Mail)**: Checks for a basic DKIM record (using the `default` selector).
  - **DMARC (Domain-based Message Authentication)**: Reports DMARC policies for email authentication.
  - **A (Address)**: Returns IPv4 addresses for the domain.
  - **NS (Nameserver)**: Lists authoritative nameservers for the domain.

- **Nameserver Cycling**: Queries rotate through a list of public nameservers (`8.8.8.8`, `1.1.1.1`, `9.9.9.9`, `8.8.4.4`, `208.67.222.222`) to prevent rate-limiting.

- **Delay Enforcement**: Ensures at least a 3-second (3000ms) delay between queries to the same nameserver.

- **Error Handling**: Gracefully handles DNS errors like non-existent domains (`NXDOMAIN`), no records (`NoAnswer`), timeouts, and generic DNS exceptions.

- **Output**: Detailed results for each domain, including the nameserver used for each query.

## Prerequisites

- **Python 3.x**: Ensure Python is installed on your system.
- **dnspython**: A Python library for DNS queries. Install it with:
  ```bash
  pip install dnspython
