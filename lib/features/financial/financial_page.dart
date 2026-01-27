import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:central_granitos_sistema/widgets/layout_base.dart';
import 'package:central_granitos_sistema/core/utils/constants.dart';
import 'package:central_granitos_sistema/core/services/firebase_service.dart';

class FinancialPage extends StatefulWidget {
  const FinancialPage({super.key});

  @override
  State<FinancialPage> createState() => _FinancialPageState();
}

class _FinancialPageState extends State<FinancialPage>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  bool carregando = true;
  List<Map<String, dynamic>> movimentacoes = [];
  List<Map<String, dynamic>> contasFixas = [];
  List<Map<String, dynamic>> servicosConcluidos = [];
  double saldoCaixa = 0;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    atualizarDados();
  }

  Future<void> atualizarDados() async {
    setState(() => carregando = true);
    final extrato = await FirebaseService.getExtrato(); //
    final saldo = await FirebaseService.getSaldoCaixa(); //
    final fixas = await FirebaseService.getCollection('contas_fixas');
    final concluidos = await FirebaseService.getCollection('producao');

    if (mounted) {
      setState(() {
        movimentacoes = extrato;
        saldoCaixa = saldo;
        contasFixas = fixas;
        // Filtra apenas o que está finalizado na produção
        servicosConcluidos = concluidos
            .where((o) => o['status'] == 'Finalizado')
            .toList();
        carregando = false;
      });
    }
  }

  // --- LÓGICA DE CORES DE VENCIMENTO ---
  Color _getCorStatus(DateTime data) {
    final hoje = DateTime.now();
    final diferenca = data.difference(hoje).inDays;
    if (hoje.isAfter(data) || diferenca == 0) return Colors.red;
    if (diferenca <= 3) return Colors.yellow.shade700;
    return Colors.green;
  }

  // --- MODAL DE CONTA FIXA (COM PARCELAMENTO) ---
  void abrirModalContaFixa({Map<String, dynamic>? item}) {
    final nomeCtrl = TextEditingController(text: item?['nome'] ?? '');
    final valorCtrl = TextEditingController(
      text: item?['valor']?.toString() ?? '',
    );
    final parcelasCtrl = TextEditingController(
      text: item?['parcelas_total']?.toString() ?? '1',
    );
    DateTime dataSelecionada = item != null
        ? DateTime.parse(item['data'])
        : DateTime.now();
    bool isMensal = item?['is_mensal'] ?? false;

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setModalState) => AlertDialog(
          title: Text(item == null ? 'Nova Conta Fixa' : 'Editar Conta'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: nomeCtrl,
                  decoration: const InputDecoration(labelText: 'Nome da Conta'),
                ),
                TextField(
                  controller: valorCtrl,
                  decoration: const InputDecoration(labelText: 'Valor Total'),
                  keyboardType: TextInputType.number,
                ),
                SwitchListTile(
                  title: const Text("Repetir todo mês?"),
                  value: isMensal,
                  onChanged: (v) => setModalState(() => isMensal = v),
                ),
                if (!isMensal)
                  TextField(
                    controller: parcelasCtrl,
                    decoration: const InputDecoration(
                      labelText: 'Nº de Parcelas',
                    ),
                    keyboardType: TextInputType.number,
                  ),
                ListTile(
                  title: Text(
                    "Data/Vencimento: ${DateFormat('dd/MM/yyyy').format(dataSelecionada)}",
                  ),
                  trailing: const Icon(Icons.calendar_month),
                  onTap: () async {
                    final picked = await showDatePicker(
                      context: context,
                      initialDate: dataSelecionada,
                      firstDate: DateTime(2000),
                      lastDate: DateTime(2100),
                    );
                    if (picked != null) {
                      setModalState(() => dataSelecionada = picked);
                    }
                  },
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cancelar'),
            ),
            ElevatedButton(
              onPressed: () async {
                final navigator = Navigator.of(context);

                final valor = double.tryParse(valorCtrl.text) ?? 0;
                final totalParc = int.tryParse(parcelasCtrl.text) ?? 1;

                final dados = {
                  'nome': nomeCtrl.text,
                  'valor': valor,
                  'data': dataSelecionada.toIso8601String(),
                  'is_mensal': isMensal,
                  'parcelas_total': totalParc,
                  'parcela_atual': 1,
                  'pago': false,
                };

                if (item == null) {
                  await FirebaseService.addDocument('contas_fixas', dados);
                } else {
                  await FirebaseService.updateDocument(
                    'contas_fixas',
                    item['id'],
                    dados,
                  );
                }

                if (!mounted) return;

                navigator.pop();
                atualizarDados();
              },

              child: const Text('Salvar'),
            ),
          ],
        ),
      ),
    );
  }

  // --- LÓGICA DE PAGAMENTO (DESCONTA DO CAIXA) ---
  void confirmarPagamento(Map<String, dynamic> conta) async {
    // 1. Lança saída no extrato
    await FirebaseService.addMovimentacao(
      'Saida',
      conta['valor'],
      "PAGAMENTO: ${conta['nome']}",
    );

    // 2. Atualiza a conta fixa (desconta parcela ou marca como pago)
    if (conta['parcela_atual'] < conta['parcelas_total']) {
      final novaData = DateTime.parse(
        conta['data'],
      ).add(const Duration(days: 30));
      await FirebaseService.updateDocument('contas_fixas', conta['id'], {
        'parcela_atual': conta['parcela_atual'] + 1,
        'data': novaData.toIso8601String(),
      });
    } else {
      await FirebaseService.updateDocument('contas_fixas', conta['id'], {
        'pago': true,
      });
    }
    atualizarDados();
  }

  // --- LÓGICA DE RECEBIMENTO (ENTRA NO CAIXA) ---
  void confirmarRecebimento(Map<String, dynamic> servico) async {
    final valor = (servico['total_geral'] as num?)?.toDouble() ?? 0.0;
    await FirebaseService.addMovimentacao(
      'Entrada',
      valor,
      "RECEBIMENTO: ${servico['cliente']}",
    );
    await FirebaseService.updateDocument('producao', servico['id'], {
      'pago': true,
    }); //
    atualizarDados();
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBase(
      titulo: 'Gestão Financeira',
      child: Column(
        children: [
          // CABEÇALHO DE SALDO
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            color: COLOR_PRIMARY,
            child: Text(
              'Saldo em Caixa: R\$ ${NumberFormat.currency(locale: 'pt_BR', symbol: '').format(saldoCaixa)}',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 22,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          TabBar(
            controller: _tabController,
            labelColor: COLOR_PRIMARY,
            tabs: const [
              Tab(text: "Dia a Dia"),
              Tab(text: "Contas Fixas"),
              Tab(text: "Recebimentos"),
            ],
          ),
          Expanded(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildListaExtrato(),
                _buildListaContasFixas(),
                _buildListaRecebimentos(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildListaExtrato() {
    return ListView.builder(
      itemCount: movimentacoes.length,
      itemBuilder: (ctx, i) {
        final m = movimentacoes[i];
        final isEntrada = m['tipo'] == 'Entrada';
        return ListTile(
          leading: Icon(
            isEntrada ? Icons.add_circle : Icons.remove_circle,
            color: isEntrada ? Colors.green : Colors.red,
          ),
          title: Text(m['descricao']),
          subtitle: Text(m['data'].toString().substring(0, 10)),
          trailing: Text(
            "R\$ ${m['valor']}",
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: isEntrada ? Colors.green : Colors.red,
            ),
          ),
        );
      },
    );
  }

  Widget _buildListaContasFixas() {
    return Scaffold(
      floatingActionButton: FloatingActionButton(
        onPressed: () => abrirModalContaFixa(),
        child: const Icon(Icons.add),
      ),
      body: ListView.builder(
        itemCount: contasFixas.length,
        itemBuilder: (ctx, i) {
          final c = contasFixas[i];
          if (c['pago'] == true) return const SizedBox.shrink();
          final dataVenc = DateTime.parse(c['data']);
          return Card(
            child: ListTile(
              leading: Icon(Icons.circle, color: _getCorStatus(dataVenc)),
              title: Text(c['nome']),
              subtitle: Text(
                "Vence: ${DateFormat('dd/MM').format(dataVenc)} | Parcela: ${c['parcela_atual']}/${c['parcelas_total']}",
              ),
              trailing: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    "R\$ ${c['valor']}",
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  Checkbox(
                    value: false,
                    onChanged: (v) => confirmarPagamento(c),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildListaRecebimentos() {
    return ListView.builder(
      itemCount: servicosConcluidos.length,
      itemBuilder: (ctx, i) {
        final s = servicosConcluidos[i];
        if (s['pago'] == true) return const SizedBox.shrink();
        return Card(
          child: ListTile(
            leading: const Icon(Icons.assignment_turned_in, color: Colors.blue),
            title: Text(s['cliente'] ?? 'Cliente N/A'),
            subtitle: Text(s['material'] ?? 'Material N/A'),
            trailing: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  "R\$ ${s['total_geral'] ?? '0.00'}",
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.green,
                  ),
                ),
                Checkbox(
                  value: false,
                  onChanged: (v) => confirmarRecebimento(s),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
