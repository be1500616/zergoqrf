/// Menu item editor screen.
/// 
/// This screen provides a comprehensive interface for creating and editing
/// menu items with tabbed sections for different aspects.

import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../application/controllers/menu_management_controller.dart';
import '../../domain/entities/menu_entities.dart';
import '../widgets/menu_item_basic_details_tab.dart';
import '../widgets/menu_item_pricing_tab.dart';
import '../widgets/menu_item_modifiers_tab.dart';
import '../widgets/menu_item_availability_tab.dart';

class MenuItemEditorScreen extends StatefulWidget {
  const MenuItemEditorScreen({super.key});

  @override
  State<MenuItemEditorScreen> createState() => _MenuItemEditorScreenState();
}

class _MenuItemEditorScreenState extends State<MenuItemEditorScreen>
    with TickerProviderStateMixin {
  late TabController _tabController;
  final MenuManagementController _controller = Get.find<MenuManagementController>();
  
  // Form controllers
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _basePriceController = TextEditingController();
  final _preparationTimeController = TextEditingController();
  final _dailyLimitController = TextEditingController();
  
  // Form state
  String? _selectedCategoryId;
  String? _imageUrl;
  List<String> _galleryImages = [];
  ItemStatus _status = ItemStatus.available;
  List<DietaryIndicator> _dietaryIndicators = [];
  List<String> _allergenInfo = [];
  Map<String, dynamic> _nutritionalInfo = {};
  List<MenuItemVariant> _variants = [];
  List<MenuItemModifierGroup> _modifierGroups = [];
  Map<String, dynamic> _availabilitySchedule = {};
  
  // Edit mode
  bool _isEditMode = false;
  MenuItem? _editingItem;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _initializeFromArguments();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _nameController.dispose();
    _descriptionController.dispose();
    _basePriceController.dispose();
    _preparationTimeController.dispose();
    _dailyLimitController.dispose();
    super.dispose();
  }

  void _initializeFromArguments() {
    final arguments = Get.arguments as Map<String, dynamic>?;
    
    if (arguments != null) {
      // Pre-select category if provided
      _selectedCategoryId = arguments['categoryId'];
      
      // Check if editing existing item
      final itemId = arguments['itemId'];
      if (itemId != null) {
        _isEditMode = true;
        _loadExistingItem(itemId);
      }
    }
  }

  void _loadExistingItem(String itemId) {
    _editingItem = _controller.menuItems.firstWhereOrNull((item) => item.id == itemId);
    
    if (_editingItem != null) {
      _nameController.text = _editingItem!.name;
      _descriptionController.text = _editingItem!.description ?? '';
      _basePriceController.text = _editingItem!.basePrice.toString();
      _preparationTimeController.text = _editingItem!.preparationTime?.toString() ?? '';
      _dailyLimitController.text = _editingItem!.dailyLimit?.toString() ?? '';
      
      _selectedCategoryId = _editingItem!.categoryId;
      _imageUrl = _editingItem!.imageUrl;
      _galleryImages = List.from(_editingItem!.galleryImages);
      _status = _editingItem!.status;
      _dietaryIndicators = List.from(_editingItem!.dietaryIndicators);
      _allergenInfo = List.from(_editingItem!.allergenInfo);
      _nutritionalInfo = Map.from(_editingItem!.nutritionalInfo);
      _variants = List.from(_editingItem!.variants);
      _modifierGroups = List.from(_editingItem!.modifierGroups);
      _availabilitySchedule = Map.from(_editingItem!.availabilitySchedule);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_isEditMode ? 'Edit Menu Item' : 'Create Menu Item'),
        elevation: 0,
        backgroundColor: Theme.of(context).colorScheme.surface,
        foregroundColor: Theme.of(context).colorScheme.onSurface,
        actions: [
          // Save button
          TextButton.icon(
            onPressed: _canSave() ? _saveItem : null,
            icon: const Icon(Icons.save),
            label: const Text('Save'),
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          labelColor: Theme.of(context).colorScheme.primary,
          unselectedLabelColor: Theme.of(context).colorScheme.onSurface.withOpacity(0.6),
          indicatorColor: Theme.of(context).colorScheme.primary,
          tabs: const [
            Tab(
              icon: Icon(Icons.info_outline),
              text: 'Details',
            ),
            Tab(
              icon: Icon(Icons.attach_money),
              text: 'Pricing',
            ),
            Tab(
              icon: Icon(Icons.add_circle_outline),
              text: 'Add-ons',
            ),
            Tab(
              icon: Icon(Icons.schedule),
              text: 'Availability',
            ),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          MenuItemBasicDetailsTab(
            nameController: _nameController,
            descriptionController: _descriptionController,
            basePriceController: _basePriceController,
            preparationTimeController: _preparationTimeController,
            dailyLimitController: _dailyLimitController,
            selectedCategoryId: _selectedCategoryId,
            imageUrl: _imageUrl,
            galleryImages: _galleryImages,
            status: _status,
            dietaryIndicators: _dietaryIndicators,
            allergenInfo: _allergenInfo,
            nutritionalInfo: _nutritionalInfo,
            onCategoryChanged: (categoryId) {
              setState(() {
                _selectedCategoryId = categoryId;
              });
            },
            onImageUrlChanged: (url) {
              setState(() {
                _imageUrl = url;
              });
            },
            onGalleryImagesChanged: (images) {
              setState(() {
                _galleryImages = images;
              });
            },
            onStatusChanged: (status) {
              setState(() {
                _status = status;
              });
            },
            onDietaryIndicatorsChanged: (indicators) {
              setState(() {
                _dietaryIndicators = indicators;
              });
            },
            onAllergenInfoChanged: (allergens) {
              setState(() {
                _allergenInfo = allergens;
              });
            },
            onNutritionalInfoChanged: (info) {
              setState(() {
                _nutritionalInfo = info;
              });
            },
          ),
          MenuItemPricingTab(
            variants: _variants,
            onVariantsChanged: (variants) {
              setState(() {
                _variants = variants;
              });
            },
          ),
          MenuItemModifiersTab(
            modifierGroups: _modifierGroups,
            onModifierGroupsChanged: (groups) {
              setState(() {
                _modifierGroups = groups;
              });
            },
          ),
          MenuItemAvailabilityTab(
            availabilitySchedule: _availabilitySchedule,
            onAvailabilityScheduleChanged: (schedule) {
              setState(() {
                _availabilitySchedule = schedule;
              });
            },
          ),
        ],
      ),
    );
  }

  bool _canSave() {
    return _nameController.text.trim().isNotEmpty &&
           _basePriceController.text.trim().isNotEmpty &&
           _selectedCategoryId != null &&
           double.tryParse(_basePriceController.text) != null &&
           double.parse(_basePriceController.text) > 0;
  }

  void _saveItem() async {
    if (!_canSave()) return;

    try {
      final basePrice = double.parse(_basePriceController.text);
      final preparationTime = _preparationTimeController.text.trim().isEmpty
          ? null
          : int.tryParse(_preparationTimeController.text);
      final dailyLimit = _dailyLimitController.text.trim().isEmpty
          ? null
          : int.tryParse(_dailyLimitController.text);

      if (_isEditMode && _editingItem != null) {
        // Update existing item
        await _controller.updateMenuItem(
          _editingItem!.id,
          {
            'category_id': _selectedCategoryId,
            'name': _nameController.text.trim(),
            'description': _descriptionController.text.trim().isEmpty
                ? null
                : _descriptionController.text.trim(),
            'base_price': basePrice,
            'image_url': _imageUrl,
            'gallery_images': _galleryImages,
            'status': _status.name,
            'dietary_indicators': _dietaryIndicators.map((e) => e.name).toList(),
            'allergen_info': _allergenInfo,
            'nutritional_info': _nutritionalInfo,
            'preparation_time': preparationTime,
            'daily_limit': dailyLimit,
            'availability_schedule': _availabilitySchedule,
            'variants': _variants.map((v) => {
              'id': v.id,
              'name': v.name,
              'description': v.description,
              'price_adjustment': v.priceAdjustment,
              'sort_order': v.sortOrder,
              'is_active': v.isActive,
            }).toList(),
            'modifier_groups': _modifierGroups.map((g) => {
              'id': g.id,
              'name': g.name,
              'description': g.description,
              'modifier_type': g.modifierType.name,
              'is_required': g.isRequired,
              'min_selections': g.minSelections,
              'max_selections': g.maxSelections,
              'sort_order': g.sortOrder,
              'is_active': g.isActive,
              'modifiers': g.modifiers.map((m) => {
                'id': m.id,
                'name': m.name,
                'description': m.description,
                'price': m.price,
                'sort_order': m.sortOrder,
                'is_active': m.isActive,
              }).toList(),
            }).toList(),
          },
        );
      } else {
        // Create new item
        await _controller.createMenuItem(
          categoryId: _selectedCategoryId!,
          name: _nameController.text.trim(),
          description: _descriptionController.text.trim().isEmpty
              ? null
              : _descriptionController.text.trim(),
          basePrice: basePrice,
          imageUrl: _imageUrl,
          galleryImages: _galleryImages,
          status: _status,
          dietaryIndicators: _dietaryIndicators,
          allergenInfo: _allergenInfo,
          nutritionalInfo: _nutritionalInfo,
          preparationTime: preparationTime,
          dailyLimit: dailyLimit,
          availabilitySchedule: _availabilitySchedule,
          variants: _variants,
          modifierGroups: _modifierGroups,
        );
      }

      Get.back();
    } catch (e) {
      // Error is handled by controller
    }
  }
}
