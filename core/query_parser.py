import re
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta


class QueryParser:
    """Parser for search queries with structured filters and free text"""
    
    @staticmethod
    def parse_search_query(query: str) -> Tuple[Dict[str, Any], str]:
        """
        Parse search query into collections, filters, and free text.
        
        Args:
            query: Search query string with optional filters (key:value)
            
        Returns:
            Tuple of (metadatastore_filters, free_text)
        """
        if not query:
            return {}, ""
        
        # Extract structured filters (key:value)
        filter_pattern = r'(\w+):([^\s]+)'
        filters = re.findall(filter_pattern, query)
        
        # Remove structured filters from query to get free text
        free_text = re.sub(filter_pattern, '', query).strip()
        free_text = ' '.join(free_text.split())  # Clean up extra spaces
        
        metadatastore_filters = {}
        
        for key, value in filters:
            if key.lower() == 'date':
                # Handle date filters
                date_filter = QueryParser.parse_date_filter(value)
                if date_filter:
                    metadatastore_filters.update(date_filter)
            
            elif key.lower() == 'type':
                # Document type filter
                metadatastore_filters["document_type"] = {"$regex": value, "$options": "i"}
            
            elif key.lower() == 'id':
                # Document ID filter
                metadatastore_filters["document_id"] = {"$regex": value, "$options": "i"}
            
            elif key.lower() == 'source':
                # Source filter
                metadatastore_filters["source"] = {"$regex": value, "$options": "i"}
            
            elif key.lower() == 'available':
                # Availability filter
                if value.lower() in ['yes', 'true', 'available']:
                    metadatastore_filters["availability"] = "Available"
                elif value.lower() in ['no', 'false', 'unavailable']:
                    metadatastore_filters["availability"] = {"$ne": "Available"}
            
            elif key.lower() == 'status':
                # Generic status filter (maps to availability for now)
                metadatastore_filters["availability"] = {"$regex": value, "$options": "i"}
        
        return metadatastore_filters, free_text
    
    @staticmethod
    def parse_date_filter(date_value: str) -> Dict[str, Any]:
        """
        Parse date filter value and return date filters.
        
        Args:
            date_value: Date filter value (e.g., "2015", "2015-01", "2015-01-31", "this-year", "last-year", "last-x-days")
            
        Returns:
            A MongoDB-style date flter dictionary.
        """
        date_filter = {}
        current_year = datetime.now().year
        
        # Handle relative dates
        if date_value.lower() == 'this-year':
            date_filter["document_date"] = {"$regex": f"^{current_year}", "$options": "i"}
        elif date_value.lower() == 'last-year':
            date_filter["document_date"] = {"$regex": f"^{current_year - 1}", "$options": "i"}
        elif date_value.lower().startswith('last-') and date_value.lower().endswith('-days'):
            # For last-X-days
            try:
                days = int(date_value.split('-')[1])
                start_date = datetime.now() - timedelta(days=days)
                
                # Add date range filter
                start_date_str = start_date.strftime("%Y-%m-%d")
                end_date_str = datetime.now().strftime("%Y-%m-%d")
                date_filter["document_date"] = {"$gte": start_date_str, "$lte": end_date_str}
                
            except (ValueError, IndexError):
                pass
        
        # Handle specific year: 2015 (get ALL documents from that year)
        elif re.match(r'^\d{4}$', date_value):
            date_filter["document_date"] = {"$regex": f"^{date_value}", "$options": "i"}
        
        # Handle year-month: 2015-01 (get documents from specific month)
        elif re.match(r'^\d{4}-\d{2}$', date_value):
            # Add month filter
            date_filter["document_date"] = {"$regex": f"^{date_value}", "$options": "i"}
        
        # Handle full date: 2015-01-31 (get documents from specific date)
        elif re.match(r'^\d{4}-\d{2}-\d{2}$', date_value):
            # Add exact date filter
            date_filter["document_date"] = date_value
        
        return date_filter


