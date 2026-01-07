import datetime
from src.services import firebase_service

def gerar_notificacoes(perfil_usuario):
    notificacoes = []
    
    # Se não tiver net, não tem como checar banco online atualizado, retorna vazio ou alertas locais
    if not firebase_service.verificar_conexao():
        return [{"titulo": "Modo Offline", "msg": "Você está sem internet. O app funcionará localmente.", "tipo": "info"}]

    # --- 1. ALERTA DE ESTOQUE BAIXO (Para Admin) ---
    if perfil_usuario != "producao":
        estoque = firebase_service.get_estoque_lista()
        for pedra in estoque:
            try:
                qtd = float(str(pedra.get('quantidade', 0)))
                nome = pedra.get('nome', 'Pedra')
                if qtd <= 2: # Regra: Menos de 2 chapas = Alerta
                    notificacoes.append({
                        "titulo": "Estoque Crítico",
                        "msg": f"A pedra '{nome}' tem apenas {qtd} unidades!",
                        "tipo": "alert"
                    })
            except: pass

    # --- 2. PAGAMENTOS PENDENTES (Para Admin) ---
    if perfil_usuario != "producao":
        orcamentos = firebase_service.get_orcamentos_lista()
        for orc in orcamentos:
            status = orc.get('status')
            # Se tá finalizado mas não tá pago (lógica simulada, ideal ter campo 'pago')
            # Vamos assumir que 'Finalizado' deveria estar pago.
            if status == 'Finalizado' and not orc.get('pago_financeiro', False):
                cliente = orc.get('cliente_nome', 'Cliente')
                val = orc.get('total_geral', 0)
                notificacoes.append({
                    "titulo": "Recebimento Pendente",
                    "msg": f"Receber R$ {val:.2f} de {cliente} (Obra Finalizada)",
                    "tipo": "money"
                })

    # --- 3. RETORNO DA PRODUÇÃO (Para Admin) ---
    if perfil_usuario != "producao":
        # Verifica orçamentos que acabaram de mudar para "Finalizado" hoje (simulação)
        # Na prática, mostraria os últimos finalizados
        orcamentos = firebase_service.get_orcamentos_lista()
        for orc in orcamentos[-3:]: # Pega os 3 ultimos para checar
            if orc.get('status') == 'Finalizado':
                notificacoes.append({
                    "titulo": "Produção Concluída",
                    "msg": f"O pedido de {orc.get('cliente_nome')} saiu da produção.",
                    "tipo": "check"
                })

    # --- 4. NOVA ORDEM DE SERVIÇO (Para Produção) ---
    if perfil_usuario == "producao":
        orcamentos = firebase_service.get_orcamentos_lista()
        count_pendentes = 0
        for orc in orcamentos:
            if orc.get('status') in ['Produção', 'Em Aberto', 'Pendente']:
                count_pendentes += 1
        
        if count_pendentes > 0:
            notificacoes.append({
                "titulo": "Novos Pedidos",
                "msg": f"Existem {count_pendentes} peças aguardando produção.",
                "tipo": "work"
            })

    return notificacoes