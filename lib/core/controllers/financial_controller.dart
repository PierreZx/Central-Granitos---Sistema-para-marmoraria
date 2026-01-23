import 'package:flutter/material.dart';

class FinancialController extends ChangeNotifier {
  // =========================
  // ESTADO
  // =========================
  bool _isLoading = false;

  double _saldoCaixa = 0.0;
  double _totalEntradas = 0.0;
  double _totalSaidas = 0.0;

  // =========================
  // GETTERS
  // =========================
  bool get isLoading => _isLoading;

  double get saldoCaixa => _saldoCaixa;
  double get totalEntradas => _totalEntradas;
  double get totalSaidas => _totalSaidas;

  // =========================
  // LOAD FINANCEIRO
  // =========================
  Future<void> loadFinanceiro() async {
    _isLoading = true;
    notifyListeners();

    try {
      // 🔥 Futuro:
      // - Firebase / API REST
      // - firebase_service.get_saldo_caixa()
      await Future.delayed(const Duration(milliseconds: 800));

      // =========================
      // MOCK (temporário)
      // =========================
      _totalEntradas = 18450.00;
      _totalSaidas = 5910.25;
      _saldoCaixa = _totalEntradas - _totalSaidas;
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
  void registrarEntrada(double valor) {
    _totalEntradas += valor;
    _saldoCaixa += valor;
    notifyListeners();
  }

  void registrarSaida(double valor) {
    _totalSaidas += valor;
    _saldoCaixa -= valor;
    notifyListeners();
  }

  // =========================
  // REFRESH
  // =========================
  Future<void> refresh() async {
    await loadFinanceiro();
  }
}
