import unittest
import concurrent.futures

# ✏️ Import your test classes normally
from test_desktop_fattal_order import FattalDesktopTests
from test_mobile_fattal import FattalMobileTests

def run_test_case(testcase):
    result = unittest.TextTestRunner(verbosity=2).run(testcase)
    return result

def suite():
    suite = unittest.TestSuite()

    # 👉 Add tests from FattalDesktopTests
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(FattalDesktopTests))

    # 👉 Add tests from FattalMobileTests
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(FattalMobileTests))

    return suite

if __name__ == "__main__":
    all_tests = list(suite())  # 💡 Expand the suite into a list of individual tests

    # Use a ThreadPool to run 3 tests in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(run_test_case, test) for test in all_tests]
        results = [f.result() for f in futures]

    # Summary
    total_tests = sum(r.testsRun for r in results)
    total_errors = sum(len(r.errors) for r in results)
    total_failures = sum(len(r.failures) for r in results)

    print(f"\n=== TEST SUMMARY ===")
    print(f"Total Tests: {total_tests}")
    print(f"Failures: {total_failures}")
    print(f"Errors: {total_errors}")
