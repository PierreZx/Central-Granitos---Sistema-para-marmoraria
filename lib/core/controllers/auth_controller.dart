import 'package:flutter/material.dart';

class AuthController extends ChangeNotifier {
  // =========================
  // ESTADO
  // =========================
  bool _isAuthenticated = false;
  bool _isLoading = false;
  String? _userEmail;
  String? _userRole;

  // =========================
  // GETTERS
  // =========================
  bool get isAuthenticated => _isAuthenticated;
  bool get isLoading => _isLoading;
  String? get userEmail => _userEmail;
  String? get userRole => _userRole;

  // =========================
  // LOGIN
  // =========================
  Future<bool> login({
    required String email,
    required String password,
  }) async {
    _isLoading = true;
    notifyListeners();

    try {
      // 🔥 AQUI futuramente entra Firebase Auth ou API
      await Future.delayed(const Duration(seconds: 1));

      // Simulação de autenticação
      if (email.isEmpty || password.isEmpty) {
        throw Exception('Credenciais inválidas');
      }

      _isAuthenticated = true;
      _userEmail = email;

      // Simulação de cargo
      _userRole = _defineRole(email);

      return true;
    } catch (e) {
      _isAuthenticated = false;
      _userEmail = null;
      _userRole = null;
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // =========================
  // LOGOUT
  // =========================
  void logout() {
    _isAuthenticated = false;
    _userEmail = null;
    _userRole = null;
    notifyListeners();
  }

  // =========================
  // CONTROLE DE PERMISSÕES
  // =========================
  bool isAdmin() => _userRole == 'admin';

  bool isProducao() => _userRole == 'producao';

  bool isFinanceiro() => _userRole == 'financeiro';

  // =========================
  // MÉTODO PRIVADO
  // =========================
  String _defineRole(String email) {
    if (email.contains('producao')) return 'producao';
    if (email.contains('financeiro')) return 'financeiro';
    return 'admin';
  }
}
