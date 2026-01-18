/// Firebase Firestore Service Template
///
/// Complete CRUD operations with Firestore
/// Features: Streams, batch operations, queries, pagination
///
/// Usage:
/// 1. Replace {{MODEL_NAME}} with your model (e.g., User, Product, Order)
/// 2. Replace {{COLLECTION_NAME}} with your Firestore collection
/// 3. Customize the model fields and queries

import 'dart:async';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Model for {{MODEL_NAME}}
class {{MODEL_NAME}} {
  final String id;
  final String name;
  final String? description;
  final DateTime createdAt;
  final DateTime updatedAt;
  final Map<String, dynamic>? metadata;

  {{MODEL_NAME}}({
    required this.id,
    required this.name,
    this.description,
    DateTime? createdAt,
    DateTime? updatedAt,
    this.metadata,
  })  : createdAt = createdAt ?? DateTime.now(),
        updatedAt = updatedAt ?? DateTime.now();

  /// Create from Firestore document
  factory {{MODEL_NAME}}.fromFirestore(DocumentSnapshot doc) {
    final data = doc.data() as Map<String, dynamic>? ?? {};
    return {{MODEL_NAME}}(
      id: doc.id,
      name: data['name'] ?? '',
      description: data['description'],
      createdAt: (data['createdAt'] as Timestamp?)?.toDate() ?? DateTime.now(),
      updatedAt: (data['updatedAt'] as Timestamp?)?.toDate() ?? DateTime.now(),
      metadata: data['metadata'],
    );
  }

  /// Convert to Firestore map
  Map<String, dynamic> toFirestore() {
    return {
      'name': name,
      'description': description,
      'createdAt': Timestamp.fromDate(createdAt),
      'updatedAt': FieldValue.serverTimestamp(),
      'metadata': metadata,
    };
  }

  {{MODEL_NAME}} copyWith({
    String? id,
    String? name,
    String? description,
    DateTime? createdAt,
    DateTime? updatedAt,
    Map<String, dynamic>? metadata,
  }) {
    return {{MODEL_NAME}}(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      metadata: metadata ?? this.metadata,
    );
  }
}

/// Firestore service for {{MODEL_NAME}}
class {{MODEL_NAME}}Service {
  final FirebaseFirestore _firestore;
  static const String _collection = '{{COLLECTION_NAME}}';

  {{MODEL_NAME}}Service({FirebaseFirestore? firestore})
      : _firestore = firestore ?? FirebaseFirestore.instance;

  CollectionReference<Map<String, dynamic>> get _ref =>
      _firestore.collection(_collection);

  // ============ CREATE ============

  /// Create a new document
  Future<{{MODEL_NAME}}> create({{MODEL_NAME}} item) async {
    final docRef = await _ref.add(item.toFirestore());
    return item.copyWith(id: docRef.id);
  }

  /// Create with custom ID
  Future<void> createWithId(String id, {{MODEL_NAME}} item) async {
    await _ref.doc(id).set(item.toFirestore());
  }

  /// Batch create multiple documents
  Future<void> batchCreate(List<{{MODEL_NAME}}> items) async {
    final batch = _firestore.batch();
    for (final item in items) {
      final docRef = _ref.doc();
      batch.set(docRef, item.toFirestore());
    }
    await batch.commit();
  }

  // ============ READ ============

  /// Get single document by ID
  Future<{{MODEL_NAME}}?> getById(String id) async {
    final doc = await _ref.doc(id).get();
    if (!doc.exists) return null;
    return {{MODEL_NAME}}.fromFirestore(doc);
  }

  /// Get all documents
  Future<List<{{MODEL_NAME}}>> getAll() async {
    final snapshot = await _ref.orderBy('createdAt', descending: true).get();
    return snapshot.docs.map((doc) => {{MODEL_NAME}}.fromFirestore(doc)).toList();
  }

  /// Get with pagination
  Future<List<{{MODEL_NAME}}>> getPaginated({
    int limit = 20,
    DocumentSnapshot? startAfter,
  }) async {
    Query<Map<String, dynamic>> query = _ref
        .orderBy('createdAt', descending: true)
        .limit(limit);

    if (startAfter != null) {
      query = query.startAfterDocument(startAfter);
    }

    final snapshot = await query.get();
    return snapshot.docs.map((doc) => {{MODEL_NAME}}.fromFirestore(doc)).toList();
  }

  /// Query by field
  Future<List<{{MODEL_NAME}}>> queryByField(String field, dynamic value) async {
    final snapshot = await _ref.where(field, isEqualTo: value).get();
    return snapshot.docs.map((doc) => {{MODEL_NAME}}.fromFirestore(doc)).toList();
  }

  /// Complex query
  Future<List<{{MODEL_NAME}}>> queryComplex({
    String? nameContains,
    DateTime? createdAfter,
    DateTime? createdBefore,
    int? limit,
  }) async {
    Query<Map<String, dynamic>> query = _ref;

    if (createdAfter != null) {
      query = query.where('createdAt', isGreaterThanOrEqualTo: Timestamp.fromDate(createdAfter));
    }
    if (createdBefore != null) {
      query = query.where('createdAt', isLessThanOrEqualTo: Timestamp.fromDate(createdBefore));
    }
    if (limit != null) {
      query = query.limit(limit);
    }

    final snapshot = await query.get();
    var results = snapshot.docs.map((doc) => {{MODEL_NAME}}.fromFirestore(doc)).toList();

    // Client-side filtering for contains (Firestore doesn't support contains)
    if (nameContains != null) {
      results = results.where((item) =>
          item.name.toLowerCase().contains(nameContains.toLowerCase())).toList();
    }

    return results;
  }

  // ============ STREAMS ============

  /// Stream all documents
  Stream<List<{{MODEL_NAME}}>> streamAll() {
    return _ref
        .orderBy('createdAt', descending: true)
        .snapshots()
        .map((snapshot) =>
            snapshot.docs.map((doc) => {{MODEL_NAME}}.fromFirestore(doc)).toList());
  }

  /// Stream single document
  Stream<{{MODEL_NAME}}?> streamById(String id) {
    return _ref.doc(id).snapshots().map((doc) {
      if (!doc.exists) return null;
      return {{MODEL_NAME}}.fromFirestore(doc);
    });
  }

  /// Stream with query
  Stream<List<{{MODEL_NAME}}>> streamByField(String field, dynamic value) {
    return _ref
        .where(field, isEqualTo: value)
        .snapshots()
        .map((snapshot) =>
            snapshot.docs.map((doc) => {{MODEL_NAME}}.fromFirestore(doc)).toList());
  }

  // ============ UPDATE ============

  /// Update document
  Future<void> update(String id, Map<String, dynamic> data) async {
    data['updatedAt'] = FieldValue.serverTimestamp();
    await _ref.doc(id).update(data);
  }

  /// Update full document
  Future<void> updateFull({{MODEL_NAME}} item) async {
    await _ref.doc(item.id).update(item.toFirestore());
  }

  /// Batch update
  Future<void> batchUpdate(Map<String, Map<String, dynamic>> updates) async {
    final batch = _firestore.batch();
    updates.forEach((id, data) {
      data['updatedAt'] = FieldValue.serverTimestamp();
      batch.update(_ref.doc(id), data);
    });
    await batch.commit();
  }

  /// Increment field
  Future<void> incrementField(String id, String field, num value) async {
    await _ref.doc(id).update({
      field: FieldValue.increment(value),
      'updatedAt': FieldValue.serverTimestamp(),
    });
  }

  /// Add to array
  Future<void> addToArray(String id, String field, dynamic value) async {
    await _ref.doc(id).update({
      field: FieldValue.arrayUnion([value]),
      'updatedAt': FieldValue.serverTimestamp(),
    });
  }

  /// Remove from array
  Future<void> removeFromArray(String id, String field, dynamic value) async {
    await _ref.doc(id).update({
      field: FieldValue.arrayRemove([value]),
      'updatedAt': FieldValue.serverTimestamp(),
    });
  }

  // ============ DELETE ============

  /// Delete document
  Future<void> delete(String id) async {
    await _ref.doc(id).delete();
  }

  /// Batch delete
  Future<void> batchDelete(List<String> ids) async {
    final batch = _firestore.batch();
    for (final id in ids) {
      batch.delete(_ref.doc(id));
    }
    await batch.commit();
  }

  /// Delete all (use with caution!)
  Future<void> deleteAll() async {
    final snapshot = await _ref.get();
    final batch = _firestore.batch();
    for (final doc in snapshot.docs) {
      batch.delete(doc.reference);
    }
    await batch.commit();
  }

  // ============ UTILITIES ============

  /// Check if document exists
  Future<bool> exists(String id) async {
    final doc = await _ref.doc(id).get();
    return doc.exists;
  }

  /// Get document count
  Future<int> count() async {
    final snapshot = await _ref.count().get();
    return snapshot.count ?? 0;
  }
}

/// Provider for the service
final {{MODEL_NAME_LOWER}}ServiceProvider = Provider<{{MODEL_NAME}}Service>((ref) {
  return {{MODEL_NAME}}Service();
});

/// Stream provider for all items
final {{MODEL_NAME_LOWER}}StreamProvider = StreamProvider<List<{{MODEL_NAME}}>>((ref) {
  final service = ref.watch({{MODEL_NAME_LOWER}}ServiceProvider);
  return service.streamAll();
});

/// Future provider for getting by ID
final {{MODEL_NAME_LOWER}}ByIdProvider = FutureProvider.family<{{MODEL_NAME}}?, String>((ref, id) {
  final service = ref.watch({{MODEL_NAME_LOWER}}ServiceProvider);
  return service.getById(id);
});
