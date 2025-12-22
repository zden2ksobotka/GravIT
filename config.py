SITE_IDENTIFIKATOR = "cms.n0ip.eu"

THEME_SKIN = "user/theme/light"
SECRET_KEY = "your-very-secret-key-that-is-long-and-random" # IMPORTANT: THIS IS FOR DEVELOPMENT ONLY! For production, generate a secure key (e.g., tr -dc A-Za-z0-9 </dev/urandom | head -c 64) and load it from environment variables.

DEBUG = True # Global debug mode switch. Affects some development features and may supplement LOG_LEVEL for more detailed development logging.
# Global logging level. Messages below this level will be ignored.
# Possible values (from most verbose to least): "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "DISABLED"
# "DISABLED" will effectively turn off all logging.
LOG_LEVEL = "DEBUG"


