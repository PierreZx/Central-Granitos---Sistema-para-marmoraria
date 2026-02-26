using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CommunityToolkit.Maui.Views;
using Marmorariacentral.Models;
using Marmorariacentral.Services;
using Marmorariacentral.Views.Estoque; 
using System.Collections.ObjectModel;
using System.Diagnostics;

#pragma warning disable CA1416 // Silencia avisos de compatibilidade de plataforma

namespace Marmorariacentral.ViewModels
{
    public partial class EstoqueViewModel : ObservableObject
    {
        private readonly DatabaseService _dbService;
        private readonly FirebaseService _firebaseService;

        private ObservableCollection<EstoqueItem> _itensEstoque = new();
        public ObservableCollection<EstoqueItem> ItensEstoque 
        { 
            get => _itensEstoque; 
            set => SetProperty(ref _itensEstoque, value); 
        }

        private bool _isBusy;
        public bool IsBusy 
        { 
            get => _isBusy; 
            set => SetProperty(ref _isBusy, value); 
        }

        public EstoqueViewModel(DatabaseService dbService, FirebaseService firebaseService)
        {
            _dbService = dbService;
            _firebaseService = firebaseService;
            _ = CarregarEstoque();
        }

        [RelayCommand]
        public async Task CarregarEstoque()
        {
            if (IsBusy) return;
            try
            {
                IsBusy = true;
                var lista = await _dbService.GetItemsAsync<EstoqueItem>();
                MainThread.BeginInvokeOnMainThread(() => 
                {
                    ItensEstoque.Clear();
                    foreach (var item in lista) ItensEstoque.Add(item);
                });
            }
            catch (Exception ex) { Debug.WriteLine(ex.Message); }
            finally { IsBusy = false; }
        }

        [RelayCommand]
        public async Task AbrirCadastro()
        {
            // O erro CS0246 morre aqui se o using acima estiver correto
            var popup = new CadastroChapaPopup();
            var resultado = await Shell.Current.ShowPopupAsync(popup);
            if (resultado is EstoqueItem novoItem) await SalvarItem(novoItem);
        }

        [RelayCommand]
        public async Task EditarItem(EstoqueItem item)
        {
            if (item == null) return;
            var popup = new CadastroChapaPopup(item);
            var resultado = await Shell.Current.ShowPopupAsync(popup);
            if (resultado is EstoqueItem itemEditado) await SalvarItem(itemEditado);
        }

        [RelayCommand]
        public async Task SalvarItem(EstoqueItem item)
        {
            await _dbService.SaveItemAsync(item);
            await CarregarEstoque();
            try { await _firebaseService.SaveEstoqueAsync(item); } catch { }
        }

        [RelayCommand]
        public async Task ExcluirItem(EstoqueItem item)
        {
            if (item == null) return;
            if (await Shell.Current.DisplayAlert("Atenção", $"Deseja excluir {item.NomeChapa}?", "Sim", "Não"))
            {
                await _dbService.DeleteItemAsync(item);
                await CarregarEstoque();
            }
        }
    }
}