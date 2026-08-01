"""
=========================================================
Civil Estimate Suite Pro v4.0
---------------------------------------------------------
Module    : Main Entry Point
Purpose   : Application Startup
Author    : OpenAI + Moula Bakhsh
Version   : 4.0.0
=========================================================
"""

from app.bootstrap import Bootstrap
from app.application import Application


def main():

    bootstrap = Bootstrap()

    try:

        context = bootstrap.initialize()

        application = Application(context)

        application.run()

    finally:

        bootstrap.shutdown()


if __name__ == "__main__":
    main()