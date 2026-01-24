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

class _FinancialPageState extends State<FinancialPage> {
  final pesquisaCtrl = TextEditingController();
  bool carregando = true;
  List<Map<String, dynamic>> movimentacoes = [];
  double saldoCaixa = 0;

  @override
  void initState() {
    super.initState();
    atualizarDados();
  }

  Future<void> atualizarDados() async {
    setState(() => carregando = true);
    final extrato = await FirebaseService.getExtrato();
    final saldo = await FirebaseService.getSaldoCaixa();
    
    if (mounted) {
      setState(() {
        movimentacoes = extrato;
        saldoCaixa = saldo;
        carregando = false;
      });
    }
  }

  void abrirModalMovimentacao({Map<String, dynamic>? item}) {
    final descCtrl = TextEditingController(text: item?['descricao'] ?? '');
    final valorCtrl = TextEditingController(text: item?['valor']?.toString() ?? '');
    String tipoSelecionado = item?['tipo'] ?? 'Entrada';

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setModalState) => AlertDialog(
          title: Text(item == null ? 'Nova Movimentação' : 'Editar Registro'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                DropdownButtonFormField<String>(
                  // ✅ Mantemos o controle de estado interno do modal
                  initialValue: tipoSelecionado,
                  items: ['Entrada', 'Saida'].map((t) => DropdownMenuItem(value: t, child: Text(t))).toList(),
                  onChanged: (v) => setModalState(() => tipoSelecionado = v!),
                  decoration: const InputDecoration(labelText: 'Tipo'),
                ),
                TextField(controller: descCtrl, decoration: const InputDecoration(labelText: 'Descrição')),
                TextField(
                  controller: valorCtrl,
                  decoration: const InputDecoration(labelText: 'Valor (Ex: 150.50)'),
                  keyboardType: TextInputType.number,
                ),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
            ElevatedButton(
              onPressed: () async {
                final valor = double.tryParse(valorCtrl.text.replaceAll(',', '.')) ?? 0;
                if (item == null) {
                  await FirebaseService.addMovimentacao(tipoSelecionado, valor, descCtrl.text);
                } else {
                  await FirebaseService.updateDocument('financeiro', item['id'], {
                    'tipo': tipoSelecionado,
                    'valor': valor,
                    'descricao': descCtrl.text,
                  });
                }
                
                // ✅ Correção: Verifica se o contexto do modal (ctx) ainda é válido
                if (!ctx.mounted) return;
                Navigator.pop(ctx);
                atualizarDados();
              },
              child: const Text('Salvar'),
            ),
          ],
        ),
      ),
    );
  }

  void confirmarExclusao(String id) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Confirmar Exclusão'),
        content: const Text('Deseja realmente apagar este registro financeiro?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Não')),
          TextButton(
            onPressed: () async {
              await FirebaseService.deleteDocument('financeiro', id);
              
              // ✅ Correção: Verifica se o contexto do modal (ctx) ainda é válido antes de fechar
              if (!ctx.mounted) return;
              Navigator.pop(ctx);
              atualizarDados();
            },
            child: const Text('Sim, Excluir', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBase(
      titulo: 'Financeiro',
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: COLOR_PRIMARY,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Saldo em Caixa', style: TextStyle(color: Colors.white70, fontSize: 16)),
                  const SizedBox(height: 8),
                  FittedBox(
                    child: Text(
                      NumberFormat.currency(locale: 'pt_BR', symbol: 'R\$').format(saldoCaixa),
                      style: const TextStyle(color: Colors.white, fontSize: 32, fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: pesquisaCtrl,
                    decoration: const InputDecoration(
                      hintText: 'Pesquisar no extrato...',
                      prefixIcon: Icon(Icons.search),
                      border: OutlineInputBorder(),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green.shade700,
                    padding: const EdgeInsets.symmetric(vertical: 18, horizontal: 12),
                  ),
                  onPressed: () => abrirModalMovimentacao(),
                  child: const Icon(Icons.add, color: Colors.white),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Expanded(
              child: carregando
                  ? const Center(child: CircularProgressIndicator())
                  : ListView.builder(
                        itemCount: movimentacoes.length,
                        itemBuilder: (context, index) {
                          final mov = movimentacoes[index];
                          final isEntrada = mov['tipo'].toString().toLowerCase() == 'entrada';
                          
                          return Card(
                            margin: const EdgeInsets.only(bottom: 8),
                            child: ListTile(
                              leading: Icon(
                                isEntrada ? Icons.arrow_upward : Icons.arrow_downward,
                                color: isEntrada ? Colors.green : Colors.red,
                              ),
                              title: Text(mov['descricao'] ?? 'Sem descrição', style: const TextStyle(fontWeight: FontWeight.bold)),
                              subtitle: Text(mov['data']?.toString().substring(0, 10) ?? ''),
                              trailing: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Text(
                                    'R\$ ${mov['valor']}',
                                    style: TextStyle(
                                      color: isEntrada ? Colors.green : Colors.red,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  IconButton(
                                    icon: const Icon(Icons.edit, size: 20),
                                    onPressed: () => abrirModalMovimentacao(item: mov),
                                  ),
                                  IconButton(
                                    icon: const Icon(Icons.delete_outline, size: 20, color: Colors.red),
                                    onPressed: () => confirmarExclusao(mov['id']),
                                  ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
            ),
          ],
        ),
      ),
    );
  }
}