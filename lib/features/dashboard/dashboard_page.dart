import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

// Imports absolutos e corrigidos
import 'package:central_granitos_sistema/widgets/layout_base.dart';
import 'package:central_granitos_sistema/core/utils/constants.dart';
import 'package:central_granitos_sistema/core/services/firebase_service.dart';

class DashboardView extends StatefulWidget {
  const DashboardView({super.key});

  @override
  State<DashboardView> createState() => _DashboardViewState();
}

class _DashboardViewState extends State<DashboardView> {
  bool carregando = true;
  int qtdEstoque = 0;
  int qtdOrcamentos = 0;
  double faturamento = 0.0;
  String? erro;

  @override
  void initState() {
    super.initState();
    carregarDashboard();
  }

  // ===================== FATURAMENTO =====================

  double calcularFaturamentoMesAtual(List<Map<String, dynamic>> extrato) {
    final hoje = DateTime.now();
    double total = 0.0;

    for (var mov in extrato) {
      try {
        // Ajustado para bater com as chaves que você definiu no FirebaseService
        if (mov['tipo']?.toString().toLowerCase() != 'entrada') continue;

        final dataMov = DateTime.parse(mov['data']);
        if (dataMov.month == hoje.month && dataMov.year == hoje.year) {
          total += (mov['valor'] as num).toDouble();
        }
      } catch (_) {}
    }

    return total;
  }

  // ===================== CARREGAR DASH =====================

  Future<void> carregarDashboard() async {
    try {
      setState(() => carregando = true);

      // Buscando dados reais usando seus métodos estáticos
      final estoque = await FirebaseService.getCollection('estoque');
      final orcamentos = await FirebaseService.getCollection('orcamentos');
      final extrato = await FirebaseService.getExtrato();

      if (!mounted) return;

      setState(() {
        qtdEstoque = estoque.length;
        qtdOrcamentos = orcamentos.length;
        faturamento = calcularFaturamentoMesAtual(extrato);
        carregando = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        erro = e.toString();
        carregando = false;
      });
    }
  }

  // ===================== CARD KPI =====================

  Widget cardIndicador({
    required String titulo,
    required String valor,
    required IconData icone,
    required Color cor,
    Color? corTexto,
  }) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: COLOR_WHITE,
        borderRadius: BorderRadius.circular(16),
        boxShadow: const [SHADOW_MD],
      ),
      child: Row(
        children: [
          Container(
            width: 54,
            height: 54,
            decoration: BoxDecoration(
              // Corrigido para evitar o aviso de deprecated
              color: cor.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icone, size: 28, color: cor),
          ),
          const SizedBox(width: 15),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  titulo,
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w500,
                    color: Colors.grey.shade600,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  valor,
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: corTexto ?? COLOR_TEXT,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ===================== BUILD =====================

  @override
  Widget build(BuildContext context) {
    return LayoutBase(
      titulo: 'Dashboard',
      child: carregando
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(color: COLOR_PRIMARY),
                  SizedBox(height: 12),
                  Text('Sincronizando dados...'),
                ],
              ),
            )
          : erro != null
              ? Center(
                  child: Text(
                    'Erro ao carregar dados:\n$erro',
                    style: const TextStyle(color: COLOR_ERROR),
                    textAlign: TextAlign.center,
                  ),
                )
              : SingleChildScrollView(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Bem-vindo de volta!',
                        style: TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.bold,
                          color: COLOR_TEXT,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        'Aqui está o resumo da sua marmoraria hoje.',
                        style: TextStyle(
                          fontSize: 15,
                          color: Colors.grey.shade600,
                        ),
                      ),
                      const SizedBox(height: 30),

                      // KPIs
                      Wrap(
                        spacing: 20,
                        runSpacing: 20,
                        children: [
                          SizedBox(
                            width: 320,
                            child: cardIndicador(
                              titulo: 'Estoque Total',
                              valor: '$qtdEstoque Chapas',
                              icone: Icons.inventory_2_rounded,
                              cor: COLOR_INFO,
                            ),
                          ),
                          SizedBox(
                            width: 320,
                            child: cardIndicador(
                              titulo: 'Orçamentos Ativos',
                              valor: '$qtdOrcamentos',
                              icone: Icons.description_rounded,
                              cor: COLOR_WARNING,
                            ),
                          ),
                          SizedBox(
                            width: 320,
                            child: cardIndicador(
                              titulo: 'Faturamento do Mês',
                              valor: 'R\$ ${NumberFormat.currency(locale: 'pt_BR', symbol: '').format(faturamento)}',
                              icone: Icons.attach_money_rounded,
                              cor: COLOR_SUCCESS,
                              corTexto: COLOR_SUCCESS,
                            ),
                          ),
                        ],
                      ),

                      const SizedBox(height: 40),
                      const Text(
                        'Ações Rápidas',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: COLOR_TEXT,
                        ),
                      ),
                      const SizedBox(height: 15),

                      Wrap(
                        spacing: 15,
                        runSpacing: 15,
                        children: [
                          SizedBox(
                            width: 240,
                            child: ElevatedButton.icon(
                              icon: const Icon(Icons.add_rounded),
                              label: const Text('Novo Orçamento'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: COLOR_PRIMARY,
                                foregroundColor: COLOR_WHITE,
                                minimumSize: const Size.fromHeight(55),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                              ),
                              onPressed: () => Navigator.pushNamed(context, '/orcamentos'),
                            ),
                          ),
                          SizedBox(
                            width: 240,
                            child: OutlinedButton.icon(
                              icon: const Icon(Icons.list_alt_rounded),
                              label: const Text('Gerenciar Estoque'),
                              style: OutlinedButton.styleFrom(
                                minimumSize: const Size.fromHeight(55),
                                foregroundColor: COLOR_PRIMARY,
                                side: const BorderSide(color: COLOR_PRIMARY),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                              ),
                              onPressed: () => Navigator.pushNamed(context, '/estoque'),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
    );
  }
}