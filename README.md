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
## Installation

### Step 1: Get the Repository

Clone or download the repository to your local machine:

```bash
git clone https://github.com/yourusername/dns-record-checker.git
cd dns-record-checker

### Step 2: Install Dependencies

Install the required Python library:
```bash
pip install dnspython


## Usage
### Creating a Domain List
Prepare a text file (e.g., mydomains.txt) with the domains you want to analyze. List each domain on a new line, like this:

```
google.com
example.com

### Executing the Script
Run the script by passing the domain list file as an argument, and redirect stdout to a file:
```bash
python check_dns_records.py mydomains.txt > dnsrecords.txt

## Interpreting Results
The script outputs DNS records for each domain, showing which nameserver was queried. Example:
```
Cycling through nameservers: ['8.8.8.8', '1.1.1.1', '9.9.9.9', '8.8.4.4', '208.67.222.222']

Checking google.com:
SPF: v=spf1 include:_spf.google.com ~all (via 8.8.8.8)
MX: 10 smtp.google.com (via 1.1.1.1)
DKIM (default): Not found (via 9.9.9.9)
DMARC: v=DMARC1; p=reject; rua=mailto:dmarc_agg@google.com; (via 8.8.4.4)
A: 142.250.190.78 (via 208.67.222.222)
NS: ns1.google.com, ns2.google.com, ns3.google.com, ns4.google.com (via 8.8.8.8)


## Customization
### Nameserver Options
To use different nameservers, edit the NAMESERVERS list in the script. Defaults are:
8.8.8.8 (Google)

1.1.1.1 (Cloudflare)

9.9.9.9 (Quad9)

8.8.4.4 (Google secondary)

208.67.222.222 (OpenDNS)

## Additional Information
####  Rate Limits: 
The 3-second delay should avoid rate-limiting, but increase it if issues arise.

#### Timeouts: 
Queries timeout after 5 seconds. Adjust resolver.timeout and resolver.lifetime for slower networks.

#### Limitations:
Subdomain enumeration isn’t included; use specialized tools for that.





