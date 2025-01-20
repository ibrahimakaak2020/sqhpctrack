# Pagination
ITEMS_PER_PAGE = 10
MAX_PAGE_LINKS = 5

# Filtering
FILTER_OPTIONS = {
    'equipment_model': {
        'type': ['Computer', 'Printer', 'Network', 'Other'],
        'status': ['Active', 'Inactive'],
        'date_range': ['Today', 'This Week', 'This Month', 'This Year', 'Custom']
    },
    'location': {
        'status': ['Active', 'Inactive'],
        'capacity': ['Empty', 'Available', 'Full']
    }
}

# Chart Types
CHART_TYPES = {
    'bar': 'Bar Chart',
    'pie': 'Pie Chart',
    'line': 'Line Chart'
} 