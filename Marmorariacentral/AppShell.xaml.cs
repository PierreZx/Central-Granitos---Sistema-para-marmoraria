using Marmorariacentral.Views.Login;
using Microsoft.Maui.Controls;

namespace Marmorariacentral;

public partial class AppShell : Shell
{
    public AppShell()
    {
        InitializeComponent();
        
        // Registrar rotas aqui se você for usar navegação por strings (Routing.RegisterRoute)
        // Por enquanto, como estamos usando Flyout, a Shell gerencia as instâncias.
    }

    /// <summary>
    /// Evento disparado pelo MenuItem "Sair do Sistema" definido no XAML.
    /// </summary>
    private async void OnLogoutClicked(object sender, EventArgs e)
    {
        // Exibe um alerta de confirmação moderno
        bool confirm = await DisplayAlert("Confirmação", "Deseja realmente encerrar sua sessão?", "Sim", "Cancelar");

        if (confirm)
        {
            try
            {
                // 1. Limpa as preferências de login para que o app não faça auto-login na próxima vez
                Preferences.Default.Remove("is_logged");
                Preferences.Default.Remove("user_email");

                // 2. Redireciona o usuário para a tela de login
                // Usamos NavigationPage para garantir que a pilha de navegação seja resetada
                if (Application.Current != null)
                {
                    Application.Current.MainPage = new NavigationPage(new LoginPage());
                }
            }
            catch (Exception ex)
            {
                // Caso ocorra algum erro inesperado na transição de telas
                await DisplayAlert("Erro", "Não foi possível deslogar: " + ex.Message, "OK");
            }
        }
    }
}