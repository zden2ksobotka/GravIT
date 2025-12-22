#!/var/www/cms.n0ip.eu/venv/bin/python3
# utils/check_workers.py

"""
Diagnostický skript pro zjištění počtu aktivních Uvicorn workerů
pro službu cms.n0ip.eu.
"""

import psutil

# Unikátní identifikátor naší služby z systemd konfigurace
SERVICE_IDENTIFIER = "uvicorn-cms.sock"

def find_and_count_workers():
    """
    Prohledá běžící procesy, najde hlavní Uvicorn proces a spočítá jeho workery.
    """
    master_process = None

    # Projdeme všechny běžící procesy
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Spojíme argumenty příkazové řádky do jednoho řetězce pro snadné hledání
            cmdline = " ".join(proc.info['cmdline'])
            
            # Hledáme náš hlavní proces podle unikátního identifikátoru
            if "uvicorn" in proc.info['name'] and SERVICE_IDENTIFIER in cmdline:
                master_process = psutil.Process(proc.info['pid'])
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if master_process:
        print(f"Nalezen hlavní Uvicorn proces s PID: {master_process.pid}")
        
        # Získáme seznam dceřiných procesů
        children = master_process.children(recursive=False)
        
        # Odfiltrujeme pouze skutečné aplikační workery (ignorujeme např. resource_tracker)
        workers = []
        for child in children:
            try:
                cmdline = " ".join(child.cmdline())
                if "spawn_main" in cmdline:
                    workers.append(child)
            except psutil.NoSuchProcess:
                continue

        if workers:
            print(f"Nalezeno {len(workers)} skutečných aplikačních workerů:")
            for worker in workers:
                print(f"  - Worker PID: {worker.pid}")
        else:
            print("Nebyly nalezeny žádné aktivní worker procesy.")
            
    else:
        print(f"Hlavní Uvicorn proces pro službu '{SERVICE_IDENTIFIER}' neběží.")

if __name__ == "__main__":
    find_and_count_workers()
