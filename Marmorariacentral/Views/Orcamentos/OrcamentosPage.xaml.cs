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

        _viewModel?.CarregarDadosCommand?.Execute(null);
    }
}
