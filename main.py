from fastapi import FastAPI , APIRouter, Query, Body
from database import collection_names, all_docs, individual_doc , db
from bson import ObjectId
from typing import Optional

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

@app.post("/search")
async def search_documents(payload: dict = Body(...)):
    query = payload.get("query", "")
    page = payload.get("page", 1)
    limit = payload.get("limit", 50)  # Default 50 items per page
    
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

    # Calculate offset
    offset = (page - 1) * limit
    
    # Build the search query with additional fields
    search_query = {
        "$or": [
            {"document_type": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}},
            {"document_id": {"$regex": query, "$options": "i"}},  # Added document_id search
            {"document_date": query}  # Exact match for date (since it's in YYYY-MM-DD format)
        ]
    }
    
    # If the query looks like a date pattern, also add partial date matching
    # This allows searching for "2015" to find all documents from 2015
    # or "2015-01" to find all documents from January 2015
    if query.replace("-", "").isdigit() and len(query) >= 4:
        search_query["$or"].append({"document_date": {"$regex": f"^{query}", "$options": "i"}})
    
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
    
    all_results = []
    total_count = 0
    
    # First, get total count across all collections
    for col in collection_names:
        count = db[col].count_documents(search_query)
        total_count += count
    
    # Then get the paginated results
    collected_results = []
    remaining_offset = offset
    remaining_limit = limit
    
    for col in collection_names:
        if remaining_limit <= 0:
            break
        
        # Get count for this collection
        col_count = db[col].count_documents(search_query)
        
        if col_count == 0:
            continue
        
        if remaining_offset >= col_count:
            # Skip this entire collection
            remaining_offset -= col_count
            continue
        
        # Get documents from this collection
        cursor = db[col].find(search_query, projection).skip(remaining_offset).limit(remaining_limit)
        col_results = [serialize_doc(doc) for doc in cursor]
        
        collected_results.extend(col_results)
        remaining_limit -= len(col_results)
        remaining_offset = 0  # We've handled the offset
    
    # Sort the collected results by date
    sorted_results = sorted(
        collected_results, 
        key=lambda x: x.get("document_date", ""), 
        reverse=True
    )
    
    # Calculate pagination info
    total_pages = (total_count + limit - 1) // limit  # Ceiling division
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
        }
    }

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

app.include_router(router)


