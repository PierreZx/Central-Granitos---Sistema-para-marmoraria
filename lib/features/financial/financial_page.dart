import 'package:flutter/material.dart';
import 'package:central_granitos_sistema/widgets/layout_base.dart';
import 'package:central_granitos_sistema/core/utils/constants.dart';

class FinancialPage extends StatefulWidget {
  const FinancialPage({super.key});

  @override
  State<FinancialPage> createState() => _FinancialPageState();
}

class _FinancialPageState extends State<FinancialPage> {
  // ===================== CONTROLLERS =====================
  final nomeCtrl = TextEditingController();
  final valorCtrl = TextEditingController();
  final dataCtrl = TextEditingController();
  final parcelasCtrl = TextEditingController(text: "1");
  final pesquisaCtrl = TextEditingController();

  bool contaFixa = false;
  bool carregando = false;

  // ===================== UTIL =====================

  DateTime? parseDateBR(String data) {
    try {
      final parts = data.split('/');
      return DateTime(
        int.parse(parts[2]),
        int.parse(parts[1]),
        int.parse(parts[0]),
      );
    } catch (_) {
      return null;
    }
  }

  void formatarData(String value) {
    final nums = value.replaceAll(RegExp(r'\D'), '');
    String result = nums;

    if (nums.length >= 5) {
      result =
          '${nums.substring(0, 2)}/${nums.substring(2, 4)}/${nums.substring(4, nums.length.clamp(4, 8))}';
    } else if (nums.length >= 3) {
      result = '${nums.substring(0, 2)}/${nums.substring(2)}';
    }

    dataCtrl.value = TextEditingValue(
      text: result,
      selection: TextSelection.collapsed(offset: result.length),
    );
  }

  // ===================== MODAIS =====================

  void abrirModalConta({Map<String, dynamic>? divida}) {
    if (divida != null) {
      nomeCtrl.text = divida['nome'] ?? '';
      valorCtrl.text = divida['valor'].toString();
      dataCtrl.text = divida['data_vencimento'] ?? '';
      parcelasCtrl.text = divida['parcelas_totais'].toString();
      contaFixa = divida['permanente'] ?? false;
    }

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(divida == null ? 'Nova Conta' : 'Editar Conta'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(controller: nomeCtrl, decoration: const InputDecoration(labelText: 'Nome')),
              TextField(
                controller: valorCtrl,
                decoration: const InputDecoration(labelText: 'Valor', prefixText: 'R\$ '),
                keyboardType: TextInputType.number,
              ),
              TextField(
                controller: dataCtrl,
                decoration: const InputDecoration(labelText: 'Vencimento (DD/MM/AAAA)'),
                onChanged: formatarData,
              ),
              if (!contaFixa)
                TextField(
                  controller: parcelasCtrl,
                  decoration: const InputDecoration(labelText: 'Parcelas'),
                  keyboardType: TextInputType.number,
                ),
              SwitchListTile(
                title: const Text('Conta fixa mensal'),
                value: contaFixa,
                onChanged: (v) {
                  setState(() => contaFixa = v);
                  Navigator.pop(ctx);
                  abrirModalConta(divida: divida);
                },
              )
            ],
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: COLOR_PRIMARY),
            onPressed: () {
              // lógica de salvar no Firebase virá aqui
              Navigator.pop(ctx);
            },
            child: const Text('Salvar', style: TextStyle(color: Colors.white)),
          )
        ],
      ),
    );
  }

  // ===================== UI COMPONENTS =====================

  Widget criarKPI(String titulo, double valor, Color cor) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: COLOR_WHITE,
        borderRadius: BorderRadius.circular(20),
        boxShadow: const [SHADOW_MD],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(titulo, style: TextStyle(color: Colors.grey.shade600, fontSize: 14)),
          const SizedBox(height: 8),
          Text(
            'R\$ ${valor.toStringAsFixed(2)}',
            style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: cor),
          ),
        ],
      ),
    );
  }

  Widget criarItemDivida(Map<String, dynamic> div) {
    final venc = parseDateBR(div['data_vencimento'] ?? '');
    final vencida = venc != null && venc.isBefore(DateTime.now());

    return Card(
      elevation: 2,
      margin: const EdgeInsets.only(bottom: 10),
      child: ListTile(
        leading: Icon(
          Icons.circle,
          size: 12,
          color: vencida ? COLOR_ERROR : COLOR_SUCCESS,
        ),
        title: Text(div['nome'] ?? '', style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text('Vencimento: ${div['data_vencimento'] ?? 'N/D'}'),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(icon: const Icon(Icons.edit, color: COLOR_PRIMARY), onPressed: () => abrirModalConta(divida: div)),
            IconButton(icon: const Icon(Icons.delete, color: COLOR_ERROR), onPressed: () {}),
          ],
        ),
      ),
    );
  }

  // ===================== BUILD =====================

  @override
  Widget build(BuildContext context) {
    return LayoutBase(
      titulo: 'Financeiro',
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            // KPIs
            LayoutBuilder(builder: (context, constraints) {
              return GridView.count(
                crossAxisCount: constraints.maxWidth < 900 ? 1 : 3,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                mainAxisSpacing: 16,
                crossAxisSpacing: 16,
                childAspectRatio: constraints.maxWidth < 900 ? 3 : 2,
                children: [
                  criarKPI('Saldo em Caixa', 0, COLOR_INFO),
                  criarKPI('Contas a Pagar', 0, COLOR_ERROR),
                  criarKPI('Contas a Receber', 0, COLOR_SUCCESS),
                ],
              );
            }),
            
            const SizedBox(height: 30),

            // Abas de Gerenciamento
            DefaultTabController(
              length: 3,
              child: Column(
                children: [
                  const TabBar(
                    labelColor: COLOR_PRIMARY,
                    indicatorColor: COLOR_PRIMARY,
                    tabs: [
                      Tab(text: 'PAGAR'),
                      Tab(text: 'RECEBER'),
                      Tab(text: 'EXTRATO'),
                    ],
                  ),
                  const SizedBox(height: 20),
                  SizedBox(
                    height: 500,
                    child: TabBarView(
                      children: [
                        // Aba Pagar
                        Column(
                          children: [
                            Row(
                              children: [
                                Expanded(
                                  child: TextField(
                                    controller: pesquisaCtrl,
                                    decoration: const InputDecoration(
                                      labelText: 'Pesquisar conta...',
                                      prefixIcon: Icon(Icons.search),
                                      border: OutlineInputBorder(),
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 10),
                                ElevatedButton.icon(
                                  onPressed: () => abrirModalConta(),
                                  icon: const Icon(Icons.add, color: Colors.white),
                                  label: const Text('NOVA CONTA', style: TextStyle(color: Colors.white)),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: COLOR_PRIMARY,
                                    padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 15),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 20),
                            const Expanded(child: Center(child: Text('Nenhuma conta pendente.'))),
                          ],
                        ),
                        const Center(child: Text('Gerenciamento de Recebíveis')),
                        const Center(child: Text('Histórico de Movimentações')),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}