using Marmorariacentral.ViewModels;

namespace Marmorariacentral.Views.Orcamentos;

public partial class CalculadoraPecaPage : ContentPage
{
    private CalculadoraPecaViewModel? _viewModel;

    public CalculadoraPecaPage(CalculadoraPecaViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;
        _viewModel = viewModel;

        _viewModel.PropertyChanged += (s, e) => CanvasPeca?.Invalidate();
    }

    protected override void OnDisappearing()
    {
        base.OnDisappearing();
        if (_viewModel != null)
        {
            _viewModel.PropertyChanged -= (s, e) => CanvasPeca?.Invalidate();
        }
    }
}