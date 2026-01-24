class ProductionModel {
  final String? id;
  final String cliente;
  final String material;
  final String status; // Pendente, Em Produção, Finalizado
  final DateTime data;
  final String? observacoes;

  ProductionModel({
    this.id,
    required this.cliente,
    required this.material,
    this.status = 'Pendente',
    required this.data,
    this.observacoes,
  });

  // 📥 Converte do Firebase (Map) para o Modelo (Objeto)
  factory ProductionModel.fromMap(Map<String, dynamic> map, String id) {
    return ProductionModel(
      id: id,
      cliente: map['cliente'] ?? 'Cliente não informado',
      material: map['material'] ?? 'Material não informado',
      status: map['status'] ?? 'Pendente',
      data: DateTime.parse(map['data'] ?? DateTime.now().toIso8601String()),
      observacoes: map['observacoes'],
    );
  }

  // 📤 Converte do Modelo para Map (Para salvar no Firebase)
  Map<String, dynamic> toMap() {
    return {
      'cliente': cliente,
      'material': material,
      'status': status,
      'data': data.toIso8601String(),
      'observacoes': observacoes,
    };
  }
}