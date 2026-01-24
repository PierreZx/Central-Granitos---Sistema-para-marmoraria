import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import 'package:central_granitos_sistema/widgets/layout_base.dart';
import 'package:central_granitos_sistema/core/utils/constants.dart';
import 'package:central_granitos_sistema/core/services/firebase_service.dart';
import 'package:central_granitos_sistema/core/services/pdf_service.dart';
import 'budget_form_page.dart';

class BudgetView extends StatefulWidget {
  const BudgetView({super.key});

  @override
  State<BudgetView> createState() => _BudgetViewState();
}

class _BudgetViewState extends State<BudgetView> {
  List<Map<String, dynamic>> orcamentos = [];
  bool carregando = true;

  @override
  void initState() {
    super.initState();
    carregarListaOrcamentos();
  }

  Future<void> carregarListaOrcamentos() async {
    setState(() => carregando = true);
    final lista = await FirebaseService.getCollection('orcamentos');
    
    if (!mounted) return;

    setState(() {
      orcamentos = lista;
      carregando = false;
    });
  }

  Future<void> gerarPdf(Map<String, dynamic> orcamento) async {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Gerando PDF...')),
    );

    final pdfService = PdfService();
    final pdfBase64 = await pdfService.gerarPdfOrcamento(orcamento);

    if (!mounted) return;

    if (pdfBase64 != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('PDF Gerado com Sucesso!')),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Erro ao gerar PDF'),
          backgroundColor: COLOR_ERROR,
        ),
      );
    }
  }

  Widget cardOrcamento(Map<String, dynamic> o) {
    final status = o['status'] ?? 'Em aberto';
    final corStatus = status == 'Em aberto' ? COLOR_WARNING : COLOR_SUCCESS;
    final total = (o['total_geral'] as num?)?.toDouble() ?? 0.0;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: COLOR_WHITE,
        borderRadius: BorderRadius.circular(BORDER_RADIUS_LG),
        boxShadow: const [SHADOW_MD],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  o['cliente_nome'] ?? 'Cliente',
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: corStatus,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  status.toString().toUpperCase(),
                  style: const TextStyle(fontSize: 9, color: COLOR_WHITE, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Investimento: R\$ ${NumberFormat.currency(locale: 'pt_BR', symbol: '').format(total)}',
            style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: COLOR_PRIMARY),
          ),
          Text(
            'Data: ${(o['data'] ?? '').toString().length >= 10 ? o['data'].toString().substring(0, 10) : 'N/D'}',
            style: const TextStyle(fontSize: 11, color: Colors.grey),
          ),
          const Divider(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              IconButton(icon: const Icon(Icons.edit_note_rounded), onPressed: () => abrirDetalhes(o)),
              IconButton(icon: const Icon(Icons.picture_as_pdf_rounded), onPressed: () => gerarPdf(o)),
              IconButton(icon: const Icon(Icons.delete_forever_rounded), color: COLOR_ERROR, onPressed: () => confirmarExclusao(o)),
            ],
          ),
        ],
      ),
    );
  }

  void novoOrcamento() {
    final nomeCtrl = TextEditingController();
    final contatoCtrl = TextEditingController();
    final enderecoCtrl = TextEditingController();

    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Iniciar Novo Orçamento'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(controller: nomeCtrl, decoration: const InputDecoration(labelText: 'Nome')),
            TextField(controller: contatoCtrl, decoration: const InputDecoration(labelText: 'Telefone')),
            TextField(controller: enderecoCtrl, decoration: const InputDecoration(labelText: 'Endereço')),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancelar')),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: COLOR_PRIMARY),
            onPressed: () async {
              if (nomeCtrl.text.isEmpty) return;

              await FirebaseService.addDocument('orcamentos', {
                'cliente_nome': nomeCtrl.text,
                'cliente_contato': contatoCtrl.text,
                'cliente_endereco': enderecoCtrl.text,
                'status': 'Em aberto',
                'itens': [],
                'total_geral': 0.0,
                'data': DateTime.now().toIso8601String(),
              });

              if (!mounted) return;
              Navigator.pop(context); // Usando o context da State para fechar
              carregarListaOrcamentos();
            },
            child: const Text('Criar', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  void abrirDetalhes(Map<String, dynamic> o) async {
  // Navega para a nova tela enviando os dados do orçamento selecionado
  final bool? atualizado = await Navigator.push(
    context,
    MaterialPageRoute(
      builder: (context) => BudgetFormPage(orcamentoExistente: o),
    ),
  );

  // Se voltou com sucesso, recarrega a lista
  if (atualizado == true) {
    carregarListaOrcamentos();
  }
}
  void confirmarExclusao(Map<String, dynamic> o) {
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Excluir orçamento?'),
        content: Text('Deseja realmente excluir o orçamento de ${o['cliente_nome']}?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Não')),
          TextButton(
            onPressed: () async {
              await FirebaseService.deleteDocument('orcamentos', o['id']);
              if (!mounted) return;
              Navigator.pop(context); // Usando o context da State para fechar
              carregarListaOrcamentos();
            },
            child: const Text('Sim', style: TextStyle(color: COLOR_ERROR)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBase(
      titulo: 'Orçamentos',
      child: carregando
          ? const Center(child: CircularProgressIndicator(color: COLOR_PRIMARY))
          : GridView.count(
              padding: const EdgeInsets.all(20),
              crossAxisCount: (MediaQuery.of(context).size.width / 350).floor().clamp(1, 4),
              crossAxisSpacing: 20,
              mainAxisSpacing: 20,
              children: [
                GestureDetector(
                  onTap: novoOrcamento,
                  child: Container(
                    decoration: BoxDecoration(
                      color: COLOR_WHITE,
                      borderRadius: BorderRadius.circular(BORDER_RADIUS_LG),
                      border: Border.all(color: COLOR_PRIMARY, width: 2),
                    ),
                    child: const Center(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.add_circle_outline, size: 40, color: COLOR_PRIMARY),
                          SizedBox(height: 8),
                          Text('Novo Orçamento', style: TextStyle(fontWeight: FontWeight.bold, color: COLOR_PRIMARY)),
                        ],
                      ),
                    ),
                  ),
                ),
                ...orcamentos.map(cardOrcamento),
              ],
            ),
    );
  }
}