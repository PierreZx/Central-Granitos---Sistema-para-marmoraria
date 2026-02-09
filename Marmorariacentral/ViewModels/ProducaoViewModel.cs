using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Marmorariacentral.Models;
using Marmorariacentral.Services;
using System.Collections.ObjectModel;

namespace Marmorariacentral.ViewModels
{
    public partial class ProducaoViewModel : ObservableObject
    {
        private readonly DatabaseService _dbService;

        [ObservableProperty]
        private ObservableCollection<Orcamento> itensNovos = new();

        [ObservableProperty]
        private ObservableCollection<Orcamento> itensEmProducao = new();

        public ProducaoViewModel(DatabaseService dbService)
        {
            _dbService = dbService;
            Task.Run(async () => await CarregarProducao());
        }

        [RelayCommand]
        public async Task CarregarProducao()
        {
            var todos = await _dbService.GetItemsAsync<Orcamento>();
            
            MainThread.BeginInvokeOnMainThread(() =>
            {
                // Limpa e filtra por EtapaProducao conforme seu fluxo
                ItensNovos.Clear();
                ItensEmProducao.Clear();

                foreach (var item in todos.Where(x => x.EtapaProducao == "Novo"))
                    ItensNovos.Add(item);

                foreach (var item in todos.Where(x => x.EtapaProducao == "Produzindo"))
                    ItensEmProducao.Add(item);
            });
        }
    }
}