using CommunityToolkit.Mvvm.ComponentModel;
using Marmorariacentral.Services;
using System.Collections.ObjectModel;

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

        public DashboardViewModel(DatabaseService dbService)
        {
            _dbService = dbService;
            Task.Run(async () => await LoadDashboardData());
        }

        public async Task LoadDashboardData()
        {
            // Busca dados reais do SQLite
            var orcamentos = await _dbService.GetItemsAsync<Models.Orcamento>();
            var estoque = await _dbService.GetItemsAsync<Models.EstoqueItem>();
            var financeiro = await _dbService.GetItemsAsync<Models.FinanceiroRegistro>();

            // Atualiza as propriedades (o que fará a tela mudar automaticamente)
            TotalOrcamentos = orcamentos.Count;
            TotalChapas = (int)estoque.Sum(x => x.QuantidadeChapas);
            
            double saldo = financeiro.Where(x => x.Tipo == "Entrada").Sum(x => x.Valor) - 
                           financeiro.Where(x => x.Tipo == "Saida" && x.FoiPago).Sum(x => x.Valor);
            
            ValorCaixa = saldo.ToString("C");
        }
    }
}