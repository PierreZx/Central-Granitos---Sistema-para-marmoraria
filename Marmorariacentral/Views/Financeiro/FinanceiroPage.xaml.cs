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
    /// Gerencia a troca de abas entre Contas, Orçamentos e Extrato.
    /// </summary>
    private void OnTabClicked(object sender, EventArgs e)
    {
        if (sender is Button btn)
        {
            var tab = btn.CommandParameter?.ToString() ?? "Contas";

            // Gerencia a visibilidade dos 3 containers do XAML para as abas
            LayoutContas.IsVisible = (tab == "Contas");
            LayoutOrcamentos.IsVisible = (tab == "Orcamentos");
            ListExtrato.IsVisible = (tab == "Extrato");

            if (BindingContext is FinanceiroViewModel vm)
            {
                // Ajusta a função do botão de lançamento principal dependendo da aba
                if (tab == "Extrato")
                {
                    BtnLancar.Text = "+ LANÇAR ENTRADA/SAÍDA";
                    BtnLancar.Command = vm.AbrirLancamentoExtratoCommand;
                    BtnLancar.IsVisible = true;
                }
                else if (tab == "Contas")
                {
                    BtnLancar.Text = "+ CADASTRAR CONTA";
                    BtnLancar.Command = vm.AbrirCadastroCommand;
                    BtnLancar.IsVisible = true;
                }
                else // Na aba de orçamentos o botão principal some (pois eles vêm da outra tela)
                {
                    BtnLancar.IsVisible = false;
                }
            }

            AtualizarVisualTabs(tab);
        }
    }

    private void AtualizarVisualTabs(string tabAtiva)
    {
        // Define as cores baseadas na aba ativa para feedback visual
        BtnTabContas.TextColor = tabAtiva == "Contas" ? Color.FromArgb("#8B1A1A") : Color.FromArgb("#777");
        BtnTabContas.FontAttributes = tabAtiva == "Contas" ? FontAttributes.Bold : FontAttributes.None;

        BtnTabOrcamentos.TextColor = tabAtiva == "Orcamentos" ? Color.FromArgb("#8B1A1A") : Color.FromArgb("#777");
        BtnTabOrcamentos.FontAttributes = tabAtiva == "Orcamentos" ? FontAttributes.Bold : FontAttributes.None;

        BtnTabExtrato.TextColor = tabAtiva == "Extrato" ? Color.FromArgb("#8B1A1A") : Color.FromArgb("#777");
        BtnTabExtrato.FontAttributes = tabAtiva == "Extrato" ? FontAttributes.Bold : FontAttributes.None;
    }

    /// <summary>
    /// Dispara o comando de confirmação de pagamento ao marcar o CheckBox.
    /// </summary>
    private async void OnPagoChanged(object sender, CheckedChangedEventArgs e)
    {
        // Se desmarcar o checkbox, não faz nada (proteção contra cliques acidentais)
        if (!e.Value) return;

        if (sender is CheckBox cb && cb.BindingContext is FinanceiroRegistro registro)
        {
            // Verificação de segurança para o BindingContext
            if (BindingContext is FinanceiroViewModel vm && registro != null)
            {
                // Envia para a lógica de confirmação e geração de histórico
                await vm.ConfirmarPagamentoCommand.ExecuteAsync(registro);
            }
        }
    }

    /// <summary>
    /// Filtro em tempo real enquanto o usuário digita na SearchBar.
    /// </summary>
    private void OnSearchTextChanged(object sender, TextChangedEventArgs e)
    {
        if (BindingContext is FinanceiroViewModel vm)
        {
            vm.FiltrarCommand.Execute(e.NewTextValue);
        }
    }

    /// <summary>
    /// Ordenação da lista através do seletor (Picker).
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