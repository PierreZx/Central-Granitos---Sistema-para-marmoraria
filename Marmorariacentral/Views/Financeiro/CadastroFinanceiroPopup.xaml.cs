using CommunityToolkit.Maui.Views;
using Marmorariacentral.Models;

namespace Marmorariacentral.Views.Financeiro;

public partial class CadastroFinanceiroPopup : Popup
{
    private FinanceiroRegistro? _itemEdicao;

    // Ajustado para aceitar um registro opcional (item)
    public CadastroFinanceiroPopup(FinanceiroRegistro? item = null)
    {
        InitializeComponent();
        _itemEdicao = item;

        // Se o item não for nulo, estamos EDITANDO
        if (_itemEdicao != null)
        {
            // Preenche os campos com os dados existentes
            EntryDesc.Text = _itemEdicao.Descricao;
            EntryValor.Text = _itemEdicao.Valor.ToString();
            PickerData.Date = _itemEdicao.DataVencimento;
            CheckMensal.IsChecked = _itemEdicao.IsFixo;
            CheckParcelado.IsChecked = _itemEdicao.IsParcelado;
            EntryParcelas.Text = _itemEdicao.TotalParcelas.ToString();
        }
    }

    private void OnSalvarClicked(object? sender, EventArgs e)
    {
        if (string.IsNullOrWhiteSpace(EntryDesc.Text)) return;

        // Se for edição, mantém o ID original. Se for novo, gera um novo GUID.
        var registro = _itemEdicao ?? new FinanceiroRegistro { Id = Guid.NewGuid().ToString() };

        registro.Descricao = EntryDesc.Text;
        registro.Valor = double.TryParse(EntryValor.Text, out var v) ? v : 0;
        registro.DataVencimento = PickerData.Date;
        registro.IsFixo = CheckMensal.IsChecked;
        registro.IsParcelado = CheckParcelado.IsChecked;
        registro.TotalParcelas = int.TryParse(EntryParcelas.Text, out var p) ? p : 1;
        registro.Tipo = "Saida"; // Padrão
        registro.FoiPago = _itemEdicao?.FoiPago ?? false;

        Close(registro);
    }

    private void OnCancelarClicked(object? sender, EventArgs e) => Close(null);
}