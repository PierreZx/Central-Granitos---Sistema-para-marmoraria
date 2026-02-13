using Microsoft.Extensions.Logging;
using CommunityToolkit.Maui;
using Marmorariacentral.Services;
using Marmorariacentral.ViewModels;
using Marmorariacentral.Views.Dashboard;
using Marmorariacentral.Views.Estoque;
using Marmorariacentral.Views.Login;
using Marmorariacentral.Views.Orcamentos;
using Marmorariacentral.Views.Producao;
using Marmorariacentral.Views.Financeiro;
using Microsoft.Maui.LifecycleEvents;

namespace Marmorariacentral;

public static class MauiProgram
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder();
        builder
            .UseMauiApp<App>()
            .UseMauiCommunityToolkit()
            .ConfigureFonts(fonts =>
            {
                fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
                fonts.AddFont("OpenSans-Semibold.ttf", "OpenSansSemibold");
            });

        // ==========================================
        // REGISTRO DE DEPENDÊNCIAS (DI)
        // ==========================================

        // Services - Singletons
        builder.Services.AddSingleton<DatabaseService>();
        builder.Services.AddSingleton<FirebaseService>();
        builder.Services.AddSingleton<AuthService>();

        // ViewModels - Transients
        builder.Services.AddTransient<LoginViewModel>();
        builder.Services.AddTransient<DashboardViewModel>();
        builder.Services.AddTransient<OrcamentoViewModel>();
        builder.Services.AddTransient<EstoqueViewModel>();
        builder.Services.AddTransient<ProducaoViewModel>();
        builder.Services.AddTransient<FinanceiroViewModel>();
        builder.Services.AddTransient<DetalhesClienteViewModel>();
        builder.Services.AddTransient<CalculadoraPecaViewModel>();

        // Views - Transients
        builder.Services.AddTransient<LoginPage>();
        builder.Services.AddTransient<DashboardPage>();
        builder.Services.AddTransient<OrcamentosPage>();
        builder.Services.AddTransient<EstoquePage>();
        builder.Services.AddTransient<ProducaoPage>();
        builder.Services.AddTransient<FinanceiroPage>();
        builder.Services.AddTransient<DetalhesClientePage>();
        builder.Services.AddTransient<CalculadoraPecaPage>();

        // Popups
        builder.Services.AddTransient<CadastroChapaPopup>();
        builder.Services.AddTransient<CadastroFinanceiroPopup>();
        builder.Services.AddTransient<CadastroClientePopup>();

        // ==========================================
        // CONFIGURAÇÃO DO WINDOW (SOMENTE WINDOWS)
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
                        appWindow.Title = "Central Granitos - Marmoraria";
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