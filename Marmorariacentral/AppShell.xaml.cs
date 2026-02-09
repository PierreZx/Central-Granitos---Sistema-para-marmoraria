using Marmorariacentral.Views.Login;
using Microsoft.Maui.Controls;

namespace Marmorariacentral;

public partial class AppShell : Shell
{
    public AppShell()
    {
        InitializeComponent();
    }

    private async void OnLogoutClicked(object sender, EventArgs e)
    {
        // Confirmação para evitar deslogar sem querer
        bool confirm = await DisplayAlert("Confirmação", "Deseja realmente encerrar sua sessão?", "Sair", "Cancelar");

        if (confirm)
        {
            try
            {
                // 1. Limpa as credenciais locais
                Preferences.Default.Remove("is_logged");
                Preferences.Default.Remove("user_email");

                // 2. Redireciona de forma segura usando o ServiceProvider com null-checks (resolve CS8602)
                var handler = App.Current?.Handler;
                var services = handler?.MauiContext?.Services;
                
                // Buscamos a LoginPage registrada no MauiProgram.cs
                var loginPage = services?.GetService<LoginPage>();

                if (loginPage != null && Application.Current != null)
                {
                    // Reseta a navegação e joga para a tela de login
                    Application.Current.MainPage = new NavigationPage(loginPage);
                }
                else
                {
                    // Fallback de segurança caso o DI falhe por algum motivo
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