/// Dietary indicator enumeration for menu items.
enum DietaryIndicator {
  vegetarian('vegetarian', '🥬', 'Vegetarian'),
  vegan('vegan', '🌱', 'Vegan'),
  glutenFree('gluten_free', '🌾', 'Gluten Free'),
  dairyFree('dairy_free', '🥛', 'Dairy Free'),
  nutFree('nut_free', '🥜', 'Nut Free'),
  spicy('spicy', '🌶️', 'Spicy'),
  halal('halal', '☪️', 'Halal'),
  kosher('kosher', '✡️', 'Kosher');

  const DietaryIndicator(this.value, this.icon, this.displayName);

  final String value;
  final String icon;
  final String displayName;

  /// Get dietary indicator from string value
  static DietaryIndicator? fromValue(String value) {
    for (final indicator in DietaryIndicator.values) {
      if (indicator.value == value) {
        return indicator;
      }
    }
    return null;
  }

  /// Get list of dietary indicators from string list
  static List<DietaryIndicator> fromValueList(List<String> values) {
    return values
        .map((value) => DietaryIndicator.fromValue(value))
        .where((indicator) => indicator != null)
        .cast<DietaryIndicator>()
        .toList();
  }

  /// Convert list of dietary indicators to string list
  static List<String> toValueList(List<DietaryIndicator> indicators) {
    return indicators.map((indicator) => indicator.value).toList();
  }
}
