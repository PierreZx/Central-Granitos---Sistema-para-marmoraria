# src/domain/budget_builder.py

from src.services.pdf_service import gerar_pdf_orcamento
from src.views.components.budget_composition import CompositionManager


def gerar_orcamento_completo(cliente: dict, itens_base: list, valor_extras: float = 0.0):
    """
    Gera o orçamento completo do cliente e chama o serviço de PDF.
    
    Args:
        cliente (dict): informações do cliente, deve conter 'nome', 'contato' e 'endereco'.
        itens_base (list[dict]): lista de itens de orçamento, geralmente saída de calcular_bancada_L/U.
        valor_extras (float): custos adicionais (montagem, transporte etc.)

    Returns:
        resultado do gerar_pdf_orcamento (geralmente um arquivo ou bytes)
    """

    # Validar cliente
    if not all(k in cliente for k in ("nome", "contato", "endereco")):
        raise ValueError("Cliente precisa ter 'nome', 'contato' e 'endereco'")

    # Garantir que itens_base seja lista de dicts com 'preco_total'
    total_itens = 0.0
    for i, item in enumerate(itens_base):
        if not isinstance(item, dict):
            raise TypeError(f"Item {i} em itens_base não é um dict")
        if "preco_total" not in item:
            raise KeyError(f"Item {i} em itens_base não possui 'preco_total'")
        total_itens += float(item["preco_total"])

    # Calcular total geral
    total_geral = total_itens + float(valor_extras)

    # Montar dicionário final de orçamento
    orcamento = {
        "cliente_nome": cliente["nome"],
        "cliente_contato": cliente["contato"],
        "cliente_endereco": cliente["endereco"],
        "itens": itens_base,
        "total_geral": round(total_geral, 2)
    }

    # Chamar serviço PDF
    return gerar_pdf_orcamento(orcamento)
