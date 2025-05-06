import unittest
from test_desktop_fattal_order import FattalDesktopTests
from test_mobile_fattal import FattalMobileTests

# Ordered list of test tuples (class name, test method)
ORDERED_TESTS = [
    # === Priority Order ===
    ("FattalDesktopTests", "test_desktop_anonymous_booking"),
    ("FattalMobileTests", "test_mobile_booking_anonymous_user"),
    ("FattalDesktopTests", "test_desktop_booking_club_member"),
    ("FattalMobileTests", "test_mobile_booking_club_member"),
    ("FattalMobileTests", "test_mobile_booking_anonymous_join_fattal_and_friends"),
    ("FattalMobileTests", "test_mobile_booking_club_member_club_renew_expired"),
    ("FattalMobileTests", "test_mobile_booking_club_member_club_renew_about_to_expire"),
    ("FattalMobileTests", "test_mobile_booking_club_member_11night"),
    ("FattalMobileTests", "test_mobile_booking_fattal_gift1"),
    ("FattalMobileTests", "test_mobile_booking_anonymous_europe"),
    ("FattalMobileTests", "test_mobile_booking_with_club_login_europe"),
    ("FattalMobileTests", "test_mobile_booking_with_club_login_11night_europe"),
    ("FattalMobileTests", "test_mobile_contact_form"),

    # === Remaining Desktop Tests ===
    ("FattalDesktopTests", "test_desktop_booking_anonymous_join_fattal_and_friends"),
    ("FattalDesktopTests", "test_desktop_booking_club_member_eilat_with_flight"),
    ("FattalDesktopTests", "test_desktop_booking_anonymous_region_eilat"),
    ("FattalDesktopTests", "test_desktop_booking_anonymous_random_guest_details"),

    # === Remaining Mobile Tests ===
    ("FattalMobileTests", "test_mobile_join_fattal_and_friends_form"),
    ("FattalMobileTests", "test_mobile_booking_eilat_with_flight"),
    ("FattalMobileTests", "test_mobile_booking_anonymous_region_eilat"),
    ("FattalMobileTests", "test_mobile_booking_fattal_gift3"),
    ("FattalMobileTests", "test_mobile_booking_club_member_deals"),
    ("FattalMobileTests", "test_mobile_booking_anonymous_random_guest_details"),
    ("FattalMobileTests", "test_mobile_booking_anonymous_user_promo_code"),
    ("FattalMobileTests", "test_mobile_club_renew_expired_form"),
]

# === Custom Result Class with Live Progress ===
class ProgressTrackingTestResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super(ProgressTrackingTestResult, self).__init__(*args, **kwargs)
        self.success_count = 0
        self.total_tests = 0

    def startTestRun(self):
        self.total_tests = self.test_count  # from custom runner
        super().startTestRun()

    def addSuccess(self, test):
        super().addSuccess(test)
        self.success_count += 1
        self._print_progress()

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._print_progress()

    def addError(self, test, err):
        super().addError(test, err)
        self._print_progress()

    def _print_progress(self):
        print(f"🟢 Progress: {self.success_count}/{self.testsRun} passed out of {self.total_tests}", end="\r")


# === Custom TestRunner to Inject Progress Tracking ===
class ProgressTrackingTestRunner(unittest.TextTestRunner):
    def _makeResult(self):
        result = ProgressTrackingTestResult(self.stream, self.descriptions, self.verbosity)
        result.test_count = self.test_count  # Inject total test count
        return result


# === Load Ordered Test Suite ===
def load_ordered_suite():
    suite = unittest.TestSuite()
    added = set()

    for class_name, test_name in ORDERED_TESTS:
        if (class_name, test_name) in added:
            continue
        if class_name == "FattalDesktopTests":
            suite.addTest(FattalDesktopTests(test_name))
        elif class_name == "FattalMobileTests":
            suite.addTest(FattalMobileTests(test_name))
        added.add((class_name, test_name))

    return suite


# === MAIN ===
if __name__ == "__main__":
    suite = load_ordered_suite()
    total_tests = suite.countTestCases()
    runner = ProgressTrackingTestRunner(verbosity=2)
    runner.test_count = total_tests  # For live progress injection
    result = runner.run(suite)

    print("\n\n🧾 FINAL SUMMARY")
    print("=" * 40)
    print(f"✅ Passed: {result.success_count} / {result.testsRun}")
    print(f"❌ Failures: {len(result.failures)}")
    print(f"💥 Errors:   {len(result.errors)}")
    print("=" * 40)
