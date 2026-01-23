import 'package:flutter/material.dart';

class DashboardController extends ChangeNotifier {
  // =========================
  // ESTADO
  // =========================
  bool _isLoading = false;

  double _saldoCaixa = 0.0;
  int _orcamentosAbertos = 0;
  int _orcamentosEmProducao = 0;
  int _orcamentosFinalizados = 0;
  int _estoqueCritico = 0;

  // =========================
  // GETTERS
  // =========================
  bool get isLoading => _isLoading;

  double get saldoCaixa => _saldoCaixa;
  int get orcamentosAbertos => _orcamentosAbertos;
  int get orcamentosEmProducao => _orcamentosEmProducao;
  int get orcamentosFinalizados => _orcamentosFinalizados;
  int get estoqueCritico => _estoqueCritico;

  // =========================
  // LOAD PRINCIPAL
  // =========================
  Future<void> loadDashboard() async {
    _isLoading = true;
    notifyListeners();

    try {
      // 🔥 Aqui futuramente entra:
      // - Firebase / API
      // - Services (financeiro, produção, estoque)
      await Future.delayed(const Duration(seconds: 1));

      // =========================
      // DADOS MOCKADOS
      // =========================
      _saldoCaixa = 12540.75;
      _orcamentosAbertos = 4;
      _orcamentosEmProducao = 2;
      _orcamentosFinalizados = 7;
      _estoqueCritico = 1;
    } catch (e) {
      // futuramente log / tratamento
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // =========================
  // REFRESH MANUAL
  // =========================
  Future<void> refresh() async {
    await loadDashboard();
  }

  // =========================
  // HELPERS
  // =========================
  bool get temEstoqueCritico => _estoqueCritico > 0;

  bool get temProducaoAtiva => _orcamentosEmProducao > 0;
}
