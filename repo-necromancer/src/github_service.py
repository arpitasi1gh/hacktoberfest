import httpx
import os
import base64
import re

async def fetch_repo_data(owner: str, repo: str) -> dict:
    token = os.getenv("GITHUB_TOKEN", "")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    async with httpx.AsyncClient(timeout=20.0) as client:
        # 1. Repo Info
        r_info = await client.get(f"https://api.github.com/repos/{owner}/{repo}", headers=headers)
        if r_info.status_code != 200:
            raise Exception(f"Repo not found: {r_info.status_code}")
        repo_info = r_info.json()
        
        # 2. Full Tree (Recursive)
        r_tree = await client.get(
            f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD",
            params={"recursive": "1"}, headers=headers
        )
        raw_tree = r_tree.json().get('tree', [])
        
        # 3. Get Top Level Folders (the secret to stopping hallucinations)
        top_level_folders = sorted(list(set([
            item['path'] for item in raw_tree 
            if item['type'] == 'tree' and '/' not in item['path'] and not item['path'].startswith('.')
        ])))
        
        # 4. Get Flat Tree (limit to 300 to save tokens)
        tree = [item['path'] for item in raw_tree if not item['path'].startswith('.')][:300]
        
        # 5. Get Commits & Lifespan
        r_commits = await client.get(f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=5", headers=headers)
        latest_commits = r_commits.json() if r_commits.status_code == 200 else []
        commits = [c['commit']['message'] for c in latest_commits]
        last_commit_date = latest_commits[0]['commit']['author']['date'][:10] if latest_commits else "Unknown"

        first_commit_date = "Unknown"
        link_header = r_commits.headers.get("link", "")
        last_page_match = re.search(r'[?&]page=(\d+)>; rel="last"', link_header)
        if last_page_match:
            r_oldest = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}/commits",
                params={"per_page": 1, "page": int(last_page_match.group(1))}, headers=headers
            )
            if r_oldest.status_code == 200 and r_oldest.json():
                first_commit_date = r_oldest.json()[0]['commit']['author']['date'][:10]
        elif latest_commits:
            first_commit_date = latest_commits[-1]['commit']['author']['date'][:10]
        
        # 6. Key Files
        key_files_to_fetch = [
            "README.md", "package.json", "requirements.txt", "pyproject.toml", 
            "go.mod", "Cargo.toml", "Dockerfile", "docker-compose.yml", 
            "main.py", "index.js", "main.go", "src/main.rs"
        ]
        file_contents = {}
        
        # Fetch root files
        for path in key_files_to_fetch:
            if path in tree:
                r_file = await client.get(f"https://api.github.com/repos/{owner}/{repo}/contents/{path}", headers=headers)
                if r_file.status_code == 200:
                    content = r_file.json().get("content", "")
                    if content:
                        try:
                            decoded = base64.b64decode(content).decode("utf-8", errors="ignore")
                            file_contents[path] = decoded[:1500]
                        except: pass
                        
        # Fetch key files inside sub-folders
        for folder in top_level_folders:
            for filename in ["package.json", "requirements.txt", "pyproject.toml", "main.py", "index.js"]:
                path = f"{folder}/{filename}"
                if path in tree:
                    r_file = await client.get(f"https://api.github.com/repos/{owner}/{repo}/contents/{path}", headers=headers)
                    if r_file.status_code == 200:
                        content = r_file.json().get("content", "")
                        if content:
                            try:
                                decoded = base64.b64decode(content).decode("utf-8", errors="ignore")
                                file_contents[path] = decoded[:1000]
                            except: pass
    
    return {
        "description": repo_info.get('description', 'None'),
        "tree": tree,
        "top_level_folders": top_level_folders,
        "commits": commits,
        "first_commit_date": first_commit_date,
        "last_commit_date": last_commit_date,
        "key_files": file_contents
    }