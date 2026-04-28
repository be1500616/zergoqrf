/// Validation utilities for form fields.
///
/// Provides reusable validators for common input types like email, password,
/// phone numbers, and OTP codes.
library;

/// Email validation utility.
class EmailValidator {
  /// Validates an email address.
  ///
  /// Returns null if valid, error message if invalid.
  static String? validate(String? value) {
    if (value == null || value.isEmpty) {
      return 'Email is required';
    }

    // Basic email regex pattern
    final emailRegex = RegExp(
      r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    );

    if (!emailRegex.hasMatch(value)) {
      return 'Please enter a valid email address';
    }

    return null;
  }
}

/// Password validation utility.
class PasswordValidator {
  /// Validates a password.
  ///
  /// Returns null if valid, error message if invalid.
  /// Requirements:
  /// - At least 8 characters
  /// - Contains at least one uppercase letter
  /// - Contains at least one lowercase letter
  /// - Contains at least one number
  static String? validate(String? value, {bool requireStrong = false}) {
    if (value == null || value.isEmpty) {
      return 'Password is required';
    }

    if (value.length < 8) {
      return 'Password must be at least 8 characters';
    }

    if (requireStrong) {
      // Check for uppercase
      if (!value.contains(RegExp(r'[A-Z]'))) {
        return 'Password must contain at least one uppercase letter';
      }

      // Check for lowercase
      if (!value.contains(RegExp(r'[a-z]'))) {
        return 'Password must contain at least one lowercase letter';
      }

      // Check for number
      if (!value.contains(RegExp(r'[0-9]'))) {
        return 'Password must contain at least one number';
      }
    }

    return null;
  }

  /// Validates password confirmation.
  static String? validateConfirmation(
    String? value,
    String? originalPassword,
  ) {
    if (value == null || value.isEmpty) {
      return 'Please confirm your password';
    }

    if (value != originalPassword) {
      return 'Passwords do not match';
    }

    return null;
  }
}

/// Phone number validation utility for India phone numbers.
class PhoneValidator {
  static const String _indiaCountryCode = '+91';
  static const int _indiaPhoneDigits = 10;

  /// Validates an India phone number.
  ///
  /// Returns null if valid, error message if invalid.
  /// Expects format: +91XXXXXXXXXX (country code + 10 digits)
  static String? validate(String? value) {
    if (value == null || value.isEmpty) {
      return 'Phone number is required';
    }

    // Remove spaces and dashes
    final cleaned = value.replaceAll(RegExp(r'[\s-]'), '');

    // Check if it starts with +91
    if (!cleaned.startsWith(_indiaCountryCode)) {
      return 'Phone number must start with $_indiaCountryCode';
    }

    // Extract digits after country code
    final digitsOnly = cleaned.substring(_indiaCountryCode.length);

    // Check if it contains only digits
    if (!RegExp(r'^\d+$').hasMatch(digitsOnly)) {
      return 'Phone number must contain only digits';
    }

    // Check if it has exactly 10 digits
    if (digitsOnly.length != _indiaPhoneDigits) {
      return 'Phone number must have exactly $_indiaPhoneDigits digits after $_indiaCountryCode';
    }

    return null;
  }

  /// Formats a phone number for display.
  static String format(String phone) {
    // Remove all non-digit characters except +
    final cleaned = phone.replaceAll(RegExp(r'[^\d+]'), '');

    // Ensure it starts with +91
    if (!cleaned.startsWith(_indiaCountryCode)) {
      final digitsOnly = cleaned.replaceAll(RegExp(r'\D'), '');
      return _indiaCountryCode + digitsOnly;
    }

    return cleaned;
  }
}

/// OTP validation utility.
class OTPValidator {
  /// Validates an OTP code.
  ///
  /// Returns null if valid, error message if invalid.
  static String? validate(String? value, {int length = 6}) {
    if (value == null || value.isEmpty) {
      return 'OTP code is required';
    }

    if (value.length != length) {
      return 'OTP code must be $length digits';
    }

    if (!RegExp(r'^\d+$').hasMatch(value)) {
      return 'OTP code must contain only digits';
    }

    return null;
  }
}

/// Name validation utility.
class NameValidator {
  /// Validates a name.
  ///
  /// Returns null if valid, error message if invalid.
  static String? validate(String? value, {bool required = false}) {
    if (value == null || value.isEmpty) {
      return required ? 'Name is required' : null;
    }

    if (value.trim().length < 2) {
      return 'Name must be at least 2 characters';
    }

    if (value.trim().length > 50) {
      return 'Name must be less than 50 characters';
    }

    // Check if name contains only letters, spaces, and common name characters
    if (!RegExp(r"^[a-zA-Z\s\-'\.]+$").hasMatch(value)) {
      return 'Name can only contain letters, spaces, hyphens, and apostrophes';
    }

    return null;
  }
}

/// Restaurant code validation utility.
class RestaurantCodeValidator {
  /// Validates a restaurant code.
  ///
  /// Returns null if valid, error message if invalid.
  static String? validate(String? value) {
    if (value == null || value.isEmpty) {
      return 'Restaurant code is required';
    }

    // Convert to uppercase for validation
    final code = value.toUpperCase();

    // Check length (typically 6-8 characters)
    if (code.length < 6 || code.length > 8) {
      return 'Restaurant code must be 6-8 characters';
    }

    // Check if it contains only alphanumeric characters
    if (!RegExp(r'^[A-Z0-9]+$').hasMatch(code)) {
      return 'Restaurant code can only contain letters and numbers';
    }

    return null;
  }

  /// Formats a restaurant code (converts to uppercase).
  static String format(String code) {
    return code.toUpperCase().replaceAll(RegExp(r'[^A-Z0-9]'), '');
  }
}

/// Generic required field validator.
class RequiredValidator {
  /// Validates that a field is not empty.
  static String? validate(String? value, String fieldName) {
    if (value == null || value.trim().isEmpty) {
      return '$fieldName is required';
    }
    return null;
  }
}

/// Restaurant name validation utility.
class RestaurantNameValidator {
  /// Validates a restaurant name.
  ///
  /// Returns null if valid, error message if invalid.
  static String? validate(String? value) {
    if (value == null || value.trim().isEmpty) {
      return 'Restaurant name is required';
    }

    final trimmedName = value.trim();

    if (trimmedName.length < 2) {
      return 'Restaurant name must be at least 2 characters';
    }

    if (trimmedName.length > 100) {
      return 'Restaurant name must be less than 100 characters';
    }

    // Check for valid characters (letters, numbers, spaces, and common punctuation)
    final validNameRegex = RegExp(r"^[a-zA-Z0-9\s\-\.\&']+$");
    if (!validNameRegex.hasMatch(trimmedName)) {
      return 'Restaurant name contains invalid characters';
    }

    return null;
  }
}

/// Restaurant description validation utility.
class RestaurantDescriptionValidator {
  /// Validates a restaurant description.
  ///
  /// Returns null if valid, error message if invalid.
  static String? validate(String? value) {
    if (value == null || value.trim().isEmpty) {
      return null; // Description is optional
    }

    final trimmedDescription = value.trim();

    if (trimmedDescription.length > 500) {
      return 'Description must be less than 500 characters';
    }

    return null;
  }
}

/// URL validation utility.
class UrlValidator {
  /// Validates a URL format.
  ///
  /// Returns null if valid, error message if invalid.
  static String? validate(String? url, {bool isRequired = false}) {
    if (url == null || url.trim().isEmpty) {
      return isRequired ? 'URL is required' : null;
    }

    try {
      final uri = Uri.parse(url.trim());
      if (!uri.hasScheme || (!uri.scheme.startsWith('http'))) {
        return 'Please enter a valid URL (starting with http:// or https://)';
      }
      return null;
    } catch (e) {
      return 'Please enter a valid URL';
    }
  }
}
