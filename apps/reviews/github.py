import re
import requests

class GitHubFetcher:
    def fetch_code_or_tree(self, repo_url: str, file_path: str = ''):
        """
        Parses GitHub repository URL and fetches raw code file contents or lists all code files in the repository.
        """
        repo_url = repo_url.strip()
        
        # Check if URL is a direct raw URL
        if 'raw.githubusercontent.com' in repo_url:
            res = requests.get(repo_url, timeout=10)
            if res.status_code == 200:
                filename = repo_url.split('/')[-1]
                return {'type': 'file', 'filename': filename, 'code': res.text}
            else:
                return {'error': f'Failed to fetch raw GitHub file (HTTP {res.status_code}).'}

        # Check if URL is a GitHub blob URL (e.g. https://github.com/owner/repo/blob/main/path/to/file.ext)
        blob_match = re.search(r'github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.*)', repo_url)
        if blob_match:
            owner, repo, branch, path = blob_match.groups()
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}"
            res = requests.get(raw_url, timeout=10)
            if res.status_code == 200:
                return {'type': 'file', 'filename': path.split('/')[-1], 'code': res.text}
            else:
                return {'error': f'Failed to fetch file from GitHub repository (HTTP {res.status_code}).'}

        # Parse standard repo URL (e.g. https://github.com/owner/repo)
        repo_match = re.search(r'github\.com/([^/]+)/([^/\?#]+)', repo_url)
        if not repo_match:
            return {'error': 'Invalid GitHub Repository URL. Expected format: https://github.com/owner/repository'}

        owner, repo = repo_match.group(1), repo_match.group(2).replace('.git', '')

        # If a specific file_path was requested
        if file_path:
            for branch in ['main', 'master']:
                raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file_path.lstrip('/')}"
                res = requests.get(raw_url, timeout=8)
                if res.status_code == 200:
                    return {'type': 'file', 'filename': file_path.split('/')[-1], 'code': res.text}

            return {'error': f"Could not find file '{file_path}' in branch 'main' or 'master'."}

        # Otherwise, fetch repository tree via GitHub API to list all code files
        valid_extensions = (
            '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.cc', '.h', 
            '.cs', '.go', '.rs', '.php', '.rb', '.html', '.css', '.sql', '.sh', '.json', '.yaml', '.yml'
        )

        files_list = []
        for branch in ['main', 'master']:
            api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
            headers = {'User-Agent': 'CodeGuardian-AI'}
            res = requests.get(api_url, headers=headers, timeout=10)
            if res.status_code == 200:
                tree_data = res.json().get('tree', [])
                for item in tree_data:
                    if item.get('type') == 'blob' and item.get('path', '').lower().endswith(valid_extensions):
                        files_list.append({
                            'path': item['path'],
                            'filename': item['path'].split('/')[-1],
                            'size': item.get('size', 0),
                            'raw_url': f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{item['path']}"
                        })
                break

        if files_list:
            return {
                'type': 'tree',
                'owner': owner,
                'repo': repo,
                'files': files_list
            }

        # If tree API rate-limited or fails, fallback to root files check
        root_api = f"https://api.github.com/repos/{owner}/{repo}/contents"
        res = requests.get(root_api, headers={'User-Agent': 'CodeGuardian-AI'}, timeout=10)
        if res.status_code == 200:
            for item in res.json():
                if item.get('type') == 'file' and item.get('name', '').lower().endswith(valid_extensions):
                    files_list.append({
                        'path': item['name'],
                        'filename': item['name'],
                        'size': item.get('size', 0),
                        'raw_url': item.get('download_url')
                    })
            if files_list:
                return {'type': 'tree', 'owner': owner, 'repo': repo, 'files': files_list}

        return {'error': f'Unable to locate code files in repository {owner}/{repo}. Please check repository permissions or specify direct file URL.'}

    def fetch_all_repo_files_code(self, repo_url: str, max_files: int = 5):
        """
        Fetches full code contents for source files in a repository to run a full repository audit.
        """
        tree_res = self.fetch_code_or_tree(repo_url=repo_url)
        if 'error' in tree_res or tree_res.get('type') != 'tree':
            return tree_res

        files = tree_res.get('files', [])[:max_files]
        file_codes = []

        for f in files:
            res = self.fetch_code_or_tree(repo_url=repo_url, file_path=f['path'])
            if res.get('type') == 'file':
                file_codes.append({
                    'path': f['path'],
                    'filename': f['filename'],
                    'code': res['code']
                })

        return {
            'type': 'repo_codes',
            'owner': tree_res.get('owner'),
            'repo': tree_res.get('repo'),
            'files': file_codes
        }
