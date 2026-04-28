import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';

/// Food-themed visual branding component for authentication screens
///
/// Features:
/// - Vibrant food background image with overlay
/// - Animated headline and tagline
/// - ZERGO QR logo placement
/// - Responsive design with compact mode for mobile
class FoodBackgroundVisual extends StatelessWidget {
  const FoodBackgroundVisual({
    super.key,
    required this.isCompact,
    this.onDismiss,
  });

  /// Whether to show compact version (for mobile)
  final bool isCompact;

  /// Optional dismiss callback (for mobile)
  final VoidCallback? onDismiss;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Container(
      decoration: BoxDecoration(
        // Food-themed gradient background
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: isDark
              ? [
                  const Color(0xFF1A5319), // Dark forest green
                  const Color(0xFF2D4A2B), // Dark olive
                  const Color(0xFF4A2C2A), // Dark chocolate
                ]
              : [
                  const Color(0xFF2E7D32), // Restaurant green
                  const Color(0xFF558B2F), // Lime green
                  const Color(0xFF689F38), // Bright olive
                ],
        ),
        // Optional: Add a food image as decoration
        // Uncomment when actual food images are available
        // image: DecorationImage(
        //   image: AssetImage('assets/images/food-background.jpg'),
        //   fit: BoxFit.cover,
        //   colorFilter: ColorFilter.mode(
        //     Colors.black.withOpacity(isDark ? 0.5 : 0.3),
        //     BlendMode.darken,
        //   ),
        // ),
      ),
      child: Stack(
        children: [
          // Decorative food icons pattern (background)
          Positioned.fill(
            child: Opacity(
              opacity: 0.1,
              child: _buildFoodIconsPattern(),
            ),
          ),

          // Main content
          Center(
            child: Padding(
              padding: EdgeInsets.all(isCompact ? 24.0 : 48.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Logo
                  if (!isCompact)
                    _buildLogo().animate().fadeIn(duration: 600.ms).scale(
                          begin: const Offset(0.8, 0.8),
                          end: const Offset(1.0, 1.0),
                          curve: Curves.easeOutBack,
                        ),

                  if (!isCompact) const SizedBox(height: 48),

                  // Headline
                  Text(
                    'Your Next Great\nMeal is a Scan Away',
                    style: theme.textTheme.displaySmall?.copyWith(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      height: 1.2,
                      fontSize: isCompact ? 28 : 40,
                      shadows: [
                        Shadow(
                          color: Colors.black.withOpacity(0.5),
                          offset: const Offset(0, 2),
                          blurRadius: 8,
                        ),
                      ],
                    ),
                  ).animate().fadeIn(delay: 300.ms, duration: 600.ms).slideX(
                        begin: -0.3,
                        end: 0,
                        curve: Curves.easeOut,
                      ),

                  const SizedBox(height: 16),

                  // Tagline
                  Text(
                    'Order, pay, and earn rewards seamlessly\nat your favorite restaurants',
                    style: theme.textTheme.titleMedium?.copyWith(
                      color: Colors.white.withOpacity(0.95),
                      height: 1.5,
                      fontSize: isCompact ? 14 : 18,
                      shadows: [
                        Shadow(
                          color: Colors.black.withOpacity(0.3),
                          offset: const Offset(0, 1),
                          blurRadius: 4,
                        ),
                      ],
                    ),
                  ).animate().fadeIn(delay: 600.ms, duration: 600.ms).slideX(
                        begin: -0.3,
                        end: 0,
                        curve: Curves.easeOut,
                      ),

                  const SizedBox(height: 32),

                  // Feature highlights
                  if (!isCompact) ...[
                    _buildFeatureItem(
                      icon: Icons.qr_code_scanner,
                      text: 'Instant QR code access',
                      delay: 900.ms,
                    ),
                    const SizedBox(height: 12),
                    _buildFeatureItem(
                      icon: Icons.restaurant_menu,
                      text: 'Browse digital menus',
                      delay: 1100.ms,
                    ),
                    const SizedBox(height: 12),
                    _buildFeatureItem(
                      icon: Icons.stars,
                      text: 'Earn loyalty rewards',
                      delay: 1300.ms,
                    ),
                  ],
                ],
              ),
            ),
          ),

          // Logo in corner for compact view
          if (isCompact)
            Positioned(
              bottom: 16,
              left: 16,
              child: _buildCompactLogo()
                  .animate()
                  .fadeIn(duration: 600.ms)
                  .scale(begin: const Offset(0.5, 0.5)),
            ),
        ],
      ),
    );
  }

  /// Builds the main logo for desktop view
  Widget _buildLogo() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.15),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.white.withOpacity(0.3),
          width: 2,
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(
            Icons.restaurant_menu,
            color: Colors.white,
            size: 32,
          ),
          const SizedBox(width: 12),
          Text(
            'ZERGO QR',
            style: TextStyle(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
              shadows: [
                Shadow(
                  color: Colors.black.withOpacity(0.3),
                  offset: const Offset(0, 2),
                  blurRadius: 4,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Builds compact logo for mobile view
  Widget _buildCompactLogo() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.2),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(
            Icons.restaurant_menu,
            color: Colors.white,
            size: 20,
          ),
          const SizedBox(width: 8),
          Text(
            'ZERGO QR',
            style: TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.bold,
              shadows: [
                Shadow(
                  color: Colors.black.withOpacity(0.3),
                  offset: const Offset(0, 1),
                  blurRadius: 2,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// Builds a feature highlight item
  Widget _buildFeatureItem({
    required IconData icon,
    required String text,
    required Duration delay,
  }) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.2),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(
            icon,
            color: Colors.white,
            size: 20,
          ),
        ),
        const SizedBox(width: 12),
        Text(
          text,
          style: TextStyle(
            color: Colors.white.withOpacity(0.95),
            fontSize: 16,
            fontWeight: FontWeight.w500,
            shadows: [
              Shadow(
                color: Colors.black.withOpacity(0.3),
                offset: const Offset(0, 1),
                blurRadius: 4,
              ),
            ],
          ),
        ),
      ],
    )
        .animate()
        .fadeIn(delay: delay, duration: 600.ms)
        .slideX(begin: -0.2, end: 0, curve: Curves.easeOut);
  }

  /// Builds decorative food icons pattern for background
  Widget _buildFoodIconsPattern() {
    return GridView.builder(
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 4,
        mainAxisSpacing: 40,
        crossAxisSpacing: 40,
      ),
      itemCount: 20,
      itemBuilder: (context, index) {
        final icons = [
          Icons.restaurant,
          Icons.local_pizza,
          Icons.lunch_dining,
          Icons.dinner_dining,
          Icons.coffee,
          Icons.cake,
          Icons.icecream,
          Icons.fastfood,
        ];
        return Icon(
          icons[index % icons.length],
          color: Colors.white,
          size: 32,
        );
      },
    );
  }
}
