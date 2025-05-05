import unittest
from test_desktop_fattal_order import FattalDesktopTests
from test_mobile_fattal import FattalMobileTests
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
    ("FattalMobileTests", "test_mobile_booking_anonymous_user_promo_code")
]

def load_ordered_suite():
    suite = unittest.TestSuite()
    added = set()

    for class_name, test_name in ORDERED_TESTS:
        if (class_name, test_name) not in added:
            if class_name == "FattalDesktopTests":
                suite.addTest(FattalDesktopTests(test_name))
            elif class_name == "FattalMobileTests":
                suite.addTest(FattalMobileTests(test_name))
            added.add((class_name, test_name))

    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(load_ordered_suite())
