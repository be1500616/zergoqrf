/// Self-validating form field component.
///
/// This component provides a reusable form field with built-in validation,
/// async validation support, debounced validation, and consistent styling
/// using the existing theme system.
library;

import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_spacing.dart';

/// Self-validating form field with enhanced features.
///
/// This widget wraps Flutter's standard TextFormField with additional
/// validation capabilities including debounced validation, async validation,
/// and real-time feedback using the existing theme system.
class ValidationField extends StatefulWidget {
  /// Creates a validation field.
  const ValidationField({
    super.key,
    required this.controller,
    this.label,
    this.hint,
    this.helperText,
    this.prefixIcon,
    this.suffixIcon,
    this.obscureText = false,
    this.keyboardType,
    this.textInputAction,
    this.maxLines = 1,
    this.maxLength,
    this.enabled = true,
    this.readOnly = false,
    this.autofocus = false,
    this.validator,
    this.asyncValidator,
    this.onChanged,
    this.onSubmitted,
    this.inputFormatters,
    this.debounceDuration = const Duration(milliseconds: 300),
    this.showValidationIcon = true,
    this.autovalidateMode = AutovalidateMode.onUserInteraction,
  });

  /// Text editing controller.
  final TextEditingController controller;

  /// Field label.
  final String? label;

  /// Field hint text.
  final String? hint;

  /// Helper text displayed below the field.
  final String? helperText;

  /// Prefix icon.
  final Widget? prefixIcon;

  /// Suffix icon.
  final Widget? suffixIcon;

  /// Whether to obscure text (for passwords).
  final bool obscureText;

  /// Keyboard type.
  final TextInputType? keyboardType;

  /// Text input action.
  final TextInputAction? textInputAction;

  /// Maximum number of lines.
  final int maxLines;

  /// Maximum character length.
  final int? maxLength;

  /// Whether the field is enabled.
  final bool enabled;

  /// Whether the field is read-only.
  final bool readOnly;

  /// Whether to autofocus.
  final bool autofocus;

  /// Synchronous validator function.
  final String? Function(String?)? validator;

  /// Asynchronous validator function.
  final Future<String?> Function(String?)? asyncValidator;

  /// Callback when the field value changes.
  final void Function(String)? onChanged;

  /// Callback when the field is submitted.
  final void Function(String)? onSubmitted;

  /// Input formatters.
  final List<TextInputFormatter>? inputFormatters;

  /// Debounce duration for validation.
  final Duration debounceDuration;

  /// Whether to show validation icon.
  final bool showValidationIcon;

  /// Auto-validate mode.
  final AutovalidateMode autovalidateMode;

  @override
  State<ValidationField> createState() => _ValidationFieldState();
}

class _ValidationFieldState extends State<ValidationField> {
  Timer? _debounceTimer;
  String? _asyncError;
  bool _isValidating = false;
  bool _isValid = false;

  @override
  void dispose() {
    _debounceTimer?.cancel();
    super.dispose();
  }

  /// Handle field value changes with debounced validation.
  void _handleChanged(String value) {
    widget.onChanged?.call(value);

    // Cancel previous timer
    _debounceTimer?.cancel();

    // Start new debounce timer
    _debounceTimer = Timer(widget.debounceDuration, () {
      _performAsyncValidation(value);
    });
  }

  /// Perform asynchronous validation.
  Future<void> _performAsyncValidation(String value) async {
    if (widget.asyncValidator == null) {
      return;
    }

    setState(() {
      _isValidating = true;
      _asyncError = null;
    });

    try {
      final error = await widget.asyncValidator!(value);
      if (mounted) {
        setState(() {
          _asyncError = error;
          _isValid = error == null;
          _isValidating = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _asyncError = 'Validation error';
          _isValid = false;
          _isValidating = false;
        });
      }
    }
  }

  /// Combined validator that includes both sync and async validation.
  String? _combinedValidator(String? value) {
    // First run synchronous validation
    if (widget.validator != null) {
      final syncError = widget.validator!(value);
      if (syncError != null) {
        _isValid = false;
        return syncError;
      }
    }

    // Then check async validation result
    if (_asyncError != null) {
      return _asyncError;
    }

    // If no errors, mark as valid
    if (!_isValidating && _asyncError == null) {
      _isValid = true;
    }

    return null;
  }

  /// Build the suffix icon with validation state.
  Widget? _buildSuffixIcon() {
    if (!widget.showValidationIcon) {
      return widget.suffixIcon;
    }

    Widget? validationIcon;

    if (_isValidating) {
      validationIcon = const SizedBox(
        width: 16,
        height: 16,
        child: CircularProgressIndicator(
          strokeWidth: 2,
        ),
      );
    } else if (_isValid && widget.controller.text.isNotEmpty) {
      validationIcon = const Icon(
        Icons.check_circle,
        color: AppColors.success,
        size: 20,
      );
    } else if (_asyncError != null) {
      validationIcon = Icon(
        Icons.error,
        color: AppColors.error,
        size: 20,
      );
    }

    if (validationIcon != null && widget.suffixIcon != null) {
      return Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          validationIcon,
          const SizedBox(width: AppSpacing.xs),
          widget.suffixIcon!,
        ],
      );
    }

    return validationIcon ?? widget.suffixIcon;
  }

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: widget.controller,
      decoration: InputDecoration(
        labelText: widget.label,
        hintText: widget.hint,
        helperText: widget.helperText,
        prefixIcon: widget.prefixIcon,
        suffixIcon: _buildSuffixIcon(),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(
            color: Theme.of(context).colorScheme.outline,
          ),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(
            color: Theme.of(context).colorScheme.primary,
            width: 2,
          ),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(
            color: Theme.of(context).colorScheme.error,
          ),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(
            color: Theme.of(context).colorScheme.error,
            width: 2,
          ),
        ),
        filled: true,
        fillColor: Theme.of(context).colorScheme.surface,
      ),
      obscureText: widget.obscureText,
      keyboardType: widget.keyboardType,
      textInputAction: widget.textInputAction,
      maxLines: widget.maxLines,
      maxLength: widget.maxLength,
      enabled: widget.enabled,
      readOnly: widget.readOnly,
      autofocus: widget.autofocus,
      validator: _combinedValidator,
      onChanged: _handleChanged,
      onFieldSubmitted: widget.onSubmitted,
      inputFormatters: widget.inputFormatters,
      autovalidateMode: widget.autovalidateMode,
    );
  }
}
