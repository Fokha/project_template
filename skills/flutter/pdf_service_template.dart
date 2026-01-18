/// PDF Generation Service Template
///
/// Create and manage PDF documents with Flutter
/// Features: Text, tables, images, headers/footers, styling
///
/// Usage:
/// 1. Add pdf and printing packages to pubspec.yaml
/// 2. Use PdfService to generate PDFs
/// 3. Preview, print, or share generated documents

import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:path_provider/path_provider.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:printing/printing.dart';

/// PDF document configuration
class PdfConfig {
  final String title;
  final String? author;
  final String? subject;
  final PdfPageFormat pageFormat;
  final pw.EdgeInsets margin;
  final bool showHeader;
  final bool showFooter;
  final bool showPageNumbers;

  PdfConfig({
    required this.title,
    this.author,
    this.subject,
    this.pageFormat = PdfPageFormat.a4,
    this.margin = const pw.EdgeInsets.all(40),
    this.showHeader = true,
    this.showFooter = true,
    this.showPageNumbers = true,
  });
}

/// Table column definition
class PdfTableColumn {
  final String header;
  final double? width;
  final pw.Alignment alignment;

  PdfTableColumn({
    required this.header,
    this.width,
    this.alignment = pw.Alignment.centerLeft,
  });
}

/// PDF generation service
class PdfService {
  pw.ThemeData? _theme;
  pw.Font? _regularFont;
  pw.Font? _boldFont;
  pw.Font? _italicFont;

  /// Initialize fonts (call once at app startup)
  Future<void> initialize() async {
    _regularFont = await PdfGoogleFonts.nunitoRegular();
    _boldFont = await PdfGoogleFonts.nunitoBold();
    _italicFont = await PdfGoogleFonts.nunitoItalic();

    _theme = pw.ThemeData.withFont(
      base: _regularFont,
      bold: _boldFont,
      italic: _italicFont,
    );
  }

  /// Generate a simple PDF document
  Future<Uint8List> generateDocument({
    required PdfConfig config,
    required List<pw.Widget> content,
  }) async {
    final pdf = pw.Document(
      theme: _theme,
      title: config.title,
      author: config.author,
      subject: config.subject,
    );

    pdf.addPage(
      pw.MultiPage(
        pageFormat: config.pageFormat,
        margin: config.margin,
        header: config.showHeader ? (context) => _buildHeader(config, context) : null,
        footer: config.showFooter ? (context) => _buildFooter(config, context) : null,
        build: (context) => content,
      ),
    );

    return pdf.save();
  }

  /// Generate PDF with custom pages
  Future<Uint8List> generateCustomDocument({
    required PdfConfig config,
    required List<pw.Page> pages,
  }) async {
    final pdf = pw.Document(
      theme: _theme,
      title: config.title,
      author: config.author,
      subject: config.subject,
    );

    for (final page in pages) {
      pdf.addPage(page);
    }

    return pdf.save();
  }

  // ============ CONTENT BUILDERS ============

  /// Build header
  pw.Widget _buildHeader(PdfConfig config, pw.Context context) {
    return pw.Container(
      decoration: const pw.BoxDecoration(
        border: pw.Border(bottom: pw.BorderSide(color: PdfColors.grey300)),
      ),
      padding: const pw.EdgeInsets.only(bottom: 10),
      margin: const pw.EdgeInsets.only(bottom: 20),
      child: pw.Row(
        mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
        children: [
          pw.Text(
            config.title,
            style: pw.TextStyle(
              fontSize: 16,
              fontWeight: pw.FontWeight.bold,
            ),
          ),
          pw.Text(
            DateTime.now().toString().split(' ')[0],
            style: const pw.TextStyle(
              fontSize: 10,
              color: PdfColors.grey600,
            ),
          ),
        ],
      ),
    );
  }

  /// Build footer
  pw.Widget _buildFooter(PdfConfig config, pw.Context context) {
    return pw.Container(
      decoration: const pw.BoxDecoration(
        border: pw.Border(top: pw.BorderSide(color: PdfColors.grey300)),
      ),
      padding: const pw.EdgeInsets.only(top: 10),
      margin: const pw.EdgeInsets.only(top: 20),
      child: pw.Row(
        mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
        children: [
          if (config.author != null)
            pw.Text(
              config.author!,
              style: const pw.TextStyle(
                fontSize: 10,
                color: PdfColors.grey600,
              ),
            )
          else
            pw.SizedBox(),
          if (config.showPageNumbers)
            pw.Text(
              'Page ${context.pageNumber} of ${context.pagesCount}',
              style: const pw.TextStyle(
                fontSize: 10,
                color: PdfColors.grey600,
              ),
            ),
        ],
      ),
    );
  }

  // ============ WIDGET BUILDERS ============

  /// Build title widget
  pw.Widget buildTitle(String text, {double fontSize = 24}) {
    return pw.Padding(
      padding: const pw.EdgeInsets.only(bottom: 20),
      child: pw.Text(
        text,
        style: pw.TextStyle(
          fontSize: fontSize,
          fontWeight: pw.FontWeight.bold,
        ),
      ),
    );
  }

  /// Build section header
  pw.Widget buildSectionHeader(String text) {
    return pw.Padding(
      padding: const pw.EdgeInsets.only(top: 15, bottom: 10),
      child: pw.Text(
        text,
        style: pw.TextStyle(
          fontSize: 16,
          fontWeight: pw.FontWeight.bold,
          color: PdfColors.blue800,
        ),
      ),
    );
  }

  /// Build paragraph
  pw.Widget buildParagraph(String text) {
    return pw.Padding(
      padding: const pw.EdgeInsets.only(bottom: 10),
      child: pw.Text(
        text,
        style: const pw.TextStyle(fontSize: 12, lineSpacing: 1.5),
      ),
    );
  }

  /// Build bullet list
  pw.Widget buildBulletList(List<String> items) {
    return pw.Padding(
      padding: const pw.EdgeInsets.only(bottom: 10),
      child: pw.Column(
        crossAxisAlignment: pw.CrossAxisAlignment.start,
        children: items.map((item) => pw.Padding(
          padding: const pw.EdgeInsets.only(bottom: 5),
          child: pw.Row(
            crossAxisAlignment: pw.CrossAxisAlignment.start,
            children: [
              pw.Text('  \u2022  ', style: const pw.TextStyle(fontSize: 12)),
              pw.Expanded(
                child: pw.Text(item, style: const pw.TextStyle(fontSize: 12)),
              ),
            ],
          ),
        )).toList(),
      ),
    );
  }

  /// Build numbered list
  pw.Widget buildNumberedList(List<String> items) {
    return pw.Padding(
      padding: const pw.EdgeInsets.only(bottom: 10),
      child: pw.Column(
        crossAxisAlignment: pw.CrossAxisAlignment.start,
        children: items.asMap().entries.map((entry) => pw.Padding(
          padding: const pw.EdgeInsets.only(bottom: 5),
          child: pw.Row(
            crossAxisAlignment: pw.CrossAxisAlignment.start,
            children: [
              pw.SizedBox(
                width: 25,
                child: pw.Text(
                  '${entry.key + 1}.',
                  style: const pw.TextStyle(fontSize: 12),
                ),
              ),
              pw.Expanded(
                child: pw.Text(entry.value, style: const pw.TextStyle(fontSize: 12)),
              ),
            ],
          ),
        )).toList(),
      ),
    );
  }

  /// Build table
  pw.Widget buildTable({
    required List<PdfTableColumn> columns,
    required List<List<String>> rows,
    bool alternateRowColors = true,
  }) {
    return pw.TableHelper.fromTextArray(
      headerStyle: pw.TextStyle(
        fontWeight: pw.FontWeight.bold,
        fontSize: 11,
      ),
      headerDecoration: const pw.BoxDecoration(
        color: PdfColors.grey200,
      ),
      cellStyle: const pw.TextStyle(fontSize: 10),
      cellAlignments: Map.fromEntries(
        columns.asMap().entries.map(
          (e) => MapEntry(e.key, e.value.alignment),
        ),
      ),
      columnWidths: Map.fromEntries(
        columns.asMap().entries
            .where((e) => e.value.width != null)
            .map((e) => MapEntry(e.key, pw.FixedColumnWidth(e.value.width!))),
      ),
      headers: columns.map((c) => c.header).toList(),
      data: rows,
      cellDecoration: alternateRowColors
          ? (index, data, rowNum) => pw.BoxDecoration(
                color: rowNum.isOdd ? PdfColors.grey50 : null,
              )
          : null,
    );
  }

  /// Build info box
  pw.Widget buildInfoBox(String text, {PdfColor? color}) {
    return pw.Container(
      margin: const pw.EdgeInsets.only(bottom: 10),
      padding: const pw.EdgeInsets.all(10),
      decoration: pw.BoxDecoration(
        color: color ?? PdfColors.blue50,
        borderRadius: const pw.BorderRadius.all(pw.Radius.circular(5)),
        border: pw.Border.all(color: color?.darker ?? PdfColors.blue200),
      ),
      child: pw.Text(text, style: const pw.TextStyle(fontSize: 11)),
    );
  }

  /// Build image from bytes
  pw.Widget buildImage(
    Uint8List imageBytes, {
    double? width,
    double? height,
    pw.BoxFit fit = pw.BoxFit.contain,
  }) {
    final image = pw.MemoryImage(imageBytes);
    return pw.Image(
      image,
      width: width,
      height: height,
      fit: fit,
    );
  }

  /// Build image from asset
  Future<pw.Widget> buildImageFromAsset(
    String assetPath, {
    double? width,
    double? height,
    pw.BoxFit fit = pw.BoxFit.contain,
  }) async {
    final data = await rootBundle.load(assetPath);
    return buildImage(
      data.buffer.asUint8List(),
      width: width,
      height: height,
      fit: fit,
    );
  }

  /// Build divider
  pw.Widget buildDivider({double thickness = 1, PdfColor? color}) {
    return pw.Container(
      margin: const pw.EdgeInsets.symmetric(vertical: 15),
      height: thickness,
      color: color ?? PdfColors.grey300,
    );
  }

  /// Build spacer
  pw.Widget buildSpacer([double height = 20]) {
    return pw.SizedBox(height: height);
  }

  // ============ OUTPUT METHODS ============

  /// Save PDF to file
  Future<File> saveToFile(Uint8List pdfBytes, String fileName) async {
    final directory = await getApplicationDocumentsDirectory();
    final file = File('${directory.path}/$fileName.pdf');
    await file.writeAsBytes(pdfBytes);
    return file;
  }

  /// Save PDF to downloads (Android) or Documents (iOS)
  Future<File> saveToDownloads(Uint8List pdfBytes, String fileName) async {
    Directory directory;
    if (Platform.isAndroid) {
      directory = Directory('/storage/emulated/0/Download');
      if (!await directory.exists()) {
        directory = await getExternalStorageDirectory() ??
                    await getApplicationDocumentsDirectory();
      }
    } else {
      directory = await getApplicationDocumentsDirectory();
    }

    final file = File('${directory.path}/$fileName.pdf');
    await file.writeAsBytes(pdfBytes);
    return file;
  }

  /// Print PDF
  Future<bool> printPdf(Uint8List pdfBytes, {String? name}) async {
    return await Printing.layoutPdf(
      onLayout: (format) async => pdfBytes,
      name: name ?? 'Document',
    );
  }

  /// Share PDF
  Future<bool> sharePdf(Uint8List pdfBytes, {String? fileName}) async {
    return await Printing.sharePdf(
      bytes: pdfBytes,
      filename: fileName ?? 'document.pdf',
    );
  }

  /// Preview PDF (opens system preview)
  Future<void> previewPdf(Uint8List pdfBytes) async {
    await Printing.layoutPdf(
      onLayout: (format) async => pdfBytes,
    );
  }
}

/// Provider for PDF service
final pdfServiceProvider = Provider<PdfService>((ref) {
  final service = PdfService();
  // Note: Call service.initialize() in main.dart before using
  return service;
});

/// Example invoice generator
class InvoiceGenerator {
  final PdfService _pdfService;

  InvoiceGenerator(this._pdfService);

  Future<Uint8List> generateInvoice({
    required String invoiceNumber,
    required String customerName,
    required String customerAddress,
    required List<Map<String, dynamic>> items,
    double taxRate = 0.1,
  }) async {
    double subtotal = 0;
    for (final item in items) {
      subtotal += (item['quantity'] as num) * (item['price'] as num);
    }
    final tax = subtotal * taxRate;
    final total = subtotal + tax;

    final content = [
      _pdfService.buildTitle('INVOICE'),
      pw.Row(
        mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
        crossAxisAlignment: pw.CrossAxisAlignment.start,
        children: [
          pw.Column(
            crossAxisAlignment: pw.CrossAxisAlignment.start,
            children: [
              pw.Text('Bill To:', style: pw.TextStyle(fontWeight: pw.FontWeight.bold)),
              pw.Text(customerName),
              pw.Text(customerAddress),
            ],
          ),
          pw.Column(
            crossAxisAlignment: pw.CrossAxisAlignment.end,
            children: [
              pw.Text('Invoice #: $invoiceNumber'),
              pw.Text('Date: ${DateTime.now().toString().split(' ')[0]}'),
            ],
          ),
        ],
      ),
      _pdfService.buildSpacer(30),
      _pdfService.buildTable(
        columns: [
          PdfTableColumn(header: 'Item'),
          PdfTableColumn(header: 'Qty', width: 50, alignment: pw.Alignment.center),
          PdfTableColumn(header: 'Price', width: 80, alignment: pw.Alignment.centerRight),
          PdfTableColumn(header: 'Total', width: 80, alignment: pw.Alignment.centerRight),
        ],
        rows: items.map((item) => [
          item['name'] as String,
          (item['quantity'] as num).toString(),
          '\$${(item['price'] as num).toStringAsFixed(2)}',
          '\$${((item['quantity'] as num) * (item['price'] as num)).toStringAsFixed(2)}',
        ]).toList(),
      ),
      _pdfService.buildSpacer(20),
      pw.Align(
        alignment: pw.Alignment.centerRight,
        child: pw.Column(
          crossAxisAlignment: pw.CrossAxisAlignment.end,
          children: [
            pw.Text('Subtotal: \$${subtotal.toStringAsFixed(2)}'),
            pw.Text('Tax (${(taxRate * 100).toInt()}%): \$${tax.toStringAsFixed(2)}'),
            pw.Divider(),
            pw.Text(
              'Total: \$${total.toStringAsFixed(2)}',
              style: pw.TextStyle(fontWeight: pw.FontWeight.bold, fontSize: 14),
            ),
          ],
        ),
      ),
    ];

    return _pdfService.generateDocument(
      config: PdfConfig(
        title: 'Invoice $invoiceNumber',
        author: 'Your Company',
        showPageNumbers: false,
      ),
      content: content,
    );
  }
}
