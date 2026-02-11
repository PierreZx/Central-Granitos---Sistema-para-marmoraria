using Marmorariacentral.ViewModels;
using System.ComponentModel;

namespace Marmorariacentral.Views.Orcamentos;

public partial class CalculadoraPecaPage : ContentPage
{
    public CalculadoraPecaPage(CalculadoraPecaViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;

        // Escuta qualquer mudança vinda da ViewModel
        viewModel.PropertyChanged += OnViewModelPropertyChanged;
    }

    private void OnViewModelPropertyChanged(object? sender, PropertyChangedEventArgs e)
    {
        // Se a propriedade que mudou for o "DesenhoPeca", forçamos o Canvas a se redesenhar
        if (e.PropertyName == nameof(CalculadoraPecaViewModel.DesenhoPeca))
        {
            // O Invalidate() faz o Windows disparar o método Draw do PecaDrawable novamente
            CanvasPeca.Invalidate();
        }
    }

    protected override void OnNavigatedTo(NavigatedToEventArgs args)
    {
        base.OnNavigatedTo(args);
        // Garante que o desenho apareça assim que a tela abrir
        CanvasPeca.Invalidate();
    }
}