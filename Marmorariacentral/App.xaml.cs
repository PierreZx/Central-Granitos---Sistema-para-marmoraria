using Marmorariacentral.Services;
using Marmorariacentral.Views.Login;
using Shiny; // ADICIONADO PARA RESOLVER O ERRO CS0103 (AccessState)
using Shiny.Notifications;

namespace Marmorariacentral;

public partial class App : Application
{
    private readonly AuthService _authService;
    private readonly IServiceProvider _serviceProvider;

    // Injetamos o AuthService, o ServiceProvider e o NotificationManager
    public App(AuthService authService, IServiceProvider serviceProvider, INotificationManager notificationManager)
    {
        InitializeComponent();

        _authService = authService ?? throw new ArgumentNullException(nameof(authService));
        _serviceProvider = serviceProvider ?? throw new ArgumentNullException(nameof(serviceProvider));

        // ============================================================
        // CONFIGURAÇÃO DE CANAL E PERMISSÕES (Android)
        // ============================================================
#if ANDROID
        try 
        {
            // 1. Cria o canal para o Android saber onde entregar os alertas
            notificationManager.AddChannel(new Channel
            {
                Identifier = "CentralAlerta",
                Description = "Alertas de Vencimento de Contas",
                Importance = ChannelImportance.High
            });

            // 2. PEDIR ACESSO: Essencial para o agendamento de 08:30 e 17:00 funcionar
            // Rodamos em background para não travar a abertura do app
            Task.Run(async () => {
                var result = await notificationManager.RequestAccess();
                if (result != AccessState.Available)
                {
                    System.Diagnostics.Debug.WriteLine("Aviso: Permissão de notificação negada.");
                }
            });
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"Erro ao configurar Shiny: {ex.Message}");
        }
#endif

        InitializeApp();
    }

    private void InitializeApp()
    {
        // Verifica se o usuário já está logado (Firebase/Preferences)
        bool isLogged = _authService.CheckAutoLogin();

        if (isLogged)
        {
            // Resolve o AppShell via DI
            MainPage = _serviceProvider.GetRequiredService<AppShell>();
        }
        else
        {
            // Resolve a LoginPage via DI e coloca dentro de uma NavigationPage
            var loginPage = _serviceProvider.GetRequiredService<LoginPage>();
            MainPage = new NavigationPage(loginPage);
        }
    }
}