import 'dart:convert';

import 'package:pdf/pdf.dart';
import 'package:flutter/foundation.dart';
import 'package:pdf/widgets.dart' as pw;

import '../utils/constants.dart';

class PdfService {
  /// Gera o PDF do orçamento e retorna em Base64
  Future<String?> gerarPdfOrcamento(Map<String, dynamic> orcamento) async {
    try {
      final pdf = pw.Document();

      final clienteNome = orcamento['cliente_nome'] ?? 'Cliente';

      final primaryColor = PdfColor.fromInt(COLOR_PRIMARY.toARGB32());
      
      pdf.addPage(
        pw.MultiPage(
          pageFormat: PdfPageFormat.a4,
          margin: const pw.EdgeInsets.all(40),
          build: (context) => [
            // Cabeçalho
            pw.Center(
              child: pw.Text(
                'CENTRAL GRANITOS',
                style: pw.TextStyle(
                  fontSize: 20,
                  fontWeight: pw.FontWeight.bold,
                  color: primaryColor,
                ),
              ),
            ),

            pw.SizedBox(height: 20),

            // Informações do cliente
            pw.Text(
              'INFORMAÇÕES DO CLIENTE',
              style: pw.TextStyle(
                fontSize: 11,
                fontWeight: pw.FontWeight.bold,
              ),
            ),

            pw.SizedBox(height: 8),

            pw.Text('Nome: $clienteNome'),
            pw.Text(
              'Contato: ${orcamento['cliente_contato'] ?? 'N/A'}',
            ),

            pw.SizedBox(height: 20),

            // Itens
            ..._buildItens(orcamento, primaryColor),

            pw.SizedBox(height: 30),

            // Total
            pw.Align(
              alignment: pw.Alignment.centerRight,
              child: pw.Text(
                'TOTAL GERAL: R\$ ${_formatValor(orcamento['total_geral'])}',
                style: pw.TextStyle(
                  fontSize: 16,
                  fontWeight: pw.FontWeight.bold,
                  color: primaryColor,
                ),
              ),
            ),
          ],
        ),
      );

      final Uint8List bytes = await pdf.save();
      return base64Encode(bytes);
    } catch (e) {
      debugPrint('Erro ao gerar PDF: $e');
      return null;
    }
  }

  // =========================
  // MÉTODOS AUXILIARES
  // =========================

  List<pw.Widget> _buildItens(
    Map<String, dynamic> orcamento,
    PdfColor primaryColor,
  ) {
    final List itens = orcamento['itens'] ?? [];

    List<pw.Widget> widgets = [];

    for (int i = 0; i < itens.length; i++) {
      final item = itens[i];
      final qtd = item['quantidade'] ?? 1;
      final precoTotal = _parseDouble(item['preco_total']);
      final precoUnit = precoTotal / qtd;

      widgets.addAll([
        pw.Container(
          width: double.infinity,
          padding: const pw.EdgeInsets.all(8),
          color: primaryColor,
          child: pw.Text(
            '${i + 1}. ${item['ambiente']} - ${item['material']} (Qtd: $qtd)',
            style: pw.TextStyle(
              color: PdfColors.white,
              fontWeight: pw.FontWeight.bold,
              fontSize: 10,
            ),
          ),
        ),

        pw.SizedBox(height: 6),

        pw.Text(
          'Valor Unitário: R\$ ${_formatValor(precoUnit)} | '
          'Subtotal: R\$ ${_formatValor(precoTotal)}',
          style: const pw.TextStyle(fontSize: 9),
        ),

        pw.SizedBox(height: 6),

        ..._buildPecas(item['pecas']),

        pw.SizedBox(height: 12),
      ]);
    }

    return widgets;
  }

  List<pw.Widget> _buildPecas(Map<String, dynamic>? pecas) {
    if (pecas == null) return [];

    return pecas.entries.map((entry) {
      final dados = entry.value;
      return pw.Text(
        '  > ${entry.key.toUpperCase()}: '
        '${dados['l']}m x ${dados['p']}m',
        style: const pw.TextStyle(fontSize: 9),
      );
    }).toList();
  }

  double _parseDouble(dynamic value) {
    return double.tryParse(
          value.toString().replaceAll(',', '.'),
        ) ??
        0;
  }

  String _formatValor(dynamic valor) {
    final v = _parseDouble(valor);
    return v.toStringAsFixed(2);
  }
}
