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
    /// Força a atualização dos dados e reconexão com o Firebase ao abrir a página.
    /// </summary>
    protected override async void OnAppearing()
    {
        base.OnAppearing();
        if (BindingContext is FinanceiroViewModel vm)
        {
            // Garante que a lista não esteja vazia ao entrar
            await vm.CarregarDados();
        }
    }

    /// <summary>
    /// Gerencia a troca de abas entre Contas, Orçamentos e Extrato.
    /// </summary>
    private void OnTabClicked(object sender, EventArgs e)
    {
        if (sender is Button btn)
        {
            var tab = btn.CommandParameter?.ToString() ?? "Contas";

            // Gerencia a visibilidade dos 3 containers do XAML
            LayoutContas.IsVisible = (tab == "Contas");
            LayoutOrcamentos.IsVisible = (tab == "Orcamentos");
            ListExtrato.IsVisible = (tab == "Extrato");

            if (BindingContext is FinanceiroViewModel vm)
            {
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
                else 
                {
                    BtnLancar.IsVisible = false;
                }
            }

            AtualizarVisualTabs(tab);
        }
    }

    private void AtualizarVisualTabs(string tabAtiva)
    {
        BtnTabContas.TextColor = tabAtiva == "Contas" ? Color.FromArgb("#8B1A1A") : Color.FromArgb("#777");
        BtnTabContas.FontAttributes = tabAtiva == "Contas" ? FontAttributes.Bold : FontAttributes.None;

        BtnTabOrcamentos.TextColor = tabAtiva == "Orcamentos" ? Color.FromArgb("#8B1A1A") : Color.FromArgb("#777");
        BtnTabOrcamentos.FontAttributes = tabAtiva == "Orcamentos" ? FontAttributes.Bold : FontAttributes.None;

        BtnTabExtrato.TextColor = tabAtiva == "Extrato" ? Color.FromArgb("#8B1A1A") : Color.FromArgb("#777");
        BtnTabExtrato.FontAttributes = tabAtiva == "Extrato" ? FontAttributes.Bold : FontAttributes.None;
    }

    private async void OnPagoChanged(object sender, CheckedChangedEventArgs e)
        {
            // Removida a trava IsFocused que estava bloqueando o clique em alguns aparelhos
            // A nova trava verifica se o valor mudou para "True" (Marcado)
            if (sender is CheckBox cb && e.Value) 
            {
                if (cb.BindingContext is FinanceiroRegistro registro && BindingContext is FinanceiroViewModel vm)
                {
                    // Dispara o comando de confirmação no ViewModel
                    await vm.ConfirmarPagamentoCommand.ExecuteAsync(registro);
                    
                    // Se o usuário cancelar no meio do caminho, o CarregarDados do ViewModel 
                    // resetará o checkbox para desmarcado automaticamente.
                }
            }
        }

    private void OnSearchTextChanged(object sender, TextChangedEventArgs e)
    {
        if (BindingContext is FinanceiroViewModel vm)
        {
            vm.FiltrarCommand.Execute(e.NewTextValue);
        }
    }

    public async Task MostrarFeedback(bool sucesso, string mensagem)
    {
        // Configura as cores e ícones
        IconFeedback.Text = sucesso ? "✅" : "❌";
        IconFeedback.TextColor = sucesso ? Colors.Green : Colors.Red;
        TxtFeedback.Text = mensagem;

        // Inicia animação
        OverlayFeedback.IsVisible = true;
        OverlayFeedback.Opacity = 0;
        OverlayFeedback.Scale = 0.5;

        // Animação de entrada (Fade in + Zoom)
        await Task.WhenAll(
            OverlayFeedback.FadeTo(1, 250),
            OverlayFeedback.ScaleTo(1, 250, Easing.SpringOut)
        );

        // Espera 2 segundos para o usuário ler
        await Task.Delay(2000);

        // Animação de saída
        await OverlayFeedback.FadeTo(0, 250);
        OverlayFeedback.IsVisible = false;
    }

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