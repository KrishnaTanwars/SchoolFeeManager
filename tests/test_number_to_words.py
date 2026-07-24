"""
Unit Tests for Indian Currency Number to Words Converter.
"""

import unittest
from utils.number_to_words import number_to_words_indian

class TestNumberToWords(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(number_to_words_indian(0), "Zero Rupees Only")

    def test_basic_rupees(self):
        self.assertEqual(number_to_words_indian(2500), "Two Thousand Five Hundred Rupees Only")

    def test_lakhs(self):
        self.assertEqual(number_to_words_indian(154250), "One Lakh Fifty Four Thousand Two Hundred Fifty Rupees Only")

    def test_crores(self):
        self.assertEqual(number_to_words_indian(12345678), "One Crore Twenty Three Lakh Forty Five Thousand Six Hundred Seventy Eight Rupees Only")

    def test_paise(self):
        self.assertEqual(number_to_words_indian(500.50), "Five Hundred Rupees and Fifty Paise Only")

if __name__ == "__main__":
    unittest.main()
