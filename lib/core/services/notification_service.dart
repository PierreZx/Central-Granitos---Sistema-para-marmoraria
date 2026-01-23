import '../services/firebase_service.dart';

class NotificationController {

  /// Retorna uma lista de notificações baseadas no perfil do usuário
  /// Tipos: alert, money, check, work, info
  Future<List<Map<String, dynamic>>> gerarNotificacoes(String perfilUsuario) async {
    List<Map<String, dynamic>> notificacoes = [];

    // 1. Verificação de conexão
    final conectado = await FirebaseService.verificarConexao();
    if (!conectado) {
      return [
        {
          'titulo': 'Modo Offline',
          'msg': 'Sem conexão com a internet. Os dados podem estar desatualizados.',
          'tipo': 'info',
        }
      ];
    }

    // =========================
    // ALERTAS ADMIN / ESCRITÓRIO
    // =========================
    if (perfilUsuario != 'producao') {
      final estoque = await FirebaseService.getCollection('estoque');

      // Estoque baixo
      for (var pedra in estoque) {
        try {
          final qtd = double.tryParse(
                pedra['quantidade'].toString().replaceAll(',', '.'),
              ) ??
              0;

          final nome = pedra['nome'] ?? 'Pedra sem nome';

          if (qtd <= 2) {
            notificacoes.add({
              'titulo': 'Estoque Crítico',
              'msg': "A pedra '$nome' tem apenas $qtd unidades!",
              'tipo': 'alert',
            });
          }
        } catch (_) {}
      }

      // Pagamentos pendentes
      final orcamentos = await FirebaseService.getCollection('orcamentos');

      for (var orc in orcamentos) {
        if (orc['status'] == 'Finalizado' &&
            (orc['pago_financeiro'] ?? false) == false) {
          try {
            final valor = double.tryParse(
                  orc['total_geral'].toString().replaceAll(',', '.'),
                ) ??
                0;

            notificacoes.add({
              'titulo': 'Recebimento Pendente',
              'msg':
                  'Receber R\$ ${valor.toStringAsFixed(2)} de ${orc['cliente_nome'] ?? 'Cliente'}',
              'tipo': 'money',
            });
          } catch (_) {}
        }
      }

      // Produção concluída (últimos 3)
      orcamentos.sort(
        (a, b) =>
            (b['data_criacao'] ?? '').compareTo(a['data_criacao'] ?? ''),
      );

      final finalizados = orcamentos
          .where((o) => o['status'] == 'Finalizado')
          .take(3);

      for (var orc in finalizados) {
        notificacoes.add({
          'titulo': 'Produção Concluída',
          'msg':
              'O pedido de ${orc['cliente_nome'] ?? 'cliente'} está pronto para entrega.',
          'tipo': 'check',
        });
      }
    }

    // =================
    // ALERTAS PRODUÇÃO
    // =================
    if (perfilUsuario == 'producao') {
      final orcamentos = await FirebaseService.getCollection('orcamentos');

      final pendentes = orcamentos.where((o) =>
          ['Produção', 'A Fazer', 'Pendente', 'Em Andamento']
              .contains(o['status']));

      if (pendentes.isNotEmpty) {
        notificacoes.add({
          'titulo': 'Fila de Produção',
          'msg':
              'Existem ${pendentes.length} pedidos aguardando ou em execução.',
          'tipo': 'work',
        });
      }
    }

    return notificacoes;
  }
}
