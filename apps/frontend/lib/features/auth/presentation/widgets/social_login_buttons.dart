import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

/// Social login buttons component for authentication
///
/// Provides styled buttons for Google and Apple sign-in with:
/// - Brand-consistent colors and icons
/// - Hover and loading states
/// - Accessibility support
/// - Responsive sizing
class SocialLoginButtons extends StatelessWidget {
  const SocialLoginButtons({
    super.key,
    required this.onGooglePressed,
    required this.onApplePressed,
    this.isLoading = false,
  });

  /// Callback when Google button is pressed
  final VoidCallback onGooglePressed;

  /// Callback when Apple button is pressed
  final VoidCallback onApplePressed;

  /// Whether social login is in progress
  final bool isLoading;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      children: [
        // Google Sign-In Button
        SizedBox(
          width: double.infinity,
          height: 56,
          child: ElevatedButton.icon(
            onPressed: isLoading ? null : onGooglePressed,
            icon: isLoading
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.black54,
                    ),
                  )
                : _buildGoogleIcon(),
            label: Text(
              isLoading ? 'Signing in...' : 'Continue with Google',
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: Colors.black87,
              ),
            ),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.white,
              foregroundColor: Colors.black87,
              elevation: 0,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
                side: BorderSide(
                  color: theme.colorScheme.outline.withOpacity(0.3),
                  width: 1,
                ),
              ),
            ),
          ),
        )
            .animate()
            .fadeIn(delay: 200.ms, duration: 400.ms)
            .slideY(begin: 0.2, end: 0, curve: Curves.easeOut),

        const SizedBox(height: 12),

        // Apple Sign-In Button
        SizedBox(
          width: double.infinity,
          height: 56,
          child: ElevatedButton.icon(
            onPressed: isLoading ? null : onApplePressed,
            icon: isLoading
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.white70,
                    ),
                  )
                : const Icon(
                    Icons.apple,
                    color: Colors.white,
                    size: 24,
                  ),
            label: Text(
              isLoading ? 'Signing in...' : 'Continue with Apple',
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: Colors.white,
              ),
            ),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.black,
              foregroundColor: Colors.white,
              elevation: 0,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
        )
            .animate()
            .fadeIn(delay: 300.ms, duration: 400.ms)
            .slideY(begin: 0.2, end: 0, curve: Curves.easeOut),
      ],
    );
  }

  /// Builds the Google icon with brand colors
  Widget _buildGoogleIcon() {
    return Container(
      width: 20,
      height: 20,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(2),
      ),
      child: Stack(
        children: [
          // Google "G" icon representation using Flutter icons
          // In production, use a proper Google logo SVG
          Icon(
            Icons.g_mobiledata_rounded,
            color: Colors.red[700],
            size: 24,
          ),
        ],
      ),
    );
  }
}
