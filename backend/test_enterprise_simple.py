#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test for enterprise reporting functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.reports.enterprise_columns import ENTERPRISE_COLUMNS, build_enterprise_query

def test_enterprise_columns():
    """Test enterprise columns definition"""
    print("🧪 Testing Enterprise Columns...")
    
    # Test column count
    print(f"✅ Total columns defined: {len(ENTERPRISE_COLUMNS)}")
    
    # Test categories
    categories = set()
    for column_data in ENTERPRISE_COLUMNS.values():
        categories.add(column_data['category'])
    
    print(f"✅ Categories: {', '.join(sorted(categories))}")
    
    # Test basic columns
    basic_columns = [k for k, v in ENTERPRISE_COLUMNS.items() if v['category'] == 'basic']
    print(f"✅ Basic columns: {len(basic_columns)}")
    
    # Test SLA columns
    sla_columns = [k for k, v in ENTERPRISE_COLUMNS.items() if v['category'] == 'sla']
    print(f"✅ SLA columns: {len(sla_columns)}")
    
    return True

def test_query_building():
    """Test SQL query building"""
    print("\n🧪 Testing Query Building...")
    
    # Test basic query
    test_columns = ['ticket_id', 'created_at', 'subject', 'status']
    query = build_enterprise_query(test_columns, limit=10)
    
    if query:
        print("✅ Basic query generated successfully")
        print(f"Query preview: {query[:100]}...")
    else:
        print("❌ Failed to generate basic query")
        return False
    
    # Test query with filters
    filters = {
        'date_from': '2024-01-01',
        'status': ['Abierto', 'En Progreso']
    }
    
    filtered_query = build_enterprise_query(test_columns, filters, limit=5)
    
    if filtered_query and 'WHERE' in filtered_query:
        print("✅ Filtered query generated successfully")
    else:
        print("❌ Failed to generate filtered query")
        return False
    
    return True

def test_column_metadata():
    """Test column metadata"""
    print("\n🧪 Testing Column Metadata...")
    
    # Test required fields
    required_fields = ['display_name', 'sql_expression', 'data_type', 'category']
    
    for column_key, column_data in ENTERPRISE_COLUMNS.items():
        for field in required_fields:
            if field not in column_data:
                print(f"❌ Column {column_key} missing required field: {field}")
                return False
    
    print("✅ All columns have required metadata")
    
    # Test data types
    valid_types = ['text', 'number', 'datetime', 'boolean']
    for column_key, column_data in ENTERPRISE_COLUMNS.items():
        if column_data['data_type'] not in valid_types:
            print(f"❌ Column {column_key} has invalid data type: {column_data['data_type']}")
            return False
    
    print("✅ All columns have valid data types")
    
    return True

def main():
    """Run all tests"""
    print("🚀 ENTERPRISE REPORTING SYSTEM - SIMPLE TEST")
    print("=" * 50)
    
    tests = [
        test_enterprise_columns,
        test_query_building,
        test_column_metadata
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test {test.__name__} failed")
        except Exception as e:
            print(f"❌ Test {test.__name__} error: {e}")
    
    print("\n" + "=" * 50)
    print(f"🎯 RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Enterprise reporting system is ready.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
