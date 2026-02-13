using Marmorariacentral.Views.Login;
using Marmorariacentral.Views.Orcamentos;
using Microsoft.Maui.Controls;

namespace Marmorariacentral;

public partial class AppShell : Shell
{
    public AppShell()
    {
        InitializeComponent();

        // --- REGISTRO DE ROTAS - PADRÃO UNIFICADO ---
        // IMPORTANTE: Use o mesmo padrão em TODOS os lugares!
        Routing.RegisterRoute("DetalhesClientePage", typeof(DetalhesClientePage));
        Routing.RegisterRoute("CalculadoraPecaPage", typeof(CalculadoraPecaPage));
    }

    private async void OnLogoutClicked(object sender, EventArgs e)
    {
        bool confirm = await DisplayAlert("Confirmação", "Deseja realmente encerrar sua sessão?", "Sair", "Cancelar");

        if (confirm)
        {
            try
            {
                Preferences.Default.Remove("is_logged");
                Preferences.Default.Remove("user_email");

                var handler = App.Current?.Handler;
                var services = handler?.MauiContext?.Services;
                var loginPage = services?.GetService<LoginPage>();

                if (loginPage != null && Application.Current != null)
                {
                    Application.Current.MainPage = new NavigationPage(loginPage);
                }
                else
                {
                    if (Application.Current != null)
                        Application.Current.MainPage = new NavigationPage(new LoginPage());
                }
            }
            catch (Exception ex)
            {
                await DisplayAlert("Erro", "Falha ao deslogar: " + ex.Message, "OK");
            }
        }
    }
}