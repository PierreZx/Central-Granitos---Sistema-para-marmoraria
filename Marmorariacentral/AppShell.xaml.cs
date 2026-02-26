using Marmorariacentral.Views.Login;
using Microsoft.Maui.Controls;

namespace Marmorariacentral;

public partial class AppShell : Shell
{
    public AppShell()
    {
        InitializeComponent();

        // Caso queira registrar rotas futuramente, use:
        // Routing.RegisterRoute(nameof(AlgumaPagina), typeof(AlgumaPagina));
    }

    /// <summary>
    /// Evento do botão "Encerrar Sessão"
    /// </summary>
    private async void OnLogoutClicked(object sender, EventArgs e)
    {
        bool confirm = await DisplayAlert(
            "Confirmação",
            "Deseja realmente encerrar sua sessão?",
            "Sair",
            "Cancelar");

        if (!confirm)
            return;

        try
        {
            // Remove dados salvos de login
            Preferences.Default.Remove("is_logged");
            Preferences.Default.Remove("user_email");

            // Redireciona para a tela de login
            Application.Current!.MainPage =
                new NavigationPage(new LoginPage());
        }
        catch (Exception ex)
        {
            await DisplayAlert("Erro", $"Falha ao deslogar: {ex.Message}", "OK");
        }
    }
}