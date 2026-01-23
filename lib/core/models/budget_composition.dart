/// ===============================
/// TIPOS AUXILIARES
/// ===============================

/// Lados possíveis para encaixe/acabamento
enum Side {
  esquerda,
  direita,
  frente,
  fundo,
}

/// Tipos de abertura possíveis
enum TipoAbertura {
  bojo,
  cooktop,
}

/// ===============================
/// ABERTURA (BOJO / COOKTOP)
/// ===============================

class Abertura {
  final TipoAbertura tipo;
  final double largura;
  final double profundidade;

  /// Posição relativa (0 a 1)
  final double xRelativo;
  final double yRelativo;

  Abertura({
    required this.tipo,
    required this.largura,
    required this.profundidade,
    required this.xRelativo,
    required this.yRelativo,
  });

  double get area => largura * profundidade;

  Map<String, dynamic> toMap() {
    return {
      "tipo": tipo.name,
      "largura": largura,
      "profundidade": profundidade,
      "x_relativo": xRelativo,
      "y_relativo": yRelativo,
      "area": area,
    };
  }
}

/// ===============================
/// PEÇA DE BANCADA
/// ===============================

class BancadaPiece {
  final String nome;
  final double largura;
  final double profundidade;

  String material;
  double precoM2;
  double precoTotal;

  /// Aberturas (bojo, cooktop, etc)
  final List<Abertura> aberturas;

  /// Para bancadas em L ou U
  Side? ladoEncaixe;

  BancadaPiece({
    required this.nome,
    required this.largura,
    required this.profundidade,
    this.material = "",
    this.precoM2 = 0.0,
    this.precoTotal = 0.0,
    this.aberturas = const [],
    this.ladoEncaixe,
  });

  double get areaM2 =>
      double.parse((largura * profundidade).toStringAsFixed(4));

  /// Recalcula o preço total com base no m²
  void calcularPreco() {
    precoTotal = areaM2 * precoM2;
  }

  Map<String, dynamic> toMap() {
    return {
      "nome": nome,
      "largura": largura,
      "profundidade": profundidade,
      "area_m2": areaM2,
      "material": material,
      "preco_m2": precoM2,
      "preco_total": precoTotal,
      "lado_encaixe": ladoEncaixe?.name,
      "aberturas": aberturas.map((a) => a.toMap()).toList(),
    };
  }
}

/// ===============================
/// GERENCIADOR DA COMPOSIÇÃO
/// ===============================

class CompositionManager {
  final List<BancadaPiece> pecas = [];

  void adicionarPeca(BancadaPiece peca) {
    pecas.add(peca);
  }

  void removerPeca(int index) {
    if (index >= 0 && index < pecas.length) {
      pecas.removeAt(index);
    }
  }

  void limpar() {
    pecas.clear();
  }

  double calcularTotalComposicao() {
    double total = 0.0;
    for (final p in pecas) {
      total += p.precoTotal;
    }
    return total;
  }

  double get areaTotal {
    double total = 0.0;
    for (final p in pecas) {
      total += p.areaM2;
    }
    return total;
  }

  List<Map<String, dynamic>> toListMap() {
    return pecas.map((p) => p.toMap()).toList();
  }
}
