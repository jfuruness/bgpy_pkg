from pathlib import Path

from .simulation_framework_v2 import Simulation


def main():
    """Runs the defaults"""

    Simulation(output_path=Path("~/Desktop/graphs").expanduser()).run()


if __name__ == "__main__":
    main()
