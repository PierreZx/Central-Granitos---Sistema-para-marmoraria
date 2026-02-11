using CommunityToolkit.Maui.Views;
using Marmorariacentral.Models;

namespace Marmorariacentral.Views.Financeiro;

public partial class CadastroFinanceiroPopup : Popup
{
    private FinanceiroRegistro? _itemEdicao;
    private bool _isModoRapido;

    // Construtor aceita o item (para edição) e uma flag para o modo rápido (extrato)
    public CadastroFinanceiroPopup(FinanceiroRegistro? item = null, bool isModoRapido = false)
    {
        InitializeComponent();
        _itemEdicao = item;
        _isModoRapido = isModoRapido;

        // Se for modo rápido (lançamento direto no extrato), simplifica a tela
        if (_isModoRapido)
        {
            LblTitulo.Text = "Lançamento Rápido";
            BtnSalvar.Text = "LANÇAR NO EXTRATO";
            
            // Esconde os campos que você não quer no extrato
            LayoutData.IsVisible = false;
            LayoutOpcoesFinanceiras.IsVisible = false;
            
            // Garante que a data interna seja HOJE
            PickerData.Date = DateTime.Today;
        }

        // Se for edição, preenche os campos com o que já existe
        if (_itemEdicao != null)
        {
            EntryDesc.Text = _itemEdicao.Descricao;
            EntryValor.Text = _itemEdicao.Valor.ToString();
            PickerData.Date = _itemEdicao.DataVencimento;
            CheckMensal.IsChecked = _itemEdicao.IsFixo;
            CheckParcelado.IsChecked = _itemEdicao.IsParcelado;
            EntryParcelas.Text = _itemEdicao.TotalParcelas.ToString();
            EntryDiaFixo.Text = _itemEdicao.DiaVencimentoFixo.ToString();
            SwitchTipo.IsToggled = _itemEdicao.Tipo == "Entrada";
        }
    }

    // Lógica para os CheckBoxes serem exclusivos
    private void OnCheckMensalChanged(object sender, CheckedChangedEventArgs e)
    {
        if (e.Value) CheckParcelado.IsChecked = false;
    }

    private void OnCheckParceladoChanged(object sender, CheckedChangedEventArgs e)
    {
        if (e.Value) CheckMensal.IsChecked = false;
    }

    private void OnSalvarClicked(object? sender, EventArgs e)
    {
        if (string.IsNullOrWhiteSpace(EntryDesc.Text)) return;

        // Mantém o ID se for edição, ou gera um novo
        var registro = _itemEdicao ?? new FinanceiroRegistro { Id = Guid.NewGuid().ToString() };

        registro.Descricao = EntryDesc.Text;
        registro.Valor = double.TryParse(EntryValor.Text, out var v) ? v : 0;
        
        // Define se é Entrada ou Saída com base no Switch
        registro.Tipo = SwitchTipo.IsToggled ? "Entrada" : "Saida";

        // Se for lançamento rápido, já entra como PAGO automaticamente
        registro.FoiPago = _isModoRapido || (_itemEdicao?.FoiPago ?? false);

        // Lógica de Data (Só processa dia fixo se NÃO for modo rápido e for mensal)
        if (!_isModoRapido && CheckMensal.IsChecked && int.TryParse(EntryDiaFixo.Text, out var dia))
        {
            registro.DiaVencimentoFixo = dia;
            registro.DataVencimento = new DateTime(DateTime.Now.Year, DateTime.Now.Month, dia);
        }
        else
        {
            registro.DataVencimento = PickerData.Date;
        }

        // Só define como fixo ou parcelado se não for o lançamento rápido do extrato
        registro.IsFixo = !_isModoRapido && CheckMensal.IsChecked;
        registro.IsParcelado = !_isModoRapido && CheckParcelado.IsChecked;
        registro.TotalParcelas = int.TryParse(EntryParcelas.Text, out var p) ? p : 1;

        Close(registro);
    }

    private void OnCancelarClicked(object? sender, EventArgs e) => Close(null);
}