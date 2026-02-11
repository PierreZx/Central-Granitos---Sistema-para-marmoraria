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

namespace Marmorariacentral;

public static class MauiProgram
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder();
        builder
            .UseMauiApp<App>()
            .UseMauiCommunityToolkit() // Essencial para Popups e lógica de UI avançada
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
        builder.Services.AddTransient<OrcamentoViewModel>();
        builder.Services.AddTransient<DashboardViewModel>();
        builder.Services.AddTransient<EstoqueViewModel>();
        builder.Services.AddTransient<LoginViewModel>();
        builder.Services.AddTransient<ProducaoViewModel>();
        builder.Services.AddTransient<FinanceiroViewModel>();
        
        // Novas ViewModels para a Calculadora
        builder.Services.AddTransient<DetalhesClienteViewModel>();
        builder.Services.AddTransient<CalculadoraPecaViewModel>();

        // Views - Transients
        builder.Services.AddTransient<DashboardPage>();
        builder.Services.AddTransient<EstoquePage>();
        builder.Services.AddTransient<LoginPage>();
        builder.Services.AddTransient<OrcamentosPage>();
        builder.Services.AddTransient<ProducaoPage>();
        builder.Services.AddTransient<FinanceiroPage>();

        // Novas Páginas do Orçamento
        builder.Services.AddTransient<DetalhesClientePage>();
        builder.Services.AddTransient<CalculadoraPecaPage>();

        // POPUPS
        builder.Services.AddTransient<CadastroChapaPopup>();
        builder.Services.AddTransient<CadastroFinanceiroPopup>();
        builder.Services.AddTransient<CadastroClientePopup>();

        // ==========================================

#if DEBUG
        builder.Logging.AddDebug();
#endif

        return builder.Build();
    }
}