"""
Pagination utilities for ProjectMeats API.

Provides enhanced pagination classes that match PowerApps data loading patterns.
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict


class PowerAppsPagination(PageNumberPagination):
    """
    Custom pagination class that provides PowerApps-like pagination metadata.
    
    Includes additional metadata that would be useful for frontend components
    and matches the pagination patterns from PowerApps galleries and forms.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        """
        Return a paginated style Response with enhanced metadata.
        
        Includes PowerApps-style pagination info that helps frontend
        components render pagination controls effectively.
        """
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('has_next', self.page.has_next()),
            ('has_previous', self.page.has_previous()),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),
            # Additional metadata for PowerApps-like UI components
            ('pagination_info', {
                'start_index': self.page.start_index(),
                'end_index': self.page.end_index(),
                'showing': f"{self.page.start_index()}-{self.page.end_index()} of {self.page.paginator.count}",
                'has_data': self.page.paginator.count > 0,
                'is_first_page': not self.page.has_previous(),
                'is_last_page': not self.page.has_next(),
            })
        ]))


class SmallResultsPagination(PageNumberPagination):
    """
    Pagination class for smaller result sets (like dropdown options).
    
    Used for lookup fields and reference data that should load quickly
    but still benefit from pagination.
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class LargeResultsPagination(PageNumberPagination):
    """
    Pagination class for large datasets with more aggressive pagination.
    
    Used for bulk data exports or heavy reporting queries.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50