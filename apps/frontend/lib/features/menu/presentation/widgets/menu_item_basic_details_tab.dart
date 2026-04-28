/// Menu item basic details tab widget.
/// 
/// This widget provides the basic information form for menu items.

import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../application/controllers/menu_management_controller.dart';
import '../../domain/entities/menu_entities.dart';

class MenuItemBasicDetailsTab extends StatelessWidget {
  const MenuItemBasicDetailsTab({
    super.key,
    required this.nameController,
    required this.descriptionController,
    required this.basePriceController,
    required this.preparationTimeController,
    required this.dailyLimitController,
    required this.selectedCategoryId,
    required this.imageUrl,
    required this.galleryImages,
    required this.status,
    required this.dietaryIndicators,
    required this.allergenInfo,
    required this.nutritionalInfo,
    required this.onCategoryChanged,
    required this.onImageUrlChanged,
    required this.onGalleryImagesChanged,
    required this.onStatusChanged,
    required this.onDietaryIndicatorsChanged,
    required this.onAllergenInfoChanged,
    required this.onNutritionalInfoChanged,
  });

  final TextEditingController nameController;
  final TextEditingController descriptionController;
  final TextEditingController basePriceController;
  final TextEditingController preparationTimeController;
  final TextEditingController dailyLimitController;
  final String? selectedCategoryId;
  final String? imageUrl;
  final List<String> galleryImages;
  final ItemStatus status;
  final List<DietaryIndicator> dietaryIndicators;
  final List<String> allergenInfo;
  final Map<String, dynamic> nutritionalInfo;
  final Function(String?) onCategoryChanged;
  final Function(String?) onImageUrlChanged;
  final Function(List<String>) onGalleryImagesChanged;
  final Function(ItemStatus) onStatusChanged;
  final Function(List<DietaryIndicator>) onDietaryIndicatorsChanged;
  final Function(List<String>) onAllergenInfoChanged;
  final Function(Map<String, dynamic>) onNutritionalInfoChanged;

  @override
  Widget build(BuildContext context) {
    final MenuManagementController controller = Get.find<MenuManagementController>();

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Basic Information Section
          _SectionHeader(title: 'Basic Information'),
          const SizedBox(height: 16),
          
          // Item name
          TextFormField(
            controller: nameController,
            decoration: const InputDecoration(
              labelText: 'Item Name *',
              hintText: 'e.g., Margherita Pizza',
              border: OutlineInputBorder(),
            ),
            textCapitalization: TextCapitalization.words,
          ),
          const SizedBox(height: 16),
          
          // Description
          TextFormField(
            controller: descriptionController,
            decoration: const InputDecoration(
              labelText: 'Description',
              hintText: 'Describe your dish...',
              border: OutlineInputBorder(),
            ),
            maxLines: 3,
            textCapitalization: TextCapitalization.sentences,
          ),
          const SizedBox(height: 16),
          
          // Category and Price row
          Row(
            children: [
              // Category dropdown
              Expanded(
                flex: 2,
                child: Obx(() => DropdownButtonFormField<String>(
                      value: selectedCategoryId,
                      decoration: const InputDecoration(
                        labelText: 'Category *',
                        border: OutlineInputBorder(),
                      ),
                      items: controller.categories.map((category) {
                        return DropdownMenuItem<String>(
                          value: category.id,
                          child: Text(category.name),
                        );
                      }).toList(),
                      onChanged: onCategoryChanged,
                    )),
              ),
              const SizedBox(width: 16),
              
              // Base price
              Expanded(
                child: TextFormField(
                  controller: basePriceController,
                  decoration: const InputDecoration(
                    labelText: 'Base Price *',
                    hintText: '0.00',
                    prefixText: '₹ ',
                    border: OutlineInputBorder(),
                  ),
                  keyboardType: TextInputType.number,
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          
          // Image Section
          _SectionHeader(title: 'Images'),
          const SizedBox(height: 16),
          
          // Main image
          _ImageUploadSection(
            title: 'Main Image',
            imageUrl: imageUrl,
            onImageChanged: onImageUrlChanged,
          ),
          const SizedBox(height: 16),
          
          // Gallery images
          _GallerySection(
            images: galleryImages,
            onImagesChanged: onGalleryImagesChanged,
          ),
          const SizedBox(height: 24),
          
          // Status and Timing Section
          _SectionHeader(title: 'Status & Timing'),
          const SizedBox(height: 16),
          
          // Status dropdown
          DropdownButtonFormField<ItemStatus>(
            value: status,
            decoration: const InputDecoration(
              labelText: 'Status',
              border: OutlineInputBorder(),
            ),
            items: ItemStatus.values.map((status) {
              return DropdownMenuItem<ItemStatus>(
                value: status,
                child: Text(status.name.capitalize ?? ''),
              );
            }).toList(),
            onChanged: (value) => onStatusChanged(value ?? ItemStatus.available),
          ),
          const SizedBox(height: 16),
          
          // Preparation time and daily limit row
          Row(
            children: [
              Expanded(
                child: TextFormField(
                  controller: preparationTimeController,
                  decoration: const InputDecoration(
                    labelText: 'Prep Time (min)',
                    hintText: '15',
                    border: OutlineInputBorder(),
                  ),
                  keyboardType: TextInputType.number,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: TextFormField(
                  controller: dailyLimitController,
                  decoration: const InputDecoration(
                    labelText: 'Daily Limit',
                    hintText: 'Optional',
                    border: OutlineInputBorder(),
                  ),
                  keyboardType: TextInputType.number,
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          
          // Dietary Information Section
          _SectionHeader(title: 'Dietary Information'),
          const SizedBox(height: 16),
          
          // Dietary indicators
          _DietaryIndicatorsSection(
            selectedIndicators: dietaryIndicators,
            onChanged: onDietaryIndicatorsChanged,
          ),
          const SizedBox(height: 16),
          
          // Allergen information
          _AllergenSection(
            allergens: allergenInfo,
            onChanged: onAllergenInfoChanged,
          ),
          const SizedBox(height: 24),
          
          // Nutritional Information Section
          _SectionHeader(title: 'Nutritional Information (Optional)'),
          const SizedBox(height: 16),
          
          _NutritionalInfoSection(
            nutritionalInfo: nutritionalInfo,
            onChanged: onNutritionalInfoChanged,
          ),
        ],
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  const _SectionHeader({required this.title});

  final String title;

  @override
  Widget build(BuildContext context) {
    return Text(
      title,
      style: Theme.of(context).textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.w600,
            color: Theme.of(context).colorScheme.primary,
          ),
    );
  }
}

class _ImageUploadSection extends StatelessWidget {
  const _ImageUploadSection({
    required this.title,
    required this.imageUrl,
    required this.onImageChanged,
  });

  final String title;
  final String? imageUrl;
  final Function(String?) onImageChanged;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: Theme.of(context).textTheme.labelLarge,
        ),
        const SizedBox(height: 8),
        Container(
          width: double.infinity,
          height: 200,
          decoration: BoxDecoration(
            border: Border.all(
              color: Theme.of(context).colorScheme.outline.withOpacity(0.5),
            ),
            borderRadius: BorderRadius.circular(8),
          ),
          child: imageUrl != null
              ? Stack(
                  children: [
                    ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: Image.network(
                        imageUrl!,
                        width: double.infinity,
                        height: double.infinity,
                        fit: BoxFit.cover,
                        errorBuilder: (context, error, stackTrace) => _UploadPlaceholder(),
                      ),
                    ),
                    Positioned(
                      top: 8,
                      right: 8,
                      child: IconButton(
                        onPressed: () => onImageChanged(null),
                        icon: const Icon(Icons.close),
                        style: IconButton.styleFrom(
                          backgroundColor: Colors.black54,
                          foregroundColor: Colors.white,
                        ),
                      ),
                    ),
                  ],
                )
              : _UploadPlaceholder(),
        ),
        const SizedBox(height: 8),
        OutlinedButton.icon(
          onPressed: () => _showImageUploadDialog(context),
          icon: const Icon(Icons.upload),
          label: Text(imageUrl != null ? 'Change Image' : 'Upload Image'),
        ),
      ],
    );
  }

  void _showImageUploadDialog(BuildContext context) {
    final urlController = TextEditingController(text: imageUrl);
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add Image'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: urlController,
              decoration: const InputDecoration(
                labelText: 'Image URL',
                hintText: 'https://example.com/image.jpg',
              ),
            ),
            const SizedBox(height: 16),
            Text(
              'Or upload from device (Coming Soon)',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.outline,
                  ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              onImageChanged(urlController.text.trim().isEmpty ? null : urlController.text.trim());
              Navigator.of(context).pop();
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }
}

class _UploadPlaceholder extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.image_outlined,
            size: 48,
            color: Theme.of(context).colorScheme.outline,
          ),
          const SizedBox(height: 8),
          Text(
            'No image selected',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Theme.of(context).colorScheme.outline,
                ),
          ),
        ],
      ),
    );
  }
}

class _GallerySection extends StatelessWidget {
  const _GallerySection({
    required this.images,
    required this.onImagesChanged,
  });

  final List<String> images;
  final Function(List<String>) onImagesChanged;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              'Gallery Images',
              style: Theme.of(context).textTheme.labelLarge,
            ),
            const Spacer(),
            TextButton.icon(
              onPressed: () => _addGalleryImage(context),
              icon: const Icon(Icons.add),
              label: const Text('Add Image'),
            ),
          ],
        ),
        const SizedBox(height: 8),
        if (images.isEmpty)
          Container(
            width: double.infinity,
            height: 100,
            decoration: BoxDecoration(
              border: Border.all(
                color: Theme.of(context).colorScheme.outline.withOpacity(0.5),
              ),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Center(
              child: Text(
                'No gallery images',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Theme.of(context).colorScheme.outline,
                    ),
              ),
            ),
          )
        else
          SizedBox(
            height: 100,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: images.length,
              itemBuilder: (context, index) {
                return Container(
                  width: 100,
                  margin: const EdgeInsets.only(right: 8),
                  child: Stack(
                    children: [
                      ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: Image.network(
                          images[index],
                          width: 100,
                          height: 100,
                          fit: BoxFit.cover,
                          errorBuilder: (context, error, stackTrace) => Container(
                            color: Theme.of(context).colorScheme.surfaceVariant,
                            child: const Icon(Icons.broken_image),
                          ),
                        ),
                      ),
                      Positioned(
                        top: 4,
                        right: 4,
                        child: IconButton(
                          onPressed: () => _removeGalleryImage(index),
                          icon: const Icon(Icons.close, size: 16),
                          style: IconButton.styleFrom(
                            backgroundColor: Colors.black54,
                            foregroundColor: Colors.white,
                            minimumSize: const Size(24, 24),
                          ),
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ),
      ],
    );
  }

  void _addGalleryImage(BuildContext context) {
    final urlController = TextEditingController();
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add Gallery Image'),
        content: TextField(
          controller: urlController,
          decoration: const InputDecoration(
            labelText: 'Image URL',
            hintText: 'https://example.com/image.jpg',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              final url = urlController.text.trim();
              if (url.isNotEmpty) {
                final newImages = List<String>.from(images)..add(url);
                onImagesChanged(newImages);
              }
              Navigator.of(context).pop();
            },
            child: const Text('Add'),
          ),
        ],
      ),
    );
  }

  void _removeGalleryImage(int index) {
    final newImages = List<String>.from(images)..removeAt(index);
    onImagesChanged(newImages);
  }
}

class _DietaryIndicatorsSection extends StatelessWidget {
  const _DietaryIndicatorsSection({
    required this.selectedIndicators,
    required this.onChanged,
  });

  final List<DietaryIndicator> selectedIndicators;
  final Function(List<DietaryIndicator>) onChanged;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Dietary Indicators',
          style: Theme.of(context).textTheme.labelLarge,
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: DietaryIndicator.values.map((indicator) {
            final isSelected = selectedIndicators.contains(indicator);
            return FilterChip(
              label: Text(_getDietaryLabel(indicator)),
              avatar: Text(_getDietaryEmoji(indicator)),
              selected: isSelected,
              onSelected: (selected) {
                final newIndicators = List<DietaryIndicator>.from(selectedIndicators);
                if (selected) {
                  newIndicators.add(indicator);
                } else {
                  newIndicators.remove(indicator);
                }
                onChanged(newIndicators);
              },
            );
          }).toList(),
        ),
      ],
    );
  }

  String _getDietaryLabel(DietaryIndicator indicator) {
    switch (indicator) {
      case DietaryIndicator.vegetarian:
        return 'Vegetarian';
      case DietaryIndicator.vegan:
        return 'Vegan';
      case DietaryIndicator.glutenFree:
        return 'Gluten Free';
      case DietaryIndicator.keto:
        return 'Keto';
      case DietaryIndicator.spicy:
        return 'Spicy';
      case DietaryIndicator.halal:
        return 'Halal';
      case DietaryIndicator.kosher:
        return 'Kosher';
    }
  }

  String _getDietaryEmoji(DietaryIndicator indicator) {
    switch (indicator) {
      case DietaryIndicator.vegetarian:
        return '🥗';
      case DietaryIndicator.vegan:
        return '🌱';
      case DietaryIndicator.glutenFree:
        return '🌾';
      case DietaryIndicator.keto:
        return '🥑';
      case DietaryIndicator.spicy:
        return '🌶️';
      case DietaryIndicator.halal:
        return '☪️';
      case DietaryIndicator.kosher:
        return '✡️';
    }
  }
}

class _AllergenSection extends StatelessWidget {
  const _AllergenSection({
    required this.allergens,
    required this.onChanged,
  });

  final List<String> allergens;
  final Function(List<String>) onChanged;

  static const commonAllergens = [
    'Nuts',
    'Dairy',
    'Eggs',
    'Soy',
    'Shellfish',
    'Fish',
    'Wheat',
    'Sesame',
  ];

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              'Allergen Information',
              style: Theme.of(context).textTheme.labelLarge,
            ),
            const Spacer(),
            TextButton.icon(
              onPressed: () => _addCustomAllergen(context),
              icon: const Icon(Icons.add),
              label: const Text('Custom'),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            ...commonAllergens.map((allergen) {
              final isSelected = allergens.contains(allergen);
              return FilterChip(
                label: Text(allergen),
                selected: isSelected,
                onSelected: (selected) {
                  final newAllergens = List<String>.from(allergens);
                  if (selected) {
                    newAllergens.add(allergen);
                  } else {
                    newAllergens.remove(allergen);
                  }
                  onChanged(newAllergens);
                },
              );
            }),
            ...allergens.where((a) => !commonAllergens.contains(a)).map((allergen) {
              return Chip(
                label: Text(allergen),
                onDeleted: () {
                  final newAllergens = List<String>.from(allergens)..remove(allergen);
                  onChanged(newAllergens);
                },
              );
            }),
          ],
        ),
      ],
    );
  }

  void _addCustomAllergen(BuildContext context) {
    final controller = TextEditingController();
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add Custom Allergen'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(
            labelText: 'Allergen Name',
            hintText: 'e.g., Peanuts',
          ),
          textCapitalization: TextCapitalization.words,
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              final allergen = controller.text.trim();
              if (allergen.isNotEmpty && !allergens.contains(allergen)) {
                final newAllergens = List<String>.from(allergens)..add(allergen);
                onChanged(newAllergens);
              }
              Navigator.of(context).pop();
            },
            child: const Text('Add'),
          ),
        ],
      ),
    );
  }
}

class _NutritionalInfoSection extends StatelessWidget {
  const _NutritionalInfoSection({
    required this.nutritionalInfo,
    required this.onChanged,
  });

  final Map<String, dynamic> nutritionalInfo;
  final Function(Map<String, dynamic>) onChanged;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Add nutritional information to help customers make informed choices',
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Theme.of(context).colorScheme.outline,
              ),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: TextFormField(
                initialValue: nutritionalInfo['calories']?.toString() ?? '',
                decoration: const InputDecoration(
                  labelText: 'Calories',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
                onChanged: (value) => _updateNutritionalInfo('calories', value),
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: TextFormField(
                initialValue: nutritionalInfo['protein']?.toString() ?? '',
                decoration: const InputDecoration(
                  labelText: 'Protein (g)',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
                onChanged: (value) => _updateNutritionalInfo('protein', value),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: TextFormField(
                initialValue: nutritionalInfo['carbs']?.toString() ?? '',
                decoration: const InputDecoration(
                  labelText: 'Carbs (g)',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
                onChanged: (value) => _updateNutritionalInfo('carbs', value),
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: TextFormField(
                initialValue: nutritionalInfo['fat']?.toString() ?? '',
                decoration: const InputDecoration(
                  labelText: 'Fat (g)',
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
                onChanged: (value) => _updateNutritionalInfo('fat', value),
              ),
            ),
          ],
        ),
      ],
    );
  }

  void _updateNutritionalInfo(String key, String value) {
    final newInfo = Map<String, dynamic>.from(nutritionalInfo);
    if (value.trim().isEmpty) {
      newInfo.remove(key);
    } else {
      final numValue = double.tryParse(value);
      if (numValue != null) {
        newInfo[key] = numValue;
      }
    }
    onChanged(newInfo);
  }
}
