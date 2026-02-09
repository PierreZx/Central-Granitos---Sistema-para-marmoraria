using Microsoft.Extensions.Logging;
using Marmorariacentral.Services;
using Marmorariacentral.ViewModels;
using Marmorariacentral.Views.Dashboard; // Ajustado conforme sua estrutura de pastas
using Marmorariacentral.Views.Estoque;   // Ajustado conforme sua estrutura de pastas
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
            .ConfigureFonts(fonts =>
            {
                fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
                fonts.AddFont("OpenSans-Semibold.ttf", "OpenSansSemibold");
            });

        // ==========================================
        // REGISTRO DE DEPENDÊNCIAS (DI)
        // ==========================================

        // Services - Singletons (Uma única instância para o app todo)
        builder.Services.AddSingleton<DatabaseService>();
        builder.Services.AddSingleton<FirebaseService>();
        builder.Services.AddSingleton<AuthService>();

        // ViewModels - Transients (Cria uma nova instância sempre que navegar)
        builder.Services.AddTransient<OrcamentoViewModel>();
        builder.Services.AddTransient<DashboardViewModel>();
        builder.Services.AddTransient<EstoqueViewModel>();
        builder.Services.AddTransient<LoginViewModel>();
        builder.Services.AddTransient<ProducaoViewModel>();
        builder.Services.AddTransient<FinanceiroViewModel>();

        // Views - Transients
        builder.Services.AddTransient<DashboardPage>();
        builder.Services.AddTransient<EstoquePage>();
        builder.Services.AddTransient<LoginPage>();
        builder.Services.AddTransient<OrcamentosPage>();
        builder.Services.AddTransient<ProducaoPage>();
        builder.Services.AddTransient<FinanceiroPage>();

        // ==========================================

#if DEBUG
        builder.Logging.AddDebug();
#endif

        return builder.Build();
    }
}