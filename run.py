"""
                            *************************************

                                    Just start the app
                                    Note: no debug=True in app.run() because the __init__.py will cover this by using:
                                        DEBUG = True  # from DevConfig
                                        DEBUG = False # from ProdConfig
                            *************************************
"""
from flask import Flask
from app import create_app

app: Flask = create_app()

if __name__ == "__main__":
    app.run(port=5001)


# ----------- For Ram calculation ------------- #
# import os
# import psutil
#
#
# def print_memory_usage():
#     process = psutil.Process(os.getpid())
#     # Converts bytes to Megabytes
#     mem_mb = process.memory_info().rss / (1024 * 1024)
#     print(f"--> [MyFinanceMap Server RAM]: {mem_mb:.2f} MB")
#
#
# if __name__ == "__main__":
#     print_memory_usage()
#     # Your existing app.run() code goes here


####Code for back up#####
"""
import sqlite3
from pathlib import Path
from datetime import datetime

source_path = Path("instance/myfinancemap.db")

backup_dir = Path("backups")
backup_dir.mkdir(exist_ok=True)

backup_path = backup_dir / (
    f"myfinancemap_{datetime.now():%Y%m%d_%H%M%S}.db"
)

# 1. Perform the backup operation

with sqlite3.connect(str(source_path)) as source:
    with sqlite3.connect(str(backup_path)) as destination:
        source.backup(destination)

print(f"Backup created: {backup_path}")

# 2. Verify database integrity 

with sqlite3.connect(str(backup_path)) as connection:
    # Run the integrity check and get the first result row
    result = connection.execute("PRAGMA integrity_check").fetchone()[0]
    
    if result == "ok":
        print("✅ Success: Backup integrity verified. The file is healthy!")
    else:
        print(f"❌ Warning: Backup database is corrupted! Error: {result}")
"""

