from fastapi import FastAPI , APIRouter, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from database import collection_names, all_docs, individual_doc , db
from bson import ObjectId
from typing import Optional, List, Dict, Any, Tuple
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()
app = FastAPI()
router = APIRouter()

@router.get("/documents")
async def get_all_doc_years():
    collections_set = []
    print(f"📊 Found {len(collection_names)} collections:")
    for collection in collection_names:
        collections_set.append(collection)
    return {
        "doc_collections" : collections_set
        }
    
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
                
    #  Years covered
    years = sorted([
        int(col.replace("gazettes_", "")) 
        for col in collection_names 
        if col.startswith("gazettes_") and col.replace("gazettes_", "").isdigit()
        ])

    years_covered = {"from": years[0], "to": years[-1]} if years else {}
    
    return {
        "total_docs" : total_docs,
        "available_languages" : list(languages),
        "years_covered": years_covered

    }

# def serialize_doc(doc):
#     """Convert Mongo _id and return only relevant fields"""
#     return {
#         "id": str(doc["_id"]),
#         "document_id": doc.get("document_id"),
#         "description": doc.get("description"),
#         "document_date": doc.get("document_date"),
#         "document_type": doc.get("document_type"),
#         "file_path": doc.get("file_path"),
#         "download_url": doc.get("download_url"),
#         "source": doc.get("source"),
#         "availability": doc.get("availability"),
#         "score": doc.get("score", 0)
#     }

# @app.post("/search")
# async def search_documents(payload: dict = Body(...)):
#     query = payload.get("query", "")
#     page = payload.get("page", 1)
#     limit = payload.get("limit", 50)  # Default 50 items per page
    
#     if not query:
#         return {
#             "results": [],
#             "pagination": {
#                 "current_page": page,
#                 "total_pages": 0,
#                 "total_count": 0,
#                 "limit": limit,
#                 "has_next": False,
#                 "has_prev": False
#             }
#         }

#     # Calculate offset
#     offset = (page - 1) * limit
    
#     # Build the search query with additional fields
#     search_query = {
#         "$or": [
#             {"document_type": {"$regex": query, "$options": "i"}},
#             {"description": {"$regex": query, "$options": "i"}},
#             {"document_id": {"$regex": query, "$options": "i"}},  # Added document_id search
#             {"document_date": query}  # Exact match for date (since it's in YYYY-MM-DD format)
#         ]
#     }
    
#     # If the query looks like a date pattern, also add partial date matching
#     # This allows searching for "2015" to find all documents from 2015
#     # or "2015-01" to find all documents from January 2015
#     if query.replace("-", "").isdigit() and len(query) >= 4:
#         search_query["$or"].append({"document_date": {"$regex": f"^{query}", "$options": "i"}})
    
#     projection = {
#         "document_id": 1,
#         "description": 1,
#         "document_date": 1,
#         "document_type": 1,
#         "file_path": 1,
#         "download_url": 1,
#         "source": 1,
#         "availability": 1
#     }
    
#     all_results = []
#     total_count = 0
    
#     # First, get total count across all collections
#     for col in collection_names:
#         count = db[col].count_documents(search_query)
#         total_count += count
    
#     # Then get the paginated results
#     collected_results = []
#     remaining_offset = offset
#     remaining_limit = limit
    
#     for col in collection_names:
#         if remaining_limit <= 0:
#             break
        
#         # Get count for this collection
#         col_count = db[col].count_documents(search_query)
        
#         if col_count == 0:
#             continue
        
#         if remaining_offset >= col_count:
#             # Skip this entire collection
#             remaining_offset -= col_count
#             continue
        
#         # Get documents from this collection
#         cursor = db[col].find(search_query, projection).skip(remaining_offset).limit(remaining_limit)
#         col_results = [serialize_doc(doc) for doc in cursor]
        
#         collected_results.extend(col_results)
#         remaining_limit -= len(col_results)
#         remaining_offset = 0  # We've handled the offset
    
#     # Sort the collected results by date
#     sorted_results = sorted(
#         collected_results, 
#         key=lambda x: x.get("document_date", ""), 
#         reverse=True
#     )
    
#     # Calculate pagination info
#     total_pages = (total_count + limit - 1) // limit  # Ceiling division
#     has_next = page < total_pages
#     has_prev = page > 1
    
#     return {
#         "results": sorted_results,
#         "pagination": {
#             "current_page": page,
#             "total_pages": total_pages,
#             "total_count": total_count,
#             "limit": limit,
#             "has_next": has_next,
#             "has_prev": has_prev,
#             "start_index": offset + 1 if total_count > 0 else 0,
#             "end_index": min(offset + len(sorted_results), total_count)
#         }
#     }


# def serialize_doc(doc):
#     """Convert Mongo _id and return only relevant fields"""
#     return {
#         "id": str(doc["_id"]),
#         "document_id": doc.get("document_id"),
#         "description": doc.get("description"),
#         "document_date": doc.get("document_date"),
#         "document_type": doc.get("document_type"),
#         "file_path": doc.get("file_path"),
#         "download_url": doc.get("download_url"),
#         "source": doc.get("source"),
#         "availability": doc.get("availability"),
#         "score": doc.get("score", 0)
#     }

# def parse_search_query(query: str) -> Tuple[List[str], Dict[str, Any], str]:
#     """
#     Parse search query into collections, filters, and free text
#     Returns: (target_collections, mongo_filters, free_text)
#     """
#     if not query:
#         return [], {}, ""
    
#     # Extract structured filters (key:value)
#     filter_pattern = r'(\w+):([^\s]+)'
#     filters = re.findall(filter_pattern, query)
    
#     # Remove structured filters from query to get free text
#     free_text = re.sub(filter_pattern, '', query).strip()
#     free_text = ' '.join(free_text.split())  # Clean up extra spaces
    
#     target_collections = []
#     mongo_filters = {}
    
#     for key, value in filters:
#         if key.lower() == 'date':
#             # Handle date filters
#             collections = parse_date_filter(value)
#             if collections:
#                 target_collections.extend(collections)
        
#         elif key.lower() == 'type':
#             # Document type filter
#             mongo_filters["document_type"] = {"$regex": value, "$options": "i"}
        
#         elif key.lower() == 'id':
#             # Document ID filter
#             mongo_filters["document_id"] = {"$regex": value, "$options": "i"}
        
#         elif key.lower() == 'source':
#             # Source filter
#             mongo_filters["source"] = {"$regex": value, "$options": "i"}
        
#         elif key.lower() == 'available':
#             # Availability filter
#             if value.lower() in ['yes', 'true', 'available']:
#                 mongo_filters["availability"] = "Available"
#             elif value.lower() in ['no', 'false', 'unavailable']:
#                 mongo_filters["availability"] = {"$ne": "Available"}
        
#         elif key.lower() == 'status':
#             # Generic status filter (maps to availability for now)
#             mongo_filters["availability"] = {"$regex": value, "$options": "i"}
    
#     return target_collections, mongo_filters, free_text

# def parse_date_filter(date_value: str) -> List[str]:
#     """
#     Parse date filter value and return target collections
#     Supports: 2015, 2015-01, 2015-01-31, last-7-days, this-year, etc.
#     """
#     collections = []
#     current_year = datetime.now().year
    
#     # Handle relative dates
#     if date_value.lower() == 'this-year':
#         collections.append(f"gazettes_{current_year}")
#     elif date_value.lower() == 'last-year':
#         collections.append(f"gazettes_{current_year - 1}")
#     elif date_value.lower().startswith('last-') and date_value.lower().endswith('-days'):
#         # For last-X-days, we need to determine which collections might have those dates
#         try:
#             days = int(date_value.split('-')[1])
#             start_date = datetime.now() - timedelta(days=days)
#             end_date = datetime.now()
            
#             # Get all years in the range
#             years = set()
#             current_date = start_date
#             while current_date <= end_date:
#                 years.add(current_date.year)
#                 current_date += timedelta(days=32)  # Move to next month
            
#             collections.extend([f"gazettes_{year}" for year in sorted(years)])
#         except (ValueError, IndexError):
#             pass
    
#     # Handle specific year: 2015
#     elif re.match(r'^\d{4}$', date_value):
#         collections.append(f"gazettes_{date_value}")
    
#     # Handle year-month: 2015-01
#     elif re.match(r'^\d{4}-\d{2}$', date_value):
#         year = date_value.split('-')[0]
#         collections.append(f"gazettes_{year}")
    
#     # Handle full date: 2015-01-31
#     elif re.match(r'^\d{4}-\d{2}-\d{2}$', date_value):
#         year = date_value.split('-')[0]
#         collections.append(f"gazettes_{year}")
    
#     return collections

# def build_mongodb_query(mongo_filters: Dict[str, Any], free_text: str) -> Dict[str, Any]:
#     """
#     Build the final MongoDB query combining filters and free text search
#     """
#     query_parts = []
    
#     # Add structured filters
#     for field, filter_condition in mongo_filters.items():
#         query_parts.append({field: filter_condition})
    
#     # Add free text search if present
#     if free_text:
#         text_search = {
#             "$or": [
#                 {"document_type": {"$regex": free_text, "$options": "i"}},
#                 {"description": {"$regex": free_text, "$options": "i"}},
#                 {"document_id": {"$regex": free_text, "$options": "i"}},
#                 {"document_date": free_text}  # Exact match for full dates
#             ]
#         }
        
#         # If free text looks like a date pattern, add partial date matching
#         if free_text.replace("-", "").isdigit() and len(free_text) >= 4:
#             text_search["$or"].append({
#                 "document_date": {"$regex": f"^{free_text}", "$options": "i"}
#             })
        
#         query_parts.append(text_search)
    
#     # Combine all parts with AND logic
#     if len(query_parts) == 0:
#         return {}
#     elif len(query_parts) == 1:
#         return query_parts[0]
#     else:
#         return {"$and": query_parts}

# @app.post("/search")
# async def search_documents(payload: dict = Body(...)):
#     query = payload.get("query", "")
#     page = payload.get("page", 1)
#     limit = payload.get("limit", 50)
    
#     if not query:
#         return {
#             "results": [],
#             "pagination": {
#                 "current_page": page,
#                 "total_pages": 0,
#                 "total_count": 0,
#                 "limit": limit,
#                 "has_next": False,
#                 "has_prev": False
#             }
#         }

#     # Parse the search query
#     target_collections, mongo_filters, free_text = parse_search_query(query)
    
#     # Determine which collections to search
#     if target_collections:
#         # Use specific collections from date filters
#         collections_to_search = target_collections
#     else:
#         # Use all collections (current behavior)
#         collections_to_search = collection_names
    
#     # Build the MongoDB query
#     search_query = build_mongodb_query(mongo_filters, free_text)
    
#     # If no valid query built and no free text, return empty
#     if not search_query and not free_text:
#         return {
#             "results": [],
#             "pagination": {
#                 "current_page": page,
#                 "total_pages": 0,
#                 "total_count": 0,
#                 "limit": limit,
#                 "has_next": False,
#                 "has_prev": False
#             }
#         }
    
#     # Calculate offset
#     offset = (page - 1) * limit
    
#     projection = {
#         "document_id": 1,
#         "description": 1,
#         "document_date": 1,
#         "document_type": 1,
#         "file_path": 1,
#         "download_url": 1,
#         "source": 1,
#         "availability": 1
#     }
    
#     # Get total count across target collections
#     total_count = 0
#     for col_name in collections_to_search:
#         if col_name in db.list_collection_names():  # Check if collection exists
#             count = db[col_name].count_documents(search_query)
#             total_count += count
    
#     # Get paginated results
#     collected_results = []
#     remaining_offset = offset
#     remaining_limit = limit
    
#     for col_name in collections_to_search:
#         if remaining_limit <= 0:
#             break
        
#         # Skip non-existent collections
#         if col_name not in db.list_collection_names():
#             continue
        
#         # Get count for this collection
#         col_count = db[col_name].count_documents(search_query)
        
#         if col_count == 0:
#             continue
        
#         if remaining_offset >= col_count:
#             # Skip this entire collection
#             remaining_offset -= col_count
#             continue
        
#         # Get documents from this collection
#         cursor = db[col_name].find(search_query, projection).skip(remaining_offset).limit(remaining_limit)
#         col_results = [serialize_doc(doc) for doc in cursor]
        
#         collected_results.extend(col_results)
#         remaining_limit -= len(col_results)
#         remaining_offset = 0  # We've handled the offset
    
#     # Sort the collected results by date (newest first)
#     sorted_results = sorted(
#         collected_results, 
#         key=lambda x: x.get("document_date", ""), 
#         reverse=True
#     )
    
#     # Calculate pagination info
#     total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
#     has_next = page < total_pages
#     has_prev = page > 1
    
#     return {
#         "results": sorted_results,
#         "pagination": {
#             "current_page": page,
#             "total_pages": total_pages,
#             "total_count": total_count,
#             "limit": limit,
#             "has_next": has_next,
#             "has_prev": has_prev,
#             "start_index": offset + 1 if total_count > 0 else 0,
#             "end_index": min(offset + len(sorted_results), total_count)
#         },
#         "query_info": {
#             "parsed_query": query,
#             "target_collections": target_collections if target_collections else "all",
#             "filters_applied": len(mongo_filters),
#             "has_free_text": bool(free_text)
#         }
#     }






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




# Example usage and expected behavior:
"""
Query Examples:

1. "date:2015" 
   → searches only gazettes_2015 collection
   → returns all documents from 2015

2. "date:2015 type:election"
   → searches only gazettes_2015 collection  
   → filters for documents containing "election" in document_type

3. "date:2015 commission reports"
   → searches only gazettes_2015 collection
   → filters for documents containing "commission reports" in description/id

4. "type:gazette available:yes"
   → searches all collections (no date filter)
   → filters for available gazette documents

5. "election commission" (no structured filters)
   → searches all collections (current behavior)
   → free text search across all fields

6. "date:last-7-days type:notice"
   → searches collections that might contain last 7 days
   → filters for notice type documents
"""


@app.get("/dashboard-status/pie-chart")
async def get_document_type_counts():
    """
    Get count of documents by document_type for pie chart visualization
    Returns data formatted for MUI pie chart component
    """
    try:
        # Dictionary to store aggregated counts
        type_counts = {}
        
        # Aggregate counts from all collections
        for col in collection_names:
            # Use MongoDB aggregation pipeline to group by document_type
            pipeline = [
                {
                    "$group": {
                        "_id": "$document_type",
                        "count": {"$sum": 1}
                    }
                },
                {
                    "$sort": {"count": -1}  # Sort by count in descending order
                }
            ]
            
            # Execute aggregation
            results = list(db[col].aggregate(pipeline))
            
            # Aggregate results across collections
            for result in results:
                doc_type = result["_id"] or "Uncategorized"  # Handle null/empty document_type
                count = result["count"]
                
                if doc_type in type_counts:
                    type_counts[doc_type] += count
                else:
                    type_counts[doc_type] = count
        
        # Convert to MUI pie chart format
        pie_data = []
        total_documents = sum(type_counts.values())
        
        # Generate colors for the pie chart (you can customize these)
        colors = [
            "#8884d8", "#82ca9d", "#ffc658", "#ff7300", "#00ff00",
            "#ff0000", "#0000ff", "#ffff00", "#ff00ff", "#00ffff",
            "#800080", "#ffa500", "#a52a2a", "#808080", "#000080"
        ]
        
        for index, (doc_type, count) in enumerate(sorted(type_counts.items(), key=lambda x: x[1], reverse=True)):
            percentage = round((count / total_documents) * 100, 1) if total_documents > 0 else 0
            
            pie_data.append({
                "id": index,
                "label": doc_type,
                "value": count,
                "percentage": percentage,
                "color": colors[index % len(colors)]  # Cycle through colors if more types than colors
            })
        
        return {
            "success": True,
            "data": pie_data,
            "summary": {
                "total_documents": total_documents,
                "total_types": len(type_counts),
                "collections_processed": len(collection_names)
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to fetch document type counts: {str(e)}",
            "data": [],
            "summary": {
                "total_documents": 0,
                "total_types": 0,
                "collections_processed": 0
            }
        }
    
@router.get("/documents/{doc_year}")
async def get_all_docs_for_year(
    doc_year: str,
    limit: Optional[int] = Query(default=None, ge=1, le=1000, description="Number of documents per page"),
    offset: int = Query(default=0, ge=0, description="Number of documents to skip"),
    search: Optional[str] = Query(default=None, description="Search query"),
    month: Optional[str] = Query(default=None, description="Filter by month name"),
    day: Optional[str] = Query(default=None, description="Filter by day (01-31)"),
    type: Optional[str] = Query(default=None, description="Filter by document type")
):
    if doc_year not in collection_names:
        return {
            "error": "Year not found"
        }
    
    collection = db[str(doc_year)]
    
    # Build MongoDB query
    query_filter = {}
    
    # Add search filter if provided
    if search and search.strip():
        search_pattern = {"$regex": search.strip(), "$options": "i"}  # Case-insensitive
        query_filter["$or"] = [
            {"document_id": search_pattern},
            {"document_type": search_pattern},
            {"reasoning": search_pattern}
        ]
    
    # Add date filters
    date_filters = []
    
    if month:
        # Convert month name to number for filtering
        month_names = {
            "January": 1, "February": 2, "March": 3, "April": 4,
            "May": 5, "June": 6, "July": 7, "August": 8,
            "September": 9, "October": 10, "November": 11, "December": 12
        }
        if month in month_names:
            # Extract month from document_date (assuming ISO date format)
            date_filters.append({
                "$expr": {
                    "$eq": [{"$month": {"$dateFromString": {"dateString": "$document_date"}}}, month_names[month]]
                }
            })
    
    if day:
        try:
            day_num = int(day)
            # Extract day from document_date
            date_filters.append({
                "$expr": {
                    "$eq": [{"$dayOfMonth": {"$dateFromString": {"dateString": "$document_date"}}}, day_num]
                }
            })
        except ValueError:
            pass  # Invalid day format, ignore
    
    # Add date filters to main query
    if date_filters:
        if "$and" not in query_filter:
            query_filter["$and"] = []
        query_filter["$and"].extend(date_filters)
    
    # Add document type filter
    if type and type.strip():
        query_filter["document_type"] = type.strip()
    
    # Get total count with filters applied
    total_count = collection.count_documents(query_filter)
    
    # Apply pagination only if limit is provided
    if limit is not None:
        docs = collection.find(query_filter).skip(offset).limit(limit)
        
        # Calculate pagination metadata
        has_next = (offset + limit) < total_count
        has_previous = offset > 0
        total_pages = (total_count + limit - 1) // limit if limit > 0 else 1
        current_page = (offset // limit) + 1 if limit > 0 else 1
        
        documents = all_docs(docs)
        
        return {
            "documents": documents,
            "pagination": {
                "total_count": total_count,
                "current_page": current_page,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_previous": has_previous,
                "limit": limit,
                "offset": offset
            },
            "filters": {
                "search": search,
                "month": month,
                "day": day,
                "type": type
            }
        }
    else:
        # Return all documents without pagination (with filters applied)
        docs = collection.find(query_filter)
        documents = all_docs(docs)
        
        return {
            "documents": documents,
            "total_count": total_count,
            "filters": {
                "search": search,
                "month": month,
                "day": day,
                "type": type
            }
        }

@router.get("/documents/filters/{doc_year}")
def get_filter_options(doc_year: str):
    if doc_year not in collection_names:
        return {"error": "Year not found"}

    collection = db[str(doc_year)]

    filter_options = {
        "months": sorted(list({int(d.split("-")[1]) for d in collection.distinct("document_date")})),
        "days": sorted(list({int(d.split("-")[2]) for d in collection.distinct("document_date")})),
        "document_types": collection.distinct("document_type")
    }
    return filter_options        


@router.get("/documents/{doc_year}/{doc_id}")
async def get_individual_doc(doc_year : str, doc_id : str):
    if doc_year not in collection_names:
        return {
            "error" : "Year not found"
        }
    collection = db[str(doc_year)]
    doc = collection.find_one({
        "_id" : ObjectId(doc_id)
    })
    if not doc:
        return {
            "error" : "Document not found"
        }
    return individual_doc(doc)


origins = [value for key, value in os.environ.items() if key.endswith("_CORS")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # or ["*"] for all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)


