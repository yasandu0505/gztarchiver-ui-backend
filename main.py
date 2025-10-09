from pydoc import doc
from fastapi import FastAPI , APIRouter, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from database import collection_names, all_docs, individual_doc , db
from bson import ObjectId
from typing import Optional, List, Dict, Any, Tuple
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import requests
import binascii
from google.protobuf.wrappers_pb2 import StringValue
import json

load_dotenv()
app = FastAPI()
router = APIRouter()

@router.get("/dashboard-status")
async def get_dashboard_status():
    #  Total documents
    total_docs = sum(db[col].count_documents({}) for col in collection_names)
    
    #  Available languages
    languages = set()
    for col in collection_names:
        cursor = db[col].find({}, {"file_path": 1})
        for doc in cursor:
            fp = doc.get("file_path", "").lower()
            if "english" in fp:
                languages.add("English")
            if "sinhala" in fp:
                languages.add("Sinhala")
            if "tamil" in fp:
                languages.add("Tamil")
                
    document_types = set()
    for col in collection_names:
        cursor = db[col].find({}, {"document_type": 1})
        for doc in cursor:
            doc_type = doc.get("document_type")
            if doc_type:
                document_types.add(doc_type.title().strip().replace("_", " "))
                
    #  Years covered
    years = sorted([
        int(col.replace("gazettes_", "")) 
        for col in collection_names 
        if col.startswith("gazettes_") and col.replace("gazettes_", "").isdigit()
        ])

    years_covered = {"from": years[0], "to": years[-1]} if years else {}
    
    return {
        "total_docs" : total_docs,
        "available_languages" : sorted(list(languages)),
        "document_types": sorted(list(document_types)),
        "years_covered": years_covered

    }

def serialize_doc(doc):
    """Convert Mongo _id and return only relevant fields"""
    return {
        "id": str(doc["_id"]),
        "document_id": doc.get("document_id"),
        "description": doc.get("description"),
        "document_date": doc.get("document_date"),
        "document_type": doc.get("document_type"),
        "file_path": doc.get("file_path"),
        "download_url": doc.get("download_url"),
        "source": doc.get("source"),
        "availability": doc.get("availability"),
        "score": doc.get("score", 0)
    }

def parse_search_query(query: str) -> Tuple[List[str], Dict[str, Any], str]:
    """
    Parse search query into collections, filters, and free text
    Returns: (target_collections, mongo_filters, free_text)
    """
    if not query:
        return [], {}, ""
    
    # Extract structured filters (key:value)
    filter_pattern = r'(\w+):([^\s]+)'
    filters = re.findall(filter_pattern, query)
    
    # Remove structured filters from query to get free text
    free_text = re.sub(filter_pattern, '', query).strip()
    free_text = ' '.join(free_text.split())  # Clean up extra spaces
    
    target_collections = []
    mongo_filters = {}
    
    for key, value in filters:
        if key.lower() == 'date':
            # Handle date filters
            collections, date_filter = parse_date_filter(value)
            if collections:
                target_collections.extend(collections)
            if date_filter:
                mongo_filters.update(date_filter)
        
        elif key.lower() == 'type':
            # Document type filter
            mongo_filters["document_type"] = {"$regex": value, "$options": "i"}
        
        elif key.lower() == 'id':
            # Document ID filter
            mongo_filters["document_id"] = {"$regex": value, "$options": "i"}
        
        elif key.lower() == 'source':
            # Source filter
            mongo_filters["source"] = {"$regex": value, "$options": "i"}
        
        elif key.lower() == 'available':
            # Availability filter
            if value.lower() in ['yes', 'true', 'available']:
                mongo_filters["availability"] = "Available"
            elif value.lower() in ['no', 'false', 'unavailable']:
                mongo_filters["availability"] = {"$ne": "Available"}
        
        elif key.lower() == 'status':
            # Generic status filter (maps to availability for now)
            mongo_filters["availability"] = {"$regex": value, "$options": "i"}
    
    return target_collections, mongo_filters, free_text

def parse_date_filter(date_value: str) -> Tuple[List[str], Dict[str, Any]]:
    """
    Parse date filter value and return target collections and additional date filters
    Returns: (collections, date_filter_dict)
    """
    collections = []
    date_filter = {}
    current_year = datetime.now().year
    
    # Handle relative dates
    if date_value.lower() == 'this-year':
        collections.append(f"gazettes_{current_year}")
    elif date_value.lower() == 'last-year':
        collections.append(f"gazettes_{current_year - 1}")
    elif date_value.lower().startswith('last-') and date_value.lower().endswith('-days'):
        # For last-X-days, we need to determine which collections might have those dates
        try:
            days = int(date_value.split('-')[1])
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get all years in the range
            years = set()
            current_date = start_date
            while current_date <= end_date:
                years.add(current_date.year)
                current_date += timedelta(days=32)  # Move to next month
            
            collections.extend([f"gazettes_{year}" for year in sorted(years)])
            
            # Add date range filter
            start_date_str = start_date.strftime("%Y-%m-%d")
            date_filter["document_date"] = {"$gte": start_date_str}
            
        except (ValueError, IndexError):
            pass
    
    # Handle specific year: 2015 (get ALL documents from that year)
    elif re.match(r'^\d{4}$', date_value):
        collections.append(f"gazettes_{date_value}")
        # No additional date filter needed - we want all docs from that year
    
    # Handle year-month: 2015-01 (get documents from specific month)
    elif re.match(r'^\d{4}-\d{2}$', date_value):
        year = date_value.split('-')[0]
        collections.append(f"gazettes_{year}")
        # Add month filter
        date_filter["document_date"] = {"$regex": f"^{date_value}", "$options": "i"}
    
    # Handle full date: 2015-01-31 (get documents from specific date)
    elif re.match(r'^\d{4}-\d{2}-\d{2}$', date_value):
        year = date_value.split('-')[0]
        collections.append(f"gazettes_{year}")
        # Add exact date filter
        date_filter["document_date"] = date_value
    
    return collections, date_filter

def build_mongodb_query(mongo_filters: Dict[str, Any], free_text: str) -> Dict[str, Any]:
    """
    Build the final MongoDB query combining filters and free text search
    Returns None if no filters needed (get all documents)
    """
    query_parts = []
    
    # Add structured filters
    for field, filter_condition in mongo_filters.items():
        query_parts.append({field: filter_condition})
    
    # Add free text search if present
    if free_text:
        text_search = {
            "$or": [
                {"document_type": {"$regex": free_text, "$options": "i"}},
                {"description": {"$regex": free_text, "$options": "i"}},
                {"document_id": {"$regex": free_text, "$options": "i"}},
                {"document_date": free_text}  # Exact match for full dates
            ]
        }
        
        # If free text looks like a date pattern, add partial date matching
        if free_text.replace("-", "").isdigit() and len(free_text) >= 4:
            text_search["$or"].append({
                "document_date": {"$regex": f"^{free_text}", "$options": "i"}
            })
        
        query_parts.append(text_search)
    
    # Combine all parts with AND logic
    if len(query_parts) == 0:
        return {}  # Empty query means get all documents
    elif len(query_parts) == 1:
        return query_parts[0]
    else:
        return {"$and": query_parts}

@app.post("/search")
async def search_documents(payload: dict = Body(...)):
    query = payload.get("query", "")
    page = payload.get("page", 1)
    limit = payload.get("limit", 50)
    
    if not query:
        return {
            "results": [],
            "pagination": {
                "current_page": page,
                "total_pages": 0,
                "total_count": 0,
                "limit": limit,
                "has_next": False,
                "has_prev": False
            }
        }

    # Parse the search query
    target_collections, mongo_filters, free_text = parse_search_query(query)
    
    # Determine which collections to search
    if target_collections:
        # Use specific collections from date filters
        collections_to_search = target_collections
    else:
        # Use all collections (current behavior)
        collections_to_search = collection_names
    
    # Build the MongoDB query
    search_query = build_mongodb_query(mongo_filters, free_text)
    
    # Calculate offset
    offset = (page - 1) * limit
    
    projection = {
        "document_id": 1,
        "description": 1,
        "document_date": 1,
        "document_type": 1,
        "file_path": 1,
        "download_url": 1,
        "source": 1,
        "availability": 1
    }
    
    # Get total count across target collections
    total_count = 0
    for col_name in collections_to_search:
        try:
            if col_name in db.list_collection_names():  # Check if collection exists
                count = db[col_name].count_documents(search_query)
                total_count += count
        except Exception as e:
            # Log error and continue with other collections
            print(f"Error counting documents in {col_name}: {e}")
            continue
    
    # Get paginated results
    collected_results = []
    remaining_offset = offset
    remaining_limit = limit
    
    for col_name in collections_to_search:
        if remaining_limit <= 0:
            break
        
        try:
            # Skip non-existent collections
            if col_name not in db.list_collection_names():
                continue
            
            # Get count for this collection
            col_count = db[col_name].count_documents(search_query)
            
            if col_count == 0:
                continue
            
            if remaining_offset >= col_count:
                # Skip this entire collection
                remaining_offset -= col_count
                continue
            
            # Get documents from this collection
            cursor = db[col_name].find(search_query, projection).skip(remaining_offset).limit(remaining_limit)
            col_results = [serialize_doc(doc) for doc in cursor]
            
            collected_results.extend(col_results)
            remaining_limit -= len(col_results)
            remaining_offset = 0  # We've handled the offset
            
        except Exception as e:
            # Log error and continue with other collections
            print(f"Error searching collection {col_name}: {e}")
            continue
    
    # Sort the collected results by date (newest first)
    sorted_results = sorted(
        collected_results, 
        key=lambda x: x.get("document_date", ""), 
        reverse=True
    )
    
    # Calculate pagination info
    total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "results": sorted_results,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "total_count": total_count,
            "limit": limit,
            "has_next": has_next,
            "has_prev": has_prev,
            "start_index": offset + 1 if total_count > 0 else 0,
            "end_index": min(offset + len(sorted_results), total_count)
        },
        "query_info": {
            "parsed_query": query,
            "target_collections": target_collections if target_collections else "all",
            "filters_applied": len(mongo_filters),
            "has_free_text": bool(free_text),
            "search_query": str(search_query)  # Debug info
        }
    }
    
def decode_protobuf(name : str) -> str:
    try:
        data = json.loads(name)
        hex_value = data.get("value")
        if not hex_value:
            return ""

        decoded_bytes = binascii.unhexlify(hex_value)
        sv = StringValue()
        try:
            sv.ParseFromString(decoded_bytes)
            return sv.value.strip()
        except Exception:
            decoded_str = decoded_bytes.decode("utf-8", errors="ignore")
            cleaned = ''.join(ch for ch in decoded_str if ch.isprintable())
            return cleaned.strip()
    except Exception as e:
        print(f"[DEBUG decode] outer exception: {e}")
        return ""

def validate_document_on_graph(documentId : str):
    QUERY_API = os.getenv("QUERY_API")
    
    url = f"{QUERY_API}/v1/entities/search"
    
    payload = {
        "kind": {
            "major": "Document",
            "minor": ""
        },
        "name": documentId,
    }
    headers = {
        "Content-Type": "application/json",
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  
        document_output = response.json()
        
        if document_output.get("body") and isinstance(document_output["body"], list):
            document = document_output["body"][0]
            encoded_document_number = document.get("name")
            if encoded_document_number:
                decoded_document_number = decode_protobuf(encoded_document_number)
                if decoded_document_number == documentId:
                    document_id = document["id"]
                    return document_id
                else:
                    return False
            else:
                return False
        else:
            return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False


@app.post("/document/{documentId}")
async def search_document(documentId : str):  
    document_output = validate_document_on_graph(documentId)  
    if document_output:
        print(f"Document Found : {document_output}")
        return document_output
    else:
        print(f"Document not Found : {document_output}")
        return document_output


def check_for_relationships_on_document(documentId : str):
    QUERY_API = os.getenv("QUERY_API")
    
    url = f"{QUERY_API}/v1/entities/{documentId}/relations"
    
    payload = {
        
            "id": "",
            "relatedEntityId": "",
            "name": "",
            "activeAt": "",
            "startTime": "",
            "endTime": "",
            "direction": ""
        
    }
    headers = {
        "Content-Type": "application/json",
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  
        relationship_output = response.json()
        return relationship_output
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {
            "error" : str(e)
        }


def fetch_document_name(documentId : str):
    QUERY_API = os.getenv("QUERY_API")
    
    url = f"{QUERY_API}/v1/entities/search"
    
    payload = {
        "id": documentId
    }
    headers = {
        "Content-Type": "application/json",
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  
        document_output = response.json()
        
        if document_output.get("body") and isinstance(document_output["body"], list):
            document = document_output["body"][0]
            encoded_document_number = document.get("name")
            if encoded_document_number:
                decoded_document_number = decode_protobuf(encoded_document_number)
                if decoded_document_number:
                    return decoded_document_number
                else:
                    return False
            else:
                return False
        else:
            return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False
    
        
@app.post("/document-rel/{documentId}")
async def search_document_rel(documentId : str):  
    relationship_response = check_for_relationships_on_document(documentId)
    if "error" not in relationship_response:
        filtered_relationship_response = [
            {
                "relatedEntityId": relationship["relatedEntityId"],
                "name": relationship["name"],
                "direction": relationship["direction"]
            }
            for relationship in relationship_response
        ]
        
        for relationship in filtered_relationship_response:
            document_name = fetch_document_name(relationship["relatedEntityId"])
            if document_name:
                relationship["document_number"] = document_name
            else:
                relationship["document_number"] = False

        return filtered_relationship_response            
    else:
        print("Error:", relationship_response["error"])
        return relationship_response["error"]
    
    

origins = [value for key, value in os.environ.items() if key.endswith("_CORS")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)











