using Marmorariacentral.Views.Login;
using Marmorariacentral.Views.Orcamentos;
using Marmorariacentral.Views.Estoque;
using Marmorariacentral.Views.Financeiro;
using Microsoft.Maui.Controls;

namespace Marmorariacentral;

public partial class AppShell : Shell
{
    public AppShell()
    {
        InitializeComponent();

        // Registro de Rotas de Navegação
        // Isso permite o uso de Shell.Current.GoToAsync("NomeDaPagina")
        
        // Módulo de Orçamentos
        Routing.RegisterRoute(nameof(OrcamentosPage), typeof(OrcamentosPage));
        Routing.RegisterRoute(nameof(DetalhesClientePage), typeof(DetalhesClientePage));
        Routing.RegisterRoute(nameof(CalculadoraPecaPage), typeof(CalculadoraPecaPage));

        // Módulo de Estoque
        Routing.RegisterRoute(nameof(EstoquePage), typeof(EstoquePage));

        // Módulo Financeiro
        Routing.RegisterRoute(nameof(FinanceiroPage), typeof(FinanceiroPage));
    }

    /// <summary>
    /// Evento do botão "Encerrar Sessão" no Flyout ou Toolbar.
    /// Limpa as credenciais locais e redefine a Stack de navegação.
    /// </summary>
    private async void OnLogoutClicked(object sender, EventArgs e)
    {
        bool confirm = await DisplayAlert(
            "Encerrar Sessão",
            "Deseja realmente sair do sistema Central Granitos?",
            "Sair",
            "Cancelar");

        if (!confirm)
            return;

        try
        {
            // Limpeza de cache e preferências de login
            Preferences.Default.Remove("is_logged");
            Preferences.Default.Remove("user_email");

            // Para um logout limpo e profissional, substituímos a MainPage.
            // Isso limpa toda a pilha de navegação anterior do Shell.
            if (Application.Current != null)
            {
                // Redireciona para a tela de login envolta em uma NavigationPage 
                // para garantir que o fluxo de login tenha sua própria stack.
                Application.Current.MainPage = new NavigationPage(new LoginPage());
            }
        }
        catch (Exception ex)
        {
            await DisplayAlert("Erro de Logout", $"Ocorreu uma falha ao encerrar a sessão: {ex.Message}", "OK");
        }
    }
}