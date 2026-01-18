/// Base List Screen Template
///
/// Reusable CRUD list pattern with search, filter, sort, and pagination
/// Features: Pull-to-refresh, infinite scroll, empty states, loading states
///
/// Usage:
/// 1. Extend BaseListScreen with your model type
/// 2. Implement required methods
/// 3. Customize UI with optional overrides

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Sort direction enum
enum SortDirection { ascending, descending }

/// Filter option
class FilterOption<T> {
  final String label;
  final T value;
  final IconData? icon;

  const FilterOption({
    required this.label,
    required this.value,
    this.icon,
  });
}

/// Sort option
class SortOption<T> {
  final String label;
  final T field;
  final SortDirection direction;

  const SortOption({
    required this.label,
    required this.field,
    this.direction = SortDirection.ascending,
  });
}

/// List state for managing data
class ListState<T> {
  final List<T> items;
  final bool isLoading;
  final bool isLoadingMore;
  final bool hasMore;
  final String? error;
  final String searchQuery;
  final dynamic activeFilter;
  final SortOption? activeSort;

  const ListState({
    this.items = const [],
    this.isLoading = false,
    this.isLoadingMore = false,
    this.hasMore = true,
    this.error,
    this.searchQuery = '',
    this.activeFilter,
    this.activeSort,
  });

  ListState<T> copyWith({
    List<T>? items,
    bool? isLoading,
    bool? isLoadingMore,
    bool? hasMore,
    String? error,
    String? searchQuery,
    dynamic activeFilter,
    SortOption? activeSort,
  }) {
    return ListState<T>(
      items: items ?? this.items,
      isLoading: isLoading ?? this.isLoading,
      isLoadingMore: isLoadingMore ?? this.isLoadingMore,
      hasMore: hasMore ?? this.hasMore,
      error: error,
      searchQuery: searchQuery ?? this.searchQuery,
      activeFilter: activeFilter ?? this.activeFilter,
      activeSort: activeSort ?? this.activeSort,
    );
  }

  bool get isEmpty => items.isEmpty && !isLoading;
  bool get hasError => error != null;
}

/// Base list notifier - extend this for your data
abstract class BaseListNotifier<T> extends StateNotifier<ListState<T>> {
  BaseListNotifier() : super(const ListState()) {
    loadItems();
  }

  /// Implement: Load items from your data source
  Future<List<T>> fetchItems({
    int offset = 0,
    int limit = 20,
    String? searchQuery,
    dynamic filter,
    SortOption? sort,
  });

  /// Implement: Delete an item
  Future<bool> deleteItem(T item);

  /// Items per page
  int get pageSize => 20;

  /// Load initial items
  Future<void> loadItems() async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final items = await fetchItems(
        limit: pageSize,
        searchQuery: state.searchQuery,
        filter: state.activeFilter,
        sort: state.activeSort,
      );

      state = state.copyWith(
        items: items,
        isLoading: false,
        hasMore: items.length >= pageSize,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Load more items (pagination)
  Future<void> loadMore() async {
    if (state.isLoadingMore || !state.hasMore) return;

    state = state.copyWith(isLoadingMore: true);

    try {
      final newItems = await fetchItems(
        offset: state.items.length,
        limit: pageSize,
        searchQuery: state.searchQuery,
        filter: state.activeFilter,
        sort: state.activeSort,
      );

      state = state.copyWith(
        items: [...state.items, ...newItems],
        isLoadingMore: false,
        hasMore: newItems.length >= pageSize,
      );
    } catch (e) {
      state = state.copyWith(isLoadingMore: false);
    }
  }

  /// Refresh list
  Future<void> refresh() async {
    await loadItems();
  }

  /// Search items
  void search(String query) {
    state = state.copyWith(searchQuery: query);
    loadItems();
  }

  /// Apply filter
  void applyFilter(dynamic filter) {
    state = state.copyWith(activeFilter: filter);
    loadItems();
  }

  /// Apply sort
  void applySort(SortOption? sort) {
    state = state.copyWith(activeSort: sort);
    loadItems();
  }

  /// Delete item
  Future<bool> delete(T item) async {
    final success = await deleteItem(item);
    if (success) {
      state = state.copyWith(
        items: state.items.where((i) => i != item).toList(),
      );
    }
    return success;
  }

  /// Add item to list (after creation)
  void addItem(T item, {bool atStart = true}) {
    state = state.copyWith(
      items: atStart ? [item, ...state.items] : [...state.items, item],
    );
  }

  /// Update item in list
  void updateItem(T oldItem, T newItem) {
    final index = state.items.indexOf(oldItem);
    if (index != -1) {
      final newItems = List<T>.from(state.items);
      newItems[index] = newItem;
      state = state.copyWith(items: newItems);
    }
  }
}

/// Base list screen widget
abstract class BaseListScreen<T> extends ConsumerStatefulWidget {
  const BaseListScreen({super.key});
}

abstract class BaseListScreenState<T, W extends BaseListScreen<T>>
    extends ConsumerState<W> {
  final ScrollController _scrollController = ScrollController();
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _scrollController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  // ============ REQUIRED OVERRIDES ============

  /// Provider for the list notifier
  StateNotifierProvider<BaseListNotifier<T>, ListState<T>> get listProvider;

  /// Build list item widget
  Widget buildListItem(BuildContext context, T item, int index);

  // ============ OPTIONAL OVERRIDES ============

  /// Screen title
  String get title => 'Items';

  /// Show search bar
  bool get showSearch => true;

  /// Show filter button
  bool get showFilter => false;

  /// Show sort button
  bool get showSort => false;

  /// Filter options
  List<FilterOption> get filterOptions => [];

  /// Sort options
  List<SortOption> get sortOptions => [];

  /// Empty state message
  String get emptyMessage => 'No items found';

  /// Empty state icon
  IconData get emptyIcon => Icons.inbox_outlined;

  /// Enable pull to refresh
  bool get enableRefresh => true;

  /// Enable swipe to delete
  bool get enableSwipeDelete => false;

  /// FAB for adding new items
  Widget? get floatingActionButton => null;

  /// Build item separator
  Widget? buildSeparator(int index) => const Divider(height: 1);

  /// On item tap
  void onItemTap(T item) {}

  /// On item long press
  void onItemLongPress(T item) {}

  /// Confirm delete dialog
  Future<bool> confirmDelete(T item) async {
    return await showDialog<bool>(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('Delete Item'),
            content: const Text('Are you sure you want to delete this item?'),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('Cancel'),
              ),
              TextButton(
                onPressed: () => Navigator.pop(context, true),
                style: TextButton.styleFrom(foregroundColor: Colors.red),
                child: const Text('Delete'),
              ),
            ],
          ),
        ) ??
        false;
  }

  // ============ INTERNAL ============

  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent - 200) {
      ref.read(listProvider.notifier).loadMore();
    }
  }

  void _onSearch(String query) {
    ref.read(listProvider.notifier).search(query);
  }

  void _showFilterSheet() {
    showModalBottomSheet(
      context: context,
      builder: (context) => _FilterSheet(
        options: filterOptions,
        onSelect: (filter) {
          ref.read(listProvider.notifier).applyFilter(filter);
          Navigator.pop(context);
        },
      ),
    );
  }

  void _showSortSheet() {
    showModalBottomSheet(
      context: context,
      builder: (context) => _SortSheet(
        options: sortOptions,
        onSelect: (sort) {
          ref.read(listProvider.notifier).applySort(sort);
          Navigator.pop(context);
        },
      ),
    );
  }

  Future<void> _onDelete(T item) async {
    if (await confirmDelete(item)) {
      await ref.read(listProvider.notifier).delete(item);
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(listProvider);

    return Scaffold(
      appBar: AppBar(
        title: Text(title),
        actions: [
          if (showFilter)
            IconButton(
              icon: const Icon(Icons.filter_list),
              onPressed: _showFilterSheet,
            ),
          if (showSort)
            IconButton(
              icon: const Icon(Icons.sort),
              onPressed: _showSortSheet,
            ),
        ],
        bottom: showSearch
            ? PreferredSize(
                preferredSize: const Size.fromHeight(60),
                child: Padding(
                  padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
                  child: TextField(
                    controller: _searchController,
                    decoration: InputDecoration(
                      hintText: 'Search...',
                      prefixIcon: const Icon(Icons.search),
                      suffixIcon: _searchController.text.isNotEmpty
                          ? IconButton(
                              icon: const Icon(Icons.clear),
                              onPressed: () {
                                _searchController.clear();
                                _onSearch('');
                              },
                            )
                          : null,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(10),
                      ),
                      filled: true,
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16),
                    ),
                    onChanged: _onSearch,
                  ),
                ),
              )
            : null,
      ),
      body: _buildBody(state),
      floatingActionButton: floatingActionButton,
    );
  }

  Widget _buildBody(ListState<T> state) {
    if (state.isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (state.hasError) {
      return _ErrorState(
        message: state.error!,
        onRetry: () => ref.read(listProvider.notifier).refresh(),
      );
    }

    if (state.isEmpty) {
      return _EmptyState(
        message: emptyMessage,
        icon: emptyIcon,
      );
    }

    Widget list = ListView.separated(
      controller: _scrollController,
      padding: const EdgeInsets.only(bottom: 80),
      itemCount: state.items.length + (state.isLoadingMore ? 1 : 0),
      separatorBuilder: (context, index) =>
          buildSeparator(index) ?? const SizedBox.shrink(),
      itemBuilder: (context, index) {
        if (index >= state.items.length) {
          return const Padding(
            padding: EdgeInsets.all(16),
            child: Center(child: CircularProgressIndicator()),
          );
        }

        final item = state.items[index];
        final child = buildListItem(context, item, index);

        if (enableSwipeDelete) {
          return Dismissible(
            key: ValueKey(item),
            direction: DismissDirection.endToStart,
            background: Container(
              color: Colors.red,
              alignment: Alignment.centerRight,
              padding: const EdgeInsets.only(right: 20),
              child: const Icon(Icons.delete, color: Colors.white),
            ),
            confirmDismiss: (_) => confirmDelete(item),
            onDismissed: (_) => ref.read(listProvider.notifier).delete(item),
            child: InkWell(
              onTap: () => onItemTap(item),
              onLongPress: () => onItemLongPress(item),
              child: child,
            ),
          );
        }

        return InkWell(
          onTap: () => onItemTap(item),
          onLongPress: () => onItemLongPress(item),
          child: child,
        );
      },
    );

    if (enableRefresh) {
      return RefreshIndicator(
        onRefresh: () => ref.read(listProvider.notifier).refresh(),
        child: list,
      );
    }

    return list;
  }
}

/// Empty state widget
class _EmptyState extends StatelessWidget {
  final String message;
  final IconData icon;

  const _EmptyState({required this.message, required this.icon});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 64, color: Colors.grey),
          const SizedBox(height: 16),
          Text(
            message,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: Colors.grey,
                ),
          ),
        ],
      ),
    );
  }
}

/// Error state widget
class _ErrorState extends StatelessWidget {
  final String message;
  final VoidCallback onRetry;

  const _ErrorState({required this.message, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, size: 64, color: Colors.red),
          const SizedBox(height: 16),
          Text(
            message,
            style: Theme.of(context).textTheme.titleMedium,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: onRetry,
            icon: const Icon(Icons.refresh),
            label: const Text('Retry'),
          ),
        ],
      ),
    );
  }
}

/// Filter bottom sheet
class _FilterSheet extends StatelessWidget {
  final List<FilterOption> options;
  final Function(dynamic) onSelect;

  const _FilterSheet({required this.options, required this.onSelect});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Text(
              'Filter',
              style: Theme.of(context).textTheme.titleLarge,
            ),
          ),
          ListTile(
            leading: const Icon(Icons.clear),
            title: const Text('Clear filter'),
            onTap: () => onSelect(null),
          ),
          ...options.map((option) => ListTile(
                leading: option.icon != null ? Icon(option.icon) : null,
                title: Text(option.label),
                onTap: () => onSelect(option.value),
              )),
        ],
      ),
    );
  }
}

/// Sort bottom sheet
class _SortSheet extends StatelessWidget {
  final List<SortOption> options;
  final Function(SortOption?) onSelect;

  const _SortSheet({required this.options, required this.onSelect});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Text(
              'Sort by',
              style: Theme.of(context).textTheme.titleLarge,
            ),
          ),
          ListTile(
            leading: const Icon(Icons.clear),
            title: const Text('Default'),
            onTap: () => onSelect(null),
          ),
          ...options.map((option) => ListTile(
                leading: Icon(
                  option.direction == SortDirection.ascending
                      ? Icons.arrow_upward
                      : Icons.arrow_downward,
                ),
                title: Text(option.label),
                onTap: () => onSelect(option),
              )),
        ],
      ),
    );
  }
}
