using Marmorariacentral.ViewModels;

namespace Marmorariacentral.Views.Orcamentos;

public partial class DetalhesClientePage : ContentPage
{
    private readonly DetalhesClienteViewModel _viewModel;

    public DetalhesClientePage(DetalhesClienteViewModel viewModel)
    {
        InitializeComponent();
        
        _viewModel = viewModel;
        BindingContext = _viewModel;
    }

    protected override void OnAppearing()
    {
        base.OnAppearing();
    }

    private async void GerarPdfTecnico_Clicked(object sender, EventArgs e)
    {
        // Valida se o container de captura existe e se o comando pode ser executado
        if (ContainerPrincipal != null && _viewModel.GerarPdfTecnicoCommand.CanExecute(ContainerPrincipal))
        {
            // O ContainerPrincipal é passado para o CaptureAsync dentro do PdfService
            await _viewModel.GerarPdfTecnicoCommand.ExecuteAsync(ContainerPrincipal);
        }
    }

    private async void GerarOrcamentoPdf_Clicked(object sender, EventArgs e)
    {
        // Valida se o container de captura existe e se o comando pode ser executado
        if (ContainerPrincipal != null && _viewModel.GerarOrcamentoPdfCommand.CanExecute(ContainerPrincipal))
        {
            // O ContainerPrincipal é passado para o CaptureAsync dentro do PdfService
            await _viewModel.GerarOrcamentoPdfCommand.ExecuteAsync(ContainerPrincipal);
        }
    }
}