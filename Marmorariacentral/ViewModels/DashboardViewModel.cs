using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Marmorariacentral.Services;
using Marmorariacentral.Models;
using System.Collections.ObjectModel;
using Microsoft.Maui.Networking;
using System.Linq;
using Shiny;
using Shiny.Notifications;

namespace Marmorariacentral.ViewModels
{
    public partial class DashboardViewModel : ObservableObject
    {
        private readonly DatabaseService _dbService;
        private readonly INotificationManager? _notificationManager;

        [ObservableProperty]
        private string valorCaixa = "R$ 0,00";

        [ObservableProperty]
        private Color wifiStatusColor = Colors.Red;

        [ObservableProperty]
        private ObservableCollection<FinanceiroRegistro> alertasProximos = new();

        public DashboardViewModel(DatabaseService dbService, INotificationManager? notificationManager = null)
        {
            _dbService = dbService;
            _notificationManager = notificationManager;

            Connectivity.ConnectivityChanged += Connectivity_ConnectivityChanged;
            AtualizarWifiStatus();
            _ = LoadDashboardData();
        }

        [RelayCommand]
        public async Task TestarNotificacao()
        {
            if (_notificationManager == null) return;
            try
            {
                var access = await _notificationManager.RequestAccess();
                if (access == AccessState.Available)
                {
                    await _notificationManager.Send(new Notification
                    {
                        Id = 999,
                        Title = "🚀 TESTE IMEDIATO",
                        Message = "Se você está lendo isso, o Shiny está ativo!",
                        BadgeCount = 1
                    });
                }
            }
            catch (Exception ex)
            {
                await Shell.Current.DisplayAlert("Erro", ex.Message, "OK");
            }
        }

        private void Connectivity_ConnectivityChanged(object? sender, ConnectivityChangedEventArgs e) => AtualizarWifiStatus();

        private void AtualizarWifiStatus()
        {
            WifiStatusColor = Connectivity.NetworkAccess == NetworkAccess.Internet ? Colors.Green : Colors.Red;
        }

        public async Task LoadDashboardData()
        {
            try 
            {
                // Busca os dados atualizados do banco
                var financeiro = await _dbService.GetItemsAsync<FinanceiroRegistro>();

                if (financeiro == null || !financeiro.Any())
                {
                    MainThread.BeginInvokeOnMainThread(() => {
                        ValorCaixa = 0.ToString("C");
                        AlertasProximos.Clear();
                    });
                    return;
                }

                // Cálculo do Saldo (Entradas - Saídas Pagas)
                double entradas = financeiro.Where(x => x.Tipo == "Entrada" && x.FoiPago).Sum(x => x.Valor);
                double saidasPagas = financeiro.Where(x => x.Tipo == "Saida" && x.FoiPago).Sum(x => x.Valor);
                double saldo = entradas - saidasPagas;

                // Busca as próximas 3 contas a vencer (Saídas não pagas)
                var proximos = financeiro
                    .Where(x => !x.FoiPago && x.Tipo == "Saida")
                    .OrderBy(x => x.DataVencimento)
                    .Take(3)
                    .ToList();

                MainThread.BeginInvokeOnMainThread(() =>
                {
                    ValorCaixa = saldo.ToString("C");
                    
                    // CORREÇÃO: Limpa e sincroniza a lista para refletir exclusões
                    AlertasProximos.Clear();
                    foreach (var item in proximos)
                    {
                        // Garante que o texto da parcela apareça no Dashboard
                        item.DescricaoDisplay = item.TotalParcelas > 1 
                            ? $"{item.Descricao} ({item.ParcelaAtual}/{item.TotalParcelas})"
                            : item.Descricao;

                        AlertasProximos.Add(item);
                    }
                });
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Erro Dashboard: {ex.Message}");
            }
        }
    }
}