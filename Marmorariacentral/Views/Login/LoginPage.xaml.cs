using Marmorariacentral.Services;

namespace Marmorariacentral.Views.Login;

public partial class LoginPage : ContentPage
{
    private readonly AuthService _authService;

    // Injeção de dependência pelo construtor (Padrão Sênior)
    public LoginPage()
    {
        InitializeComponent();
        _authService = new AuthService(); // No futuro, usaremos o Handler do MAUI aqui
    }

    private async void OnLoginClicked(object sender, EventArgs e)
    {
        if (sender is not Button button) return;

        // Animação de clique
        await button.ScaleTo(0.95, 50);
        await button.ScaleTo(1.0, 50);

        string email = EmailEntry.Text ?? string.Empty;
        string password = PasswordEntry.Text ?? string.Empty;

        if (string.IsNullOrWhiteSpace(email) || string.IsNullOrWhiteSpace(password))
        {
            await DisplayAlert("Erro", "Preencha todos os campos.", "OK");
            return;
        }

        bool success = await _authService.LoginAsync(email, password);

        if (success)
        {
            // Uso seguro do Application.Current
            if (Application.Current != null)
            {
                Application.Current.MainPage = new AppShell();
            }
        }
        else
        {
            await DisplayAlert("Acesso Negado", "E-mail ou senha incorretos.", "Tentar novamente");
        }
    }
}