using Marmorariacentral.Services;
using Marmorariacentral.Views.Login;

namespace Marmorariacentral;

public partial class App : Application
{
    // Usamos readonly para segurança e CamelCase para o campo privado
    private readonly AuthService _authService;

    public App(AuthService authService)
    {
        InitializeComponent();

        _authService = authService;

        // Verifica se o usuário já está logado
        bool isLogged = _authService.CheckAutoLogin();

        if (isLogged)
        {
            // Se logado, vai para a casca do app (Sidebar)
            MainPage = new AppShell();
        }
        else
        {
            // Se não, vai para a tela de Login
            // Usamos NavigationPage para permitir navegação se necessário
            MainPage = new NavigationPage(new LoginPage());
        }
    }
}