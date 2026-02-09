using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Marmorariacentral.Models;
using Marmorariacentral.Services;
using System.Collections.ObjectModel;

namespace Marmorariacentral.ViewModels
{
    public partial class OrcamentoViewModel : ObservableObject
    {
        private readonly DatabaseService _dbService;
        private readonly FirebaseService _firebaseService;

        [ObservableProperty]
        private ObservableCollection<Orcamento> orcamentos = new();

        public OrcamentoViewModel(DatabaseService dbService, FirebaseService firebaseService)
        {
            _dbService = dbService;
            _firebaseService = firebaseService;
            Task.Run(async () => await CarregarOrcamentos());
        }

        [RelayCommand]
        public async Task CarregarOrcamentos()
        {
            var lista = await _dbService.GetItemsAsync<Orcamento>();
            MainThread.BeginInvokeOnMainThread(() =>
            {
                Orcamentos.Clear();
                foreach (var item in lista)
                    Orcamentos.Add(item);
            });
        }

        [RelayCommand]
        public async Task SalvarNovoOrcamento(Orcamento novo)
        {
            // 1. Salva Local (Offline-first)
            await _dbService.SaveItemAsync(novo);
            Orcamentos.Insert(0, novo);

            // 2. Sincroniza Online
            try
            {
                await _firebaseService.SaveOrcamentoAsync(novo);
                novo.IsSynced = true;
                await _dbService.SaveItemAsync(novo);
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Erro Firebase: {ex.Message}");
            }
        }
    }
}