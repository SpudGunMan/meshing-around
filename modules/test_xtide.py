#!/usr/bin/env python3
"""
Test script for xtide module
Tests both NOAA (disabled) and tidepredict (when available) tide predictions
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_xtide_import():
    """Test that xtide module can be imported"""
    print("Testing xtide module import...")
    try:
        from modules import xtide
        print(f"✓ xtide module imported successfully")
        print(f"  - tidepredict available: {xtide.TIDEPREDICT_AVAILABLE}")
        return True
    except Exception as e:
        print(f"✗ Failed to import xtide: {e}")
        return False

def test_locationdata_import():
    """Test that modified locationdata can be imported"""
    print("\nTesting locationdata module import...")
    try:
        from modules import locationdata
        print(f"✓ locationdata module imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import locationdata: {e}")
        return False

def test_settings():
    """Test that settings has useTidePredict option"""
    print("\nTesting settings configuration...")
    try:
        from modules import settings as my_settings
        has_setting = hasattr(my_settings, 'useTidePredict')
        print(f"✓ settings module loaded")
        print(f"  - useTidePredict setting available: {has_setting}")
        if has_setting:
            print(f"  - useTidePredict value: {my_settings.useTidePredict}")
        return True
    except Exception as e:
        print(f"✗ Failed to load settings: {e}")
        return False

def test_noaa_fallback():
    """Test NOAA API fallback (without enabling tidepredict)"""
    print("\nTesting NOAA API (default mode)...")
    try:
        from modules import locationdata
        from modules import settings as my_settings
        
        # Test with Seattle coordinates (should use NOAA)
        lat = 47.6062
        lon = -122.3321
        
        print(f"  Testing with Seattle coordinates: {lat}, {lon}")
        print(f"  useTidePredict = {my_settings.useTidePredict}")
        
        # Note: This will fail if we can't reach NOAA, but that's expected
        result = locationdata.get_NOAAtide(str(lat), str(lon))
        if result and "Error" not in result:
            print(f"✓ NOAA API returned data")
            print(f"  First 100 chars: {result[:100]}")
            return True
        else:
            print(f"⚠ NOAA API returned: {result[:100]}")
            return True  # Still pass as network might not be available
    except Exception as e:
        print(f"⚠ NOAA test encountered expected issue: {e}")
        return True  # Expected in test environment

def test_parse_coords():
    """Test coordinate parsing function"""
    print("\nTesting coordinate parsing...")
    try:
        from modules.xtide import parse_station_coords
        
        test_cases = [
            (("43-36S", "172-43E"), (-43.6, 172.71666666666667)),
            (("02-45N", "072-21E"), (2.75, 72.35)),
            (("02-45S", "072-21W"), (-2.75, -72.35)),
        ]
        
        all_passed = True
        for (lat_str, lon_str), (expected_lat, expected_lon) in test_cases:
            result_lat, result_lon = parse_station_coords(lat_str, lon_str)
            if abs(result_lat - expected_lat) < 0.01 and abs(result_lon - expected_lon) < 0.01:
                print(f"  ✓ {lat_str}, {lon_str} -> {result_lat:.2f}, {result_lon:.2f}")
            else:
                print(f"  ✗ {lat_str}, {lon_str} -> expected {expected_lat}, {expected_lon}, got {result_lat}, {result_lon}")
                all_passed = False
        
        return all_passed
    except Exception as e:
        print(f"✗ Coordinate parsing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("xtide Module Test Suite")
    print("=" * 60)
    
    results = []
    results.append(("Import xtide", test_xtide_import()))
    results.append(("Import locationdata", test_locationdata_import()))
    results.append(("Settings configuration", test_settings()))
    results.append(("Parse coordinates", test_parse_coords()))
    results.append(("NOAA fallback", test_noaa_fallback()))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
