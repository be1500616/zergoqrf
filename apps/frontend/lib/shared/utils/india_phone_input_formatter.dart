import 'package:flutter/services.dart';

/// Custom TextInputFormatter for India phone numbers.
///
/// Enforces the format: +91XXXXXXXXXX (country code + 10 digits)
/// - Automatically prefixes "+91" (non-editable)
/// - Restricts input to exactly 10 digits after the country code
/// - Prevents deletion of the country code prefix
class IndiaPhoneInputFormatter extends TextInputFormatter {
  static const String _countryCode = '+91';
  static const int _maxDigits = 10;

  @override
  TextEditingValue formatEditUpdate(
    TextEditingValue oldValue,
    TextEditingValue newValue,
  ) {
    // Get the new text
    String newText = newValue.text;

    // If the text is empty or being cleared, reset to country code
    if (newText.isEmpty) {
      return TextEditingValue(
        text: _countryCode,
        selection: TextSelection.collapsed(offset: _countryCode.length),
      );
    }

    // Prevent deletion of country code
    if (!newText.startsWith(_countryCode)) {
      return TextEditingValue(
        text: _countryCode,
        selection: TextSelection.collapsed(offset: _countryCode.length),
      );
    }

    // Extract digits after country code
    String digitsOnly = newText.substring(_countryCode.length).replaceAll(RegExp(r'\D'), '');

    // Limit to maximum digits
    if (digitsOnly.length > _maxDigits) {
      digitsOnly = digitsOnly.substring(0, _maxDigits);
    }

    // Construct the formatted text
    String formattedText = _countryCode + digitsOnly;

    // Calculate cursor position
    int cursorPosition = formattedText.length;
    
    // If user is typing, place cursor at the end
    // If user is deleting, maintain cursor position
    if (newValue.selection.baseOffset < formattedText.length) {
      cursorPosition = newValue.selection.baseOffset;
      // Ensure cursor doesn't go before country code
      if (cursorPosition < _countryCode.length) {
        cursorPosition = _countryCode.length;
      }
    }

    return TextEditingValue(
      text: formattedText,
      selection: TextSelection.collapsed(offset: cursorPosition),
    );
  }

  /// Helper method to check if a phone number is complete
  static bool isComplete(String phoneNumber) {
    if (!phoneNumber.startsWith(_countryCode)) return false;
    String digits = phoneNumber.substring(_countryCode.length);
    return digits.length == _maxDigits && RegExp(r'^\d+$').hasMatch(digits);
  }

  /// Helper method to format a phone number for display
  static String format(String phoneNumber) {
    if (!phoneNumber.startsWith(_countryCode)) {
      phoneNumber = _countryCode + phoneNumber.replaceAll(RegExp(r'\D'), '');
    }
    String digits = phoneNumber.substring(_countryCode.length).replaceAll(RegExp(r'\D'), '');
    if (digits.length > _maxDigits) {
      digits = digits.substring(0, _maxDigits);
    }
    return _countryCode + digits;
  }
}

