using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using CommunityToolkit.Maui.Views;
using Marmorariacentral.Models;
using Marmorariacentral.Services;
using Marmorariacentral.Views.Orcamentos;
using System.Collections.ObjectModel;
using System.Diagnostics;

namespace Marmorariacentral.ViewModels
{
    public partial class OrcamentoViewModel : ObservableObject
    {
        private readonly DatabaseService _dbService;
        private readonly FirebaseService _firebaseService;

        private ObservableCollection<Cliente> _clientes = new();
        public ObservableCollection<Cliente> Clientes 
        { 
            get => _clientes; 
            set => SetProperty(ref _clientes, value); 
        }

        public OrcamentoViewModel(DatabaseService dbService, FirebaseService firebaseService)
        {
            _dbService = dbService;
            _firebaseService = firebaseService;
            _ = CarregarDados();
        }

        [RelayCommand]
        public async Task CarregarDados()
        {
            try
            {
                var lista = await _dbService.GetItemsAsync<Cliente>();
                MainThread.BeginInvokeOnMainThread(() => 
                {
                    Clientes.Clear();
                    foreach (var c in lista.OrderBy(x => x.Nome)) 
                    {
                        Clientes.Add(c);
                    }
                });
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Erro ao carregar clientes: {ex.Message}");
            }
        }

        [RelayCommand]
        public async Task AbrirCadastroCliente()
        {
            await MainThread.InvokeOnMainThreadAsync(async () =>
            {
                try 
                {
                    var popup = new CadastroClientePopup();
                    var resultado = await Shell.Current.ShowPopupAsync(popup);

                    if (resultado is Cliente novo)
                    {
                        await _dbService.SaveItemAsync(novo);
                        _ = Task.Run(async () => {
                            try { await _firebaseService.SaveClienteAsync(novo); }
                            catch { }
                        });
                        await CarregarDados();
                    }
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"Erro ao abrir cadastro: {ex.Message}");
                }
            });
        }

        [RelayCommand]
        public async Task EditarCliente(Cliente cliente)
        {
            if (cliente == null) return;

            await MainThread.InvokeOnMainThreadAsync(async () =>
            {
                var popup = new CadastroClientePopup(cliente);
                var resultado = await Shell.Current.ShowPopupAsync(popup);

                if (resultado is Cliente editado)
                {
                    await _dbService.SaveItemAsync(editado);
                    _ = Task.Run(async () => {
                        try { await _firebaseService.SaveClienteAsync(editado); }
                        catch { }
                    });
                    await CarregarDados();
                }
            });
        }

        [RelayCommand]
        public async Task ExcluirCliente(Cliente cliente)
        {
            if (cliente == null) return;

            bool confirmar = await Shell.Current.DisplayAlert("Excluir", 
                $"Deseja remover permanentemente o cliente {cliente.Nome}?", "Sim", "Não");
            
            if (confirmar)
            {
                await _dbService.DeleteItemAsync(cliente);
                await CarregarDados();
            }
        }

        [RelayCommand]
        public async Task AbrirDetalhesCliente(Cliente cliente)
        {
            if (cliente == null) return;

            var navigationParameter = new Dictionary<string, object>
            {
                { "Cliente", cliente }
            };

            // AJUSTE: Rota corrigida de "Detalhe" para "Detalhes" para bater com AppShell.xaml.cs
            await Shell.Current.GoToAsync("DetalhesClientePage", navigationParameter);
        }
    }
}