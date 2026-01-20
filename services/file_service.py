import asyncio
from urllib import response
import httpx
from config import settings
import base64
from pathlib import Path
import json
import aiohttp

class FileService:
    def __init__(self):
        self.repo_url = f"{settings.github_api}repos/{settings.github_user}/{settings.github_repository}"
        self.github_file_download_url = f"{settings.github_file_download_url}{settings.github_user}/{settings.github_repository}/{settings.github_target_branch}/"
        self.branch = settings.github_target_branch
        self.github_api_key = settings.github_api_key
        self.target_dir = settings.github_target_dir
        self.cache_metadata_saving_dir = settings.cache_metadata_saving_dir
        
        project_root = Path.cwd()
        cache_dir = project_root / self.cache_metadata_saving_dir
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.cache_file = cache_dir / "metadata_cache.json"
        
        # self.cache_file = project_root / self.cache_metadata_saving_dir / "metadata_cache.json"
        # self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        # In-memory storage
        self.metadataList = []
        self.idIndex = {}
        self.dateIndex = {}

    async def get_the_root_tree(self):
        """
        Fetch the root tree of the repository (top-level only, no recursion)
        """
        url = f"{self.repo_url}/git/trees/{self.branch}"  
        headers = {
            "Authorization": f"token {self.github_api_key}"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            root_tree = [
                {"path": item["path"], "type": item["type"], "sha": item["sha"]}
                for item in data.get("tree", [])
            ]

            return root_tree
        
    async def get_the_tree_of_target_folder(self, folder_sha):
        """
        Fetch the tree of target folder recursively, and only find the .json files
        and return only the tree contains .jsons
        """
        target_folder_tree = []
        url = f"{self.repo_url}/git/trees/{folder_sha}?recursive=1"
        headers = {
            "Authorization" : f"token {self.github_api_key}"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            print("Tree truncated?", data.get("truncated", False))
            print("Total items returned:", len(data.get("tree", [])))
            
            for item in data.get("tree", []):
                if item["type"] == "blob" and item["path"].endswith(".json"):
                    file_object = {
                        "path": item['path'],
                        "type": item["type"],
                        "sha": item["sha"]
                    }
                    target_folder_tree.append(file_object)
            
        return target_folder_tree
    
    async def get_the_top_level_of_target_folder(self, folder_name):
        """
        getting the top level direcoties of a given folder
        """
        top_level_folders = []
        url = f"{self.repo_url}/contents/{folder_name}?ref={self.branch}"
        headers = {
            "Authorization" : f"token {self.github_api_key}"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            for item in data:
                file_object = {
                    "path" : item['path'],
                    "type" : item['type'],
                    "sha" : item['sha']
                }
                top_level_folders.append(file_object)            
            
            return top_level_folders
        
    def decode_base64_metadata_content(self, content):
        """
        deocode base64 content to JSON dict
        """        
        decoded_metadata_content = content
        
        try:
            decode_bytes = base64.b64decode(content)
            decoded_string = decode_bytes.decode("utf-8")
            decoded_metadata_content = json.loads(decoded_string)
            return decoded_metadata_content
        except Exception as e:
            print(f"❌ Failed to decode metadata: {e}")
            return None 
            
    async def get_metadata_content(self, metadata_sha):
        """
        get the content of a github sha
        """
        url = f"{self.repo_url}/git/blobs/{metadata_sha}"
        headers = {
            "Authorization" : f"token {self.github_api_key}"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            decoded_metadata_content = self.decode_base64_metadata_content(data['content'])
            print(decoded_metadata_content)
            return decoded_metadata_content
    
    # async def download_raw_metadata_file(self, file_path):
    #     url = f"{self.github_file_download_url}{file_path}"
    #     print(f"Downloading: {url}")
    #     filename = Path(file_path).name
    #     project_root = Path.cwd()
    #     saving_dir = project_root / 'tmp' / self.cache_metadata_saving_dir
    #     saving_dir.mkdir(parents=True, exist_ok=True)
    #     saving_path = saving_dir / filename
    #     proc = await asyncio.create_subprocess_exec(
    #         "wget",
    #         "-q",
    #         "-O", str(saving_path),
    #         url,
    #         stdout=asyncio.subprocess.PIPE,
    #         stderr=asyncio.subprocess.PIPE,
    #     )
    #     stdout, stderr = await proc.communicate()
        
    #     if proc.returncode != 0:
    #         raise RuntimeError(
    #             f"Failed to download {url}. Error: {stderr.decode().strip()}"
    #         )
            
    #     print(f"Saved to: {saving_path} ({saving_path.stat().st_size} bytes)")
        
    #     with open(saving_path, 'r') as f:
    #         file_content = json.load(f)
        
    #     metadata_path = project_root / 'metadata.json'
        
    #     if metadata_path.exists():
    #         with open(metadata_path, 'r') as f:
    #             metadata = json.load(f)
    #     else:
    #         metadata = {"metadata": []}
        
    #     if isinstance(file_content, list):
    #         metadata["metadata"].extend(file_content)
    #     else:
    #         metadata["metadata"].append(file_content)
        
    #     # Write and flush to metadata.json
    #     with open(metadata_path, 'w') as f:
    #         json.dump(metadata, f, indent=2)
    #         f.flush()
        
    #     saving_path.unlink()
        
    #     print(f"Updated metadata.json with content from {filename}")
        
    #     return str(saving_path)
    
    async def download_raw_metadata_file(self, file_path: str) -> dict:
        """
        Downloads a single metadata JSON from GitHub directly into memory
        and merges it into a single cache file.
        """
        url = f"{self.github_file_download_url}{file_path}"
        print(f"Downloading: {url}")

        # Download JSON directly into memory
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise RuntimeError(f"Failed to download {url}, status: {response.status}")
                metadata = await response.json(content_type=None)

        # # Load existing cache if it exists
        # if self.cache_file.exists():
        #     with open(self.cache_file, "r") as f:
        #         cache = json.load(f)
        # else:
        #     cache = {}
        
        # Load existing list cache
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r") as f:
                    cache = json.load(f)
                    if not isinstance(cache, list):
                        cache = []
            except Exception:
                cache = []
        else:
            cache = []

        # if self.cache_file.exists():
        #     with open(self.cache_file, "r") as f:
        #         cache = json.load(f)
        #         if not isinstance(cache, list):
        #             raise RuntimeError("Cache file is not a list — delete it and retry")
        #         else:   
        #             cache = []
    
        # Append new object
        cache.append(metadata)

        # Write back the merged cache
        with open(self.cache_file, "w") as f:
            json.dump(cache, f, indent=2)

        print(f"Appended metadata to cache ({len(cache)} total): {self.cache_file}")
        return metadata
    
    async def process_folder(self, item, batch_size=50):
        tasks = []
        all_results = []
        count = 0
        print(f"\nSub directory >>>> {item['path']}")
        target_folder_tree = await self.get_the_tree_of_target_folder(item["sha"])
        
        for file in range(0, len(target_folder_tree), batch_size):
            batch = target_folder_tree[file:file + batch_size]
            tasks = [self.download_raw_metadata_file(f"{item['path']}/{file['path']}") for file in batch]
            batch_results = await asyncio.gather(*tasks)
            all_results.extend(batch_results)
            
        count = len(all_results)
        print(f"Metadata document count: {count}")
        return { 
                "path": item['path'], 
                "count": count 
            }
            
                        
        
