namespace Marmorariacentral.Views.Financeiro;

public partial class FinanceiroPage : ContentPage
{
    public FinanceiroPage(ViewModels.FinanceiroViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;
    }

    // Lógica para trocar de aba
    private void OnTabClicked(object sender, EventArgs e)
    {
        var btn = (Button)sender;
        var tab = btn.CommandParameter.ToString();

        // Esconde tudo
        ViewContas.IsVisible = false;
        ViewExtrato.IsVisible = false;
        ViewProducao.IsVisible = false;

        // Mostra a selecionada
        if (tab == "Contas") ViewContas.IsVisible = true;
        else if (tab == "Extrato") ViewExtrato.IsVisible = true;
        else if (tab == "Producao") ViewProducao.IsVisible = true;
    }

    private async void OnPagoChanged(object sender, CheckedChangedEventArgs e)
    {
        if (e.Value && sender is CheckBox cb && cb.BindingContext is Models.FinanceiroRegistro registro)
        {
            var vm = (ViewModels.FinanceiroViewModel)BindingContext;
            await vm.ConfirmarPagamentoCommand.ExecuteAsync(registro);
        }
    }
}