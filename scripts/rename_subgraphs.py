from pathlib import Path

og_dir = Path(__file__).parent.parent / "bgp_simulator_pkg" / "simulation_framework"
og_dir = og_dir / "subgraphs" / "disconnected_subgraphs"
all_paths = list()
# https://stackoverflow.com/a/54046843/8903959
for old_path in og_dir.rglob("*"):
    new_path = Path(str(old_path).replace("attacker_success", "disconnected"))
    if new_path.is_dir() or str(new_path).endswith(".py"):
        all_paths.append((old_path, new_path))

all_dirs = list()
for old_path, new_path in all_paths:
    if old_path.is_dir():
        all_dirs.append((old_path, new_path))
    else:
        with old_path.open() as old_f, new_path.open("w") as new_f:
            new_text = old_f.read().replace("attacker_success", "disconnected")
            new_text = new_text.replace("ATTACKER_SUCCESS", "DISCONNECTED")
            new_f.write(new_text)
        old_path.unlink()

for old_dir, new_dir in all_dirs:
    old_dir.rename(new_dir)
