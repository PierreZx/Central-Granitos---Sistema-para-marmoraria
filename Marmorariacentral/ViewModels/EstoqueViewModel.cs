using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Marmorariacentral.Models;
using Marmorariacentral.Services;
using System.Collections.ObjectModel;

namespace Marmorariacentral.ViewModels
{
    public partial class EstoqueViewModel : ObservableObject
    {
        private readonly DatabaseService _dbService;
        private readonly FirebaseService _firebaseService;

        [ObservableProperty]
        private ObservableCollection<EstoqueItem> itensEstoque = new();

        public EstoqueViewModel(DatabaseService dbService, FirebaseService firebaseService)
        {
            _dbService = dbService;
            _firebaseService = firebaseService;
            
            // Carrega os dados ao iniciar
            Task.Run(async () => await CarregarEstoque());
        }

        [RelayCommand]
        public async Task CarregarEstoque()
        {
            var lista = await _dbService.GetItemsAsync<EstoqueItem>();
            MainThread.BeginInvokeOnMainThread(() =>
            {
                ItensEstoque.Clear();
                foreach (var item in lista)
                    ItensEstoque.Add(item);
            });
        }

        [RelayCommand]
        public async Task AdicionarChapa(EstoqueItem novoItem)
        {
            // 1. Salva no SQLite (Garante o funcionamento Offline)
            await _dbService.SaveItemAsync(novoItem);
            
            // Atualiza a lista na tela
            ItensEstoque.Insert(0, novoItem);

            // 2. Tenta sincronizar com o Firebase (Online)
            try 
            {
                await _firebaseService.SaveEstoqueAsync(novoItem);
                novoItem.IsSynced = true;
                await _dbService.SaveItemAsync(novoItem); // Marca como sincronizado localmente
            }
            catch (Exception ex)
            {
                // Se falhar (sem internet), o IsSynced continua false para tentarmos depois
                System.Diagnostics.Debug.WriteLine($"Erro sincronia Firebase: {ex.Message}");
            }
        }
    }
}