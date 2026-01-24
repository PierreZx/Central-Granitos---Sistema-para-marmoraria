import 'package:flutter/material.dart';

import 'core/utils/constants.dart';
import 'features/auth/login_page.dart';
import 'features/dashboard/dashboard_page.dart';
import 'features/inventory/inventory_page.dart';
import 'features/budget/budget_page.dart';
import 'features/budget/budget_form_page.dart'; // ✅ 1. Importe a nova página aqui
import 'features/financial/financial_page.dart';
import 'features/production/production_page.dart';

class CentralGranitosApp extends StatefulWidget {
  const CentralGranitosApp({super.key});

  @override
  State<CentralGranitosApp> createState() => _CentralGranitosAppState();
}

class _CentralGranitosAppState extends State<CentralGranitosApp> {
  String? userRole;

  void _setRole(String role) {
    setState(() {
      userRole = role;
    });
  }

  Route<dynamic> _onGenerateRoute(RouteSettings settings) {
    final rotaAtual = settings.name ?? '/login';

    if (userRole == null && rotaAtual != '/login') {
      return _buildRoute(LoginPage(onLoginSuccess: _setRole), '/login', center: true);
    }

    switch (rotaAtual) {
      case '/login':
        return _buildRoute(LoginPage(onLoginSuccess: _setRole), '/login', center: true);
      case '/dashboard':
        return _buildRoute(const DashboardView(), '/dashboard');
      case '/estoque':
        return _buildRoute(const InventoryPage(), '/estoque');
      case '/orcamentos':
        return _buildRoute(const BudgetView(), '/orcamentos');
      
      // ✅ 2. Adicione a rota para o formulário de orçamento
      case '/orcamento_form':
        // Recebe os dados do orçamento se houver (para edição)
        final args = settings.arguments as Map<String, dynamic>?;
        return _buildRoute(BudgetFormPage(orcamentoExistente: args), '/orcamento_form');

      case '/financeiro':
        return _buildRoute(const FinancialPage(), '/financeiro');
      case '/producao':
        return _buildRoute(const ProductionPage(), '/producao');
      default:
        return _errorRoute('Rota não encontrada: $rotaAtual');
    }
  }

  Route _buildRoute(Widget page, String routeName, {bool center = false}) {
    return MaterialPageRoute(
      settings: RouteSettings(name: routeName),
      builder: (_) => Scaffold(
        backgroundColor: COLOR_BACKGROUND,
        body: center ? Center(child: page) : page,
      ),
    );
  }

  Route _errorRoute(String message) {
    return MaterialPageRoute(
      builder: (_) => Scaffold(
        body: Center(child: Text(message, style: const TextStyle(color: Colors.red))),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Marmoraria Central',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorSchemeSeed: COLOR_PRIMARY,
        useMaterial3: true,
      ),
      initialRoute: '/login',
      onGenerateRoute: _onGenerateRoute,
    );
  }
}