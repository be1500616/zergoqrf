/// Menu item status enumeration.
enum ItemStatus {
  available('available', 'Available'),
  unavailable('unavailable', 'Unavailable'),
  featured('featured', 'Featured');

  const ItemStatus(this.value, this.displayName);

  final String value;
  final String displayName;

  /// Get item status from string value
  static ItemStatus fromValue(String value) {
    for (final status in ItemStatus.values) {
      if (status.value == value) {
        return status;
      }
    }
    return ItemStatus.available; // Default fallback
  }

  /// Check if item is available for ordering
  bool get isAvailable => this == ItemStatus.available || this == ItemStatus.featured;

  /// Check if item is featured
  bool get isFeatured => this == ItemStatus.featured;
}
