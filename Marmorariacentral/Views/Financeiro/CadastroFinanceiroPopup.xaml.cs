using CommunityToolkit.Maui.Views;
using Marmorariacentral.Models;
using System.Globalization;

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

        // Eventos para calcular valor da parcela em tempo real
        EntryValor.TextChanged += (s, e) => CalcularParcela();
        EntryParcelas.TextChanged += (s, e) => CalcularParcela();

        ConfigurarModoTela();

        if (_itemEdicao != null)
        {
            PreencherCamposEdicao();
        }
    }

    private void ConfigurarModoTela()
    {
        if (_isModoRapido)
        {
            LblTitulo.Text = "Lançamento de Caixa";
            BtnSalvar.Text = "LANÇAR NO EXTRATO";
            LayoutData.IsVisible = false;
            LayoutOpcoesFinanceiras.IsVisible = false;
            FrameTipo.IsVisible = true;
            PickerData.Date = DateTime.Today;
        }
        else if (_itemEdicao != null && (_itemEdicao.Descricao?.StartsWith("Orçamento:") ?? false))
        {
            LblTitulo.Text = "Configurar Orçamento";
            BtnSalvar.Text = "DEFINIR PAGAMENTO";
            FrameTipo.IsVisible = true;
            SwitchTipo.IsToggled = true; 
            ContainerCheckMensal.IsVisible = false; 
            CheckParcelado.IsChecked = true; 
            LayoutData.IsVisible = true;
            LayoutOpcoesFinanceiras.IsVisible = true;
        }
        else
        {
            LblTitulo.Text = "Nova Conta a Pagar";
            BtnSalvar.Text = "CADASTRAR CONTA";
            FrameTipo.IsVisible = false;
            SwitchTipo.IsToggled = false;
            LayoutData.IsVisible = true;
            LayoutOpcoesFinanceiras.IsVisible = true;
        }
    }

    private void PreencherCamposEdicao()
    {
        if (_itemEdicao == null) return;

        EntryDesc.Text = _itemEdicao.Descricao;
        EntryValor.Text = _itemEdicao.Valor.ToString("N2", CultureInfo.GetCultureInfo("pt-BR"));
        SwitchTipo.IsToggled = _itemEdicao.Tipo == "Entrada";
        PickerData.Date = _itemEdicao.DataVencimento;
        CheckMensal.IsChecked = _itemEdicao.IsFixo;
        CheckParcelado.IsChecked = _itemEdicao.IsParcelado;
        EntryDiaFixo.Text = _itemEdicao.DiaVencimentoFixo.ToString();
        EntryParcelas.Text = _itemEdicao.TotalParcelas > 0 ? _itemEdicao.TotalParcelas.ToString() : "1";
        
        CalcularParcela();
    }

    private void CalcularParcela()
    {
        if (!CheckParcelado.IsChecked)
        {
            LblValorParcela.Text = "";
            return;
        }

        // Limpeza rigorosa para evitar erro com pontos de milhar (Ex: 3.660,00)
        string valorTexto = EntryValor.Text?.Replace(".", "").Replace(",", ".") ?? "0";
        double.TryParse(valorTexto, NumberStyles.Any, CultureInfo.InvariantCulture, out double total);
        int.TryParse(EntryParcelas.Text, out int parcelas);

        if (total > 0 && parcelas > 0)
        {
            double valorParcela = total / parcelas;
            LblValorParcela.Text = valorParcela.ToString("C", CultureInfo.GetCultureInfo("pt-BR"));
        }
        else
        {
            LblValorParcela.Text = "R$ 0,00";
        }
    }

    private void OnCheckMensalChanged(object sender, CheckedChangedEventArgs e)
    {
        if (e.Value) CheckParcelado.IsChecked = false;
    }

    private void OnCheckParceladoChanged(object sender, CheckedChangedEventArgs e)
    {
        if (e.Value) CheckMensal.IsChecked = false;
        CalcularParcela();
    }

    private void OnSalvarClicked(object sender, EventArgs e)
    {
        if (string.IsNullOrWhiteSpace(EntryDesc.Text)) return;

        var registro = _itemEdicao ?? new FinanceiroRegistro { Id = Guid.NewGuid().ToString() };

        registro.Descricao = EntryDesc.Text;
        
        // Conversão segura do valor total
        string valorTexto = EntryValor.Text?.Replace(".", "").Replace(",", ".") ?? "0";
        double valorTotal = double.TryParse(valorTexto, NumberStyles.Any, CultureInfo.InvariantCulture, out var v) ? v : 0;
        
        registro.Tipo = SwitchTipo.IsToggled ? "Entrada" : "Saida";
        registro.FoiPago = _isModoRapido || registro.FoiPago;
        registro.IsFixo = !_isModoRapido && CheckMensal.IsChecked;
        registro.IsParcelado = !_isModoRapido && CheckParcelado.IsChecked;

        // LÓGICA DE PARCELAMENTO: Se for parcelado, o valor do registro vira o valor da PARCELA
        if (registro.IsParcelado)
        {
            registro.TotalParcelas = int.TryParse(EntryParcelas.Text, out var p) ? Math.Max(p, 1) : 1;
            registro.ParcelaAtual = registro.ParcelaAtual > 0 ? registro.ParcelaAtual : 1;
            registro.Valor = valorTotal / registro.TotalParcelas; // Aqui salva o valor que vai ser descontado por vez
        }
        else
        {
            registro.TotalParcelas = 1;
            registro.Valor = valorTotal;
        }

        if (!_isModoRapido && CheckMensal.IsChecked && int.TryParse(EntryDiaFixo.Text, out var dia))
        {
            registro.DiaVencimentoFixo = dia;
            registro.DataVencimento = new DateTime(DateTime.Now.Year, DateTime.Now.Month, Math.Clamp(dia, 1, 28));
        }
        else
        {
            registro.DataVencimento = PickerData.Date;
        }

        Close(registro);
    }

    private void OnCancelarClicked(object sender, EventArgs e) => Close(null);
}