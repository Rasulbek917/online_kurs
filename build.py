import os
import subprocess
import sys


def main():
    if os.environ.get("VERCEL_ENV") == "production":
        subprocess.run(
            [sys.executable, "manage.py", "migrate", "--noinput"],
            check=True,
        )


if __name__ == "__main__":
    main()
