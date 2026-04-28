import 'package:flutter/material.dart';

import '../../domain/entities/menu_category.dart';

/// Category tabs widget for menu navigation.
class CategoryTabs extends StatelessWidget {
  const CategoryTabs({
    super.key,
    required this.categories,
    required this.selectedCategory,
    required this.onCategorySelected,
  });

  final List<MenuCategory> categories;
  final MenuCategory? selectedCategory;
  final Function(MenuCategory?) onCategorySelected;

  @override
  Widget build(BuildContext context) {
    if (categories.isEmpty) {
      return const SliverToBoxAdapter(child: SizedBox.shrink());
    }

    return SliverToBoxAdapter(
      child: Container(
        height: 50,
        margin: const EdgeInsets.symmetric(vertical: 8),
        child: ListView.builder(
          scrollDirection: Axis.horizontal,
          padding: const EdgeInsets.symmetric(horizontal: 16),
          itemCount: categories.length + 1, // +1 for "All" tab
          itemBuilder: (context, index) {
            if (index == 0) {
              // "All" tab
              final isSelected = selectedCategory == null;
              return _CategoryTab(
                title: 'All',
                itemCount: null,
                isSelected: isSelected,
                onTap: () => onCategorySelected(null),
              );
            }

            final category = categories[index - 1];
            final isSelected = selectedCategory?.id == category.id;

            return _CategoryTab(
              title: category.name,
              itemCount: category.itemCount,
              isSelected: isSelected,
              onTap: () => onCategorySelected(category),
            );
          },
        ),
      ),
    );
  }
}

class _CategoryTab extends StatelessWidget {
  const _CategoryTab({
    required this.title,
    required this.itemCount,
    required this.isSelected,
    required this.onTap,
  });

  final String title;
  final int? itemCount;
  final bool isSelected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(right: 12),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: isSelected ? Theme.of(context).primaryColor : Colors.grey[100],
          borderRadius: BorderRadius.circular(25),
          border: Border.all(
            color:
                isSelected ? Theme.of(context).primaryColor : Colors.grey[300]!,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              title,
              style: TextStyle(
                color: isSelected ? Colors.white : Colors.black87,
                fontWeight: isSelected ? FontWeight.w600 : FontWeight.normal,
              ),
            ),
            if (itemCount != null && itemCount! > 0) ...[
              const SizedBox(width: 6),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: isSelected
                      ? Colors.white.withValues(alpha: 0.2)
                      : Colors.grey[300],
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  itemCount.toString(),
                  style: TextStyle(
                    color: isSelected ? Colors.white : Colors.black54,
                    fontSize: 12,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
