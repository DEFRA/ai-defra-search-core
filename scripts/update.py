import asyncio
import os
import pathlib


async def main():
    cwd = pathlib.Path.cwd()

    services_path = f"{cwd}/service-compose"
    repos_path = cwd.parent

    services = [f for f in os.listdir(services_path) if f.endswith((".yaml", ".yml"))]

    tasks = []

    for service in services:
        repo = service.replace(".yaml", "").replace(".yml", "")
        
        task = update_repo(repo, repos_path)
        tasks.append(task)

    await asyncio.gather(*tasks)


async def update_repo(repo: str, repos_path: pathlib.Path):
    repo_path = repos_path / repo
    
    process = await asyncio.create_subprocess_exec(
        "git", "checkout", "main",
        cwd=repo_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    _, stderr = await process.communicate()

    if process.returncode != 0:
        print(f"Failed to checkout main for {repo}: {stderr.decode()}")
        return

    process = await asyncio.create_subprocess_exec(
        "git", "pull",
        cwd=repo_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    _, stderr = await process.communicate()

    if process.returncode == 0:
        print(f"Successfully updated {repo}")
    else:
        print(f"{stderr.decode()}")


if __name__ == "__main__":
    asyncio.run(main())