import 'package:flutter/material.dart';
import 'package:central_granitos_sistema/widgets/layout_base.dart';
import 'package:central_granitos_sistema/core/utils/constants.dart';
import 'package:central_granitos_sistema/core/services/firebase_service.dart';

class ProductionPage extends StatefulWidget {
  const ProductionPage({super.key});

  @override
  State<ProductionPage> createState() => _ProductionPageState();
}

class _ProductionPageState extends State<ProductionPage> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  bool carregando = true;
  List<Map<String, dynamic>> todasOrdens = [];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    carregarDados();
  }

  Future<void> carregarDados() async {
    setState(() => carregando = true);
    final dados = await FirebaseService.getCollection('producao');
    if (mounted) {
      setState(() {
        todasOrdens = dados;
        carregando = false;
      });
    }
  }

  List<Map<String, dynamic>> filtrarPorStatus(String status) {
    return todasOrdens.where((o) => 
      o['status']?.toString().toLowerCase() == status.toLowerCase()
    ).toList();
  }

  void mudarStatus(Map<String, dynamic> ordem, String novoStatus) async {
    await FirebaseService.updateDocument('producao', ordem['id'], {'status': novoStatus});
    carregarDados();
  }

  void confirmarExclusao(String id) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Excluir O.S.?'),
        content: const Text('Esta ação não pode ser desfeita.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
          TextButton(
            onPressed: () async {
              await FirebaseService.deleteDocument('producao', id);
              
              // ✅ Correção: Verifica se o contexto do modal ainda é válido antes de fechar
              if (!ctx.mounted) return;
              Navigator.pop(ctx);
              carregarDados();
            },
            child: const Text('Excluir', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBase(
      titulo: 'Área de Produção',
      child: Column(
        children: [
          TabBar(
            controller: _tabController,
            labelColor: COLOR_PRIMARY,
            unselectedLabelColor: Colors.grey,
            indicatorColor: COLOR_PRIMARY,
            tabs: const [
              Tab(text: 'Pendentes', icon: Icon(Icons.hourglass_empty)),
              Tab(text: 'Em Produção', icon: Icon(Icons.build_circle_outlined)),
              Tab(text: 'Finalizados', icon: Icon(Icons.check_circle_outline)),
            ],
          ),
          Expanded(
            child: carregando 
              ? const Center(child: CircularProgressIndicator())
              : TabBarView(
                  controller: _tabController,
                  children: [
                    _buildListaProducao(filtrarPorStatus('Pendente')),
                    _buildListaProducao(filtrarPorStatus('Em Produção')),
                    _buildListaProducao(filtrarPorStatus('Finalizado')),
                  ],
                ),
          ),
        ],
      ),
    );
  }

  Widget _buildListaProducao(List<Map<String, dynamic>> ordens) {
    if (ordens.isEmpty) {
      return const Center(child: Text('Nenhuma ordem encontrada neste status.'));
    }

    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: (MediaQuery.of(context).size.width / 200).floor().clamp(1, 3),
        mainAxisSpacing: 12,
        crossAxisSpacing: 12,
        mainAxisExtent: 180,
      ),
      itemCount: ordens.length,
      itemBuilder: (context, index) => _CardProducao(
        order: ordens[index],
        onDelete: () => confirmarExclusao(ordens[index]['id']),
        onUpdate: (status) => mudarStatus(ordens[index], status),
      ),
    );
  }
}

class _CardProducao extends StatelessWidget {
  final Map<String, dynamic> order;
  final VoidCallback onDelete;
  final Function(String) onUpdate;

  const _CardProducao({required this.order, required this.onDelete, required this.onUpdate});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            // ✅ Correção: Usando withValues em vez de withOpacity
            color: Colors.black.withValues(alpha: 0.05), 
            blurRadius: 5
          )
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  order['cliente'] ?? 'Sem Nome',
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              IconButton(
                icon: const Icon(Icons.delete_outline, size: 18, color: Colors.red),
                onPressed: onDelete,
                visualDensity: VisualDensity.compact,
              )
            ],
          ),
          const Divider(),
          Text(
            "Material: ${order['material'] ?? 'Não informado'}",
            style: const TextStyle(fontSize: 12),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const Spacer(),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              if (order['status'] == 'Pendente')
                ElevatedButton(
                  onPressed: () => onUpdate('Em Produção'),
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.orange, padding: const EdgeInsets.symmetric(horizontal: 8)),
                  child: const Text('Iniciar', style: TextStyle(fontSize: 10, color: Colors.white)),
                ),
              if (order['status'] == 'Em Produção')
                ElevatedButton(
                  onPressed: () => onUpdate('Finalizado'),
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.green, padding: const EdgeInsets.symmetric(horizontal: 8)),
                  child: const Text('Finalizar', style: TextStyle(fontSize: 10, color: Colors.white)),
                ),
               Text(
                "#${order['id']?.toString().substring(0, 4) ?? ''}",
                style: const TextStyle(fontSize: 10, color: Colors.grey),
              ),
            ],
          ),
        ],
      ),
    );
  }
}