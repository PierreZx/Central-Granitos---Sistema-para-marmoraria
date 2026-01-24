class InventoryModel {
  final String? id;
  final String nome;
  final String tipo; // Ex: Granito, Mármore, Quartzito
  final double largura;
  final double profundidade;
  final int quantidade;
  final double precoM2;
  final String? imagemUrl;

  InventoryModel({
    this.id,
    required this.nome,
    required this.tipo,
    required this.largura,
    required this.profundidade,
    required this.quantidade,
    required this.precoM2,
    this.imagemUrl,
  });

  // ✅ Calcula a área total da chapa/peça
  double get areaTotal => largura * profundidade;

  // ✅ Calcula o valor total em estoque deste item
  double get valorEmEstoque => areaTotal * quantidade * precoM2;

  // 📥 Converte do Firebase (Map) para o Modelo (Objeto)
  factory InventoryModel.fromMap(Map<String, dynamic> map, String id) {
    return InventoryModel(
      id: id,
      nome: map['nome'] ?? '',
      tipo: map['tipo'] ?? 'Outros',
      largura: (map['largura'] as num?)?.toDouble() ?? 0.0,
      profundidade: (map['profundidade'] as num?)?.toDouble() ?? 0.0,
      quantidade: (map['quantidade'] as num?)?.toInt() ?? 0,
      precoM2: (map['preco_m2'] as num?)?.toDouble() ?? 0.0,
      imagemUrl: map['imagem_url'],
    );
  }

  // 📤 Converte do Modelo para Map (Para salvar no Firebase)
  Map<String, dynamic> toMap() {
    return {
      'nome': nome,
      'tipo': tipo,
      'largura': largura,
      'profundidade': profundidade,
      'quantidade': quantidade,
      'preco_m2': precoM2,
      'imagem_url': imagemUrl,
    };
  }
}