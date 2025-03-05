import dns.resolver
import sys
import time
from collections import deque

# List of nameservers to cycle through
NAMESERVERS = [
    "8.8.8.8",      # Google
    "1.1.1.1",      # Cloudflare
    "9.9.9.9",      # Quad9
    "8.8.4.4",      # Google secondary
    "208.67.222.222" # OpenDNS
]

# Minimum delay between queries to the same nameserver (in seconds)
DELAY_BETWEEN_SAME_NS = 3.0

# Track last query time for each nameserver
last_query_times = {ns: 0.0 for ns in NAMESERVERS}

# Queue to cycle through nameservers
nameserver_queue = deque(NAMESERVERS)

# Configure the resolver
resolver = dns.resolver.Resolver()
resolver.timeout = 5  # Timeout per query
resolver.lifetime = 5  # Total query lifetime

# Function to get the next available nameserver with delay enforcement
def get_next_nameserver():
    while True:
        ns = nameserver_queue[0]  # Peek at the next nameserver
        current_time = time.time()
        time_since_last = current_time - last_query_times[ns]
        
        if time_since_last >= DELAY_BETWEEN_SAME_NS:
            # Use this nameserver and update its last query time
            last_query_times[ns] = current_time
            nameserver_queue.rotate(-1)  # Move it to the end
            return ns
        else:
            # Wait until the delay is satisfied
            wait_time = DELAY_BETWEEN_SAME_NS - time_since_last
            print(f"Waiting {wait_time:.2f}s to avoid rate-limiting {ns}")
            time.sleep(wait_time)

# Function to check SPF record
def check_spf(domain):
    ns = get_next_nameserver()
    resolver.nameservers = [ns]
    try:
        answers = resolver.resolve(domain, "TXT")
        for rdata in answers:
            txt = rdata.to_text().strip('"')
            if txt.startswith("v=spf1"):
                return f"SPF: {txt} (via {ns})"
        return f"SPF: Not found (via {ns})"
    except dns.resolver.NXDOMAIN:
        return f"SPF: Not found (domain does not exist) (via {ns})"
    except dns.resolver.NoAnswer:
        return f"SPF: Not found (no TXT records) (via {ns})"
    except dns.resolver.Timeout:
        return f"SPF: Query timed out (via {ns})"
    except dns.exception.DNSException as e:
        return f"SPF: Error - {str(e)} (via {ns})"

# Function to check DKIM (basic check for a common selector)
def check_dkim(domain, selector="default"):
    ns = get_next_nameserver()
    resolver.nameservers = [ns]
    dkim_domain = f"{selector}._domainkey.{domain}"
    try:
        answers = resolver.resolve(dkim_domain, "TXT")
        for rdata in answers:
            txt = rdata.to_text().strip('"')
            if "v=DKIM1" in txt:
                return f"DKIM ({selector}): {txt} (via {ns})"
        return f"DKIM ({selector}): Not found (via {ns})"
    except dns.resolver.NXDOMAIN:
        return f"DKIM ({selector}): Not found (domain does not exist) (via {ns})"
    except dns.resolver.NoAnswer:
        return f"DKIM ({selector}): Not found (no TXT records) (via {ns})"
    except dns.resolver.Timeout:
        return f"DKIM ({selector}): Query timed out (via {ns})"
    except dns.exception.DNSException as e:
        return f"DKIM ({selector}): Error - {str(e)} (via {ns})"

# Function to check MX records
def check_mx(domain):
    ns = get_next_nameserver()
    resolver.nameservers = [ns]
    try:
        answers = resolver.resolve(domain, "MX")
        mx_records = [f"{rdata.preference} {rdata.exchange}" for rdata in answers]
        return f"MX: {', '.join(mx_records)} (via {ns})"
    except dns.resolver.NXDOMAIN:
        return f"MX: Not found (domain does not exist) (via {ns})"
    except dns.resolver.NoAnswer:
        return f"MX: Not found (no MX records) (via {ns})"
    except dns.resolver.Timeout:
        return f"MX: Query timed out (via {ns})"
    except dns.exception.DNSException as e:
        return f"MX: Error - {str(e)} (via {ns})"

# Function to check DMARC record
def check_dmarc(domain):
    ns = get_next_nameserver()
    resolver.nameservers = [ns]
    dmarc_domain = f"_dmarc.{domain}"
    try:
        answers = resolver.resolve(dmarc_domain, "TXT")
        for rdata in answers:
            txt = rdata.to_text().strip('"')
            if txt.startswith("v=DMARC1"):
                return f"DMARC: {txt} (via {ns})"
        return f"DMARC: Not found (via {ns})"
    except dns.resolver.NXDOMAIN:
        return f"DMARC: Not found (domain does not exist) (via {ns})"
    except dns.resolver.NoAnswer:
        return f"DMARC: Not found (no TXT records) (via {ns})"
    except dns.resolver.Timeout:
        return f"DMARC: Query timed out (via {ns})"
    except dns.exception.DNSException as e:
        return f"DMARC: Error - {str(e)} (via {ns})"
    
 # Function to check A records
def check_a(domain):
    ns = get_next_nameserver()
    resolver.nameservers = [ns]
    try:
        answers = resolver.resolve(domain, "A")
        a_records = [rdata.address for rdata in answers]
        return f"A: {', '.join(a_records)} (via {ns})"
    except dns.resolver.NXDOMAIN:
        return f"A: Not found (domain does not exist) (via {ns})"
    except dns.resolver.NoAnswer:
        return f"A: Not found (no A records) (via {ns})"
    except dns.resolver.Timeout:
        return f"A: Query timed out (via {ns})"
    except dns.exception.DNSException as e:
        return f"A: Error - {str(e)} (via {ns})"

# Function to check NS records
def check_ns(domain):
    ns = get_next_nameserver()
    resolver.nameservers = [ns]
    try:
        answers = resolver.resolve(domain, "NS")
        ns_records = [rdata.to_text().rstrip('.') for rdata in answers]
        return f"NS: {', '.join(ns_records)} (via {ns})"
    except dns.resolver.NXDOMAIN:
        return f"NS: Not found (domain does not exist) (via {ns})"
    except dns.resolver.NoAnswer:
        return f"NS: Not found (no NS records) (via {ns})"
    except dns.resolver.Timeout:
        return f"NS: Query timed out (via {ns})"
    except dns.exception.DNSException as e:
        return f"NS: Error - {str(e)} (via {ns})"   

# Main function to process the file
def check_domain_records(file_path):
    try:
        with open(file_path, "r") as file:
            domains = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    print(f"Cycling through nameservers: {NAMESERVERS}")
    for domain in domains:
        print(f"\nChecking {domain}:")
        print(check_spf(domain))
        print(check_mx(domain))
        print(check_dkim(domain, selector="default"))
        print(check_dmarc(domain))
        print(check_a(domain))
        print(check_ns(domain))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py domains.txt")
        sys.exit(1)
    
    file_path = sys.argv[1]
    check_domain_records(file_path)
