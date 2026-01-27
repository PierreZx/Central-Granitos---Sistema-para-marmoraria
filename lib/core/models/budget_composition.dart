enum Side { frente, fundo, esquerda, direita }

enum BancadaTipo { reta, l, u }

enum EmbutidoTipo { bojo, cooktop }

/// ------------------------------
/// EMBUTIDO
/// ------------------------------
class Embutido {
  final EmbutidoTipo tipo;

  /// posição relativa na peça (0.0 a 1.0)
  final double offsetX;
  final double offsetY;

  Embutido({required this.tipo, this.offsetX = 0.5, this.offsetY = 0.5});

  Map<String, dynamic> toMap() => {
    'tipo': tipo.name,
    'offsetX': offsetX,
    'offsetY': offsetY,
  };
}

/// ------------------------------
/// PEÇA DA BANCADA
/// ------------------------------
class BancadaPiece {
  final String nome;

  double comprimento;
  double largura;

  /// 🔢 Quantidade de peças iguais
  int quantidade;

  /// Lado onde a peça encaixa em outra (se existir)
  Side? ladoEncaixe;

  /// Rodobanca por lado
  Map<Side, bool> rodobanca;

  /// Saia por lado
  Map<Side, bool> saia;

  /// Bojo / Cooktop (opcionais)
  List<Embutido> embutidos;

  BancadaPiece({
    required this.nome,
    required this.comprimento,
    required this.largura,
    this.quantidade = 1,
    this.ladoEncaixe,
    Map<Side, bool>? rodobanca,
    Map<Side, bool>? saia,
    List<Embutido>? embutidos,
  }) : rodobanca =
           rodobanca ??
           {
             Side.frente: false,
             Side.fundo: false,
             Side.esquerda: false,
             Side.direita: false,
           },
       saia =
           saia ??
           {
             Side.frente: false,
             Side.fundo: false,
             Side.esquerda: false,
             Side.direita: false,
           },
       embutidos = embutidos ?? [];

  // ------------------------------
  // ÁREA
  // ------------------------------
  double get areaUnit => comprimento * largura;

  double get areaTotal => areaUnit * quantidade;

  // ------------------------------
  // ML
  // ------------------------------
  double _comprimentoDoLado(Side side) {
    switch (side) {
      case Side.frente:
      case Side.fundo:
        return comprimento;
      case Side.esquerda:
      case Side.direita:
        return largura;
    }
  }

  double mlRodobancaUnit() {
    double ml = 0;
    rodobanca.forEach((side, ativo) {
      if (!ativo) return;
      if (ladoEncaixe == side) return;
      ml += _comprimentoDoLado(side);
    });
    return ml;
  }

  double mlSaiaUnit() {
    double ml = 0;
    saia.forEach((side, ativo) {
      if (!ativo) return;
      if (ladoEncaixe == side) return;
      ml += _comprimentoDoLado(side);
    });
    return ml;
  }

  double get mlRodobancaTotal => mlRodobancaUnit() * quantidade;

  double get mlSaiaTotal => mlSaiaUnit() * quantidade;

  double get mlTotal => mlRodobancaTotal + mlSaiaTotal;

  // ------------------------------
  // EMBUTIDOS
  // ------------------------------
  int get totalBojos =>
      embutidos.where((e) => e.tipo == EmbutidoTipo.bojo).length * quantidade;

  int get totalCooktops =>
      embutidos.where((e) => e.tipo == EmbutidoTipo.cooktop).length *
      quantidade;

  bool get temBojo => embutidos.any((e) => e.tipo == EmbutidoTipo.bojo);

  bool get temCooktop => embutidos.any((e) => e.tipo == EmbutidoTipo.cooktop);

  set temBojo(bool value) {
    if (value && !temBojo) {
      embutidos.add(Embutido(tipo: EmbutidoTipo.bojo));
    } else if (!value) {
      embutidos.removeWhere((e) => e.tipo == EmbutidoTipo.bojo);
    }
  }

  set temCooktop(bool value) {
    if (value && !temCooktop) {
      embutidos.add(Embutido(tipo: EmbutidoTipo.cooktop));
    } else if (!value) {
      embutidos.removeWhere((e) => e.tipo == EmbutidoTipo.cooktop);
    }
  }

  // ------------------------------
  // SERIALIZAÇÃO
  // ------------------------------
  Map<String, dynamic> toMap() => {
    'nome': nome,
    'quantidade': quantidade,
    'comprimento': comprimento,
    'largura': largura,
    'area_unit': areaUnit,
    'area_total': areaTotal,
    'lado_encaixe': ladoEncaixe?.name,
    'rodobanca': rodobanca.map((k, v) => MapEntry(k.name, v)),
    'saia': saia.map((k, v) => MapEntry(k.name, v)),
    'ml_rodobanca_total': mlRodobancaTotal,
    'ml_saia_total': mlSaiaTotal,
    'bojos': totalBojos,
    'cooktops': totalCooktops,
    'embutidos': embutidos.map((e) => e.toMap()).toList(),
  };
}

/// ------------------------------
/// COMPOSIÇÃO DA BANCADA
/// ------------------------------
class BancadaComposition {
  BancadaTipo tipo;
  List<BancadaPiece> pecas;

  BancadaComposition({required this.tipo, required this.pecas});

  // ------------------------------
  // TOTAIS
  // ------------------------------
  double get areaTotal => pecas.fold(0, (sum, p) => sum + p.areaTotal);

  double get mlRodobancaTotal =>
      pecas.fold(0, (sum, p) => sum + p.mlRodobancaTotal);

  double get mlSaiaTotal => pecas.fold(0, (sum, p) => sum + p.mlSaiaTotal);

  int get totalBojos => pecas.fold(0, (sum, p) => sum + p.totalBojos);

  int get totalCooktops => pecas.fold(0, (sum, p) => sum + p.totalCooktops);

  // ------------------------------
  // CÁLCULO FINAL 💰
  // ------------------------------
  double calcularTotal({
    required double precoM2,
    required double precoMLRodobanca,
    required double precoMLSaia,
    required double precoBojo,
    required double precoCooktop,
  }) {
    return (areaTotal * precoM2) +
        (mlRodobancaTotal * precoMLRodobanca) +
        (mlSaiaTotal * precoMLSaia) +
        (totalBojos * precoBojo) +
        (totalCooktops * precoCooktop);
  }

  Map<String, dynamic> toMap({
    required double precoM2,
    required double precoMLRodobanca,
    required double precoMLSaia,
    required double precoBojo,
    required double precoCooktop,
  }) {
    return {
      'tipo': tipo.name,
      'area_total': areaTotal,
      'ml_rodobanca_total': mlRodobancaTotal,
      'ml_saia_total': mlSaiaTotal,
      'total_bojos': totalBojos,
      'total_cooktops': totalCooktops,
      'precos': {
        'm2': precoM2,
        'ml_rodobanca': precoMLRodobanca,
        'ml_saia': precoMLSaia,
        'bojo': precoBojo,
        'cooktop': precoCooktop,
      },
      'total': calcularTotal(
        precoM2: precoM2,
        precoMLRodobanca: precoMLRodobanca,
        precoMLSaia: precoMLSaia,
        precoBojo: precoBojo,
        precoCooktop: precoCooktop,
      ),
      'pecas': pecas.map((p) => p.toMap()).toList(),
    };
  }
}
