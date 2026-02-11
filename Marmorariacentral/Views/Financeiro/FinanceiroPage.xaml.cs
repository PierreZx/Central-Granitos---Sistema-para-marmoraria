using Marmorariacentral.ViewModels;
using Marmorariacentral.Models;

namespace Marmorariacentral.Views.Financeiro;

public partial class FinanceiroPage : ContentPage
{
    public FinanceiroPage(FinanceiroViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;
    }

    /// <summary>
    /// Troca de abas (Contas, Extrato, Produção)
    /// </summary>
    private void OnTabClicked(object sender, EventArgs e)
    {
        if (sender is Button btn && btn.CommandParameter != null)
        {
            var tab = btn.CommandParameter.ToString();

            ListContas.IsVisible = (tab == "Contas");
            ListExtrato.IsVisible = (tab == "Extrato");
            ViewProducao.IsVisible = (tab == "Producao");

            // Ajuste do Botão de Lançamento
            if (tab == "Extrato")
            {
                BtnLancar.Text = "+ LANÇAR ENTRADA/SAÍDA";
                BtnLancar.Command = ((FinanceiroViewModel)BindingContext).AbrirLancamentoExtratoCommand;
            }
            else
            {
                BtnLancar.Text = "+ CADASTRAR CONTA";
                BtnLancar.Command = ((FinanceiroViewModel)BindingContext).AbrirCadastroCommand;
            }

            // Estética das Tabs
            BtnTabContas.TextColor = (tab == "Contas") ? Color.FromArgb("#8B1A1A") : Color.FromArgb("#777");
            BtnTabExtrato.TextColor = (tab == "Extrato") ? Color.FromArgb("#8B1A1A") : Color.FromArgb("#777");
        }
    }

    /// <summary>
    /// Popup de confirmação de pagamento
    /// </summary>
    private async void OnPagoChanged(object sender, CheckedChangedEventArgs e)
    {
        // só dispara quando o usuário marca
        if (!e.Value) return;

        if (sender is CheckBox cb && cb.BindingContext is FinanceiroRegistro registro)
        {
            if (BindingContext is FinanceiroViewModel vm)
            {
                await vm.ConfirmarPagamentoCommand.ExecuteAsync(registro);
            }
        }
    }

    /// <summary>
    /// Filtro em tempo real enquanto digita
    /// </summary>
    private void OnSearchTextChanged(object sender, TextChangedEventArgs e)
    {
        if (BindingContext is FinanceiroViewModel vm)
        {
            vm.FiltrarCommand.Execute(e.NewTextValue);
        }
    }

    /// <summary>
    /// Ordenação da lista
    /// </summary>
    private void OnSortChanged(object sender, EventArgs e)
    {
        if (sender is Picker picker && BindingContext is FinanceiroViewModel vm)
        {
            var criterio = picker.SelectedItem?.ToString();
            if (!string.IsNullOrEmpty(criterio))
            {
                vm.OrdenarLista(criterio);
            }
        }
    }
}
