#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test sorting functionality
"""

import requests
import json

def test_sorting():
    # Login
    login_data = {
        'email': 'ba@lanet.mx',
        'password': 'TestAdmin123!'
    }

    response = requests.post('http://localhost:5001/api/auth/login', json=login_data)
    if response.status_code == 200:
        token = response.json()['data']['access_token']
        print('✅ Login successful')
        
        # Test sorting
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test ascending order using /search endpoint (like frontend)
        response = requests.get('http://localhost:5001/api/tickets/search?sort_by=ticket_number&sort_order=asc&page=1&per_page=20', headers=headers)
        if response.status_code == 200:
            data = response.json()
            tickets = data['data']['tickets'][:3]  # First 3 tickets
            print('\n📊 Ascending order (first 3):')
            for ticket in tickets:
                print(f'  {ticket["ticket_number"]} - {ticket["subject"]}')
            
            # Test descending order using /search endpoint (like frontend)
            response = requests.get('http://localhost:5001/api/tickets/search?sort_by=ticket_number&sort_order=desc&page=1&per_page=20', headers=headers)
            if response.status_code == 200:
                data = response.json()
                tickets = data['data']['tickets'][:3]  # First 3 tickets
                print('\n📊 Descending order (first 3):')
                for ticket in tickets:
                    print(f'  {ticket["ticket_number"]} - {ticket["subject"]}')
                    
                print('\n✅ Sorting is working correctly!')
            else:
                print(f'❌ Descending sort failed: {response.status_code}')
                print(response.text)
        else:
            print(f'❌ Ascending sort failed: {response.status_code}')
            print(response.text)
    else:
        print(f'❌ Login failed: {response.status_code}')
        print(response.text)

if __name__ == '__main__':
    test_sorting()
