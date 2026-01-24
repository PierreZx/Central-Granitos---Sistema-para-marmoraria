
class OrcamentoModel {
  String? id;
  String clienteNome;
  String clienteContato;
  String clienteEndereco;
  String status;
  DateTime data;
  double totalGeral;
  List<Map<String, dynamic>> itens;

  OrcamentoModel({
    this.id,
    required this.clienteNome,
    required this.clienteContato,
    required this.clienteEndereco,
    this.status = 'Em aberto',
    required this.data,
    this.totalGeral = 0.0,
    this.itens = const [],
  });

  // Converte de Map (Firebase) para o Modelo
  factory OrcamentoModel.fromMap(Map<String, dynamic> map, String id) {
    return OrcamentoModel(
      id: id,
      clienteNome: map['cliente_nome'] ?? '',
      clienteContato: map['cliente_contato'] ?? '',
      clienteEndereco: map['cliente_endereco'] ?? '',
      status: map['status'] ?? 'Em aberto',
      data: DateTime.parse(map['data'] ?? DateTime.now().toIso8601String()),
      totalGeral: (map['total_geral'] as num?)?.toDouble() ?? 0.0,
      itens: List<Map<String, dynamic>>.from(map['itens'] ?? []),
    );
  }

  // Converte do Modelo para Map (Salvar no Firebase)
  Map<String, dynamic> toMap() {
    return {
      'cliente_nome': clienteNome,
      'cliente_contato': clienteContato,
      'cliente_endereco': clienteEndereco,
      'status': status,
      'data': data.toIso8601String(),
      'total_geral': totalGeral,
      'itens': itens,
    };
  }
}