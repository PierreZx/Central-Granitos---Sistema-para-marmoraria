using CommunityToolkit.Mvvm.ComponentModel;
using Marmorariacentral.Services;
using System.Collections.ObjectModel;
using Microsoft.Maui.Networking;

namespace Marmorariacentral.ViewModels
{
    public partial class DashboardViewModel : ObservableObject
    {
        private readonly DatabaseService _dbService;

        [ObservableProperty]
        private string valorCaixa = "R$ 0,00";

        [ObservableProperty]
        private int totalChapas = 0;

        [ObservableProperty]
        private int totalOrcamentos = 0;

        [ObservableProperty]
        private Color wifiStatusColor = Colors.Red;

        public DashboardViewModel(DatabaseService dbService)
        {
            _dbService = dbService;

            Connectivity.ConnectivityChanged += Connectivity_ConnectivityChanged;
            AtualizarWifiStatus();
        }

        private void Connectivity_ConnectivityChanged(object? sender, ConnectivityChangedEventArgs e)

        {
            AtualizarWifiStatus();
        }

        private void AtualizarWifiStatus()
        {
            if (Connectivity.NetworkAccess == NetworkAccess.Internet)
                WifiStatusColor = Colors.Green;
            else
                WifiStatusColor = Colors.Red;
        }

        public async Task LoadDashboardData()
        {
            var orcamentos = await _dbService.GetItemsAsync<Models.Orcamento>();
            var estoque = await _dbService.GetItemsAsync<Models.EstoqueItem>();
            var financeiro = await _dbService.GetItemsAsync<Models.FinanceiroRegistro>();

            TotalOrcamentos = orcamentos.Count;
            TotalChapas = estoque.Sum(x => x.QuantidadeChapas);

            double saldo = financeiro
                .Where(x => x.Tipo == "Entrada")
                .Sum(x => x.Valor)
                - financeiro
                .Where(x => x.Tipo == "Saida" && x.FoiPago)
                .Sum(x => x.Valor);

            ValorCaixa = saldo.ToString("C");
        }
    }
}
