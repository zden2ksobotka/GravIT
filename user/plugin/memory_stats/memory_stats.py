# user/plugin/memory_stats/memory_stats.py

import os
import sys
import json
import logging
import psutil
import glob
import time
from fastapi import Request
from fastapi.responses import HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Any

# Import z konfiguračního souboru
from user.plugin.memory_stats.memory_stats_config import REFRESH_INTERVAL

# Globální proměnné
_page_cache_getter = None
_last_update_time: float = 0
STATS_DIR = "/tmp/cms_memory_stats/"

logger = logging.getLogger(__name__)

def get_size(obj, seen=None):
    """Rekurzivně zjišťuje velikost objektu v bajtech."""
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)
    size = sys.getsizeof(obj)
    if isinstance(obj, dict):
        size += sum(get_size(v, seen) for v in obj.values())
        size += sum(get_size(k, seen) for k in obj.keys())
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum(get_size(i, seen) for i in obj)
    return size

def _update_my_stats():
    """Vypočítá a zapíše statistiky pro aktuální worker do jeho souboru."""
    global _last_update_time
    os.makedirs(STATS_DIR, exist_ok=True)
    pid = os.getpid()
    page_cache = _page_cache_getter() if _page_cache_getter else {}
    
    cache_size_bytes = get_size(page_cache)
    cache_size_mb = round(cache_size_bytes / (1024 * 1024), 2)
    item_count = len(page_cache)

    worker_stats = {
        "pid": pid,
        "cache_size_mb": cache_size_mb,
        "item_count": item_count,
        "last_updated": time.time()
    }
    
    my_stats_file = os.path.join(STATS_DIR, f"cms_stats_{pid}.json")
    try:
        with open(my_stats_file, 'w') as f:
            json.dump(worker_stats, f)
        _last_update_time = worker_stats["last_updated"]
        logger.debug(f"Statistiky pro PID {pid} byly aktualizovány.")
    except IOError as e:
        logger.error(f"Nepodařilo se zapsat statistiky pro PID {pid}: {e}")

def _read_all_stats_and_cleanup():
    """Načte statistiky ze všech souborů a vyčistí staré."""
    all_stats = {}
    stat_files = glob.glob(os.path.join(STATS_DIR, "cms_stats_*.json"))
    
    for file_path in stat_files:
        try:
            pid_from_filename = int(os.path.basename(file_path).split('_')[-1].split('.')[0])
            
            if not psutil.pid_exists(pid_from_filename):
                os.remove(file_path)
                continue

            with open(file_path, 'r') as f:
                stats = json.load(f)
                all_stats[str(stats['pid'])] = stats
        except (ValueError, IndexError, json.JSONDecodeError, IOError):
            pass # Ignorujeme poškozené nebo neplatné soubory

    return all_stats

class MemoryStatsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        global _last_update_time
        current_time = time.time()
        
        # Aktualizujeme statistiky na pozadí, pokud uplynul interval
        if current_time - _last_update_time > REFRESH_INTERVAL:
            _update_my_stats()

        response = await call_next(request)
        return response

def register_routes(app, get_full_page_cache):
    """Registruje middleware a /memory_stats endpoint."""
    global _page_cache_getter
    _page_cache_getter = get_full_page_cache

    # Registrace middleware
    app.add_middleware(MemoryStatsMiddleware)

    @app.get("/memory_stats", response_class=HTMLResponse)
    async def memory_stats_page(request: Request):
        logger.info(f"Zobrazuji /memory_stats z workeru {os.getpid()}")
        
        # Jen přečteme a zobrazíme data
        all_stats = _read_all_stats_and_cleanup()
        
        # Sestavení HTML odpovědi
        html = "<html><head><title>Statistiky paměti workerů</title>"
        html += "<style>body { font-family: sans-serif; } table { border-collapse: collapse; } th, td { border: 1px solid #ccc; padding: 8px; text-align: left; } th { background-color: #f2f2f2; }</style>"
        html += "</head><body>"
        html += "<h1>Statistiky využití paměti pro PAGE_CACHE</h1>"
        html += f"<p>Data jsou automaticky aktualizována na pozadí každým workerem, pokud je aktivní (max jednou za {REFRESH_INTERVAL} sekund).</p>"
        
        if not all_stats:
            html += "<p>Zatím nebyly nasbírány žádné statistiky. Obnovte stránku za chvíli.</p>"
        else:
            html += "<table><tr><th>Worker PID</th><th>Počet položek v cache</th><th>Velikost cache (MB)</th><th>Poslední aktualizace</th></tr>"
            total_size = 0
            sorted_pids = sorted(all_stats.keys(), key=lambda x: int(x))
            
            for pid in sorted_pids:
                stats = all_stats[pid]
                last_updated_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stats.get('last_updated', 0)))
                html += f"<tr><td>{stats['pid']}</td><td>{stats['item_count']}</td><td>{stats['cache_size_mb']}</td><td>{last_updated_str}</td></tr>"
                total_size += stats['cache_size_mb']
            html += "</table>"
            html += f"<h3>Celková velikost všech cachí: {round(total_size, 2)} MB</h3>"
            html += f"<p>Počet aktivních workerů: {len(all_stats)}</p>"
        
        html += f"<p><small>Zobrazeno workerem s PID: {os.getpid()}.</small></p>"
        html += "</body></html>"
        
        return HTMLResponse(content=html)
