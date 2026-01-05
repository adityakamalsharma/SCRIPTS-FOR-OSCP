import requests
import concurrent.futures

# --- CONFIGURATION ---
PROXY_IP = "10.10.10.10" # REPLACE WITH TARGET IP
PROXY_PORT = 3128
TARGET_URL = "http://127.0.0.1" 
PORT_RANGE = range(1, 65535) 
THREADS = 20
# ---------------------

proxies = {
    "http": f"http://{PROXY_IP}:{PROXY_PORT}",
    "https": f"http://{PROXY_IP}:{PROXY_PORT}",
}

def scan_port(port):
    url = f"{TARGET_URL}:{port}"
    try:
        # Timeout is crucial. 2 seconds is usually enough for internal localhost.
        r = requests.get(url, proxies=proxies, timeout=2)
        
        # Squid returns 503 if the port is closed/unreachable.
        # It returns 403 if Squid itself blocks the request (ACL).
        # We generally care about things that are NOT 503.
        if r.status_code != 503:
            return port, r.status_code, "OPEN/FILTERED"
            
    except requests.exceptions.ProxyError:
        pass # Proxy connection failed
    except requests.exceptions.ConnectTimeout:
        pass # Port likely filtered
    except Exception as e:
        pass
    return None

print(f"[*] Scanning {TARGET_URL} via {PROXY_IP}:{PROXY_PORT}...")

with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
    results = executor.map(scan_port, PORT_RANGE)
    
    for result in results:
        if result:
            port, code, status = result
            print(f"[+] Port {port:<5} | Status: {code}")
