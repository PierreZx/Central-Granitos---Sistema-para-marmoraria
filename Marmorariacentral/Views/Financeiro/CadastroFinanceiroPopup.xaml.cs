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
        // Caso 1: Lançamento direto no extrato (Modo Rápido)
        if (_isModoRapido)
        {
            LblTitulo.Text = "Lançamento de Caixa";
            BtnSalvar.Text = "LANÇAR NO EXTRATO";
            LayoutData.IsVisible = true; 
            LayoutOpcoesFinanceiras.IsVisible = false; 
            FrameTipo.IsVisible = true;
            PickerData.Date = DateTime.Today;
        }
        // Caso 2: Edição de um Orçamento vindo do cliente
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
            
            // TRAVA: Orçamento é sempre entrada e parcelado, não deixa mudar
            CheckParcelado.IsEnabled = false;
            SwitchTipo.IsEnabled = false;
        }
        // Caso 3: Edição de uma conta que JÁ FOI PAGA (Extrato)
        else if (_itemEdicao != null && _itemEdicao.FoiPago)
        {
            LblTitulo.Text = "Editar Lançamento Pago";
            BtnSalvar.Text = "ATUALIZAR REGISTRO";
            LayoutOpcoesFinanceiras.IsVisible = false; // Bloqueia mudar parcelamento de algo já pago
            LayoutData.IsVisible = true;
            FrameTipo.IsVisible = true;
        }
        // Caso 4: Cadastro de nova conta a pagar ou edição de conta pendente
        else
        {
            bool isEdicao = _itemEdicao != null;
            LblTitulo.Text = isEdicao ? "Editar Conta" : "Nova Conta a Pagar";
            BtnSalvar.Text = isEdicao ? "SALVAR ALTERAÇÕES" : "CADASTRAR CONTA";
            
            // TRAVA DE SEGURANÇA: Se for edição, bloqueia a mudança de tipo (Mensal/Parcelado/Entrada/Saída)
            // Para mudar isso, o usuário deve excluir e criar de novo.
            FrameTipo.IsEnabled = !isEdicao;
            CheckMensal.IsEnabled = !isEdicao;
            CheckParcelado.IsEnabled = !isEdicao;
            
            // Se for novo, o frame tipo (Saída/Entrada) começa visível para escolha.
            // Se for mensal fixo (via código abaixo), ele sumirá conforme a regra do XAML.
            FrameTipo.IsVisible = true; 
            SwitchTipo.IsToggled = isEdicao ? (_itemEdicao?.Tipo == "Entrada") : false;
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
        EntryDiaFixo.Text = _itemEdicao.DiaVencimentoFixo > 0 ? _itemEdicao.DiaVencimentoFixo.ToString() : "";
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
        if (e.Value) 
        {
            CheckParcelado.IsChecked = false;
            LayoutData.IsVisible = false; // Regra: Fixa não usa data cheia, só o dia
        }
        else if (!CheckParcelado.IsChecked)
        {
            LayoutData.IsVisible = true; 
        }
    }

    private void OnCheckParceladoChanged(object sender, CheckedChangedEventArgs e)
    {
        if (e.Value) 
        {
            CheckMensal.IsChecked = false;
            LayoutData.IsVisible = true; 
        }
        CalcularParcela();
    }

    private void OnSalvarClicked(object sender, EventArgs e)
    {
        if (string.IsNullOrWhiteSpace(EntryDesc.Text)) return;

        // Garante que o ID seja mantido na edição para não duplicar
        var registro = _itemEdicao ?? new FinanceiroRegistro { Id = Guid.NewGuid().ToString() };

        registro.Descricao = EntryDesc.Text.Trim();
        
        string valorTexto = EntryValor.Text?.Replace(".", "").Replace(",", ".") ?? "0";
        double valorTotal = double.TryParse(valorTexto, NumberStyles.Any, CultureInfo.InvariantCulture, out var v) ? v : 0;
        
        registro.Tipo = SwitchTipo.IsToggled ? "Entrada" : "Saida";
        
        // Regra de Pagamento: Mantém se já estava pago ou marca se for modo rápido
        registro.FoiPago = _isModoRapido || registro.FoiPago;
        
        registro.IsFixo = !_isModoRapido && CheckMensal.IsChecked;
        registro.IsParcelado = !_isModoRapido && CheckParcelado.IsChecked;

        // Lógica de Parcelamento
        if (registro.IsParcelado)
        {
            registro.TotalParcelas = int.TryParse(EntryParcelas.Text, out var p) ? Math.Max(p, 1) : 1;
            registro.ParcelaAtual = registro.ParcelaAtual > 0 ? registro.ParcelaAtual : 1;
            registro.Valor = valorTotal / registro.TotalParcelas; 
        }
        else
        {
            registro.TotalParcelas = 1;
            registro.Valor = valorTotal;
        }

        // Lógica de Agendamento (Mensal Fixo vs Data Normal)
        if (!_isModoRapido && CheckMensal.IsChecked && int.TryParse(EntryDiaFixo.Text, out var dia))
        {
            registro.DiaVencimentoFixo = Math.Clamp(dia, 1, 28);
            DateTime dataBase = new DateTime(DateTime.Now.Year, DateTime.Now.Month, registro.DiaVencimentoFixo);
            
            // Verifica o Switch de Pulo de Mês
            if (SwitchPularMes.IsToggled)
            {
                registro.DataVencimento = dataBase.AddMonths(1);
            }
            else
            {
                registro.DataVencimento = dataBase;
            }
        }
        else
        {
            registro.DataVencimento = PickerData.Date;
        }

        Close(registro);
    }

    private void OnCancelarClicked(object sender, EventArgs e) => Close(null);
}