using CommunityToolkit.Maui.Views;
using Marmorariacentral.Models;
using System.Globalization;

namespace Marmorariacentral.Views.Estoque;

public partial class CadastroChapaPopup : Popup
{
    private EstoqueItem? _itemEdicao;

    public CadastroChapaPopup(EstoqueItem? item = null)
    {
        InitializeComponent();
        _itemEdicao = item;

        if (_itemEdicao != null)
        {
            LblTitulo.Text = "Editar Chapa";
            EntryNome.Text = _itemEdicao.NomeChapa;
            EntryMetro.Text = _itemEdicao.MetroQuadradoTotal.ToString(CultureInfo.InvariantCulture);
            EntryQtd.Text = _itemEdicao.QuantidadeChapas.ToString();
            EntryValor.Text = _itemEdicao.ValorPorMetro.ToString(CultureInfo.InvariantCulture);
        }
    }

    private void OnSalvarClicked(object? sender, EventArgs e)
    {
        if (string.IsNullOrWhiteSpace(EntryNome.Text))
            return;

        var item = _itemEdicao ?? new EstoqueItem
        {
            Id = Guid.NewGuid().ToString()
        };

        item.NomeChapa = EntryNome.Text;

        item.MetroQuadradoTotal = double.TryParse(EntryMetro.Text, NumberStyles.Any, CultureInfo.InvariantCulture, out var m2) ? m2 : 0;
        item.QuantidadeChapas = int.TryParse(EntryQtd.Text, out var qtd) ? qtd : 0;
        item.ValorPorMetro = double.TryParse(EntryValor.Text, NumberStyles.Any, CultureInfo.InvariantCulture, out var valor) ? valor : 0;

        Close(item);
    }

    private void OnCancelarClicked(object? sender, EventArgs e)
    {
        Close(null);
    }
}
