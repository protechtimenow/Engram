#!/usr/bin/env python3
"""
Consolidate All Test Results
Aggregates all test result JSON files into a comprehensive final report
"""

import json
from pathlib import Path
from datetime import datetime

def load_test_results(filename):
    """Load test results from JSON file"""
    path = Path(filename)
    if not path.exists():
        return None
    
    try:
        data = json.loads(path.read_text())
        return data
    except Exception as e:
        print(f"Warning: Could not load {filename}: {e}")
        return None

def extract_stats(data):
    """Extract test statistics from various JSON formats"""
    if not data or not isinstance(data, dict):
        return None
    
    # Try different JSON structures
    if 'tests' in data and 'passed' in data:
        return {
            'total': data['tests'],
            'passed': data['passed'],
            'failed': data.get('failed', 0),
            'skipped': data.get('skipped', 0)
        }
    elif 'total_tests' in data:
        return {
            'total': data['total_tests'],
            'passed': data.get('passed', 0),
            'failed': data.get('failed', 0),
            'skipped': data.get('skipped', 0)
        }
    elif 'summary' in data and isinstance(data['summary'], dict):
        summary = data['summary']
        return {
            'total': summary.get('total', 0),
            'passed': summary.get('passed', 0),
            'failed': summary.get('failed', 0),
            'skipped': summary.get('skipped', 0)
        }
    
    return None

def main():
    """Main consolidation function"""
    
    # List of all test result files
    test_files = [
        'simple_test_results.json',
        'test_results.json',
        'thorough_test_results.json',
        'edge_case_test_results.json',
        'advanced_dependency_test_results.json',
        'soak_endurance_test_results.json',
        'live_trading_simulation_test_results.json',
        'interactive_test_results.json'
    ]
    
    consolidated = {
        'timestamp': datetime.now().isoformat(),
        'test_suites': {},
        'summary': {
            'total_suites': 0,
            'total_tests': 0,
            'total_passed': 0,
            'total_failed': 0,
            'total_skipped': 0,
            'overall_pass_rate': 0.0
        }
    }
    
    print("=" * 80)
    print("CONSOLIDATING ALL TEST RESULTS")
    print("=" * 80)
    print()
    
    for filename in test_files:
        data = load_test_results(filename)
        if not data:
            continue
        
        stats = extract_stats(data)
        if not stats:
            continue
        
        # Add to consolidated results
        consolidated['test_suites'][filename] = stats
        consolidated['summary']['total_suites'] += 1
        consolidated['summary']['total_tests'] += stats['total']
        consolidated['summary']['total_passed'] += stats['passed']
        consolidated['summary']['total_failed'] += stats['failed']
        consolidated['summary']['total_skipped'] += stats['skipped']
        
        # Print suite results
        pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
        status = "✅ PASS" if pass_rate >= 80 else "⚠️ PARTIAL" if pass_rate >= 60 else "❌ FAIL"
        print(f"{filename:45} {stats['passed']:3}/{stats['total']:3} ({pass_rate:5.1f}%) {status}")
    
    # Calculate overall pass rate
    total = consolidated['summary']['total_tests']
    passed = consolidated['summary']['total_passed']
    if total > 0:
        consolidated['summary']['overall_pass_rate'] = round(passed / total * 100, 2)
    
    print()
    print("=" * 80)
    print("CONSOLIDATED SUMMARY")
    print("=" * 80)
    print(f"Total Test Suites:  {consolidated['summary']['total_suites']}")
    print(f"Total Tests:        {consolidated['summary']['total_tests']}")
    print(f"Total Passed:       {consolidated['summary']['total_passed']}")
    print(f"Total Failed:       {consolidated['summary']['total_failed']}")
    print(f"Total Skipped:      {consolidated['summary']['total_skipped']}")
    print(f"Overall Pass Rate:  {consolidated['summary']['overall_pass_rate']:.2f}%")
    print()
    
    # Determine overall status
    pass_rate = consolidated['summary']['overall_pass_rate']
    if pass_rate >= 90:
        status = "✅ EXCELLENT - PRODUCTION READY"
    elif pass_rate >= 80:
        status = "✅ GOOD - PRODUCTION READY"
    elif pass_rate >= 70:
        status = "⚠️ ACCEPTABLE - REVIEW FAILURES"
    else:
        status = "❌ NEEDS IMPROVEMENT"
    
    print(f"Overall Status:     {status}")
    print("=" * 80)
    
    # Save consolidated results
    output_file = Path('CONSOLIDATED_TEST_RESULTS.json')
    output_file.write_text(json.dumps(consolidated, indent=2))
    print(f"\n✅ Consolidated results saved to {output_file}")
    
    return consolidated

if __name__ == '__main__':
    main()
