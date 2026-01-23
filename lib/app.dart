import 'package:flutter/material.dart';

import 'core/utils/constants.dart';
import 'features/auth/login_page.dart';
import 'features/dashboard/dashboard_page.dart';
import 'features/inventory/inventory_page.dart';
import 'features/budget/budget_page.dart';
import 'features/financial/financial_page.dart';
import 'features/production/production_page.dart';

class CentralGranitosApp extends StatefulWidget {
  const CentralGranitosApp({super.key});

  @override
  State<CentralGranitosApp> createState() => _CentralGranitosAppState();
}

class _CentralGranitosAppState extends State<CentralGranitosApp> {
  /// 🔐 Simula o page.session do Flet
  /// depois você troca por Provider / Riverpod / GetX
  String? userRole;

  /// 🔁 Controle de rotas (equivalente ao route_change)
Route<dynamic> _onGenerateRoute(RouteSettings settings) {
    final rotaAtual = settings.name ?? '/login';

    if (userRole == null && rotaAtual != '/login') {
      return _buildRoute(const LoginPage(), '/login');
    }

    switch (rotaAtual) {
      case '/login':
        return _buildRoute(const LoginPage(), '/login', center: true);

      case '/dashboard':
        // Alterado de DashboardPage para DashboardView
        return _buildRoute(const DashboardView(), '/dashboard'); 

      case '/estoque':
        return _buildRoute(const InventoryPage(), '/estoque');

      case '/orcamentos':
        // Alterado de BudgetPage para BudgetView
        return _buildRoute(const BudgetView(), '/orcamentos');

      case '/financeiro':
        // Verifique se no seu financial_page.dart a classe é FinancialPage ou FinancialView
        return _buildRoute(const FinancialPage(), '/financeiro');

      case '/producao':
        return _buildRoute(const ProductionPage(), '/producao');

      default:
        return _errorRoute('Rota não encontrada');
    }
  }

  /// 🧱 Builder padrão de páginas
  Route _buildRoute(
    Widget page,
    String routeName, {
    bool center = false,
  }) {
    return MaterialPageRoute(
      settings: RouteSettings(name: routeName),
      builder: (_) => Scaffold(
        backgroundColor: COLOR_BACKGROUND,
        body: center
            ? Center(child: page)
            : page,
      ),
    );
  }

  /// ❌ View de erro amigável (igual você fez no try/except)
  Route _errorRoute(String message) {
    return MaterialPageRoute(
      builder: (_) => Scaffold(
        body: SafeArea(
          child: Center(
            child: Text(
              'Ops! Algo deu errado.\n$message',
              style: const TextStyle(color: Colors.red),
              textAlign: TextAlign.center,
            ),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Marmoraria Central',
      debugShowCheckedModeBanner: false,

      // 🎨 Tema global (equivalente ao page.theme)
      theme: ThemeData(
        colorSchemeSeed: COLOR_PRIMARY,
        brightness: Brightness.light,
        visualDensity: VisualDensity.comfortable,
        scaffoldBackgroundColor: COLOR_BACKGROUND,
      ),

      initialRoute: '/login',
      onGenerateRoute: _onGenerateRoute,
    );
  }
}
