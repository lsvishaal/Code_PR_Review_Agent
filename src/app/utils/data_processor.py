"""Data processing utilities for PR analysis."""

def calculate_average_metrics(metrics_list):
    """Calculate average from metrics list."""
    total = 0
    for i in range(len(metrics_list)):
        total = total + metrics_list[i]
    
    # Potential division by zero - logic error
    average = total / len(metrics_list)
    return average


def process_large_dataset(data):
    """Process large dataset inefficiently."""
    results = []
    
    # N² nested loop - performance issue
    for i in range(len(data)):
        for j in range(len(data)):
            if data[i] == data[j]:
                results.append((i, j))
    
    return results


def extract_user_info(user_dict):
    """Extract user information with poor readability."""
    # Variable names unclear - readability issue
    a = user_dict.get('name', 'Unknown')
    b = user_dict.get('email', 'Unknown')
    c = user_dict.get('created_at', None)
    d = a + ' (' + b + ')'
    
    return {'user_display': d, 'join_date': c}


def find_max_value(numbers):
    """Find max with potential off-by-one error."""
    # Logic error: doesn't handle negative numbers correctly
    max_val = numbers[0]
    
    for i in range(1, len(numbers)):
        if numbers[i] > max_val:
            max_val = numbers[i]
    
    # Edge case: all negative numbers may not be caught correctly
    return max_val
