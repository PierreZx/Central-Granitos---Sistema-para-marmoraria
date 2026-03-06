using Marmorariacentral.Services;
using Marmorariacentral.Views.Login;
using Marmorariacentral.Models;
using Shiny; 
using Shiny.Notifications;
using System.Diagnostics;

namespace Marmorariacentral;

public partial class App : Application
{
    private readonly AuthService _authService;
    private readonly IServiceProvider _serviceProvider;
    private readonly DatabaseService _dbService;
    private readonly FirebaseService _firebaseService;

    // Injetamos todos os serviços necessários via Construtor
    public App(
        AuthService authService, 
        IServiceProvider serviceProvider, 
        INotificationManager notificationManager,
        DatabaseService dbService,
        FirebaseService firebaseService)
    {
        InitializeComponent();

        _authService = authService ?? throw new ArgumentNullException(nameof(authService));
        _serviceProvider = serviceProvider ?? throw new ArgumentNullException(nameof(serviceProvider));
        _dbService = dbService ?? throw new ArgumentNullException(nameof(dbService));
        _firebaseService = firebaseService ?? throw new ArgumentNullException(nameof(firebaseService));

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

            // 2. PEDIR ACESSO: Rodamos em background para não travar a abertura do app
            Task.Run(async () => {
                var result = await notificationManager.RequestAccess();
                if (result != AccessState.Available)
                {
                    Debug.WriteLine("Aviso: Permissão de notificação negada.");
                }
            });
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"Erro ao configurar Shiny: {ex.Message}");
        }
#endif

        InitializeApp();
    }

    /// <summary>
    /// Método responsável por varrer o SQLite e subir dados pendentes para o Firebase
    /// Limpa o banco local após a confirmação do upload.
    /// </summary>
    public async Task ExecutarSincronizacaoGlobal()
    {
        try 
        {
            Debug.WriteLine("Iniciando varredura de dados offline...");

            // 1. Busca TUDO o que está no SQLite (segurando a barra offline)
            var clientesOffline = await _dbService.GetItemsAsync<Cliente>();
            var pecasOffline = await _dbService.GetItemsAsync<PecaOrcamento>();
            var financeiroOffline = await _dbService.GetItemsAsync<FinanceiroRegistro>();

            // Se não houver nada para sincronizar, encerra
            if (!clientesOffline.Any() && !pecasOffline.Any() && !financeiroOffline.Any())
            {
                Debug.WriteLine("Nenhum dado offline encontrado.");
                return;
            }

            // 2. Tenta subir para o Firebase via método consolidado
            await _firebaseService.SincronizarTudoOfflineAsync(clientesOffline, pecasOffline, financeiroOffline);

            // 3. LIMPEZA TOTAL DO SQLITE (Online é tudo Firebase)
            foreach (var c in clientesOffline) await _dbService.DeleteItemAsync(c);
            foreach (var p in pecasOffline) await _dbService.DeleteItemAsync(p);
            foreach (var f in financeiroOffline) await _dbService.DeleteItemAsync(f);
            
            Debug.WriteLine("Sincronização concluída. SQLite limpo e sistema 100% online.");
        }
        catch (Exception ex)
        {
            // Se houver erro (falta de internet), os dados permanecem seguros no SQLite
            Debug.WriteLine($"Falha na sincronização (ainda offline?): {ex.Message}");
        }
    }

    private void InitializeApp()
    {
        // Verifica se o usuário já está logado
        bool isLogged = _authService.CheckAutoLogin();

        if (isLogged)
        {
            // Dispara a sincronização em segundo plano para não travar a UI
            _ = Task.Run(async () => await ExecutarSincronizacaoGlobal());

            // Define a página principal como o Shell
            MainPage = _serviceProvider.GetRequiredService<AppShell>();
        }
        else
        {
            // Encaminha para a tela de Login
            var loginPage = _serviceProvider.GetRequiredService<LoginPage>();
            MainPage = new NavigationPage(loginPage);
        }
    }
}