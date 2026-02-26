using Marmorariacentral.ViewModels;
using Microsoft.Maui.Controls.Xaml;

namespace Marmorariacentral.Views.Dashboard;

[XamlCompilation(XamlCompilationOptions.Compile)]
public partial class DashboardPage : ContentPage
{
    private readonly DashboardViewModel _viewModel;

    public DashboardPage(DashboardViewModel viewModel)
    {
        InitializeComponent();
        
        // Define o ViewModel recebido por Injeção de Dependência
        _viewModel = viewModel;
        BindingContext = _viewModel;
    }

    /// <summary>
    /// Sobrescreve o método de exibição da página para atualizar 
    /// os dados do caixa sempre que o usuário navegar para o Dashboard.
    /// </summary>
    protected override async void OnAppearing()
    {
        base.OnAppearing();
        
        if (_viewModel != null)
        {
            // Carrega os dados de Saldo e status de Conexão configurados no ViewModel simplificado
            await _viewModel.LoadDashboardData();
        }
    }
}