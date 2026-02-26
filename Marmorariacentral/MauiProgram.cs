using Microsoft.Extensions.Logging;
using CommunityToolkit.Maui;
using Marmorariacentral.Services;
using Marmorariacentral.ViewModels;
using Marmorariacentral.Views.Dashboard;
using Marmorariacentral.Views.Login;
using Marmorariacentral.Views.Financeiro;
using Microsoft.Maui.LifecycleEvents;
using Shiny;
using Shiny.Notifications;

namespace Marmorariacentral;

public static class MauiProgram
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder();
        builder
            .UseMauiApp<App>()
            .UseMauiCommunityToolkit()
            .UseShiny() 
            .ConfigureFonts(fonts =>
            {
                fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
                fonts.AddFont("OpenSans-Semibold.ttf", "OpenSansSemibold");
            });

        // ============================================================
        // CONFIGURAÇÃO DE NOTIFICAÇÕES (Shiny 3.3.1)
        // ============================================================
#if !WINDOWS
        // REGISTRO SIMPLES: Necessário para a versão 3.3.1 evitar o erro CS1660.
        // A configuração do canal (AddChannel) foi movida para o App.xaml.cs.
        builder.Services.AddNotifications();
#endif

        // ==========================================
        // REGISTRO DE SERVIÇOS (Singletons)
        // ==========================================
        builder.Services.AddSingleton<DatabaseService>();
        builder.Services.AddSingleton<FirebaseService>();
        builder.Services.AddSingleton<AuthService>();

        // ==========================================
        // VIEWMODELS (Transients)
        // ==========================================
        builder.Services.AddTransient<LoginViewModel>();
        builder.Services.AddTransient<DashboardViewModel>();
        builder.Services.AddTransient<FinanceiroViewModel>();

        // ==========================================
        // PAGES / VIEWS (Transients)
        // ==========================================
        builder.Services.AddTransient<LoginPage>();
        builder.Services.AddTransient<DashboardPage>();
        builder.Services.AddTransient<FinanceiroPage>();
        builder.Services.AddTransient<AppShell>();

        // ==========================================
        // POPUPS (Financeiro apenas)
        // ==========================================
        builder.Services.AddTransient<CadastroFinanceiroPopup>();

        // ==========================================
        // CONFIGURAÇÃO DA JANELA NO WINDOWS
        // ==========================================
#if WINDOWS
        builder.ConfigureLifecycleEvents(events =>
        {
            events.AddWindows(windows =>
            {
                windows.OnWindowCreated(window =>
                {
                    window.ExtendsContentIntoTitleBar = false;
                    var handle = WinRT.Interop.WindowNative.GetWindowHandle(window);
                    var id = Microsoft.UI.Win32Interop.GetWindowIdFromWindow(handle);
                    var appWindow = Microsoft.UI.Windowing.AppWindow.GetFromWindowId(id);
                    if (appWindow is not null)
                    {
                        appWindow.Title = "Central Granitos - Gestão de Caixa";
                        appWindow.MoveAndResize(new Windows.Graphics.RectInt32(100, 100, 1280, 800));
                    }
                });
            });
        });
#endif

#if DEBUG
        builder.Logging.AddDebug();
#endif

        return builder.Build();
    }
}