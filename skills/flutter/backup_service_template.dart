/// Backup & Restore Service Template
///
/// Cloud backup with Firestore + Firebase Storage
/// Features: JSON serialization, batch operations, file handling
///
/// Usage:
/// 1. Add firebase_storage and path_provider to pubspec.yaml
/// 2. Configure Firebase Storage rules
/// 3. Replace {{COLLECTIONS}} with your collection names

import 'dart:convert';
import 'dart:io';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:path_provider/path_provider.dart';

/// Backup metadata
class BackupMetadata {
  final String id;
  final String userId;
  final DateTime createdAt;
  final int itemCount;
  final int sizeBytes;
  final List<String> collections;
  final String? description;

  BackupMetadata({
    required this.id,
    required this.userId,
    required this.createdAt,
    required this.itemCount,
    required this.sizeBytes,
    required this.collections,
    this.description,
  });

  factory BackupMetadata.fromJson(Map<String, dynamic> json) {
    return BackupMetadata(
      id: json['id'],
      userId: json['userId'],
      createdAt: DateTime.parse(json['createdAt']),
      itemCount: json['itemCount'],
      sizeBytes: json['sizeBytes'],
      collections: List<String>.from(json['collections']),
      description: json['description'],
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'userId': userId,
        'createdAt': createdAt.toIso8601String(),
        'itemCount': itemCount,
        'sizeBytes': sizeBytes,
        'collections': collections,
        'description': description,
      };
}

/// Backup result
class BackupResult {
  final bool success;
  final BackupMetadata? metadata;
  final String? error;
  final String? downloadUrl;

  BackupResult({
    required this.success,
    this.metadata,
    this.error,
    this.downloadUrl,
  });
}

/// Restore result
class RestoreResult {
  final bool success;
  final int itemsRestored;
  final String? error;
  final Map<String, int> collectionsRestored;

  RestoreResult({
    required this.success,
    this.itemsRestored = 0,
    this.error,
    this.collectionsRestored = const {},
  });
}

/// Backup & Restore Service
class BackupService {
  final FirebaseFirestore _firestore;
  final FirebaseStorage _storage;

  // Collections to backup - customize this
  static const List<String> _collections = [
    '{{COLLECTION_1}}',
    '{{COLLECTION_2}}',
    '{{COLLECTION_3}}',
  ];

  BackupService({
    FirebaseFirestore? firestore,
    FirebaseStorage? storage,
  })  : _firestore = firestore ?? FirebaseFirestore.instance,
        _storage = storage ?? FirebaseStorage.instance;

  /// Create a backup of all collections
  Future<BackupResult> createBackup({
    required String userId,
    String? description,
    List<String>? collectionsToBackup,
  }) async {
    try {
      final collections = collectionsToBackup ?? _collections;
      final backupData = <String, dynamic>{};
      int totalItems = 0;

      // Collect data from each collection
      for (final collection in collections) {
        final snapshot = await _firestore.collection(collection).get();
        final docs = <String, dynamic>{};

        for (final doc in snapshot.docs) {
          docs[doc.id] = _serializeDocument(doc.data());
          totalItems++;
        }

        backupData[collection] = docs;
      }

      // Create backup file
      final backupId = DateTime.now().millisecondsSinceEpoch.toString();
      final jsonString = json.encode(backupData);
      final bytes = utf8.encode(jsonString);

      // Save to local file first
      final directory = await getTemporaryDirectory();
      final file = File('${directory.path}/backup_$backupId.json');
      await file.writeAsBytes(bytes);

      // Upload to Firebase Storage
      final storageRef = _storage.ref().child('backups/$userId/$backupId.json');
      await storageRef.putFile(file);
      final downloadUrl = await storageRef.getDownloadURL();

      // Clean up local file
      await file.delete();

      // Create metadata
      final metadata = BackupMetadata(
        id: backupId,
        userId: userId,
        createdAt: DateTime.now(),
        itemCount: totalItems,
        sizeBytes: bytes.length,
        collections: collections,
        description: description,
      );

      // Save metadata to Firestore
      await _firestore
          .collection('backups')
          .doc(backupId)
          .set(metadata.toJson());

      return BackupResult(
        success: true,
        metadata: metadata,
        downloadUrl: downloadUrl,
      );
    } catch (e) {
      return BackupResult(
        success: false,
        error: e.toString(),
      );
    }
  }

  /// Restore from a backup
  Future<RestoreResult> restoreBackup({
    required String backupId,
    required String userId,
    bool clearExisting = false,
  }) async {
    try {
      // Download backup file
      final storageRef = _storage.ref().child('backups/$userId/$backupId.json');
      final directory = await getTemporaryDirectory();
      final file = File('${directory.path}/restore_$backupId.json');

      await storageRef.writeToFile(file);
      final jsonString = await file.readAsString();
      final backupData = json.decode(jsonString) as Map<String, dynamic>;

      // Clean up
      await file.delete();

      int totalRestored = 0;
      final collectionsRestored = <String, int>{};

      // Restore each collection
      for (final entry in backupData.entries) {
        final collection = entry.key;
        final docs = entry.value as Map<String, dynamic>;

        // Optionally clear existing data
        if (clearExisting) {
          await _clearCollection(collection);
        }

        // Restore documents in batches
        final batch = _firestore.batch();
        int batchCount = 0;

        for (final docEntry in docs.entries) {
          final docRef = _firestore.collection(collection).doc(docEntry.key);
          final data = _deserializeDocument(docEntry.value as Map<String, dynamic>);
          batch.set(docRef, data);
          batchCount++;
          totalRestored++;

          // Commit batch every 500 documents (Firestore limit)
          if (batchCount >= 500) {
            await batch.commit();
            batchCount = 0;
          }
        }

        // Commit remaining
        if (batchCount > 0) {
          await batch.commit();
        }

        collectionsRestored[collection] = docs.length;
      }

      return RestoreResult(
        success: true,
        itemsRestored: totalRestored,
        collectionsRestored: collectionsRestored,
      );
    } catch (e) {
      return RestoreResult(
        success: false,
        error: e.toString(),
      );
    }
  }

  /// Get list of backups for user
  Future<List<BackupMetadata>> getBackups(String userId) async {
    final snapshot = await _firestore
        .collection('backups')
        .where('userId', isEqualTo: userId)
        .orderBy('createdAt', descending: true)
        .get();

    return snapshot.docs
        .map((doc) => BackupMetadata.fromJson(doc.data()))
        .toList();
  }

  /// Delete a backup
  Future<bool> deleteBackup(String backupId, String userId) async {
    try {
      // Delete from Storage
      final storageRef = _storage.ref().child('backups/$userId/$backupId.json');
      await storageRef.delete();

      // Delete metadata from Firestore
      await _firestore.collection('backups').doc(backupId).delete();

      return true;
    } catch (e) {
      return false;
    }
  }

  /// Export backup to local file
  Future<File?> exportToLocal({
    required String userId,
    String? description,
  }) async {
    try {
      final collections = _collections;
      final backupData = <String, dynamic>{};

      for (final collection in collections) {
        final snapshot = await _firestore.collection(collection).get();
        final docs = <String, dynamic>{};

        for (final doc in snapshot.docs) {
          docs[doc.id] = _serializeDocument(doc.data());
        }

        backupData[collection] = docs;
      }

      final jsonString = json.encode(backupData);
      final directory = await getApplicationDocumentsDirectory();
      final timestamp = DateTime.now().toIso8601String().replaceAll(':', '-');
      final file = File('${directory.path}/backup_$timestamp.json');
      await file.writeAsString(jsonString);

      return file;
    } catch (e) {
      return null;
    }
  }

  /// Import from local file
  Future<RestoreResult> importFromLocal(File file) async {
    try {
      final jsonString = await file.readAsString();
      final backupData = json.decode(jsonString) as Map<String, dynamic>;

      int totalRestored = 0;
      final collectionsRestored = <String, int>{};

      for (final entry in backupData.entries) {
        final collection = entry.key;
        final docs = entry.value as Map<String, dynamic>;

        final batch = _firestore.batch();
        int batchCount = 0;

        for (final docEntry in docs.entries) {
          final docRef = _firestore.collection(collection).doc(docEntry.key);
          final data = _deserializeDocument(docEntry.value as Map<String, dynamic>);
          batch.set(docRef, data, SetOptions(merge: true));
          batchCount++;
          totalRestored++;

          if (batchCount >= 500) {
            await batch.commit();
            batchCount = 0;
          }
        }

        if (batchCount > 0) {
          await batch.commit();
        }

        collectionsRestored[collection] = docs.length;
      }

      return RestoreResult(
        success: true,
        itemsRestored: totalRestored,
        collectionsRestored: collectionsRestored,
      );
    } catch (e) {
      return RestoreResult(
        success: false,
        error: e.toString(),
      );
    }
  }

  // ============ HELPERS ============

  /// Serialize document for JSON (handle Timestamps, GeoPoints, etc.)
  Map<String, dynamic> _serializeDocument(Map<String, dynamic> data) {
    return data.map((key, value) {
      if (value is Timestamp) {
        return MapEntry(key, {'_type': 'timestamp', 'value': value.toDate().toIso8601String()});
      } else if (value is GeoPoint) {
        return MapEntry(key, {'_type': 'geopoint', 'lat': value.latitude, 'lng': value.longitude});
      } else if (value is Map<String, dynamic>) {
        return MapEntry(key, _serializeDocument(value));
      } else if (value is List) {
        return MapEntry(key, value.map((e) => e is Map<String, dynamic> ? _serializeDocument(e) : e).toList());
      }
      return MapEntry(key, value);
    });
  }

  /// Deserialize document from JSON
  Map<String, dynamic> _deserializeDocument(Map<String, dynamic> data) {
    return data.map((key, value) {
      if (value is Map<String, dynamic>) {
        if (value['_type'] == 'timestamp') {
          return MapEntry(key, Timestamp.fromDate(DateTime.parse(value['value'])));
        } else if (value['_type'] == 'geopoint') {
          return MapEntry(key, GeoPoint(value['lat'], value['lng']));
        }
        return MapEntry(key, _deserializeDocument(value));
      } else if (value is List) {
        return MapEntry(key, value.map((e) => e is Map<String, dynamic> ? _deserializeDocument(e) : e).toList());
      }
      return MapEntry(key, value);
    });
  }

  /// Clear all documents in a collection
  Future<void> _clearCollection(String collection) async {
    final snapshot = await _firestore.collection(collection).get();
    final batch = _firestore.batch();
    int count = 0;

    for (final doc in snapshot.docs) {
      batch.delete(doc.reference);
      count++;

      if (count >= 500) {
        await batch.commit();
        count = 0;
      }
    }

    if (count > 0) {
      await batch.commit();
    }
  }
}

/// Provider
final backupServiceProvider = Provider<BackupService>((ref) {
  return BackupService();
});
