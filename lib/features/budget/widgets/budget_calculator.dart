import 'dart:math';

/// ===============================
/// MODELOS AUXILIARES
/// ===============================

class Peca {
  final double largura;
  final double profundidade;

  Peca({
    required this.largura,
    required this.profundidade,
  });

  double get area => largura * profundidade;
}

class ItemOrcamento {
  final String ambiente;
  final String material;
  final int quantidade;
  final double valorMetroQuadrado;
  final Map<String, Peca> pecas;

  ItemOrcamento({
    required this.ambiente,
    required this.material,
    required this.quantidade,
    required this.valorMetroQuadrado,
    required this.pecas,
  });

  double get areaTotal {
    double total = 0;
    for (final p in pecas.values) {
      total += p.area;
    }
    return total * quantidade;
  }

  double get precoTotal => areaTotal * valorMetroQuadrado;
}

/// ===============================
/// CALCULADORA DE ORÇAMENTO
/// ===============================

class BudgetCalculator {
  final List<ItemOrcamento> _itens = [];

  /// Percentuais e adicionais
  double _percentualPerda = 0.1; // 10%
  double _percentualLucro = 0.0;
  double _valorFrete = 0.0;
  double _valorInstalacao = 0.0;
  double _desconto = 0.0;

  /// ===============================
  /// CONFIGURAÇÕES
  /// ===============================

  void setPercentualPerda(double value) {
    _percentualPerda = max(0, value);
  }

  void setPercentualLucro(double value) {
    _percentualLucro = max(0, value);
  }

  void setFrete(double value) {
    _valorFrete = max(0, value);
  }

  void setInstalacao(double value) {
    _valorInstalacao = max(0, value);
  }

  void setDesconto(double value) {
    _desconto = max(0, value);
  }

  /// ===============================
  /// ITENS
  /// ===============================

  void adicionarItem(ItemOrcamento item) {
    _itens.add(item);
  }

  void removerItem(int index) {
    if (index >= 0 && index < _itens.length) {
      _itens.removeAt(index);
    }
  }

  void limparItens() {
    _itens.clear();
  }

  List<ItemOrcamento> get itens => List.unmodifiable(_itens);

  /// ===============================
  /// CÁLCULOS
  /// ===============================

  double get areaTotal {
    double total = 0;
    for (final item in _itens) {
      total += item.areaTotal;
    }
    return total;
  }

  double get areaComPerda {
    return areaTotal * (1 + _percentualPerda);
  }

  double get subtotalMateriais {
    double total = 0;
    for (final item in _itens) {
      total += item.precoTotal;
    }
    return total;
  }

  double get subtotalComPerda {
    return subtotalMateriais * (1 + _percentualPerda);
  }

  double get valorLucro {
    return subtotalComPerda * _percentualLucro;
  }

  double get totalAntesDesconto {
    return subtotalComPerda +
        valorLucro +
        _valorFrete +
        _valorInstalacao;
  }

  double get totalGeral {
    return max(0, totalAntesDesconto - _desconto);
  }

  /// ===============================
  /// EXPORTAÇÃO (MAP / FIREBASE)
  /// ===============================

  Map<String, dynamic> toMap() {
    return {
      "area_total": areaTotal,
      "area_com_perda": areaComPerda,
      "subtotal_materiais": subtotalMateriais,
      "subtotal_com_perda": subtotalComPerda,
      "percentual_perda": _percentualPerda,
      "percentual_lucro": _percentualLucro,
      "valor_lucro": valorLucro,
      "frete": _valorFrete,
      "instalacao": _valorInstalacao,
      "desconto": _desconto,
      "total_geral": totalGeral,
      "itens": _itens.map((item) {
        return {
          "ambiente": item.ambiente,
          "material": item.material,
          "quantidade": item.quantidade,
          "valor_m2": item.valorMetroQuadrado,
          "area_total": item.areaTotal,
          "preco_total": item.precoTotal,
          "pecas": item.pecas.map((k, p) {
            return MapEntry(k, {
              "l": p.largura,
              "p": p.profundidade,
              "area": p.area,
            });
          }),
        };
      }).toList(),
    };
  }
}
