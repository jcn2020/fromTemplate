
#!/usr/bin/env python3

import os
import sys
import logging
import time
import json
import requests 
from datetime import datetime, timedelta 

from st2common.runners.base_action import Action 


class ListIncidents_REST_call(Action):
    def run(self, team_id, team_key): 
        """
        List acknowledged incidents based on the provided parameters.
        """
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Set up instance variables
        self.team_id = team_id
        self.team_key = team_key
        self.base_url = "https://api.pagerduty.com/incidents"
        self.headers = {
            'Authorization': f"Token token={self.team_key}",
            'Accept': 'application/vnd.pagerduty+json;version=2',
            'Content-Type': 'application/json'
        }
        
        # Calculate date range (last 7 days)
        since = (datetime.now() - timedelta(days=7)).isoformat()
        
        self.params = {
            'team_ids[]': self.team_id,
            'statuses[]': ['acknowledged'],  # Only get acknowledged incidents
            'since': since,
            'sort_by': 'created_at:desc',
            'limit': 100,
            'include[]': ['teams', 'assignees', 'services']
        }

        try:
            self.logger.info(f"Fetching acknowledged incidents for team {self.team_id}")
            
            response = requests.get(
                url=self.base_url, 
                params=self.params,
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()  # Raise an error for HTTP errors
            
            data = response.json()
            incidents = data.get('incidents', [])
            
            # Process and display incidents
            processed_incidents = []
            for incident in incidents:
                processed_incident = {
                    'id': incident.get('id'),
                    'title': incident.get('title'),
                    'status': incident.get('status'),
                    'created_at': incident.get('created_at'),
                    'acknowledged_at': incident.get('last_status_change_at'),
                    'urgency': incident.get('urgency'),
                    'service': incident.get('service', {}).get('summary'),
                    'html_url': incident.get('html_url')
                }
                processed_incidents.append(processed_incident)
                
                # Print incident details
                print(f"ID: {incident.get('id')} - {incident.get('title')}")
                print(f"  Status: {incident.get('status')}")
                print(f"  Service: {incident.get('service', {}).get('summary')}")
                print(f"  Created: {incident.get('created_at')}")
                print(f"  URL: {incident.get('html_url')}")
                print("-" * 50)
            
            result = {
                'success': True,
                'total_incidents': len(processed_incidents),
                'team_id': self.team_id,
                'incidents': processed_incidents
            }
            
            self.logger.info(f"Successfully retrieved {len(processed_incidents)} acknowledged incidents")
            return result
            
        except requests.RequestException as e:
            error_msg = f"Error fetching incidents: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'total_incidents': 0,
                'incidents': []
            }
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            self.logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'total_incidents': 0,
                'incidents': []
            }