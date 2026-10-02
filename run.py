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
