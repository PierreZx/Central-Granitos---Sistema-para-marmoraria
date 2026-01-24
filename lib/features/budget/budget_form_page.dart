import 'package:flutter/material.dart';
import 'package:central_granitos_sistema/core/utils/constants.dart';
import 'package:central_granitos_sistema/core/services/firebase_service.dart';
// ✅ Import corrigido para o local onde a calculadora está:
import 'package:central_granitos_sistema/features/budget/widgets/budget_calculator.dart'; 

class BudgetFormPage extends StatefulWidget {
  final Map<String, dynamic>? orcamentoExistente;

  const BudgetFormPage({super.key, this.orcamentoExistente});

  @override
  State<BudgetFormPage> createState() => _BudgetFormPageState();
}

class _BudgetFormPageState extends State<BudgetFormPage> {
  final _calc = BudgetCalculator();
  final _nomeCtrl = TextEditingController();
  final _contatoCtrl = TextEditingController();
  final _enderecoCtrl = TextEditingController();
  
  bool _salvando = false;

  @override
  void initState() {
    super.initState();
    if (widget.orcamentoExistente != null) {
      _nomeCtrl.text = widget.orcamentoExistente!['cliente_nome'] ?? '';
      _contatoCtrl.text = widget.orcamentoExistente!['cliente_contato'] ?? '';
      _enderecoCtrl.text = widget.orcamentoExistente!['cliente_endereco'] ?? '';
    }
  }

  void _adicionarItemRapido() {
    setState(() {
      _calc.adicionarItem(ItemOrcamento(
        ambiente: "Cozinha",
        material: "Preto São Gabriel",
        quantidade: 1,
        valorMetroQuadrado: 550.0,
        pecas: {"Bancada": Peca(largura: 2.10, profundidade: 0.65)},
      ));
    });
  }

  Future<void> _salvarOrcamento() async {
    if (_nomeCtrl.text.isEmpty) return;

    setState(() => _salvando = true);

    final dados = {
      'cliente_nome': _nomeCtrl.text,
      'cliente_contato': _contatoCtrl.text,
      'cliente_endereco': _enderecoCtrl.text,
      'status': widget.orcamentoExistente?['status'] ?? 'Em aberto',
      'data': widget.orcamentoExistente?['data'] ?? DateTime.now().toIso8601String(),
      'total_geral': _calc.totalGeral,
      'itens': _calc.toMap()['itens'], 
    };

    bool ok;
    if (widget.orcamentoExistente?['id'] != null) {
      ok = await FirebaseService.updateDocument('orcamentos', widget.orcamentoExistente!['id'], dados);
    } else {
      ok = await FirebaseService.addDocument('orcamentos', dados);
    }

    if (mounted) {
      setState(() => _salvando = false);
      if (ok) Navigator.pop(context, true);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.orcamentoExistente == null ? 'Novo Orçamento' : 'Editar Orçamento'),
        backgroundColor: COLOR_PRIMARY,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            TextField(controller: _nomeCtrl, decoration: const InputDecoration(labelText: 'Nome do Cliente')),
            TextField(controller: _contatoCtrl, decoration: const InputDecoration(labelText: 'Contato')),
            TextField(controller: _enderecoCtrl, decoration: const InputDecoration(labelText: 'Endereço')),
            const SizedBox(height: 30),
            
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text("Itens do Orçamento", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                ElevatedButton.icon(
                  onPressed: _adicionarItemRapido,
                  icon: const Icon(Icons.add),
                  label: const Text("Adicionar Item"),
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.green, foregroundColor: Colors.white),
                ),
              ],
            ),

            const SizedBox(height: 10),

            // Exibição dos itens calculados
            ...List.generate(_calc.itens.length, (index) {
              final item = _calc.itens[index];
              return Card(
                child: ListTile(
                  leading: const Icon(Icons.architecture_rounded, color: COLOR_PRIMARY),
                  title: Text(item.ambiente),
                  subtitle: Text("${item.material} | ${item.areaTotal.toStringAsFixed(2)} m²"),
                  trailing: Text("R\$ ${item.precoTotal.toStringAsFixed(2)}", style: const TextStyle(fontWeight: FontWeight.bold)),
                ),
              );
            }),

            const Divider(height: 40),
            
            // Resumo Financeiro
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(color: Colors.grey.shade100, borderRadius: BorderRadius.circular(12)),
              child: Column(
                children: [
                  _rowTotal("Área Total:", "${_calc.areaTotal.toStringAsFixed(2)} m²"),
                  _rowTotal("Subtotal Materiais:", "R\$ ${_calc.subtotalMateriais.toStringAsFixed(2)}"),
                  const Divider(),
                  _rowTotal("TOTAL GERAL:", "R\$ ${_calc.totalGeral.toStringAsFixed(2)}", isBold: true),
                ],
              ),
            ),
            
            const SizedBox(height: 30),
            SizedBox(
              width: double.infinity,
              height: 55,
              child: ElevatedButton(
                style: ElevatedButton.styleFrom(backgroundColor: COLOR_PRIMARY),
                onPressed: _salvando ? null : _salvarOrcamento,
                child: _salvando 
                  ? const CircularProgressIndicator(color: Colors.white) 
                  : const Text("SALVAR NO SISTEMA", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
              ),
            )
          ],
        ),
      ),
    );
  }

  Widget _rowTotal(String label, String valor, {bool isBold = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(fontWeight: isBold ? FontWeight.bold : FontWeight.normal, fontSize: isBold ? 18 : 14)),
          Text(valor, style: TextStyle(fontWeight: isBold ? FontWeight.bold : FontWeight.normal, fontSize: isBold ? 18 : 14)),
        ],
      ),
    );
  }
}