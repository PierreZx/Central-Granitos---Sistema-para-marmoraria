import 'package:flutter/material.dart';
import '../../../core/models/budget_composition.dart';

class BancadaPreview extends StatelessWidget {
  final BancadaComposition composition;

  const BancadaPreview({super.key, required this.composition});

  @override
  Widget build(BuildContext context) {
    return AspectRatio(
      aspectRatio: 1.4,
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.grey.shade100,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.grey.shade300),
        ),
        child: CustomPaint(painter: _BancadaPainter(composition)),
      ),
    );
  }
}

class _BancadaPainter extends CustomPainter {
  final BancadaComposition composition;

  _BancadaPainter(this.composition);

  static const scale = 100.0;

  final pedraPaint = Paint()
    ..color = Colors.blueGrey
    ..style = PaintingStyle.fill;

  final borderPaint = Paint()
    ..color = Colors.black
    ..style = PaintingStyle.stroke
    ..strokeWidth = 2;

  final rodobancaPaint = Paint()
    ..color = Colors.brown
    ..strokeWidth = 6;

  final saiaPaint = Paint()
    ..color = Colors.grey.shade800
    ..strokeWidth = 8;

  final cooktopPaint = Paint()
    ..color = Colors.black
    ..style = PaintingStyle.stroke
    ..strokeWidth = 2;

  final bojoPaint = Paint()
    ..color = Colors.white
    ..style = PaintingStyle.fill;

  @override
  void paint(Canvas canvas, Size size) {
    if (composition.pecas.isEmpty) return;

    // -------- PEÇA 1 --------
    final p1 = composition.pecas[0];
    final r1 = Rect.fromLTWH(0, 0, p1.comprimento * scale, p1.largura * scale);
    _drawPiece(canvas, r1, p1);

    // -------- L --------
    if (composition.tipo == BancadaTipo.l && composition.pecas.length >= 2) {
      final p2 = composition.pecas[1];
      final r2 = Rect.fromLTWH(
        r1.right - p2.largura * scale,
        r1.bottom,
        p2.largura * scale,
        p2.comprimento * scale,
      );
      _drawPiece(canvas, r2, p2);
    }

    // -------- U --------
    if (composition.tipo == BancadaTipo.u && composition.pecas.length >= 3) {
      final p2 = composition.pecas[1];
      final p3 = composition.pecas[2];

      final r2 = Rect.fromLTWH(
        r1.right - p2.largura * scale,
        r1.bottom,
        p2.largura * scale,
        p2.comprimento * scale,
      );

      final r3 = Rect.fromLTWH(
        r1.left,
        r2.bottom - p3.largura * scale,
        p3.comprimento * scale,
        p3.largura * scale,
      );

      _drawPiece(canvas, r2, p2);
      _drawPiece(canvas, r3, p3);
    }
  }

  void _drawPiece(Canvas canvas, Rect rect, BancadaPiece p) {
    // Pedra
    canvas.drawRect(rect, pedraPaint);
    canvas.drawRect(rect, borderPaint);

    // Texto (dimensões)
    final textPainter = TextPainter(
      text: TextSpan(
        text:
            '${p.comprimento.toStringAsFixed(2)} x ${p.largura.toStringAsFixed(2)} m',
        style: const TextStyle(
          color: Colors.white,
          fontSize: 12,
          fontWeight: FontWeight.bold,
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout();

    textPainter.paint(
      canvas,
      Offset(
        rect.center.dx - textPainter.width / 2,
        rect.center.dy - textPainter.height / 2,
      ),
    );

    // =========================
    // RODOBANCA (por lado)
    // =========================
    p.rodobanca.forEach((side, ativo) {
      if (!ativo) return;

      switch (side) {
        case Side.frente:
          canvas.drawLine(rect.bottomLeft, rect.bottomRight, rodobancaPaint);
          break;
        case Side.fundo:
          canvas.drawLine(rect.topLeft, rect.topRight, rodobancaPaint);
          break;
        case Side.esquerda:
          canvas.drawLine(rect.topLeft, rect.bottomLeft, rodobancaPaint);
          break;
        case Side.direita:
          canvas.drawLine(rect.topRight, rect.bottomRight, rodobancaPaint);
          break;
      }
    });

    // =========================
    // SAIA (por lado)
    // =========================
    p.saia.forEach((side, ativo) {
      if (!ativo) return;

      const offset = 6.0;

      switch (side) {
        case Side.frente:
          canvas.drawLine(
            rect.bottomLeft.translate(0, offset),
            rect.bottomRight.translate(0, offset),
            saiaPaint,
          );
          break;
        case Side.fundo:
          canvas.drawLine(
            rect.topLeft.translate(0, -offset),
            rect.topRight.translate(0, -offset),
            saiaPaint,
          );
          break;
        case Side.esquerda:
          canvas.drawLine(
            rect.topLeft.translate(-offset, 0),
            rect.bottomLeft.translate(-offset, 0),
            saiaPaint,
          );
          break;
        case Side.direita:
          canvas.drawLine(
            rect.topRight.translate(offset, 0),
            rect.bottomRight.translate(offset, 0),
            saiaPaint,
          );
          break;
      }
    });

    // =========================
    // EMBUTIDOS (bojo / cooktop)
    // =========================
    for (final e in p.embutidos) {
      final center = Offset(
        rect.left + rect.width * e.offsetX,
        rect.top + rect.height * e.offsetY,
      );

      if (e.tipo == EmbutidoTipo.cooktop) {
        final cooktopRect = Rect.fromCenter(
          center: center,
          width: rect.width * 0.35,
          height: rect.height * 0.25,
        );
        canvas.drawRect(cooktopRect, cooktopPaint);
      }

      if (e.tipo == EmbutidoTipo.bojo) {
        final bojoRect = Rect.fromCenter(
          center: center,
          width: rect.width * 0.4,
          height: rect.height * 0.25,
        );
        canvas.drawRect(bojoRect, bojoPaint);
        canvas.drawRect(bojoRect, borderPaint);
      }
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
