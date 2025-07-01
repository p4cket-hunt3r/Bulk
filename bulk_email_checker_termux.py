import os
import sys
import subprocess

# ---------- Auto-install part ---------- #
def install_requirements():
    try:
        import dns.resolver
    except ImportError:
        print("[+] Installing missing Python module: dnspython")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "dnspython"])

    if not shutil.which('python'):
        print("[+] Python not found, installing Python via Termux pkg...")
        os.system('pkg install python -y')

try:
    import shutil
except ImportError:
    os.system('pkg install python -y')
    import shutil

install_requirements()

import smtplib
import dns.resolver
import time

# ---------- Email verification functions ---------- #
def get_mx_record(domain):
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        return str(mx_records[0].exchange)
    except:
        return None

def verify_email(email, from_address='test@example.com'):
    domain = email.split('@')[-1]
    mx_record = get_mx_record(domain)

    if not mx_record:
        return "No MX Record"

    try:
        server = smtplib.SMTP(timeout=10)
        server.connect(mx_record)
        server.helo('example.com')
        server.mail(from_address)
        code, message = server.rcpt(email)
        server.quit()

        if code in [250, 251]:
            return "Valid"
        else:
            return f"Invalid / Blocked ({code})"
    except Exception as e:
        return f"Connection Error: {e}"

def bulk_check(input_file, output_file):
    try:
        with open(input_file, 'r') as f:
            emails = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[-] Input file '{input_file}' not found!")
        return

    results = []
    print(f"[+] Starting verification for {len(emails)} emails...\n")

    for idx, email in enumerate(emails, 1):
        print(f"[{idx}/{len(emails)}] Checking: {email}")
        status = verify_email(email)
        print(f" --> {status}")
        results.append(f"{email},{status}")
        time.sleep(1)  # Small delay to avoid getting blocked

    with open(output_file, 'w') as f:
        f.write('\n'.join(results))

    print(f"\n[+] Done. Results saved to '{output_file}'.")

# ---------- Main runner ---------- #
if __name__ == "__main__":
    input_file = "emails.txt"
    output_file = "results.csv"
    bulk_check(input_file, output_file)