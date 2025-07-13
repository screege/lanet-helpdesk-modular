#!/usr/bin/env python3
"""
Test script to investigate ticket display limitations
"""

import psycopg2
import sys
import os

def test_ticket_retrieval():
    """Test ticket retrieval to understand display limitations"""
    try:
        # Connect to database
        conn = psycopg2.connect(
            host='localhost',
            database='lanet_helpdesk',
            user='postgres',
            password='Poikl55+*'
        )
        
        cur = conn.cursor()
        
        # Test the exact query used by the service
        query = """
        SELECT t.ticket_id, t.ticket_number, t.client_id, t.site_id, t.asset_id,
               t.created_by, t.assigned_to, t.subject, t.description, t.affected_person,
               t.affected_person_phone, t.affected_person_contact, t.notification_email, 
               t.additional_emails, t.priority, t.category_id,
               t.status, t.channel, t.is_email_originated, t.from_email,
               t.email_message_id, t.email_thread_id, t.approval_status,
               t.approved_by, t.approved_at, t.created_at, t.updated_at,
               t.assigned_at, t.resolved_at, t.closed_at, t.resolution_notes,
               c.name as client_name,
               s.name as site_name,
               cat.name as category_name,
               creator.name as created_by_name,
               assignee.name as assigned_to_name
        FROM tickets t
        LEFT JOIN clients c ON t.client_id = c.client_id
        LEFT JOIN sites s ON t.site_id = s.site_id
        LEFT JOIN categories cat ON t.category_id = cat.category_id
        LEFT JOIN users creator ON t.created_by = creator.user_id
        LEFT JOIN users assignee ON t.assigned_to = assignee.user_id
        WHERE t.is_active = true
        ORDER BY t.created_at DESC
        LIMIT 20 OFFSET 0
        """
        
        cur.execute(query)
        tickets = cur.fetchall()
        
        print(f'=== TICKET RETRIEVAL TEST ===')
        print(f'Found {len(tickets)} tickets with LIMIT 20')
        print()
        print('First 10 tickets:')
        for i, ticket in enumerate(tickets[:10]):
            print(f'{i+1}. {ticket[1]} - {ticket[7][:50]}... - {ticket[25]}')  # ticket_number, subject, created_at
        
        # Test with higher limit
        cur.execute(query.replace('LIMIT 20 OFFSET 0', 'LIMIT 50 OFFSET 0'))
        tickets_50 = cur.fetchall()
        print(f'\nFound {len(tickets_50)} tickets with LIMIT 50')
        
        # Test without limit
        cur.execute(query.replace('LIMIT 20 OFFSET 0', ''))
        all_tickets = cur.fetchall()
        print(f'Found {len(all_tickets)} tickets without limit')
        
        # Check if there are tickets with numbers > 131
        print('\nTickets with numbers containing 13[2-9]:')
        high_tickets = []
        for ticket in all_tickets:
            ticket_num = ticket[1]  # ticket_number
            if any(num in ticket_num for num in ['132', '133', '134', '135', '136', '137', '138', '139']):
                high_tickets.append((ticket_num, ticket[25]))
        
        for ticket_num, created_at in high_tickets:
            print(f'  {ticket_num} - {created_at}')
        
        print(f'\nTotal high-numbered tickets found: {len(high_tickets)}')
        
        # Test basic tickets endpoint query
        print('\n=== BASIC ENDPOINT QUERY TEST ===')
        basic_query = "SELECT * FROM tickets ORDER BY created_at DESC LIMIT 50"
        cur.execute(basic_query)
        basic_tickets = cur.fetchall()
        print(f'Basic endpoint would return {len(basic_tickets)} tickets')
        
        if basic_tickets:
            print('First 5 from basic endpoint:')
            for i, ticket in enumerate(basic_tickets[:5]):
                # ticket_number is at index 1 in the basic query
                print(f'{i+1}. {ticket[1]} - {ticket[25]}')  # ticket_number, created_at
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f'Error: {e}')
        return False
    
    return True

if __name__ == '__main__':
    test_ticket_retrieval()
