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
    app.run()
