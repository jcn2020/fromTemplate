#!/usr/bin/env python3
"""
StackStorm action to format PagerDuty incident data showing ID and Title
"""

import sys
import json


def format_incidents(incidents_data):
    """
    Format incident data to show ID and Title clearly.
    
    Args:
        incidents_data: List of incident dictionaries or JSON string
        
    Returns:
        dict: Formatted incident data with IDs and titles
    """
    
    if isinstance(incidents_data, str):
        try:
            incidents_data = json.loads(incidents_data)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON provided", "success": False}
    
    if not isinstance(incidents_data, list):
        return {"error": "Expected list of incidents", "success": False}
    
    formatted_incidents = []
    
    for incident in incidents_data:
        try:
            formatted = {
                'incident_id': incident.get('id'),
                'incident_number': incident.get('incident_number'),
                'title': incident.get('title'),
                'status': incident.get('status'),
                'urgency': incident.get('urgency', 'unknown'),
                'created_at': incident.get('created_at'),
                'service_name': incident.get('service', {}).get('name', 'Unknown Service')
            }
            
            # Only include if we have the essential fields
            if formatted['incident_id'] and formatted['title']:
                formatted_incidents.append(formatted)
                
        except Exception as e:
            print(f"Warning: Error processing incident: {e}", file=sys.stderr)
            continue
    
    # Create summary
    result = {
        'success': True,
        'total_count': len(formatted_incidents),
        'incidents': formatted_incidents,
        'incident_ids': [inc['incident_id'] for inc in formatted_incidents],
        'titles': [inc['title'] for inc in formatted_incidents],
        'id_title_pairs': [
            {
                'id': inc['incident_id'], 
                'title': inc['title'],
                'status': inc['status']
            } 
            for inc in formatted_incidents
        ]
    }
    
    return result


def main():
    """Main function for command line usage."""
    
    if len(sys.argv) < 2:
        print("Usage: python format_incidents.py <json_file>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    try:
        with open(filename, 'r') as file:
            incidents_data = json.load(file)
        
        result = format_incidents(incidents_data)
        
        if result['success']:
            print(f"\nFound {result['total_count']} incidents:\n")
            print(f"{'ID':<25} {'Status':<15} {'Title'}")
            print("-" * 80)
            
            for incident in result['incidents']:
                title = incident['title'][:45] + "..." if len(incident['title']) > 45 else incident['title']
                print(f"{incident['incident_id']:<25} {incident['status']:<15} {title}")
        else:
            print(f"Error: {result['error']}")
            
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in file '{filename}'")
        sys.exit(1)


if __name__ == "__main__":
    main()
