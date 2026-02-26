using Marmorariacentral.ViewModels;

namespace Marmorariacentral.Views.Orcamentos;

public partial class DetalhesClientePage : ContentPage // SEM ACENTO
{
    public DetalhesClientePage(DetalhesClienteViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;
    }
}