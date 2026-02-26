using Marmorariacentral.ViewModels;

namespace Marmorariacentral.Views.Orcamentos;

public partial class CalculadoraPecaPage : ContentPage
{
    private readonly CalculadoraPecaViewModel _viewModel;

    public CalculadoraPecaPage(CalculadoraPecaViewModel viewModel)
    {
        InitializeComponent();
        
        _viewModel = viewModel;
        BindingContext = _viewModel;

        // Invalida os dois canvas (Tablet e Mobile) sempre que houver mudança nas propriedades
        _viewModel.PropertyChanged += OnViewModelPropertyChanged;
    }

    private void OnViewModelPropertyChanged(object? sender, System.ComponentModel.PropertyChangedEventArgs e)
    {
        // Força a atualização do desenho técnico em tempo real
        MainThread.BeginInvokeOnMainThread(() =>
        {
            CanvasPeca?.Invalidate();       // Canvas da coluna lateral (Tablet)
            CanvasPecaMobile?.Invalidate(); // Canvas do topo da lista (Celular)
        });
    }

    protected override void OnDisappearing()
    {
        base.OnDisappearing();
        
        // Remove o evento para evitar vazamento de memória
        if (_viewModel != null)
        {
            _viewModel.PropertyChanged -= OnViewModelPropertyChanged;
        }
    }
}