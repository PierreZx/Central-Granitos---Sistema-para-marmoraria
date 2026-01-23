import 'package:flutter/material.dart';
import 'package:central_granitos_sistema/widgets/layout_base.dart';
import 'package:central_granitos_sistema/core/controllers/production_controller.dart';
import 'package:central_granitos_sistema/core/utils/constants.dart';

class ProductionPage extends StatefulWidget {
  const ProductionPage({super.key});

  @override
  State<ProductionPage> createState() => _ProductionPageState();
}

class _ProductionPageState extends State<ProductionPage>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  // O seu controlador usa ChangeNotifier, então vamos escutar as mudanças
  final ProductionController _controller = ProductionController();

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    // CORREÇÃO: O método correto no seu controller é loadProducao()
    _controller.loadProducao(); 
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: _controller,
      builder: (context, _) {
        return LayoutBase(
          titulo: 'Área de Produção', // CORREÇÃO: parâmetro é 'titulo'
          subtitulo: 'Gestão de Ordens de Serviço', // CORREÇÃO: parâmetro é 'subtitulo'
          child: Column(
            children: [
              TabBar(
                controller: _tabController,
                labelColor: COLOR_PRIMARY,
                unselectedLabelColor: Colors.grey,
                indicatorColor: COLOR_PRIMARY,
                tabs: const [
                  Tab(icon: Icon(Icons.timer_outlined), text: 'Fila de Espera'),
                  Tab(icon: Icon(Icons.precision_manufacturing), text: 'Na Bancada'),
                  Tab(icon: Icon(Icons.check_circle_outline), text: 'Concluídos'),
                ],
              ),
              const SizedBox(height: 16),
              Expanded(
                child: _controller.isLoading 
                  ? const Center(child: CircularProgressIndicator(color: COLOR_PRIMARY))
                  : TabBarView(
                      controller: _tabController,
                      children: [
                        _buildColumn('Pendente', Colors.orange),
                        _buildColumn('Em Produção', Colors.blue),
                        _buildColumn('Finalizado', Colors.green),
                      ],
                    ),
              ),
            ],
          ),
        );
      }
    );
  }

  Widget _buildColumn(String status, Color statusColor) {
    // CORREÇÃO: Seu controller não tem getByStatus, filtramos a lista 'pedidos' diretamente
    final orders = _controller.pedidos.where((p) => p['status'] == status).toList();

    if (orders.isEmpty) {
      return const Center( // Adicionado const para performance
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.inbox_rounded, size: 64, color: Colors.grey),
            SizedBox(height: 12),
            Text('Nenhum pedido nesta fase',
                style: TextStyle(color: Colors.grey)),
          ],
        ),
      );
    }

    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 4,
        mainAxisSpacing: 16,
        crossAxisSpacing: 16,
        childAspectRatio: 1.1,
      ),
      itemCount: orders.length,
      itemBuilder: (context, index) {
        final order = orders[index];
        return _OrderCard(
          order: order,
          statusColor: statusColor,
          onOpen: () => _openOrderDetails(order),
        );
      },
    );
  }

  void _openOrderDetails(Map<String, dynamic> order) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Row(
          children: [
            const Icon(Icons.assignment, color: COLOR_PRIMARY), // Adicionado const
            const SizedBox(width: 8),
            Text('O.S. - ${order['cliente'] ?? 'Cliente'}'), // Corrigido chave para 'cliente'
          ],
        ),
        content: SizedBox(
          width: 450,
          height: 300,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Data: ${order['data']}'),
              const Divider(),
              const Text('Peças e Detalhes:', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 10),
              const Center(child: Text('Detalhes da composição disponíveis no orçamento.')),
            ],
          ),
        ),
        actions: [
          ElevatedButton(
            onPressed: () => Navigator.pop(context),
            style: ElevatedButton.styleFrom(backgroundColor: COLOR_PRIMARY),
            child: const Text('Fechar', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }
}

class _OrderCard extends StatelessWidget {
  final Map<String, dynamic> order;
  final Color statusColor;
  final VoidCallback onOpen;

  const _OrderCard({
    required this.order,
    required this.statusColor,
    required this.onOpen,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: COLOR_WHITE,
        borderRadius: BorderRadius.circular(16),
        boxShadow: const [
          BoxShadow(blurRadius: 12, color: Color(0x11000000), offset: Offset(0, 4)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(color: statusColor, borderRadius: BorderRadius.circular(6)),
                child: Text(
                  order['status'] ?? '',
                  style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                ),
              ),
              Text(
                '#${order['id'] ?? ''}',
                style: const TextStyle(fontSize: 10, color: Colors.grey),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            order['cliente'] ?? 'Cliente', // Chave corrigida para 'cliente'
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const Spacer(),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              icon: const Icon(Icons.reorder, color: Colors.white),
              label: const Text('VER O.S.', style: TextStyle(color: Colors.white)),
              onPressed: onOpen,
              style: ElevatedButton.styleFrom(
                backgroundColor: COLOR_SECONDARY,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
            ),
          ),
        ],
      ),
    );
  }
}