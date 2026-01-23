import 'package:flutter/material.dart';

class ProductionController extends ChangeNotifier {
  // =========================
  // ESTADO
  // =========================
  bool _isLoading = false;

  int _pendentes = 0;
  int _emProducao = 0;
  int _finalizados = 0;

  // Lista de pedidos (depois vem do Firebase)
  List<Map<String, dynamic>> _pedidos = [];

  // =========================
  // GETTERS
  // =========================
  bool get isLoading => _isLoading;

  int get pendentes => _pendentes;
  int get emProducao => _emProducao;
  int get finalizados => _finalizados;

  List<Map<String, dynamic>> get pedidos => _pedidos;

  // =========================
  // LOAD PRODUÇÃO
  // =========================
  Future<void> loadProducao() async {
    _isLoading = true;
    notifyListeners();

    try {
      // 🔥 Futuro:
      // firebase_service.get_orcamentos_by_status()
      await Future.delayed(const Duration(seconds: 1));

      // =========================
      // MOCK
      // =========================
      _pedidos = [
        {
          "id": "1",
          "cliente": "João Silva",
          "status": "Em Produção",
          "data": DateTime.now().subtract(const Duration(days: 1)),
        },
        {
          "id": "2",
          "cliente": "Maria Souza",
          "status": "Pendente",
          "data": DateTime.now(),
        }
      ];

      _pendentes =
          _pedidos.where((p) => p["status"] == "Pendente").length;
      _emProducao =
          _pedidos.where((p) => p["status"] == "Em Produção").length;
      _finalizados =
          _pedidos.where((p) => p["status"] == "Finalizado").length;
    } catch (e) {
      // log futuro
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // =========================
  // AÇÕES
  // =========================
  void iniciarProducao(String id) {
    final index = _pedidos.indexWhere((p) => p["id"] == id);
    if (index != -1) {
      _pedidos[index]["status"] = "Em Produção";
      loadProducao();
    }
  }

  void finalizarProducao(String id) {
    final index = _pedidos.indexWhere((p) => p["id"] == id);
    if (index != -1) {
      _pedidos[index]["status"] = "Finalizado";
      loadProducao();
    }
  }

  // =========================
  // REFRESH
  // =========================
  Future<void> refresh() async {
    await loadProducao();
  }
}
