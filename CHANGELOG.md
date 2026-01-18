# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-19

### Added
- **Flutter Templates** - 11 new service templates from fokha_apps patterns:
  - `live_data_service_template.dart` - Multi-source API aggregation with fallbacks
  - `firebase_service_template.dart` - Complete Firestore CRUD with streams/pagination
  - `notification_service_template.dart` - FCM + local notifications
  - `backup_service_template.dart` - Cloud backup/restore with Firebase Storage
  - `storage_service_template.dart` - Dual-layer (SharedPreferences + Hive)
  - `logger_service_template.dart` - Production logging with API/performance tracking
  - `connectivity_service_template.dart` - Network monitoring with retry logic
  - `analytics_service_template.dart` - Event tracking with Firebase Analytics
  - `pdf_service_template.dart` - PDF generation, printing, sharing
  - `theme_service_template.dart` - Dynamic light/dark mode with persistence
  - `base_list_screen_template.dart` - CRUD list with search, filter, pagination

- **Data Layer Skills** - 47 template files for unified data handling:
  - Models, Factory, Processors, Unifiers, Storage, Pipeline modules
  - Data classification system (Source, Validity, Intensity, Origin)

- **Claude Code Skills** - 10+ slash commands:
  - `/release` - Automated release workflow
  - `/session-log` - Session reporting
  - `/commit`, `/task`, `/status`, and more

- **Multi-Agent System** - Hierarchical agent architecture:
  - THE_ASSISTANT (Supervisor)
  - THE_MASTER (Architect)
  - Specialist agents (Backend, Frontend, DevOps, etc.)

- **Skills Library** - 107 patterns across 9 categories:
  - Agentic AI (21 patterns)
  - Data Layer (7 modules, 47 files)
  - DevOps (10 patterns)
  - Flutter (21 patterns)
  - Integration (8 patterns)
  - Machine Learning (12 patterns)
  - MQL5 (8 patterns)
  - N8N (10 patterns)
  - Python API (10 patterns)

### Changed
- Updated SKILLS_INDEX.md with comprehensive template documentation

---

*Extracted from Fokha Trading System (v2.3.7 Flutter, v4.3.21 Python, v19.0.37 MQL5)*
