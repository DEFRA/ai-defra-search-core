"""
Clone service repos into core/services/<repo-name>.
Run from core repo root. Skips if dir already exists (use pull for updates).
"""
import asyncio
import os
import pathlib


async def main():
    cwd = pathlib.Path.cwd()
    services_dir = cwd / "services"
    services_dir.mkdir(exist_ok=True)

    git_base_url = "https://github.com/DEFRA"
    services_path = cwd / "service-compose"

    services = [f for f in os.listdir(services_path) if f.endswith((".yaml", ".yml"))]

    tasks = []
    for service in services:
        repo = service.replace(".yaml", "").replace(".yml", "")
        clone_url = f"{git_base_url}/{repo}.git"
        target = services_dir / repo

        task = clone_repo(clone_url, target)
        tasks.append(task)

    await asyncio.gather(*tasks)


async def clone_repo(clone_url: str, target: pathlib.Path):
    if target.exists():
        print(f"Skipping {clone_url} (already exists at {target}, use 'uv run task pull' to update)")
        return

    process = await asyncio.create_subprocess_exec(
        "git", "clone", clone_url, str(target),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    _, stderr = await process.communicate()

    if process.returncode == 0:
        print(f"Successfully cloned {clone_url} -> {target}")
    else:
        print(stderr.decode())


if __name__ == "__main__":
    asyncio.run(main())
