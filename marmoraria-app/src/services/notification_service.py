import datetime
from src.services import firebase_service

def gerar_notificacoes(perfil_usuario):
    """
    Gera alertas dinâmicos baseados no cargo do usuário e estado do banco de dados.
    Tipos: 'alert' (Erro/Crítico), 'money' (Financeiro), 'check' (Sucesso), 'work' (Produção), 'info' (Aviso)
    """
    notificacoes = []
    
    # 1. Verificação de Conexão
    if not firebase_service.verificar_conexao():
        return [{
            "titulo": "Modo Offline", 
            "msg": "Sem conexão com a internet. Os dados podem estar desatualizados.", 
            "tipo": "info"
        }]

    # --- 1. ALERTAS PARA ADMIN / ESCRITÓRIO ---
    if perfil_usuario != "producao":
        # Chamada corrigida para o padrão do novo firebase_service
        estoque = firebase_service.get_collection("estoque")
        
        # Alerta de Estoque Baixo
        for pedra in estoque:
            try:
                # Tratamento para garantir que quantidade seja número
                qtd = float(str(pedra.get('quantidade', 0)).replace(',', '.'))
                nome = pedra.get('nome', 'Pedra sem nome')
                
                if qtd <= 2: 
                    notificacoes.append({
                        "titulo": "Estoque Crítico",
                        "msg": f"A pedra '{nome}' tem apenas {qtd} unidades!",
                        "tipo": "alert"
                    })
            except (ValueError, TypeError):
                continue

        # Alerta de Pagamentos Pendentes
        orcamentos = firebase_service.get_collection("orcamentos")
        for orc in orcamentos:
            status = orc.get('status')
            # Se a obra foi finalizada mas o financeiro não deu baixa
            if status == 'Finalizado' and not orc.get('pago_financeiro', False):
                cliente = orc.get('cliente_nome', 'Cliente não identificado')
                try:
                    val = float(str(orc.get('total_geral', 0)).replace(',', '.'))
                    notificacoes.append({
                        "titulo": "Recebimento Pendente",
                        "msg": f"Receber R$ {val:,.2f} de {cliente} (Obra Finalizada)",
                        "tipo": "money"
                    })
                except:
                    continue

        # Alerta de Retorno da Produção (Últimos 3 pedidos finalizados)
        # Ordenamos pela data de criação se disponível
        orcamentos_sorted = sorted(orcamentos, key=lambda x: x.get('data_criacao', ''), reverse=True)
        finalizados_recentes = [o for o in orcamentos_sorted if o.get('status') == 'Finalizado'][:3]
        
        for orc in finalizados_recentes:
            notificacoes.append({
                "titulo": "Produção Concluída",
                "msg": f"O pedido de {orc.get('cliente_nome')} está pronto para entrega.",
                "tipo": "check"
            })

    # --- 2. ALERTAS PARA PRODUÇÃO ---
    if perfil_usuario == "producao":
        orcamentos = firebase_service.get_collection("orcamentos")
        # Filtra pedidos que realmente precisam de atenção na fábrica
        pedidos_pendentes = [
            o for o in orcamentos 
            if o.get('status') in ['Produção', 'A Fazer', 'Pendente', 'Em Andamento']
        ]
        
        count_pendentes = len(pedidos_pendentes)
        if count_pendentes > 0:
            notificacoes.append({
                "titulo": "Fila de Produção",
                "msg": f"Existem {count_pendentes} pedidos aguardando ou em execução na fábrica.",
                "tipo": "work"
            })

    return notificacoes