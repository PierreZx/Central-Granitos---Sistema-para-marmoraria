import 'package:flutter/material.dart';
// Corrigindo imports para o padrão absoluto do seu projeto
import 'package:central_granitos_sistema/widgets/layout_base.dart';
import 'package:central_granitos_sistema/core/utils/constants.dart';
import 'package:central_granitos_sistema/core/services/firebase_service.dart';

class InventoryPage extends StatefulWidget {
  const InventoryPage({super.key});

  @override
  State<InventoryPage> createState() => _InventoryPageState();
}

class _InventoryPageState extends State<InventoryPage> {
  // Removida a instância do FirebaseService pois os métodos são estáticos
  
  final TextEditingController nomeCtrl = TextEditingController();
  final TextEditingController precoCtrl = TextEditingController();
  final TextEditingController metrosCtrl = TextEditingController();
  final TextEditingController qtdCtrl = TextEditingController();

  List<Map<String, dynamic>> estoque = [];
  bool carregando = true;

  @override
  void initState() {
    super.initState();
    carregarDados();
  }

  Future<void> carregarDados() async {
    setState(() => carregando = true);
    // Chamada direta à classe FirebaseService (Acesso estático)
    final lista = await FirebaseService.getCollection('estoque');
    
    if (!mounted) return;
    
    setState(() {
      estoque = lista;
      carregando = false;
    });
  }

  void abrirDialogoNovo({Map<String, dynamic>? item}) {
    if (item != null) {
      nomeCtrl.text = item['nome'] ?? '';
      precoCtrl.text = item['preco_m2'].toString();
      metrosCtrl.text = item['metros'].toString();
      qtdCtrl.text = item['quantidade'].toString();
    } else {
      nomeCtrl.clear();
      precoCtrl.clear();
      metrosCtrl.clear();
      qtdCtrl.clear();
    }

    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: Text(item == null ? 'Nova Pedra' : 'Editar Pedra'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(controller: nomeCtrl, decoration: const InputDecoration(labelText: 'Nome')),
              TextField(controller: precoCtrl, decoration: const InputDecoration(labelText: 'Preço por m²'), keyboardType: TextInputType.number),
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: metrosCtrl,
                      decoration: const InputDecoration(labelText: 'm² disponíveis'),
                      keyboardType: TextInputType.number,
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: TextField(
                      controller: qtdCtrl,
                      decoration: const InputDecoration(labelText: 'Quantidade'),
                      keyboardType: TextInputType.number,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancelar')),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: COLOR_PRIMARY),
            onPressed: () async {
              final dados = {
                'nome': nomeCtrl.text,
                'preco_m2': double.tryParse(precoCtrl.text.replaceAll(',', '.')) ?? 0.0,
                'metros': double.tryParse(metrosCtrl.text.replaceAll(',', '.')) ?? 0.0,
                'quantidade': int.tryParse(qtdCtrl.text) ?? 0,
              };

              if (item == null) {
                await FirebaseService.addDocument('estoque', dados);
              } else {
                await FirebaseService.updateDocument('estoque', item['id'], dados);
              }

              if (!mounted) return;
              Navigator.of(context).pop(); 
                carregarDados();
            },
            child: const Text('Salvar', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  void confirmarExclusao(String id, String nome) {
    showDialog(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Excluir'),
        content: Text('Deseja excluir $nome?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancelar')),
          TextButton(
            onPressed: () async {
              await FirebaseService.deleteDocument('estoque', id);
              if (!mounted) return;
              Navigator.of(context).pop(); 
                carregarDados();
            },
            child: const Text('Excluir', style: TextStyle(color: COLOR_ERROR)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBase(
      titulo: 'Estoque', // Ajustado para bater com o parâmetro do seu LayoutBase
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Materiais', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: COLOR_TEXT)),
              ElevatedButton.icon(
                icon: const Icon(Icons.add, color: Colors.white),
                label: const Text('Adicionar Pedra', style: TextStyle(color: Colors.white)),
                style: ElevatedButton.styleFrom(backgroundColor: COLOR_PRIMARY),
                onPressed: () => abrirDialogoNovo(),
              ),
            ],
          ),
          const SizedBox(height: 20),
          Expanded(
            child: carregando 
                ? const Center(child: CircularProgressIndicator(color: COLOR_PRIMARY))
                : estoque.isEmpty
                    ? const Center(child: Text('Nenhum item no estoque'))
                    : GridView.builder(
                        gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                          crossAxisCount: (MediaQuery.of(context).size.width / 300).floor().clamp(1, 4),
                          crossAxisSpacing: 20,
                          mainAxisSpacing: 20,
                          childAspectRatio: 1.2,
                        ),
                        itemCount: estoque.length,
                        itemBuilder: (_, i) {
                          final item = estoque[i];
                          return Card(
                            color: COLOR_WHITE,
                            elevation: 4,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(BORDER_RADIUS_MD),
                            ),
                            child: Padding(
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(item['nome'] ?? 'Sem nome', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                                  const SizedBox(height: 5),
                                  Text('R\$ ${item['preco_m2']} / m²', style: const TextStyle(color: COLOR_PRIMARY, fontWeight: FontWeight.w600)),
                                  Text('${item['metros']} m² disponíveis'),
                                  Text('${item['quantidade']} unidades'),
                                  const Spacer(),
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.end,
                                    children: [
                                      IconButton(
                                        icon: const Icon(Icons.edit, color: COLOR_PRIMARY),
                                        onPressed: () => abrirDialogoNovo(item: item),
                                      ),
                                      IconButton(
                                        icon: const Icon(Icons.delete, color: COLOR_ERROR),
                                        onPressed: () => confirmarExclusao(item['id'], item['nome'] ?? ''),
                                      ),
                                    ],
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
    );
  }
}