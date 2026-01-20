from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
# from api.routes import api_router
from database import connect_to_github 
from services.file_service import FileService
import asyncio
import time


# Initialize FastAPI app
app = FastAPI(
    title="GZT Archiver UI Backend",
    description="Backend API for GZT Archiver",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# # Register API routes
# app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    print("Starting up...")
    fileservice = FileService()
    try:
        root_tree = await fileservice.get_the_root_tree()
        for item in root_tree:
            if item["path"] == fileservice.target_dir and item["type"] == "tree":
                print(f"target repo found : {item}")
                target_sha = item["sha"]
                folder_name = item["path"]
                break
        
        if not target_sha and folder_name:
            raise RuntimeError(f"Target folder '{fileservice.target_dir}' not found in root tree")
        
        top_level_folders_of_target_folder = await fileservice.get_the_top_level_of_target_folder(folder_name)
        # start = time.perf_counter() 
        # for item in top_level_folders_of_target_folder:
        #     print(f"\nSub directory >>>> {item['path']}")
        #     target_folder_tree = await fileservice.get_the_tree_of_target_folder(item["sha"])
        #     count = 0
        #     for item in target_folder_tree:
        #         # decoded_metadata_content = await fileservice.get_metadata_content(item['sha'])
        #         count += 1
        #     print(f"Metadata document count : {count}")  
             
        # end = time.perf_counter()     # ⏱️ stop timer
        # print(f"Total time: {end - start:.2f} seconds")
        
        
        # start = time.perf_counter()  
        # tasks = []
        
        # for item in top_level_folders_of_target_folder:
        #     print(f"\nSub directory >>>> {item['path']}")
        #     tasks.append(fileservice.get_the_tree_of_target_folder(item["sha"]))       
            
        # results = await asyncio.gather(*tasks)
        
        # for item, tree in zip(top_level_folders_of_target_folder, results):
        #     count = len(tree)
        #     print(f"{item['path']} -> Metadata document count: {count}")
        
        # end = time.perf_counter()     # ⏱️ stop timer
        # print(f"Total time: {end - start:.2f} seconds")
        
        
        start = time.perf_counter()
        tasks = []
        for item in top_level_folders_of_target_folder:
            if item['path'] == 'doc-archive/2015':
                tasks.append(fileservice.process_folder(item))
        
        all_results = await asyncio.gather(*tasks)
        print("\nDONE")
        print(all_results)
        print(f"\nTotal time: {time.perf_counter() - start:.2f}s")

    except Exception as e:
        print("⚠️ WARNING: Could not load metadata on startup:", e)
    
    
    

    
    
    
    
    
    
