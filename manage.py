import sys
import argparse
import asyncio

from database.migrations.m001_create_sensor_index import create_indexes
from database.seeds.seed_sensor_data import seed_sensor_data

def main():
    parser = argparse.ArgumentParser(description="Project management commands")
    parser.add_argument(
        "command",
        help="Command to run",
        choices=["migrate", "seed", "all"],
        type=str
    )
    args = parser.parse_args()

    if args.command == "migrate":
        print("Running migrations...")
        asyncio.run(create_indexes())
    elif args.command == "seed":
        print("Running seed scripts...")
        asyncio.run(seed_sensor_data())
    elif args.command == "all":
        print("Running migrations...")
        asyncio.run(create_indexes())
        print("Running seed scripts...")
        asyncio.run(seed_sensor_data())
    else:
        print("Unknown command")
        sys.exit(1)

if __name__ == "__main__":
    main()
