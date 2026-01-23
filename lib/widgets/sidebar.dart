import 'package:flutter/material.dart';
import '../core/utils/constants.dart';

class Sidebar extends StatelessWidget {
  final String userRole;
  final String currentRoute;
  final bool isMobile;
  final VoidCallback onLogout;

  const Sidebar({
    super.key,
    required this.userRole,
    required this.currentRoute,
    this.isMobile = false,
    required this.onLogout,
  });

  @override
  Widget build(BuildContext context) {
    final menuItems = userRole == "admin"
        ? [
            _MenuItem("Dashboard", Icons.grid_view_rounded, "/dashboard"),
            _MenuItem("Estoque", Icons.inventory_2_outlined, "/estoque"),
            _MenuItem("Orçamentos", Icons.receipt_long_rounded, "/orcamentos"),
            _MenuItem("Financeiro", Icons.account_balance_wallet_rounded, "/financeiro"),
            _MenuItem("Produção", Icons.precision_manufacturing_outlined, "/producao"),
          ]
        : [
            _MenuItem("Produção", Icons.precision_manufacturing_outlined, "/producao"),
          ];

    return Container(
      width: isMobile ? null : 260,
      decoration: BoxDecoration(
        color: COLOR_WHITE,
        border: isMobile
            ? null
            : const Border(
                right: BorderSide(color: Color(0xFFF0F0F0), width: 1),
              ),
        boxShadow: isMobile ? null : const [SHADOW_MD],
      ),
      padding: EdgeInsets.fromLTRB(15, 25, 15, isMobile ? 20 : 10),
      child: Column(
        children: [
          _buildHeader(),
          const SizedBox(height: 30),
          Expanded(
            child: Column(
              children: menuItems
                  .map((item) => _buildMenuItem(context, item))
                  .toList(),
            ),
          ),
          const Divider(height: 1),
          const SizedBox(height: 10),
          _buildLogout(context),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      children: [
        Container(
          width: 38,
          height: 38,
          decoration: BoxDecoration(
            color: COLOR_PRIMARY,
            borderRadius: BorderRadius.circular(10),
          ),
          child: const Icon(
            Icons.precision_manufacturing_rounded,
            color: Colors.white,
            size: 20,
          ),
        ),
        const SizedBox(width: 12),
        const Text(
          "CENTRAL",
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: COLOR_PRIMARY,
            letterSpacing: 1,
          ),
        ),
      ],
    );
  }

  Widget _buildMenuItem(BuildContext context, _MenuItem item, {bool danger = false}) {
    final isActive = currentRoute == item.route;

    final Color itemColor = danger
        ? Colors.red.shade600
        : (isActive ? COLOR_PRIMARY : Colors.blueGrey.shade700);

    // CORREÇÃO: Lógica do hoverBg consertada usando operador ternário
    final Color hoverBg = danger
        ? Colors.red.shade50
        : COLOR_PRIMARY.withValues(alpha: 0.1);

    return InkWell(
      onTap: () {
        if (!isActive) {
          Navigator.pushReplacementNamed(context, item.route);
        }
      },
      borderRadius: BorderRadius.circular(12),
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 15),
        decoration: BoxDecoration(
          color: isActive ? hoverBg : Colors.transparent,
          borderRadius: BorderRadius.circular(12),
          border: isActive && !danger
              ? const Border(
                  left: BorderSide(color: COLOR_PRIMARY, width: 3),
                )
              : null,
        ),
        child: Row(
          children: [
            Icon(item.icon, color: itemColor, size: 22),
            const SizedBox(width: 15),
            Text(
              item.label,
              style: TextStyle(
                fontSize: 14,
                fontWeight: isActive ? FontWeight.bold : FontWeight.w500,
                color: itemColor,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLogout(BuildContext context) {
    return InkWell(
      onTap: () {
        onLogout();
        Navigator.pushNamedAndRemoveUntil(context, "/login", (route) => false);
      },
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 15),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          children: [
            Icon(Icons.logout_rounded, color: Colors.red.shade600, size: 22),
            const SizedBox(width: 15),
            Text(
              "Sair do Sistema",
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w500,
                color: Colors.red.shade600,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _MenuItem {
  final String label;
  final IconData icon;
  final String route;

  _MenuItem(this.label, this.icon, this.route);
}