using Microsoft.Extensions.Logging;
using CommunityToolkit.Maui;
using Marmorariacentral.Services;
using Marmorariacentral.ViewModels;
using Marmorariacentral.Views.Dashboard;
using Marmorariacentral.Views.Login;
using Marmorariacentral.Views.Financeiro;
using Marmorariacentral.Views.Estoque;
using Marmorariacentral.Views.Orcamentos;
using Marmorariacentral.Drawables;
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

        // ==========================================
        // NOTIFICAÇÕES
        // ==========================================
#if !WINDOWS
        builder.Services.AddNotifications();
#endif

        // ==========================================
        // SERVIÇOS
        // ==========================================

        builder.Services.AddSingleton<DatabaseService>();
        builder.Services.AddSingleton<FirebaseService>();
        builder.Services.AddSingleton<AuthService>();

        // Serviço de geração de PDF
        builder.Services.AddSingleton<PdfService>();

        // Adapter de canvas usado para desenhar no PDF
        builder.Services.AddTransient<SkiaCanvasAdapter>();

        // ==========================================
        // VIEWMODELS
        // ==========================================

        builder.Services.AddTransient<LoginViewModel>();
        builder.Services.AddTransient<DashboardViewModel>();
        builder.Services.AddTransient<FinanceiroViewModel>();
        builder.Services.AddTransient<EstoqueViewModel>();
        builder.Services.AddTransient<OrcamentoViewModel>();
        builder.Services.AddTransient<DetalhesClienteViewModel>();
        builder.Services.AddTransient<CalculadoraPecaViewModel>();

        // ==========================================
        // PAGES
        // ==========================================

        builder.Services.AddTransient<LoginPage>();
        builder.Services.AddTransient<DashboardPage>();
        builder.Services.AddTransient<FinanceiroPage>();
        builder.Services.AddTransient<EstoquePage>();
        builder.Services.AddTransient<OrcamentosPage>();
        builder.Services.AddTransient<DetalhesClientePage>();
        builder.Services.AddTransient<CalculadoraPecaPage>();
        builder.Services.AddTransient<AppShell>();

        // ==========================================
        // POPUPS
        // ==========================================

        builder.Services.AddTransient<CadastroFinanceiroPopup>();
        builder.Services.AddTransient<CadastroChapaPopup>();
        builder.Services.AddTransient<CadastroClientePopup>();

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
                        appWindow.Title = "Central Granitos - Gestão Integrada";

                        appWindow.MoveAndResize(
                            new Windows.Graphics.RectInt32(
                                100,
                                100,
                                1280,
                                800
                            )
                        );
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