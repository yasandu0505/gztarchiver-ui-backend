# import re
# from typing import List, Dict, Any, Tuple
# from datetime import datetime, timedelta


# class QueryParser:
#     """Parser for search queries with structured filters and free text"""
    
#     @staticmethod
#     def parse_search_query(query: str) -> Tuple[List[str], Dict[str, Any], str]:
#         """
#         Parse search query into collections, filters, and free text.
        
#         Args:
#             query: Search query string with optional filters (key:value)
            
#         Returns:
#             Tuple of (target_collections, mongo_filters, free_text)
#         """
#         if not query:
#             return [], {}, ""
        
#         # Extract structured filters (key:value)
#         filter_pattern = r'(\w+):([^\s]+)'
#         filters = re.findall(filter_pattern, query)
        
#         # Remove structured filters from query to get free text
#         free_text = re.sub(filter_pattern, '', query).strip()
#         free_text = ' '.join(free_text.split())  # Clean up extra spaces
        
#         target_collections = []
#         mongo_filters = {}
        
#         for key, value in filters:
#             if key.lower() == 'date':
#                 # Handle date filters
#                 collections, date_filter = QueryParser.parse_date_filter(value)
#                 if collections:
#                     target_collections.extend(collections)
#                 if date_filter:
#                     mongo_filters.update(date_filter)
            
#             elif key.lower() == 'type':
#                 # Document type filter
#                 mongo_filters["document_type"] = {"$regex": value, "$options": "i"}
            
#             elif key.lower() == 'id':
#                 # Document ID filter
#                 mongo_filters["document_id"] = {"$regex": value, "$options": "i"}
            
#             elif key.lower() == 'source':
#                 # Source filter
#                 mongo_filters["source"] = {"$regex": value, "$options": "i"}
            
#             elif key.lower() == 'available':
#                 # Availability filter
#                 if value.lower() in ['yes', 'true', 'available']:
#                     mongo_filters["availability"] = "Available"
#                 elif value.lower() in ['no', 'false', 'unavailable']:
#                     mongo_filters["availability"] = {"$ne": "Available"}
            
#             elif key.lower() == 'status':
#                 # Generic status filter (maps to availability for now)
#                 mongo_filters["availability"] = {"$regex": value, "$options": "i"}
        
#         return target_collections, mongo_filters, free_text
    
#     @staticmethod
#     def parse_date_filter(date_value: str) -> Tuple[List[str], Dict[str, Any]]:
#         """
#         Parse date filter value and return target collections and additional date filters.
        
#         Args:
#             date_value: Date filter value (e.g., "2015", "2015-01", "2015-01-31", "this-year")
            
#         Returns:
#             Tuple of (collections, date_filter_dict)
#         """
#         collections = []
#         date_filter = {}
#         current_year = datetime.now().year
        
#         # Handle relative dates
#         if date_value.lower() == 'this-year':
#             collections.append(f"gazettes_{current_year}")
#         elif date_value.lower() == 'last-year':
#             collections.append(f"gazettes_{current_year - 1}")
#         elif date_value.lower().startswith('last-') and date_value.lower().endswith('-days'):
#             # For last-X-days, we need to determine which collections might have those dates
#             try:
#                 days = int(date_value.split('-')[1])
#                 end_date = datetime.now()
#                 start_date = end_date - timedelta(days=days)
                
#                 # Get all years in the range
#                 years = set()
#                 current_date = start_date
#                 while current_date <= end_date:
#                     years.add(current_date.year)
#                     current_date += timedelta(days=32)  # Move to next month
                
#                 collections.extend([f"gazettes_{year}" for year in sorted(years)])
                
#                 # Add date range filter
#                 start_date_str = start_date.strftime("%Y-%m-%d")
#                 date_filter["document_date"] = {"$gte": start_date_str}
                
#             except (ValueError, IndexError):
#                 pass
        
#         # Handle specific year: 2015 (get ALL documents from that year)
#         elif re.match(r'^\d{4}$', date_value):
#             collections.append(f"gazettes_{date_value}")
#             # No additional date filter needed - we want all docs from that year
        
#         # Handle year-month: 2015-01 (get documents from specific month)
#         elif re.match(r'^\d{4}-\d{2}$', date_value):
#             year = date_value.split('-')[0]
#             collections.append(f"gazettes_{year}")
#             # Add month filter
#             date_filter["document_date"] = {"$regex": f"^{date_value}", "$options": "i"}
        
#         # Handle full date: 2015-01-31 (get documents from specific date)
#         elif re.match(r'^\d{4}-\d{2}-\d{2}$', date_value):
#             year = date_value.split('-')[0]
#             collections.append(f"gazettes_{year}")
#             # Add exact date filter
#             date_filter["document_date"] = date_value
        
#         return collections, date_filter

