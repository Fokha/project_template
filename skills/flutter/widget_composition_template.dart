// ignore_for_file: avoid_print, prefer_const_constructors

// ═══════════════════════════════════════════════════════════════
// WIDGET COMPOSITION TEMPLATE
// Reusable UI component patterns
// ═══════════════════════════════════════════════════════════════
//
// Usage:
// 1. Copy to your project's lib/widgets/ directory
// 2. Replace {{WIDGET_NAME}} with your widget name
// 3. Customize appearance and behavior
//
// ═══════════════════════════════════════════════════════════════

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

// ═══════════════════════════════════════════════════════════════
// CARD WIDGET (Base reusable card)
// ═══════════════════════════════════════════════════════════════

class AppCard extends StatelessWidget {
  final Widget child;
  final EdgeInsets? padding;
  final EdgeInsets? margin;
  final Color? backgroundColor;
  final double? elevation;
  final BorderRadius? borderRadius;
  final VoidCallback? onTap;
  final VoidCallback? onLongPress;

  const AppCard({
    super.key,
    required this.child,
    this.padding,
    this.margin,
    this.backgroundColor,
    this.elevation,
    this.borderRadius,
    this.onTap,
    this.onLongPress,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    Widget card = Container(
      padding: padding ?? const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: backgroundColor ?? theme.cardColor,
        borderRadius: borderRadius ?? BorderRadius.circular(12),
        boxShadow: elevation != null && elevation! > 0
          ? [
              BoxShadow(
                color: Colors.black.withOpacity(0.1),
                blurRadius: elevation!,
                offset: Offset(0, elevation! / 2),
              ),
            ]
          : null,
      ),
      child: child,
    );

    if (onTap != null || onLongPress != null) {
      card = InkWell(
        onTap: onTap,
        onLongPress: onLongPress,
        borderRadius: borderRadius ?? BorderRadius.circular(12),
        child: card,
      );
    }

    if (margin != null) {
      card = Padding(padding: margin!, child: card);
    }

    return card;
  }
}

// ═══════════════════════════════════════════════════════════════
// ASYNC BUILDER (Loading states)
// ═══════════════════════════════════════════════════════════════

class AsyncBuilder<T> extends StatelessWidget {
  final Future<T>? future;
  final Stream<T>? stream;
  final T? initialData;
  final Widget Function(BuildContext context, T data) builder;
  final Widget Function(BuildContext context)? loadingBuilder;
  final Widget Function(BuildContext context, Object error)? errorBuilder;
  final Widget Function(BuildContext context)? emptyBuilder;

  const AsyncBuilder({
    super.key,
    this.future,
    this.stream,
    this.initialData,
    required this.builder,
    this.loadingBuilder,
    this.errorBuilder,
    this.emptyBuilder,
  }) : assert(future != null || stream != null);

  @override
  Widget build(BuildContext context) {
    if (stream != null) {
      return StreamBuilder<T>(
        stream: stream,
        initialData: initialData,
        builder: _buildAsync,
      );
    }

    return FutureBuilder<T>(
      future: future,
      initialData: initialData,
      builder: _buildAsync,
    );
  }

  Widget _buildAsync(BuildContext context, AsyncSnapshot<T> snapshot) {
    if (snapshot.hasError) {
      return errorBuilder?.call(context, snapshot.error!) ??
        _DefaultErrorWidget(error: snapshot.error!);
    }

    if (snapshot.connectionState == ConnectionState.waiting &&
        snapshot.data == null) {
      return loadingBuilder?.call(context) ??
        const _DefaultLoadingWidget();
    }

    final data = snapshot.data;
    if (data == null || (data is List && data.isEmpty)) {
      return emptyBuilder?.call(context) ??
        const _DefaultEmptyWidget();
    }

    return builder(context, data);
  }
}

class _DefaultLoadingWidget extends StatelessWidget {
  const _DefaultLoadingWidget();

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: CircularProgressIndicator(),
    );
  }
}

class _DefaultErrorWidget extends StatelessWidget {
  final Object error;

  const _DefaultErrorWidget({required this.error});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.error_outline, size: 48, color: Colors.red),
          const SizedBox(height: 16),
          Text(
            'Error: $error',
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.bodyMedium,
          ),
        ],
      ),
    );
  }
}

class _DefaultEmptyWidget extends StatelessWidget {
  const _DefaultEmptyWidget();

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.inbox, size: 48, color: Colors.grey[400]),
          const SizedBox(height: 16),
          Text(
            'No data available',
            style: TextStyle(color: Colors.grey[600]),
          ),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════
// REFRESHABLE LIST (Pull to refresh + pagination)
// ═══════════════════════════════════════════════════════════════

class RefreshableList<T> extends StatefulWidget {
  final Future<List<T>> Function(int page) onLoad;
  final Widget Function(BuildContext context, T item, int index) itemBuilder;
  final Widget? separator;
  final Widget Function(BuildContext context)? emptyBuilder;
  final Widget Function(BuildContext context, Object error)? errorBuilder;
  final int initialPage;
  final ScrollController? controller;

  const RefreshableList({
    super.key,
    required this.onLoad,
    required this.itemBuilder,
    this.separator,
    this.emptyBuilder,
    this.errorBuilder,
    this.initialPage = 1,
    this.controller,
  });

  @override
  State<RefreshableList<T>> createState() => _RefreshableListState<T>();
}

class _RefreshableListState<T> extends State<RefreshableList<T>> {
  late ScrollController _scrollController;
  final List<T> _items = [];
  int _currentPage = 1;
  bool _isLoading = false;
  bool _hasMore = true;
  Object? _error;

  @override
  void initState() {
    super.initState();
    _currentPage = widget.initialPage;
    _scrollController = widget.controller ?? ScrollController();
    _scrollController.addListener(_onScroll);
    _loadPage(_currentPage);
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent - 200) {
      _loadMore();
    }
  }

  Future<void> _loadPage(int page, {bool refresh = false}) async {
    if (_isLoading) return;

    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final items = await widget.onLoad(page);

      setState(() {
        if (refresh) {
          _items.clear();
        }
        _items.addAll(items);
        _currentPage = page;
        _hasMore = items.isNotEmpty;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e;
        _isLoading = false;
      });
    }
  }

  Future<void> _refresh() async {
    _currentPage = widget.initialPage;
    _hasMore = true;
    await _loadPage(_currentPage, refresh: true);
  }

  void _loadMore() {
    if (!_isLoading && _hasMore) {
      _loadPage(_currentPage + 1);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_error != null && _items.isEmpty) {
      return widget.errorBuilder?.call(context, _error!) ??
        _DefaultErrorWidget(error: _error!);
    }

    if (!_isLoading && _items.isEmpty) {
      return widget.emptyBuilder?.call(context) ??
        const _DefaultEmptyWidget();
    }

    return RefreshIndicator(
      onRefresh: _refresh,
      child: ListView.separated(
        controller: _scrollController,
        itemCount: _items.length + (_hasMore ? 1 : 0),
        separatorBuilder: (_, __) => widget.separator ?? const SizedBox.shrink(),
        itemBuilder: (context, index) {
          if (index >= _items.length) {
            return const Padding(
              padding: EdgeInsets.all(16),
              child: Center(child: CircularProgressIndicator()),
            );
          }
          return widget.itemBuilder(context, _items[index], index);
        },
      ),
    );
  }

  @override
  void dispose() {
    if (widget.controller == null) {
      _scrollController.dispose();
    }
    super.dispose();
  }
}

// ═══════════════════════════════════════════════════════════════
// STATUS BADGE
// ═══════════════════════════════════════════════════════════════

enum StatusType { success, warning, error, info, neutral }

class StatusBadge extends StatelessWidget {
  final String label;
  final StatusType type;
  final IconData? icon;
  final bool outlined;

  const StatusBadge({
    super.key,
    required this.label,
    this.type = StatusType.neutral,
    this.icon,
    this.outlined = false,
  });

  Color get _backgroundColor {
    switch (type) {
      case StatusType.success: return Colors.green;
      case StatusType.warning: return Colors.orange;
      case StatusType.error: return Colors.red;
      case StatusType.info: return Colors.blue;
      case StatusType.neutral: return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    final color = _backgroundColor;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: outlined ? Colors.transparent : color.withOpacity(0.2),
        border: outlined ? Border.all(color: color) : null,
        borderRadius: BorderRadius.circular(4),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 14, color: color),
            const SizedBox(width: 4),
          ],
          Text(
            label,
            style: TextStyle(
              color: color,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════
// COPYABLE TEXT
// ═══════════════════════════════════════════════════════════════

class CopyableText extends StatelessWidget {
  final String text;
  final TextStyle? style;
  final String? copyMessage;

  const CopyableText({
    super.key,
    required this.text,
    this.style,
    this.copyMessage,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: () {
        Clipboard.setData(ClipboardData(text: text));
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(copyMessage ?? 'Copied to clipboard'),
            duration: const Duration(seconds: 2),
          ),
        );
      },
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Flexible(
            child: Text(text, style: style, overflow: TextOverflow.ellipsis),
          ),
          const SizedBox(width: 4),
          Icon(Icons.copy, size: 14, color: Colors.grey[500]),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════
// ACTION BUTTON GROUP
// ═══════════════════════════════════════════════════════════════

class ActionButton {
  final String label;
  final IconData? icon;
  final VoidCallback onPressed;
  final bool isPrimary;
  final bool isDestructive;

  const ActionButton({
    required this.label,
    this.icon,
    required this.onPressed,
    this.isPrimary = false,
    this.isDestructive = false,
  });
}

class ActionButtonGroup extends StatelessWidget {
  final List<ActionButton> actions;
  final Axis direction;
  final double spacing;

  const ActionButtonGroup({
    super.key,
    required this.actions,
    this.direction = Axis.horizontal,
    this.spacing = 8,
  });

  @override
  Widget build(BuildContext context) {
    final children = actions.map((action) {
      final style = action.isPrimary
        ? ElevatedButton.styleFrom(
            backgroundColor: action.isDestructive ? Colors.red : null,
          )
        : TextButton.styleFrom(
            foregroundColor: action.isDestructive ? Colors.red : null,
          );

      if (action.isPrimary) {
        return ElevatedButton.icon(
          onPressed: action.onPressed,
          icon: action.icon != null ? Icon(action.icon, size: 18) : const SizedBox.shrink(),
          label: Text(action.label),
          style: style,
        );
      }

      return TextButton.icon(
        onPressed: action.onPressed,
        icon: action.icon != null ? Icon(action.icon, size: 18) : const SizedBox.shrink(),
        label: Text(action.label),
        style: style,
      );
    }).toList();

    if (direction == Axis.vertical) {
      return Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          for (int i = 0; i < children.length; i++) ...[
            children[i],
            if (i < children.length - 1) SizedBox(height: spacing),
          ],
        ],
      );
    }

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        for (int i = 0; i < children.length; i++) ...[
          children[i],
          if (i < children.length - 1) SizedBox(width: spacing),
        ],
      ],
    );
  }
}

// ═══════════════════════════════════════════════════════════════
// LABELED VALUE (Key-value display)
// ═══════════════════════════════════════════════════════════════

class LabeledValue extends StatelessWidget {
  final String label;
  final String value;
  final TextStyle? labelStyle;
  final TextStyle? valueStyle;
  final Widget? trailing;
  final bool dense;

  const LabeledValue({
    super.key,
    required this.label,
    required this.value,
    this.labelStyle,
    this.valueStyle,
    this.trailing,
    this.dense = false,
  });

  @override
  Widget build(BuildContext context) {
    // Theme available for customization: Theme.of(context)
    return Padding(
      padding: EdgeInsets.symmetric(vertical: dense ? 4 : 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            flex: 2,
            child: Text(
              label,
              style: labelStyle ?? TextStyle(
                color: Colors.grey[600],
                fontSize: dense ? 12 : 14,
              ),
            ),
          ),
          const SizedBox(width: 8),
          Expanded(
            flex: 3,
            child: Text(
              value,
              style: valueStyle ?? TextStyle(
                fontWeight: FontWeight.w500,
                fontSize: dense ? 12 : 14,
              ),
            ),
          ),
          if (trailing != null) ...[
            const SizedBox(width: 8),
            trailing!,
          ],
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════
// CONFIRMATION DIALOG
// ═══════════════════════════════════════════════════════════════

Future<bool> showConfirmationDialog({
  required BuildContext context,
  required String title,
  required String message,
  String confirmLabel = 'Confirm',
  String cancelLabel = 'Cancel',
  bool isDestructive = false,
}) async {
  final result = await showDialog<bool>(
    context: context,
    builder: (context) => AlertDialog(
      title: Text(title),
      content: Text(message),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(false),
          child: Text(cancelLabel),
        ),
        TextButton(
          onPressed: () => Navigator.of(context).pop(true),
          style: isDestructive
            ? TextButton.styleFrom(foregroundColor: Colors.red)
            : null,
          child: Text(confirmLabel),
        ),
      ],
    ),
  );

  return result ?? false;
}

// ═══════════════════════════════════════════════════════════════
// SHIMMER LOADING
// ═══════════════════════════════════════════════════════════════

class ShimmerLoading extends StatefulWidget {
  final Widget child;
  final bool isLoading;

  const ShimmerLoading({
    super.key,
    required this.child,
    this.isLoading = true,
  });

  @override
  State<ShimmerLoading> createState() => _ShimmerLoadingState();
}

class _ShimmerLoadingState extends State<ShimmerLoading>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat();

    _animation = Tween<double>(begin: -1, end: 2).animate(
      CurvedAnimation(parent: _controller, curve: Curves.linear),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.isLoading) return widget.child;

    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return ShaderMask(
          shaderCallback: (bounds) {
            return LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: const [
                Color(0xFFEEEEEE),
                Color(0xFFF5F5F5),
                Color(0xFFEEEEEE),
              ],
              stops: [
                _animation.value - 1,
                _animation.value,
                _animation.value + 1,
              ],
            ).createShader(bounds);
          },
          blendMode: BlendMode.srcATop,
          child: widget.child,
        );
      },
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}

// ═══════════════════════════════════════════════════════════════
// USAGE EXAMPLE
// ═══════════════════════════════════════════════════════════════

class ExampleScreen extends StatelessWidget {
  const ExampleScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Widget Examples')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Card example
            AppCard(
              onTap: () => print('Card tapped'),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Card Title', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  const Text('Card content goes here'),
                  const SizedBox(height: 16),
                  ActionButtonGroup(
                    actions: [
                      ActionButton(label: 'Cancel', onPressed: () {}),
                      ActionButton(label: 'Confirm', onPressed: () {}, isPrimary: true),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Status badges
            Wrap(
              spacing: 8,
              children: const [
                StatusBadge(label: 'Active', type: StatusType.success, icon: Icons.check),
                StatusBadge(label: 'Warning', type: StatusType.warning),
                StatusBadge(label: 'Error', type: StatusType.error),
                StatusBadge(label: 'Info', type: StatusType.info),
              ],
            ),

            const SizedBox(height: 24),

            // Labeled values
            const LabeledValue(label: 'Status', value: 'Connected'),
            const LabeledValue(label: 'Balance', value: '\$10,250.00'),
            const LabeledValue(label: 'Last Update', value: '2 minutes ago'),

            const SizedBox(height: 24),

            // Copyable text
            const CopyableText(
              text: '0x1234...abcd',
              copyMessage: 'Address copied!',
            ),
          ],
        ),
      ),
    );
  }
}
