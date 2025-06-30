import polars as pl
import traceback

try:
    print("Attempting to import get_base_data...")
    from baseData import get_base_data

    print("Calling get_base_data()...")
    # Get the base data
    base_data = get_base_data()
    print(f"Successfully loaded base data. Shape: {base_data.shape}")

    # Test for tests with periods
    tests_with_periods = ["STAR"]
    for test in tests_with_periods:
        print(f"\nChecking {test} data (with testing periods):")
        # Get all columns containing this test name
        test_columns = [col for col in base_data.columns if test in col]
        if not test_columns:
            print(f"No columns found for {test}")
        else:
            print(f"Found {len(test_columns)} columns for {test}")
            print(f"Sample columns: {test_columns[:5]}")
            # Sample first 3 rows of these columns to verify data
            sample_data = base_data.select(["SSID"] + test_columns).head(3)
            print("Sample data:")
            print(sample_data)

    # Test for tests without periods (ELPAC, CAASPP)
    tests_without_periods = ["ELPAC", "CAASPP"]
    for test in tests_without_periods:
        print(f"\nChecking {test} data (without testing periods):")
        # Get all columns containing this test name
        test_columns = [col for col in base_data.columns if test in col]
        if not test_columns:
            print(f"No columns found for {test}")
        else:
            print(f"Found {len(test_columns)} columns for {test}")
            print(f"Sample columns: {test_columns[:5]}")
            # Sample first 3 rows of these columns to verify data
            sample_data = base_data.select(["SSID"] + test_columns).head(3)
            print("Sample data:")
            print(sample_data)

    # Also test the CAASPP-specific function
    try:
        print("\nChecking casspp_data function:")
        from baseData import casspp_data
        caaspp_data = casspp_data()
        print(f"Successfully loaded CAASPP data. Shape: {caaspp_data.shape}")

        caaspp_columns = [
            col for col in caaspp_data.columns if "CAASPP" in col]
        if not caaspp_columns:
            print("No CAASPP columns found in casspp_data()")
        else:
            print(
                f"Found {len(caaspp_columns)} CAASPP columns in casspp_data()")
            print(f"Sample columns: {caaspp_columns[:5]}")
            # Sample first 3 rows of these columns to verify data
            sample_data = caaspp_data.select(["SSID"] + caaspp_columns).head(3)
            print("Sample data:")
            print(sample_data)
    except Exception as e:
        print(f"Error in casspp_data: {e}")
        traceback.print_exc()

except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
