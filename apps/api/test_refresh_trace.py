#!/usr/bin/env python3
"""
Test and trace the refresh process to identify issues.
"""

import requests
import json
import time
from datetime import datetime

API_URL = "https://waardhaven-api-backend.onrender.com"

def pretty_print(data, title=""):
    """Pretty print JSON data."""
    if title:
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
    print(json.dumps(data, indent=2))

def test_refresh_flow():
    """Test the complete refresh flow and identify issues."""
    
    print("\n🔍 WAARDHAVEN REFRESH DIAGNOSTIC TRACE")
    print("=" * 60)
    
    # Step 1: Check current data status
    print("\n📊 Step 1: Current Data Status")
    print("-" * 40)
    
    # Check database status
    response = requests.get(f"{API_URL}/api/v1/diagnostics/database-status")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Database Status:")
        print(f"   - Latest price date: {data['tables']['prices'].get('latest_date', 'N/A')}")
        print(f"   - Price count: {data['tables']['prices']['count']}")
        print(f"   - Index values: {data['tables']['index_values']['count']}")
        print(f"   - Assets: {data['tables']['assets']['count']}")
        
        # Calculate days old
        if 'latest_date' in data['tables']['prices']:
            latest = datetime.strptime(data['tables']['prices']['latest_date'], "%Y-%m-%d")
            days_old = (datetime.now() - latest).days
            print(f"   - Data age: {days_old} days old")
            
            if days_old > 3:
                print(f"   ⚠️ Data is stale (>3 days old)")
    else:
        print(f"❌ Failed to get database status: {response.status_code}")
    
    # Step 2: Check refresh requirements
    print("\n📋 Step 2: Refresh Requirements Check")
    print("-" * 40)
    
    response = requests.get(f"{API_URL}/api/v1/diagnostics/refresh-status")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Refresh Status:")
        print(f"   - Days old: {data['prices'].get('days_old', 'N/A')}")
        print(f"   - Needs update: {data['prices'].get('needs_update', False)}")
        print(f"   - Asset count: {data['assets']['count']}")
        print(f"   - Has benchmark: {data['assets']['has_benchmark']}")
        print(f"   - Recommendation: {data['recommendation']}")
    else:
        print(f"❌ Failed to get refresh status: {response.status_code}")
    
    # Step 3: Check API configuration
    print("\n🔧 Step 3: API Configuration Check")
    print("-" * 40)
    
    response = requests.get(f"{API_URL}/api/v1/diagnostics/config-check")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Configuration:")
        print(f"   - TwelveData API Key: {'Configured' if data.get('twelvedata_configured') else 'Missing'}")
        print(f"   - Rate limit: {data.get('rate_limit', 'N/A')} credits/min")
        print(f"   - Refresh mode: {data.get('refresh_mode', 'N/A')}")
        print(f"   - Cache enabled: {data.get('cache_enabled', False)}")
    else:
        print(f"⚠️ Config check endpoint not available")
    
    # Step 4: Test minimal refresh first
    print("\n🧪 Step 4: Testing Minimal Refresh (Safe Test)")
    print("-" * 40)
    
    response = requests.post(f"{API_URL}/api/v1/manual/minimal-refresh")
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'SUCCESS':
            print(f"✅ Minimal refresh succeeded:")
            for step in data.get('steps', []):
                print(f"   - {step['step']}: {step}")
        else:
            print(f"❌ Minimal refresh failed:")
            print(f"   Error: {data.get('error', 'Unknown')}")
            if 'traceback' in data:
                print(f"\n   Traceback:\n{data['traceback']}")
    else:
        print(f"❌ Minimal refresh request failed: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
    
    # Step 5: Attempt smart refresh
    print("\n🚀 Step 5: Attempting Smart Refresh")
    print("-" * 40)
    
    print("Triggering smart refresh in 'minimal' mode...")
    response = requests.post(f"{API_URL}/api/v1/manual/smart-refresh?mode=minimal")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {data.get('status')}")
        print(f"Message: {data.get('message')}")
        
        if data.get('status') == 'SMART_REFRESH_STARTED':
            print("✅ Refresh started in background")
            print("   Waiting 30 seconds for completion...")
            
            # Wait and check progress
            for i in range(6):
                time.sleep(5)
                print(f"   Checking progress... ({(i+1)*5}s)")
                
                # Check if refresh completed
                response = requests.get(f"{API_URL}/api/v1/diagnostics/database-status")
                if response.status_code == 200:
                    check_data = response.json()
                    new_latest = check_data['tables']['prices'].get('latest_date')
                    if new_latest and new_latest != data['tables']['prices'].get('latest_date'):
                        print(f"   ✅ Data updated! New latest date: {new_latest}")
                        break
            else:
                print("   ⚠️ No update detected after 30 seconds")
        else:
            print(f"⚠️ Unexpected status: {data}")
    else:
        print(f"❌ Smart refresh request failed: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
    
    # Step 6: Final status check
    print("\n📈 Step 6: Final Status Check")
    print("-" * 40)
    
    response = requests.get(f"{API_URL}/api/v1/diagnostics/database-status")
    if response.status_code == 200:
        data = response.json()
        final_latest = data['tables']['prices'].get('latest_date', 'N/A')
        print(f"Final data status:")
        print(f"   - Latest price date: {final_latest}")
        
        if final_latest != 'N/A':
            latest = datetime.strptime(final_latest, "%Y-%m-%d")
            days_old = (datetime.now() - latest).days
            print(f"   - Data age: {days_old} days")
            
            if days_old == 0:
                print(f"   ✅ Data is current!")
            elif days_old <= 1:
                print(f"   ✅ Data is fresh (1 day old)")
            elif days_old <= 3:
                print(f"   ⚠️ Data is getting stale ({days_old} days old)")
            else:
                print(f"   ❌ Data is stale ({days_old} days old)")
    
    # Step 7: Diagnose common issues
    print("\n🔎 Step 7: Common Issue Diagnosis")
    print("-" * 40)
    
    issues = []
    
    # Check for API key issues
    response = requests.get(f"{API_URL}/api/v1/diagnostics/test-refresh")
    if response.status_code == 200:
        data = response.json()
        if 'error' in data and 'API key' in data.get('error', ''):
            issues.append("API Key issue: TwelveData API key might be invalid or missing")
        if 'rate' in data.get('error', '').lower():
            issues.append("Rate limiting: API rate limit exceeded")
    
    if issues:
        print("⚠️ Potential issues detected:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print("✅ No obvious issues detected")
    
    print("\n" + "="*60)
    print("Diagnostic trace complete!")

if __name__ == "__main__":
    test_refresh_flow()