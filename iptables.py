import subprocess

def run_cmd(cmd):
    try:
        result = subprocess.run(
            cmd,
            shell = True,
            check = True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.stdout.decode().strip()
    except subprocess.CalledProcessError as e:
        print(f"[iptables ERROR] {e.stderr.decode().strip()}")
        return None

def add_rule(rule):
    cmd = f"iptables {rule}"
    return run_cmd(cmd)

def delete_rule(rule):
    cmd = f"iptables {rule}"
    return run_cmd(cmd)

def list_rules():
    return run_cmd("iptables -L")

def flush_rules():
    return run_cmd("iptables -F")


