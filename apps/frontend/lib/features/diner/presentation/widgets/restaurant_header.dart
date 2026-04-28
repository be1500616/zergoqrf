import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';

import '../../domain/entities/restaurant_branding.dart';

/// Restaurant header widget with branding and theming.
class RestaurantHeader extends StatelessWidget {
  const RestaurantHeader({
    super.key,
    required this.restaurant,
  });

  final RestaurantBranding restaurant;

  @override
  Widget build(BuildContext context) {
    final primaryColor = _parseColor(restaurant.primaryColor);
    final secondaryColor = _parseColor(restaurant.secondaryColor);

    return SliverAppBar(
      expandedHeight: 200,
      pinned: true,
      backgroundColor: primaryColor,
      flexibleSpace: FlexibleSpaceBar(
        title: Text(
          restaurant.name,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        background: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                primaryColor,
                secondaryColor,
              ],
            ),
          ),
          child: Stack(
            children: [
              // Background pattern
              Positioned.fill(
                child: Opacity(
                  opacity: 0.1,
                  child: Container(
                    decoration: const BoxDecoration(
                      image: DecorationImage(
                        image: AssetImage('assets/images/pattern.png'),
                        repeat: ImageRepeat.repeat,
                      ),
                    ),
                  ),
                ),
              ),

              // Restaurant logo
              if (restaurant.logoUrl != null)
                Positioned(
                  top: 60,
                  left: 20,
                  child: Container(
                    width: 60,
                    height: 60,
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(30),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withValues(alpha: 0.2),
                          blurRadius: 8,
                          offset: const Offset(0, 2),
                        ),
                      ],
                    ),
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(30),
                      child: CachedNetworkImage(
                        imageUrl: restaurant.logoUrl!,
                        fit: BoxFit.cover,
                        placeholder: (context, url) => const Center(
                          child: CircularProgressIndicator(),
                        ),
                        errorWidget: (context, url, error) => const Icon(
                          Icons.restaurant,
                          color: Colors.grey,
                        ),
                      ),
                    ),
                  ),
                ),

              // Restaurant info
              Positioned(
                bottom: 20,
                left: 20,
                right: 20,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (restaurant.cuisineType != null)
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.white.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          restaurant.cuisineType!,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    if (restaurant.description != null) ...[
                      const SizedBox(height: 8),
                      Text(
                        restaurant.description!,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 14,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.info_outline, color: Colors.white),
          onPressed: () => _showRestaurantInfo(context),
        ),
      ],
    );
  }

  Color _parseColor(String colorString) {
    try {
      return Color(int.parse(colorString.replaceFirst('#', '0xFF')));
    } catch (e) {
      // Use theme primary color as fallback instead of hardcoded blue
      return const Color(0xFF2E7D32); // AppColors primary seed
    }
  }

  void _showRestaurantInfo(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) {
        final colorScheme = Theme.of(context).colorScheme;
        return Container(
          decoration: BoxDecoration(
            color: colorScheme.surface,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
          ),
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Handle bar
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: colorScheme.outlineVariant,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 20),

              // Restaurant name
              Text(
                restaurant.name,
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),

              if (restaurant.cuisineType != null) ...[
                const SizedBox(height: 8),
                Text(
                  restaurant.cuisineType!,
                  style: TextStyle(
                    fontSize: 16,
                    color: colorScheme.onSurfaceVariant,
                  ),
                ),
              ],

              if (restaurant.description != null) ...[
                const SizedBox(height: 16),
                Text(
                  restaurant.description!,
                  style: const TextStyle(fontSize: 16),
                ),
              ],

              if (restaurant.address != null) ...[
                const SizedBox(height: 16),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.location_on, size: 20),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        restaurant.address!,
                        style: const TextStyle(fontSize: 14),
                      ),
                    ),
                  ],
                ),
              ],

              if (restaurant.phone != null) ...[
                const SizedBox(height: 12),
                Row(
                  children: [
                    const Icon(Icons.phone, size: 20),
                    const SizedBox(width: 8),
                    Text(
                      restaurant.phone!,
                      style: const TextStyle(fontSize: 14),
                    ),
                  ],
                ),
              ],

              const SizedBox(height: 24),
            ],
          ),
        );
      },
    );
  }
}
