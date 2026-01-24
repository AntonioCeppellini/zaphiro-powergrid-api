from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
)
