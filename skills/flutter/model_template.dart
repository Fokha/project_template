// ═══════════════════════════════════════════════════════════════
// ModelName MODEL
// Data structure with JSON serialization
// ═══════════════════════════════════════════════════════════════
//
// Usage:
// 1. Copy this file to lib/models/{{model_name}}_model.dart
// 2. Replace ModelName with your model name
// 3. Define your fields
//
// ═══════════════════════════════════════════════════════════════

/// ModelName data model
///
/// Example:
/// ```dart
/// final item = ModelNameModel(
///   id: '123',
///   name: 'Example',
///   status: 'active',
/// );
///
/// // To JSON
/// final json = item.toJson();
///
/// // From JSON
/// final fromJson = ModelNameModel.fromJson(json);
/// ```
class ModelNameModel {
  // ═══════════════════════════════════════════════════════════════
  // FIELDS
  // ═══════════════════════════════════════════════════════════════

  final String id;
  final String name;
  final String? description;
  final String status;
  final DateTime createdAt;
  final DateTime? updatedAt;
  final Map<String, dynamic>? metadata;

  // ═══════════════════════════════════════════════════════════════
  // CONSTRUCTOR
  // ═══════════════════════════════════════════════════════════════

  ModelNameModel({
    required this.id,
    required this.name,
    this.description,
    this.status = 'active',
    DateTime? createdAt,
    this.updatedAt,
    this.metadata,
  }) : createdAt = createdAt ?? DateTime.now();

  // ═══════════════════════════════════════════════════════════════
  // FACTORY CONSTRUCTORS
  // ═══════════════════════════════════════════════════════════════

  /// Create from JSON map
  factory ModelNameModel.fromJson(Map<String, dynamic> json) {
    return ModelNameModel(
      id: json['id']?.toString() ?? '',
      name: json['name']?.toString() ?? '',
      description: json['description']?.toString(),
      status: json['status']?.toString() ?? 'active',
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'].toString())
          : null,
      updatedAt: json['updated_at'] != null
          ? DateTime.tryParse(json['updated_at'].toString())
          : null,
      metadata: json['metadata'] is Map
          ? Map<String, dynamic>.from(json['metadata'])
          : null,
    );
  }

  /// Create empty model
  factory ModelNameModel.empty() {
    return ModelNameModel(
      id: '',
      name: '',
    );
  }

  // ═══════════════════════════════════════════════════════════════
  // SERIALIZATION
  // ═══════════════════════════════════════════════════════════════

  /// Convert to JSON map
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      if (description != null) 'description': description,
      'status': status,
      'created_at': createdAt.toIso8601String(),
      if (updatedAt != null) 'updated_at': updatedAt!.toIso8601String(),
      if (metadata != null) 'metadata': metadata,
    };
  }

  /// Convert to JSON for API create (no id)
  Map<String, dynamic> toCreateJson() {
    final json = toJson();
    json.remove('id');
    json.remove('created_at');
    json.remove('updated_at');
    return json;
  }

  // ═══════════════════════════════════════════════════════════════
  // COPY WITH
  // ═══════════════════════════════════════════════════════════════

  /// Create a copy with updated fields
  ModelNameModel copyWith({
    String? id,
    String? name,
    String? description,
    String? status,
    DateTime? createdAt,
    DateTime? updatedAt,
    Map<String, dynamic>? metadata,
  }) {
    return ModelNameModel(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      status: status ?? this.status,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      metadata: metadata ?? this.metadata,
    );
  }

  // ═══════════════════════════════════════════════════════════════
  // COMPUTED PROPERTIES
  // ═══════════════════════════════════════════════════════════════

  /// Check if model is valid
  bool get isValid => id.isNotEmpty && name.isNotEmpty;

  /// Check if active
  bool get isActive => status == 'active';

  /// Display name (for UI)
  String get displayName => name.isEmpty ? 'Unnamed' : name;

  /// Age since creation
  Duration get age => DateTime.now().difference(createdAt);

  // ═══════════════════════════════════════════════════════════════
  // EQUALITY
  // ═══════════════════════════════════════════════════════════════

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is ModelNameModel && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;

  // ═══════════════════════════════════════════════════════════════
  // STRING REPRESENTATION
  // ═══════════════════════════════════════════════════════════════

  @override
  String toString() {
    return 'ModelNameModel(id: $id, name: $name, status: $status)';
  }
}

// ═══════════════════════════════════════════════════════════════
// EXTENSION METHODS (Optional)
// ═══════════════════════════════════════════════════════════════

extension ModelNameListExtension on List<ModelNameModel> {
  /// Filter by status
  List<ModelNameModel> whereStatus(String status) {
    return where((item) => item.status == status).toList();
  }

  /// Get active items
  List<ModelNameModel> get active => whereStatus('active');

  /// Sort by name
  List<ModelNameModel> sortedByName() {
    return [...this]..sort((a, b) => a.name.compareTo(b.name));
  }

  /// Sort by date (newest first)
  List<ModelNameModel> sortedByDate() {
    return [...this]..sort((a, b) => b.createdAt.compareTo(a.createdAt));
  }
}
