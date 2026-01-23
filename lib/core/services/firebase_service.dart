import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class FirebaseService {
  static const String projectId = 'marmoraria-app';
  static const String baseUrl =
      'https://firestore.googleapis.com/v1/projects/$projectId/databases/(default)/documents';

  /* ======================================================
   * CONEXÃO
   * ====================================================== */

  static Future<bool> verificarConexao() async {
    try {
      final socket = await Socket.connect('8.8.8.8', 53,
          timeout: const Duration(seconds: 2));
      socket.destroy();
      return true;
    } catch (_) {
      return false;
    }
  }

  /* ======================================================
   * CONVERSORES
   * ====================================================== */

  static Map<String, dynamic> _toFirestore(Map<String, dynamic> data) {
    final Map<String, dynamic> fields = {};

    data.forEach((key, value) {
      if (value == null) {
        fields[key] = {'nullValue': null};
      } else if (value is bool) {
        fields[key] = {'booleanValue': value};
      } else if (value is int) {
        fields[key] = {'integerValue': value.toString()};
      } else if (value is double) {
        fields[key] = {'doubleValue': value};
      } else if (value is List) {
        fields[key] = {
          'arrayValue': {
            'values': value.map((v) {
              if (v is Map<String, dynamic>) {
                return {'mapValue': _toFirestore(v)};
              }
              return {'stringValue': v.toString()};
            }).toList()
          }
        };
      } else if (value is Map<String, dynamic>) {
        fields[key] = {'mapValue': _toFirestore(value)};
      } else {
        fields[key] = {'stringValue': value.toString()};
      }
    });

    return {'fields': fields};
  }

  static dynamic _fromValue(Map<String, dynamic> v) {
    if (v.containsKey('stringValue')) return v['stringValue'];
    if (v.containsKey('integerValue')) return int.parse(v['integerValue']);
    if (v.containsKey('doubleValue')) return v['doubleValue'];
    if (v.containsKey('booleanValue')) return v['booleanValue'];
    if (v.containsKey('nullValue')) return null;

    if (v.containsKey('arrayValue')) {
      return (v['arrayValue']['values'] ?? [])
          .map((e) => _fromValue(e))
          .toList();
    }

    if (v.containsKey('mapValue')) {
      final Map<String, dynamic> map = {};
      (v['mapValue']['fields'] ?? {}).forEach((k, val) {
        map[k] = _fromValue(val);
      });
      return map;
    }

    return null;
  }

  static Map<String, dynamic> _fromFirestore(Map<String, dynamic> doc) {
    final Map<String, dynamic> obj = {};
    obj['id'] = doc['name'].split('/').last;

    (doc['fields'] ?? {}).forEach((k, v) {
      obj[k] = _fromValue(v);
    });

    return obj;
  }

  /* ======================================================
   * CRUD BASE
   * ====================================================== */

  static Future<List<Map<String, dynamic>>> getCollection(
      String collection) async {
    if (!await verificarConexao()) return [];

    final res =
        await http.get(Uri.parse('$baseUrl/$collection?pageSize=300'));

    if (res.statusCode != 200) return [];

    final body = jsonDecode(res.body);
    if (!body.containsKey('documents')) return [];

    return body['documents']
        .map<Map<String, dynamic>>((d) => _fromFirestore(d))
        .toList();
  }

  static Future<bool> addDocument(
      String collection, Map<String, dynamic> data) async {
    final res = await http.post(
      Uri.parse('$baseUrl/$collection'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(_toFirestore(data)),
    );
    return res.statusCode == 200;
  }

  static Future<bool> updateDocument(
      String collection, String id, Map<String, dynamic> data) async {
    final mask = data.keys.map((k) => 'updateMask.fieldPaths=$k').join('&');
    final url = '$baseUrl/$collection/$id?$mask';

    final res = await http.patch(
      Uri.parse(url),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(_toFirestore(data)),
    );
    return res.statusCode == 200;
  }

  static Future<bool> deleteDocument(
      String collection, String id) async {
    final res =
        await http.delete(Uri.parse('$baseUrl/$collection/$id'));
    return res.statusCode == 200;
  }

  /* ======================================================
   * FINANCEIRO
   * ====================================================== */

  static Future<double> getSaldoCaixa() async {
    final movs = await getCollection('financeiro');
    double saldo = 0;

    for (final m in movs) {
      final valor = double.tryParse(
              m['valor'].toString().replaceAll(',', '.')) ??
          0;
      final tipo = (m['tipo'] ?? '').toString().toUpperCase();

      if (['ENTRADA', 'RECEITA'].contains(tipo)) {
        saldo += valor;
      } else if (['SAIDA', 'DESPESA'].contains(tipo)) {
        saldo -= valor;
      }
    }
    return saldo;
  }

  static Future<List<Map<String, dynamic>>> getExtrato() async {
    final dados = await getCollection('financeiro');
    dados.sort((a, b) =>
        (b['data'] ?? '').compareTo(a['data'] ?? ''));
    return dados;
  }

  static Future<bool> addMovimentacao(
      String tipo, double valor, String descricao,
      {String origem = 'Manual'}) {
    return addDocument('financeiro', {
      'tipo': tipo,
      'valor': valor,
      'descricao': descricao,
      'origem': origem,
      'data': DateTime.now().toIso8601String(),
      'status': tipo == 'Saida' ? 'Pago' : 'Recebido',
    });
  }

  /* ======================================================
   * PRODUÇÃO
   * ====================================================== */

  static Future<List<Map<String, dynamic>>> getOrcamentosByStatus(
      String status) async {
    final todos = await getCollection('orcamentos');
    return todos.where((o) => o['status'] == status).toList();
  }
}
