using Marmorariacentral.ViewModels;

namespace Marmorariacentral.Views.Orcamentos;

public partial class DetalhesClientePage : ContentPage
{
    public DetalhesClientePage(DetalhesClienteViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;
    }
}