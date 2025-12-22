import json
import logging
from pathlib import Path
from fastapi import Request

logger = logging.getLogger(__name__)

def register_routes(app, get_full_page_cache):
    @app.get("/dumpcache")
    async def dump_cache(request: Request):
        logger.info("--- PAGE_CACHE dump request received ---")
        try:
            page_cache = get_full_page_cache()
            dump_file_path = Path("user/plugin/test_dump_page_cache/test_dump_page_cache.txt")
            
            # Convert Path objects to strings for JSON serialization
            serializable_cache = {}
            for key, value in page_cache.items():
                if isinstance(value, dict):
                    serializable_value = value.copy()
                    if "file_path" in serializable_value:
                        serializable_value["file_path"] = str(Path(serializable_value["file_path"])) # Ensure Path is str
                else:
                    serializable_value = value
                serializable_cache[key] = serializable_value

            with open(dump_file_path, "w", encoding="utf-8") as f:
                json.dump(serializable_cache, f, indent=2, ensure_ascii=False)
            logger.info(f"PAGE_CACHE dumped to {dump_file_path}")
            return {"message": f"PAGE_CACHE dumped successfully to {dump_file_path}"}
        except Exception as e:
            logger.error(f"Error dumping PAGE_CACHE: {e}", exc_info=True)
            return {"message": f"Error dumping PAGE_CACHE: {e}"}
