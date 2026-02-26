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
    /// Gerencia a troca de abas entre Pendências e Extrato.
    /// Utiliza referências diretas aos layouts reais para evitar erros de renderização.
    /// </summary>
    private void OnTabClicked(object sender, EventArgs e)
    {
        if (sender is Button btn)
        {
            var tab = btn.CommandParameter?.ToString() ?? "Contas";

            // CORREÇÃO DEFINITIVA: Referencia os containers reais do XAML
            LayoutContas.IsVisible = (tab == "Contas");
            ListExtrato.IsVisible = (tab == "Extrato");

            if (BindingContext is FinanceiroViewModel vm)
            {
                if (tab == "Extrato")
                {
                    BtnLancar.Text = "+ LANÇAR ENTRADA/SAÍDA";
                    BtnLancar.Command = vm.AbrirLancamentoExtratoCommand;
                }
                else
                {
                    BtnLancar.Text = "+ CADASTRAR CONTA";
                    BtnLancar.Command = vm.AbrirCadastroCommand;
                }
            }

            AtualizarVisualTabs(tab);
        }
    }

    private void AtualizarVisualTabs(string tabAtiva)
    {
        bool isContas = tabAtiva == "Contas";

        // Estética das abas para feedback visual ao usuário
        BtnTabContas.TextColor = isContas ? Color.FromArgb("#8B1A1A") : Color.FromArgb("#777");
        BtnTabContas.FontAttributes = isContas ? FontAttributes.Bold : FontAttributes.None;

        BtnTabExtrato.TextColor = !isContas ? Color.FromArgb("#8B1A1A") : Color.FromArgb("#777");
        BtnTabExtrato.FontAttributes = !isContas ? FontAttributes.Bold : FontAttributes.None;
    }

    /// <summary>
    /// Dispara o comando de confirmação de pagamento ao marcar o CheckBox.
    /// </summary>
    private async void OnPagoChanged(object sender, CheckedChangedEventArgs e)
    {
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
    /// Filtro em tempo real enquanto o usuário digita.
    /// </summary>
    private void OnSearchTextChanged(object sender, TextChangedEventArgs e)
    {
        if (BindingContext is FinanceiroViewModel vm)
        {
            vm.FiltrarCommand.Execute(e.NewTextValue);
        }
    }

    /// <summary>
    /// Ordenação da lista através do seletor.
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