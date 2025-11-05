import asyncio
import os
import pathlib


async def main():
    cwd = pathlib.Path.cwd()

    git_base_url = "https://github.com/DEFRA"
    services_path = f"{cwd}/service-compose"
    repos_path = cwd.parent

    services = [f for f in os.listdir(services_path) if f.endswith((".yaml", ".yml"))]

    tasks = []

    for service in services:
        repo = service.replace(".yaml", "").replace(".yml", "")
        clone_url = f"{git_base_url}/{repo}.git"

        task = clone_repo(clone_url, repos_path)
        tasks.append(task)

    await asyncio.gather(*tasks)


async def clone_repo(clone_url: str, repos_path: pathlib.Path):
    process = await asyncio.create_subprocess_exec(
        "git", "clone", clone_url,
        cwd=repos_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    _, stderr = await process.communicate()

    if process.returncode == 0:
        print(f"Successfully cloned {clone_url}")
    else:
        print(f"{stderr.decode()}")

if __name__ == "__main__":
    asyncio.run(main())
