from pathlib import Path

og_dir = Path(__file__).parent / "bgp_simulator_pkg" / "simulation_framework"
og_dir = og_dir / "subgraphs" / "disconnected_subgraphs"
all_paths = list()
# https://stackoverflow.com/a/54046843/8903959
for old_path in og_dir.rglob("*"):
    new_path = str(old_path).replace("attacker_success", "disconnected")
    all_paths.append((old_path, new_path))

for old_path, new_path in all_paths:
    with old_path.open() as old_f, new_path.open("w") as new_f:
        new_text = old_path.read().replace("attacker_success", "disconnected")
        new_text = new_text.replace("ATTACKER_SUCCESS", "DISCONNECTED")
        new_f.write(new_text)
    old_path.unlink()
