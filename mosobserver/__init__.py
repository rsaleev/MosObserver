__version__ = "0.1.0"


import os
import dotenv
from pathlib import Path

dotenv.load_dotenv(f"{Path(os.getcwd()).absolute()}/.env")
