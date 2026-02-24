"""
Checkout main and pull for each service. Run from core repo root.
"""
import asyncio
import os
import pathlib


async def main():
    cwd = pathlib.Path.cwd()
    services_dir = cwd / "services"
    services_path = cwd / "service-compose"

    services = [f for f in os.listdir(services_path) if f.endswith((".yaml", ".yml"))]

    tasks = []
    for service in services:
        repo = service.replace(".yaml", "").replace(".yml", "")
        repo_path = services_dir / repo

        task = update_repo(repo_path, repo)
        tasks.append(task)

    await asyncio.gather(*tasks)


async def update_repo(repo_path: pathlib.Path, label: str):
    if not repo_path.exists():
        print(f"Skipping {label} (not cloned, run 'uv run task clone' first)")
        return

    process = await asyncio.create_subprocess_exec(
        "git", "checkout", "main",
        cwd=repo_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    _, stderr = await process.communicate()

    if process.returncode != 0:
        print(f"Failed to checkout main for {label}: {stderr.decode()}")
        return

    process = await asyncio.create_subprocess_exec(
        "git", "pull",
        cwd=repo_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    _, stderr = await process.communicate()

    if process.returncode == 0:
        print(f"Successfully updated {label}")
    else:
        print(stderr.decode())


if __name__ == "__main__":
    asyncio.run(main())