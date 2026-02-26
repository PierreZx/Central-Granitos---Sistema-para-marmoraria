using CommunityToolkit.Maui.Views;
using Marmorariacentral.Models;

namespace Marmorariacentral.Views.Financeiro;

public partial class CadastroFinanceiroPopup : Popup
{
    private FinanceiroRegistro? _itemEdicao;
    private bool _isModoRapido;

    public CadastroFinanceiroPopup(FinanceiroRegistro? item = null, bool isModoRapido = false)
    {
        InitializeComponent();
        _itemEdicao = item;
        _isModoRapido = isModoRapido;

        if (_isModoRapido)
        {
            // MODO EXTRATO: Lançamento imediato de entrada ou saída
            LblTitulo.Text = "Lançamento de Caixa";
            BtnSalvar.Text = "LANÇAR NO EXTRATO";
            
            if (LayoutData != null) LayoutData.IsVisible = false;
            if (LayoutOpcoesFinanceiras != null) LayoutOpcoesFinanceiras.IsVisible = false;
            if (LayoutTipo != null) LayoutTipo.IsVisible = true;
            
            PickerData.Date = DateTime.Today;
        }
        else
        {
            // MODO CONTAS: Cadastro de conta a pagar (sempre saída)
            LblTitulo.Text = "Nova Conta a Pagar";
            BtnSalvar.Text = "CADASTRAR CONTA";
            
            if (LayoutTipo != null) LayoutTipo.IsVisible = false;
            if (SwitchTipo != null) SwitchTipo.IsToggled = false;
            if (LayoutData != null) LayoutData.IsVisible = true;
            if (LayoutOpcoesFinanceiras != null) LayoutOpcoesFinanceiras.IsVisible = true;
        }

        if (_itemEdicao != null)
        {
            PreencherCamposEdicao();
        }
    }

    private void PreencherCamposEdicao()
    {
        if (_itemEdicao == null) return;

        EntryDesc.Text = _itemEdicao.Descricao;
        EntryValor.Text = _itemEdicao.Valor.ToString();
        SwitchTipo.IsToggled = _itemEdicao.Tipo == "Entrada";
        PickerData.Date = _itemEdicao.DataVencimento;
        CheckMensal.IsChecked = _itemEdicao.IsFixo;
        CheckParcelado.IsChecked = _itemEdicao.IsParcelado;
        EntryDiaFixo.Text = _itemEdicao.DiaVencimentoFixo.ToString();
        EntryParcelas.Text = _itemEdicao.TotalParcelas.ToString();
    }

    private void OnCheckMensalChanged(object sender, CheckedChangedEventArgs e)
    {
        if (e.Value && CheckParcelado != null) 
            CheckParcelado.IsChecked = false;
    }

    private void OnCheckParceladoChanged(object sender, CheckedChangedEventArgs e)
    {
        if (e.Value && CheckMensal != null) 
            CheckMensal.IsChecked = false;
    }

    private void OnSalvarClicked(object sender, EventArgs e)
    {
        if (string.IsNullOrWhiteSpace(EntryDesc.Text)) return;

        var registro = _itemEdicao ?? new FinanceiroRegistro { Id = Guid.NewGuid().ToString() };

        registro.Descricao = EntryDesc.Text;
        registro.Valor = double.TryParse(EntryValor.Text, out var v) ? v : 0;
        
        // Define se é Entrada ou Saída com base na visibilidade do Switch
        bool isEntradaVisible = LayoutTipo?.IsVisible ?? false;
        registro.Tipo = isEntradaVisible ? (SwitchTipo.IsToggled ? "Entrada" : "Saida") : "Saida";

        // Se for modo rápido, já marca como pago automaticamente
        registro.FoiPago = _isModoRapido || (registro.FoiPago);

        if (!_isModoRapido && CheckMensal.IsChecked && int.TryParse(EntryDiaFixo.Text, out var dia))
        {
            registro.DiaVencimentoFixo = dia;
            registro.DataVencimento = new DateTime(DateTime.Now.Year, DateTime.Now.Month, dia);
        }
        else
        {
            registro.DataVencimento = PickerData.Date;
        }

        registro.IsFixo = !_isModoRapido && CheckMensal.IsChecked;
        registro.IsParcelado = !_isModoRapido && CheckParcelado.IsChecked;
        registro.TotalParcelas = int.TryParse(EntryParcelas.Text, out var p) ? p : 1;

        Close(registro);
    }

    private void OnCancelarClicked(object sender, EventArgs e) => Close(null);
}