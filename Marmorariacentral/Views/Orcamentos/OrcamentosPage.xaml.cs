using Microsoft.Maui.Controls;
using Marmorariacentral.ViewModels;

namespace Marmorariacentral.Views.Orcamentos;

public partial class OrcamentosPage : ContentPage
{
    private readonly OrcamentoViewModel _viewModel;

    public OrcamentosPage(OrcamentoViewModel viewModel)
    {
        InitializeComponent();

        _viewModel = viewModel;
        BindingContext = _viewModel;
    }

    protected override void OnAppearing()
    {
        base.OnAppearing();

        // O comando de carregar dados é essencial para atualizar a lista 
        // sempre que você volta de uma tela de cadastro ou detalhes.
        _viewModel?.CarregarDadosCommand?.Execute(null);
    }
}